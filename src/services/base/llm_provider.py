from abc import ABC, abstractmethod
from typing import Dict, Any

class LLMProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str, context: Dict[str, Any]) -> str:
        """Generate text based on prompt and context"""
        pass

    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the model configuration"""
        pass