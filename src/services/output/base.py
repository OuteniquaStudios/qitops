from abc import ABC, abstractmethod
from typing import Dict, Any

class OutputProvider(ABC):
    def write(self, data: Dict[str, Any], file_path: str) -> None:
        """Template method that formats data and delegates writing"""
        formatted_data = self._format_data(data)
        self._write_formatted(formatted_data, file_path)
    
    def _format_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Common data formatting logic"""
        return {
            "pr_number": data["pr_number"],
            "pr_title": data["pr_title"],
            "risk_analysis": data["risk_analysis"],
            "test_cases": data["test_cases"]  # Already in correct format
        }
    
    @abstractmethod
    def _write_formatted(self, formatted_data: Dict[str, Any], file_path: str) -> None:
        """Format-specific write implementation"""
        pass

    @abstractmethod
    def get_format(self) -> str:
        """Get format identifier"""
        pass