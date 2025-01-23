import litellm
from typing import Dict, Any
from services.base.llm_provider import LLMProvider

class LLMService(LLMProvider):
    def __init__(self, model: str, temperature: float):
        self.model = model
        self.temperature = temperature

    def generate(self, prompt: str, context: Dict[str, Any]) -> str:
        response = litellm.completion(
            model=self.model,
            messages=[{
                "role": "user",
                "content": f"{prompt}\n\nContext:\n{context}"
            }],
            temperature=self.temperature
        )
        return response.choices[0].message.content

    def get_model_info(self) -> Dict[str, Any]:
        return {
            "name": self.model,
            "temperature": self.temperature,
            "provider": "litellm"
        }