from typing import Dict, Any, TypeVar, Generic
from services.base.vcs_provider import VCSProvider
from services.base.llm_provider import LLMProvider 
from services.base.output_provider import OutputProvider
from .registry import ProviderRegistry

T = TypeVar('T')

class ProviderFactory(Generic[T]):
    def __init__(self, registry: ProviderRegistry):
        self.registry = registry
    
    def create(self, provider_type: str, **kwargs) -> T:
        provider_class = self.registry.get_provider(provider_type)
        provider_config = self.registry.get_config(provider_type)
        config = {**provider_config, **kwargs}
        return provider_class(**config)

class FactoryManager:
    def __init__(self):
        self.vcs_registry = ProviderRegistry()
        self.llm_registry = ProviderRegistry()
        self.output_registry = ProviderRegistry()
        
        self.vcs_factory = ProviderFactory[VCSProvider](self.vcs_registry)
        self.llm_factory = ProviderFactory[LLMProvider](self.llm_registry)
        self.output_factory = ProviderFactory[OutputProvider](self.output_registry)
    
    def configure(self, config: Dict[str, Any]) -> None:
        """Configure providers with settings from config file"""
        for provider_type, provider_config in config.get('providers', {}).items():
            if provider_type in ['vcs', 'llm', 'output']:
                registry = getattr(self, f"{provider_type}_registry")
                for name, cfg in provider_config.items():
                    # Register provider with its config in one step
                    if provider_type == 'vcs' and name == 'github':
                        from services.vcs.github_service import GitHubService
                        registry.register(name, GitHubService, cfg)
                    elif provider_type == 'llm' and name == 'litellm':
                        from services.llm.llm_service import LLMService
                        registry.register(name, LLMService, cfg)
                    elif provider_type == 'output' and name == 'yaml':
                        from services.output.yaml_writer import YAMLWriter
                        registry.register(name, YAMLWriter, cfg)
                    elif provider_type == 'output' and name == 'json':
                        from services.output.json_writer import JSONWriter
                        registry.register(name, JSONWriter, cfg)

# Global factory manager instance
factory_manager = FactoryManager()