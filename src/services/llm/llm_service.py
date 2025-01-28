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
            # Log the raw inputs
            self.logger.debug("=== START PROMPT FORMATTING ===")
            self.logger.debug(f"Raw context keys: {list(context.keys())}")
            self.logger.debug(f"Raw context values: {context}")
            
            # Create formatted context with explicit type conversion to strings
            formatted_context = {
                'pr_title': str(context.get('pr_title', 'No title')),
                'pr_description': str(context.get('pr_description', 'No description')),
                'risk_level': str(context.get('risk_level', 'Unknown')),
                'risk_factors': str(context.get('risk_factors', 'None')),
                'changes': str(context.get('changes', '')),
                'diffs': str(context.get('diffs', ''))
            }
            
            self.logger.debug("=== FORMATTED CONTEXT ===")
            for key, value in formatted_context.items():
                self.logger.debug(f"{key}: {value[:100]}...")  # Log first 100 chars of each value
            
            # Format the prompt
            formatted_prompt = prompt.format(**formatted_context)
            
            self.logger.debug("=== FORMATTING COMPLETE ===")
            return formatted_prompt
            
        except KeyError as e:
            self.logger.error(f"KeyError in prompt formatting: {e}")
            self.logger.error(f"Available context keys: {list(context.keys())}")
            self.logger.error(f"Required keys: {['pr_title', 'pr_description', 'risk_level', 'risk_factors', 'changes', 'diffs']}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error in prompt formatting: {str(e)}")
            self.logger.error(f"Context: {context}")
            self.logger.error(f"Prompt template: {prompt}")
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