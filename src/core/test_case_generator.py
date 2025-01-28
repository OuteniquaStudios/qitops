from datetime import datetime
from services.base.vcs_provider import VCSProvider
from services.base.llm_provider import LLMProvider
from services.base.output_provider import OutputProvider
from models.test_case import TestCase
from models.pull_request import PullRequest
from utils.risk_analyzer import RiskAnalyzer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
import yaml
from typing import List, Dict, Any
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
        self.risk_analyzer = RiskAnalyzer()
        self.console = Console()
        self.logger = logging.getLogger(__name__)

    def generate(self, repo: str, pr_number: int, output_file: str) -> None:
        self.console.print(f"[bold blue]🚀 Generating test cases for PR #{pr_number}[/bold blue]")
        
        with self.console.status("[bold yellow]Analyzing PR...") as status:
            try:
                pr = self.vcs_provider.get_pull_request(repo, pr_number)
                risk_analysis = self._analyze_risk(pr)
                self._display_risk_analysis(risk_analysis)
                
                status.update("[bold yellow]Generating test cases...")
                prompt = self._load_prompt()
                context = self._create_context(pr, risk_analysis)
                
                llm_output = self.llm_provider.generate(prompt, context)
                test_cases = self._parse_test_cases(llm_output)
                
                if not test_cases:
                    self.console.print("[red]Warning: No test cases were generated[/red]")
                
                self._save_results(pr, risk_analysis, test_cases, output_file)
                self.console.print(f"\n[green]✅ Results saved to {output_file}[/green]")
                
            except Exception as e:
                self.logger.error(f"Generation error: {str(e)}")
                self.console.print(f"[red]Error: {str(e)}[/red]")
                raise

    def _analyze_risk(self, pr: PullRequest) -> Dict[str, Any]:
        return self.risk_analyzer.analyze(pr.changes, pr.diffs)

    def _create_context(self, pr: PullRequest, risk_analysis: dict) -> dict:
        try:
            # Ensure risk_analysis is a dict
            if not isinstance(risk_analysis, dict):
                self.logger.warning(f"Invalid risk_analysis type: {type(risk_analysis)}")
                risk_analysis = {
                    "level": "Unknown",
                    "factors": [],
                    "details": []
                }
            
            # Format risk factors safely using 'factors' instead of 'risk_factors'
            factors = risk_analysis.get("factors", [])
            risk_factors = ", ".join(str(f) for f in factors) if factors else "None"
            
            return {
                "pr_title": pr.title,
                "pr_description": pr.description,
                "risk_level": risk_analysis.get("level", "Unknown"),
                "risk_factors": risk_factors,
                "changes": self._format_changes(pr.changes),
                "diffs": self._format_diffs(pr.diffs)
            }
        except Exception as e:
            self.logger.error(f"Error creating context: {e}")
            raise

    def _format_changes(self, changes: Dict[str, Any]) -> str:
        try:
            if not isinstance(changes, dict):
                return str(changes)
            
            formatted = []
            for change_type, files in changes.items():
                if isinstance(files, list):
                    formatted.append(f"{change_type.capitalize()}:")
                    formatted.extend(f"  - {file}" for file in files)
                else:
                    formatted.append(f"{change_type}: {files}")
            return "\n".join(formatted)
        except Exception as e:
            self.logger.error(f"Error formatting changes: {e}")
            return str(changes)

    def _format_diffs(self, diffs: Dict[str, Any]) -> str:
        try:
            if not isinstance(diffs, dict):
                return str(diffs)
                
            formatted = []
            for file_path, diff in diffs.items():
                formatted.extend([
                    f"File: {file_path}",
                    "```diff",
                    str(diff).strip(),
                    "```\n"
                ])
            return "\n".join(formatted)
        except Exception as e:
            self.logger.error(f"Error formatting diffs: {e}")
            return str(diffs)

    def _load_prompt(self) -> str:
        with open('prompts/templates/test_case.txt', 'r') as f:
            return f.read()

    def _parse_test_cases(self, llm_output: str) -> List[Dict]:
        test_cases = []
        try:
            # Split into individual test cases
            case_blocks = re.split(r'TC-\d+:', llm_output)
            if not case_blocks[0].strip():
                case_blocks = case_blocks[1:]
                
            for i, block in enumerate(case_blocks, 1):
                if not block.strip():
                    continue
                    
                # Extract fields with improved regex patterns
                title_match = re.search(r'Title:\s*([^\n]+)', block)
                priority_match = re.search(r'Priority:\s*([^\n]+)', block)
                description_match = re.search(r'Description:\s*([^\n]+)', block)
                
                # Extract steps as list
                steps = []
                steps_match = re.search(r'Steps:(.*?)(?=Expected Results:|$)', block, re.DOTALL)
                if steps_match:
                    steps = [
                        s.strip()[2:] for s in steps_match.group(1).splitlines() 
                        if s.strip().startswith('-')
                    ]
                
                expected_match = re.search(r'Expected Results:\s*([^\n]+(?:\n(?!\n).*)*)', block, re.DOTALL)
                
                self.logger.debug(f"Title match: {title_match.group(1) if title_match else 'No match'}")
                
                test_cases.append({
                    "id": f"TC-{i:03d}",
                    "title": title_match.group(1).strip() if title_match else "No title",
                    "priority": priority_match.group(1).strip() if priority_match else "Medium",
                    "description": description_match.group(1).strip() if description_match else "No description",
                    "steps": steps,
                    "expected_result": expected_match.group(1).strip() if expected_match else "No expected results",
                    "generated_at": datetime.now().isoformat(),
                    "approved": False,
                    "approved_by": None
                })
                
        except Exception as e:
            self.logger.error(f"Error parsing test cases: {str(e)}")
            self.logger.debug(f"Raw LLM output:\n{llm_output}")
            
        return test_cases

    def _extract_field(self, text: str, pattern: str, default: str, flags: re.RegexFlag = 0) -> str:
        match = re.search(pattern, text, flags)
        return match.group(1).strip() if match else default

    def _save_results(self, pr: PullRequest, risk_analysis: dict, test_cases: List[Dict], output_file: str) -> None:
        results = {
            "pr_number": pr.number,
            "pr_title": pr.title,
            "risk_analysis": risk_analysis,
            "test_cases": test_cases  # Already in dict format
        }
        self.output_provider.write(results, output_file)

    def _display_risk_analysis(self, risk_analysis: Dict[str, Any]) -> None:
        table = Table(title="Risk Analysis Results")
        
        table.add_column("Category", style="cyan")
        table.add_column("Details", style="magenta")
        
        # Safely get risk level
        level = risk_analysis.get('level', 'Unknown')
        table.add_row("Risk Level", f"[bold]{level}[/bold]")
        
        # Safely handle factors and details
        factors = risk_analysis.get('factors', [])
        details = risk_analysis.get('details', [])
        
        # If we have both factors and details, zip them
        if factors and details:
            for factor, detail in zip(factors, details):
                table.add_row(str(factor), str(detail))
        # Otherwise just show factors
        elif factors:
            for factor in factors:
                table.add_row(str(factor), "")
        
        self.console.print("\n")
        self.console.print(table)
        self.console.print("\n")