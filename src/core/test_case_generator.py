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
                self.console.print(f"[red]Error: {str(e)}[/red]")
                raise

    def _analyze_risk(self, pr: PullRequest) -> Dict[str, Any]:
        return self.risk_analyzer.analyze(pr.changes, pr.diffs)

    def _create_context(self, pr: PullRequest, risk_analysis: dict) -> dict:
        try:
            changes = pr.changes if isinstance(pr.changes, dict) else {"changes": str(pr.changes)}
            diffs = pr.diffs if isinstance(pr.diffs, dict) else {"diffs": str(pr.diffs)}
            
            return {
                "pr": {
                    "number": pr.number,
                    "title": pr.title,
                    "description": pr.description,
                    "base_branch": pr.base_branch,
                    "head_branch": pr.head_branch,
                    "changes": self._format_changes(changes),
                    "diffs": self._format_diffs(diffs)
                },
                "risk_analysis": {
                    "level": risk_analysis.get("level", "Unknown"),
                    "factors": risk_analysis.get("factors", []),
                    "details": risk_analysis.get("details", [])
                },
                "metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "generator_version": "1.0.0"
                }
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
            case_blocks = re.split(r'TC-\d+:', llm_output)
            if not case_blocks[0].strip():
                case_blocks = case_blocks[1:]
                
            for i, block in enumerate(case_blocks, 1):
                if not block.strip():
                    continue
                    
                # Extract fields with multiline support
                title = self._extract_field(block, r'Title:\s*(.*?)(?=\n-|$)', "No title")
                priority = self._extract_field(block, r'Priority:\s*(.*?)(?=\n-|$)', "Medium")
                description = self._extract_field(block, r'Description:\s*(.*?)(?=\n-|$)', "No description")
                
                # Extract steps as list
                steps = []
                steps_match = re.search(r'Steps:(.*?)(?=Expected Results:|$)', block, re.DOTALL)
                if steps_match:
                    steps = [s.strip()[2:] for s in steps_match.group(1).splitlines() if s.strip().startswith('-')]
                
                expected = self._extract_field(block, r'Expected Results:\s*(.*?)(?=\n\n|$)', "No expected results", re.DOTALL)
                
                test_cases.append({
                    "id": f"TC-{i:03d}",
                    "title": title,
                    "priority": priority,
                    "description": description,
                    "steps": steps,
                    "expected_result": expected,
                    "generated_at": datetime.now().isoformat(),
                    "approved": False,
                    "approved_by": None
                })
                
        except Exception as e:
            self.logger.error(f"Error parsing test cases: {str(e)}")
            self.logger.debug(f"Raw LLM output: {llm_output}")
            
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
        
        table.add_row("Risk Level", f"[bold]{risk_analysis['level']}[/bold]")
        
        for factor, detail in zip(risk_analysis['factors'], risk_analysis['details']):
            table.add_row(factor, detail)
        
        self.console.print("\n")
        self.console.print(table)
        self.console.print("\n")