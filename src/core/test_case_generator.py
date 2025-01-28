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
from typing import List, Dict, Any, Optional
import re
import logging
from itertools import zip_longest

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

    def _safe_get_value(self, data: Dict[str, Any], key: str, default: Any) -> Any:
        """Safely retrieve a value from a dictionary with logging."""
        try:
            return data.get(key, default)
        except Exception as e:
            self.logger.warning(f"Error getting {key}: {str(e)}")
            return default

    def _ensure_dict(self, data: Any, default: Optional[Dict] = None) -> Dict:
        """Ensure input is a dictionary with logging."""
        if default is None:
            default = {}
        if not isinstance(data, dict):
            self.logger.warning(f"Expected dict, got {type(data)}. Using default.")
            return default
        return data

    def generate(self, repo: str, pr_number: int, output_file: str) -> None:
        self.console.print(f"[bold blue]🚀 Generating test cases for PR #{pr_number}[/bold blue]")
        
        with self.console.status("[bold yellow]Analyzing PR...") as status:
            try:
                pr = self.vcs_provider.get_pull_request(repo, pr_number)
                self.logger.debug(f"PR Data: title='{pr.title}', description='{pr.description}'")
                
                risk_analysis = self._analyze_risk(pr)
                self.logger.debug(f"Risk Analysis Result: {risk_analysis}")
                
                self._display_risk_analysis(risk_analysis)
                
                status.update("[bold yellow]Generating test cases...")
                prompt = self._load_prompt()
                self.logger.debug(f"Loaded prompt template: {prompt[:100]}...")
                
                context = self._create_context(pr, risk_analysis)
                self.logger.debug(f"Created context: {context}")
                
                llm_output = self.llm_provider.generate(prompt, context)
                test_cases = self._parse_test_cases(llm_output)
                
                if not test_cases:
                    self.console.print("[red]Warning: No test cases were generated[/red]")
                
                self._save_results(pr, risk_analysis, test_cases, output_file)
                self.console.print(f"\n[green]✅ Results saved to {output_file}[/green]")
                
            except Exception as e:
                self.logger.error(f"Generation error: {str(e)}", exc_info=True)
                self.console.print(f"[red]Error: {str(e)}[/red]")
                raise

    def _analyze_risk(self, pr: PullRequest) -> Dict[str, Any]:
        """Analyze PR for risks and handle None values."""
        try:
            # Convert None values to empty dicts
            changes = {} if pr.changes is None else pr.changes
            diffs = {} if pr.diffs is None else pr.diffs
            
            # Ensure we have dictionaries
            changes = self._ensure_dict(changes, {"modified": []})
            diffs = self._ensure_dict(diffs, {"file": ""})
            
            self.logger.debug(f"Analyzing PR with changes: {changes}")
            self.logger.debug(f"Diffs: {diffs}")
            
            return self.risk_analyzer.analyze(changes, diffs)
        except Exception as e:
            self.logger.error(f"Error in risk analysis: {str(e)}")
            return self._create_error_analysis(str(e))

    def _create_error_analysis(self, error_msg: str) -> Dict[str, Any]:
        """Create a standardized error analysis response."""
        return {
            "level": "High",
            "factors": ["Analysis Error"],
            "details": [error_msg]
        }

    def _create_context(self, pr: PullRequest, risk_analysis: dict) -> dict:
        """Create focused context for test case generation."""
        # Format risk factors with details
        factors = risk_analysis.get("factors", [])
        details = risk_analysis.get("details", [])
        risk_factors = []
        for f, d in zip_longest(factors, details, fillvalue=""):
            if f and d:
                risk_factors.append(f"- {f}: {d}")
            elif f:
                risk_factors.append(f"- {f}")
        
        return {
            "pr_title": str(pr.title),
            "pr_description": str(pr.description),
            "risk_level": str(risk_analysis.get("level", "High")),
            "risk_factors": "\n".join(risk_factors),
            "changes": self._format_changes(pr.changes),
            "diffs": self._format_diffs(pr.diffs)
        }

    def _format_changes(self, changes: Dict[str, List[str]]) -> str:
        """Format changes in a more descriptive way for the LLM."""
        result = []
        if changes.get('added'):
            result.append("Added files:")
            result.extend(f"  - {f}" for f in changes['added'])
        if changes.get('modified'):
            result.append("Modified files:")
            result.extend(f"  - {f}" for f in changes['modified'])
        if changes.get('removed'):
            result.append("Removed files:")
            result.extend(f"  - {f}" for f in changes['removed'])
        return "\n".join(result) if result else "No file changes"

    def _format_diffs(self, diffs: Dict[str, str]) -> str:
        """Format diffs to highlight important code changes."""
        result = []
        for filename, diff in diffs.items():
            if diff:  # Only include files with actual changes
                result.append(f"File: {filename}")
                result.append("```diff")
                result.append(diff[:1000] if len(diff) > 1000 else diff)  # Limit diff size
                result.append("```\n")
        return "\n".join(result) if result else "No code changes available"

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
                
                fields = {
                    'title': r'Title:\s*([^\n]+)',
                    'priority': r'Priority:\s*([^\n]+)',
                    'description': r'Description:\s*([^\n]+)',
                }
                
                extracted_fields = {
                    field: re.search(pattern, block).group(1).strip() 
                    if re.search(pattern, block) else f"No {field}"
                    for field, pattern in fields.items()
                }
                
                steps = []
                steps_match = re.search(r'Steps:(.*?)(?=Expected Results:|$)', block, re.DOTALL)
                if steps_match:
                    steps = [
                        s.strip()[2:] for s in steps_match.group(1).splitlines() 
                        if s.strip().startswith('-')
                    ]
                
                expected_match = re.search(r'Expected Results:\s*([^\n]+(?:\n(?!\n).*)*)', block, re.DOTALL)
                
                test_cases.append({
                    "id": f"TC-{i:03d}",
                    **extracted_fields,
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

    def _save_results(self, pr: PullRequest, risk_analysis: dict, test_cases: List[Dict], output_file: str) -> None:
        results = {
            "pr_number": pr.number,
            "pr_title": pr.title,
            "risk_analysis": risk_analysis,
            "test_cases": test_cases
        }
        self.output_provider.write(results, output_file)

    def _display_risk_analysis(self, risk_analysis: Dict[str, Any]) -> None:
        table = Table(title="Risk Analysis Results")
        
        table.add_column("Category", style="cyan")
        table.add_column("Details", style="magenta")
        
        level = self._safe_get_value(risk_analysis, 'level', 'Unknown')
        table.add_row("Risk Level", f"[bold]{level}[/bold]")
        
        factors = self._safe_get_value(risk_analysis, 'factors', [])
        details = self._safe_get_value(risk_analysis, 'details', [])
        
        if factors and details:
            for factor, detail in zip(factors, details):
                table.add_row(str(factor), str(detail))
        elif factors:
            for factor in factors:
                table.add_row(str(factor), "")
        
        self.console.print("\n")
        self.console.print(table)
        self.console.print("\n")