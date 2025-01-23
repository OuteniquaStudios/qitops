from abc import ABC, abstractmethod
from typing import Dict, Any

class OutputProvider(ABC):
    @abstractmethod
    def write(self, data: Dict[str, Any], file_path: str) -> None:
        pass
    
    @abstractmethod
    def get_format(self) -> str:
        pass