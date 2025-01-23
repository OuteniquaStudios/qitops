from abc import ABC, abstractmethod
from typing import Dict, Any

class OutputProvider(ABC):
    @abstractmethod
    def write(self, data: Dict[str, Any], file_path: str) -> None:
        """Write data to file in specified format"""
        pass

    @abstractmethod
    def get_format(self) -> str:
        """Return format identifier"""
        pass