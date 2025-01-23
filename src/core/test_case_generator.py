from services.base.vcs_provider import VCSProvider
from services.base.llm_provider import LLMProvider
from services.base.output_provider import OutputProvider
from models.test_case import TestCase
from models.pull_request import PullRequest
from utils.risk_analysis import analyze_diff
from rich.console import Console
from rich.panel import Panel
import yaml

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
            test_cases = self.llm_provider.generate(
                self._load_prompt(), 
                self._create_context(pr, risk_analysis)
            )
            
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

    def _save_results(self, pr: PullRequest, risk_analysis: dict, test_cases: str, output_file: str) -> None:
        results = {
            "pr_number": pr.number,
            "pr_title": pr.title,
            "risk_analysis": risk_analysis,
            "test_cases": test_cases
        }
        self.output_provider.write(results, output_file)