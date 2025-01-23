from services.base.vcs_provider import VCSProvider
from services.base.llm_provider import LLMProvider
from services.base.output_provider import OutputProvider
from models.test_case import TestCase
from models.pull_request import PullRequest
from utils.risk_analysis import analyze_diff
from rich.console import Console
from rich.panel import Panel
import yaml
from typing import List, Dict
import re
import logging

class TestCaseGenerator:
    def __init__(self, 
                 vcs_provider: VCSProvider, 
                 llm_provider: LLMProvider,
                 output_provider: OutputProvider):
        self.vcs_provider = vcs_provider
        self.llm_provider = llm_provider
        self.output_provider = output_provider
        self.console = Console()

    def generate(self, repo: str, pr_number: int, output_file: str) -> None:
        self.console.print(f"[bold blue]🚀 Generating test cases for PR #{pr_number}[/bold blue]")
        
        try:
            pr = self.vcs_provider.get_pull_request(repo, pr_number)
            risk_analysis = self._analyze_risk(pr)
            
            # Load and format prompt
            prompt = self._load_prompt()
            context = self._create_context(pr, risk_analysis)
            
            # Generate test cases
            self.console.print("[yellow]Generating test cases from LLM...[/yellow]")
            llm_output = self.llm_provider.generate(prompt, context)
            logging.debug(f"LLM Output: {llm_output}")
            
            # Parse test cases
            test_cases = self._parse_test_cases(llm_output)
            if not test_cases:
                self.console.print("[red]Warning: No test cases were generated[/red]")
            
            self._save_results(pr, risk_analysis, test_cases, output_file)
            self.console.print(f"\n[green]✅ Results saved to {output_file}[/green]")
            
        except Exception as e:
            self.console.print(f"[red]Error: {str(e)}[/red]")
            raise

    def _analyze_risk(self, pr: PullRequest) -> dict:
        return {
            "level": "High" if len(pr.changes["modified"]) > 5 else "Medium",
            "factors": [analyze_diff(diff) for diff in pr.diffs.values()]
        }

    def _create_context(self, pr: PullRequest, risk_analysis: dict) -> dict:
        return {
            "pr": {
                "number": pr.number,
                "title": pr.title,
                "description": pr.description,
                "changes": pr.changes,
                "diffs": pr.diffs
            },
            "risk_analysis": risk_analysis
        }

    def _load_prompt(self) -> str:
        with open('prompts/templates/test_case.txt', 'r') as f:
            return f.read()

    def _parse_test_cases(self, llm_output: str) -> List[Dict]:
        test_cases = []
        try:
            # Split into individual test cases
            case_blocks = re.split(r'TC-\d+:', llm_output)
            if not case_blocks[0].strip():
                case_blocks = case_blocks[1:]  # Remove empty first split
                
            for i, block in enumerate(case_blocks, 1):
                if not block.strip():
                    continue
                    
                # Extract fields using multiline patterns
                title_match = re.search(r'Title:\s*(.*?)(?=\n-|\Z)', block, re.MULTILINE)
                priority_match = re.search(r'Priority:\s*(.*?)(?=\n-|\Z)', block, re.MULTILINE)
                desc_match = re.search(r'Description:\s*(.*?)(?=\n-|\Z)', block, re.MULTILINE)
                
                # Extract steps as list
                steps = []
                steps_section = re.search(r'Steps:(.*?)(?=Expected Results:|\Z)', block, re.DOTALL)
                if steps_section:
                    steps = [
                        s.strip().lstrip('- ') 
                        for s in steps_section.group(1).strip().split('\n')
                        if s.strip() and s.strip().startswith('-')
                    ]
                
                # Extract expected results
                expected_match = re.search(r'Expected Results:\s*(.*?)(?=\n\n|\Z)', block, re.DOTALL)
                
                test_case = {
                    "id": f"TC-{i:03d}",
                    "title": title_match.group(1).strip() if title_match else "No title",
                    "priority": priority_match.group(1).strip() if priority_match else "Medium",
                    "description": desc_match.group(1).strip() if desc_match else "No description",
                    "steps": steps,
                    "expected_result": expected_match.group(1).strip() if expected_match else "No expected results"
                }
                test_cases.append(test_case)
                
        except Exception as e:
            self.logger.error(f"Error parsing test cases: {str(e)}")
            self.logger.debug(f"Raw LLM output:\n{llm_output}")
        
        return test_cases

    def _save_results(self, pr: PullRequest, risk_analysis: dict, test_cases: List[Dict], output_file: str) -> None:
        results = {
            "pr_number": pr.number,
            "pr_title": pr.title,
            "risk_analysis": risk_analysis,
            "test_cases": test_cases  # Already in dict format
        }
        self.output_provider.write(results, output_file)