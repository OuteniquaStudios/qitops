import litellm
from typing import Dict, Any
import logging
from services.base.llm_provider import LLMProvider

class LLMService(LLMProvider):
    def __init__(self, model: str, temperature: float):
        self.model = model
        self.temperature = temperature
        self.logger = logging.getLogger(__name__)

    def generate(self, prompt: str, context: Dict[str, Any]) -> str:
        formatted_prompt = self._format_prompt(prompt, context)
        self.logger.debug(f"Formatted prompt:\n{formatted_prompt}")
        
        response = litellm.completion(
            model=self.model,
            messages=[{
                "role": "user",
                "content": formatted_prompt
            }],
            temperature=self.temperature
        )
        
        result = response.choices[0].message.content
        self.logger.debug(f"LLM Response:\n{result}")
        return result

    def _format_prompt(self, prompt: str, context: Dict[str, Any]) -> str:
        try:
            return prompt.format(
                pr_title=context.get('pr_title', ''),
                pr_description=context.get('pr_description', ''),
                risk_level=context.get('risk_level', ''),
                risk_factors=context.get('risk_factors', ''),
                changes=context.get('changes', ''),
                diffs=context.get('diffs', '')
            )
        except KeyError as e:
            self.logger.error(f"Missing required key in context: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error formatting prompt: {e}")
            raise

    def _format_changes(self, changes: Dict[str, Any]) -> str:
        result = []
        for change_type, files in changes.items():
            if files:
                result.append(f"{change_type.capitalize()}:")
                result.extend(f"- {file}" for file in files)
        return "\n".join(result)

    def _format_diffs(self, diffs: Dict[str, str]) -> str:
        result = []
        for filename, diff in diffs.items():
            result.append(f"File: {filename}")
            result.append(diff)
        return "\n".join(result)

    def get_model_info(self) -> Dict[str, Any]:
        return {
            "name": self.model,
            "temperature": self.temperature,
            "provider": "litellm"
        }