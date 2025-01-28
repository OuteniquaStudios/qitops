from typing import Dict, List, Any, Union
from enum import Enum
import re
import logging

class RiskLevel(Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"

class RiskAnalyzer:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.security_patterns = [
            r'auth\w*',
            r'password',
            r'secret',
            r'token',
            r'crypt'
        ]
        self.breaking_patterns = [
            r'break.*change',
            r'deprecat\w*',
            r'remov\w+\s+\w+',
            r'delet\w+\s+\w+'
        ]

    def analyze(self, changes: Union[Dict[str, List[str]], str], diffs: Union[Dict[str, str], str]) -> Dict[str, Any]:
        try:
            # Normalize inputs
            changes_dict = changes if isinstance(changes, dict) else {"modified": [str(changes)]}
            diffs_dict = diffs if isinstance(diffs, dict) else {"file": str(diffs)}
            
            risk_factors = []
            details = []

            # Check security risks
            if self._check_security_risks(diffs_dict):
                risk_factors.append("Security Risk")
                details.append("Security-sensitive code changes detected")

            # Check dependency changes
            if self._check_dependency_changes(changes_dict):
                risk_factors.append("Dependency Changes")
                details.append("Package dependencies modified")

            # Check breaking changes
            if self._check_breaking_changes(diffs_dict):
                risk_factors.append("Breaking Changes")
                details.append("Breaking changes detected")

            level = self._determine_risk_level(risk_factors)
            
            return {
                "level": level,
                "factors": risk_factors,
                "details": details
            }
        except Exception as e:
            self.logger.error(f"Error in risk analysis: {e}")
            return {
                "level": "High",
                "factors": ["Analysis Error"],
                "details": [str(e)]
            }

    def _check_security_risks(self, diffs: Dict[str, str]) -> bool:
        return any(
            any(re.search(pattern, content, re.I) for pattern in self.security_patterns)
            for content in diffs.values()
        )

    def _check_dependency_changes(self, changes: Dict[str, List[str]]) -> bool:
        dependency_files = ['requirements.txt', 'package.json', 'build.gradle', 'pom.xml']
        modified = changes.get('modified', [])
        return any(dep in str(file) for dep in dependency_files for file in modified)

    def _check_breaking_changes(self, diffs: Dict[str, str]) -> bool:
        return any(
            any(re.search(pattern, content, re.I) for pattern in self.breaking_patterns)
            for content in diffs.values()
        )

    def _determine_risk_level(self, factors: List[str]) -> str:
        return "High" if len(factors) >= 2 else "Medium" if factors else "Low"