from typing import Dict, Type, Any, List
from services.base.vcs_provider import VCSProvider
from services.base.llm_provider import LLMProvider
from services.base.output_provider import OutputProvider

class ProviderRegistry:
    """Registry for managing provider implementations."""
    
    def __init__(self):
        self._providers: Dict[str, Type] = {}
        self._configs: Dict[str, Dict[str, Any]] = {}
    
    def register(self, name: str, provider: Type, config: Dict[str, Any] = None) -> None:
        """Register a new provider implementation."""
        if not name or not isinstance(name, str):
            raise ValueError("Provider name must be a non-empty string")
        
        if name not in self._providers:
            self._providers[name] = provider
            if config:
                self._configs[name] = config
        else:
            # Update config if provider exists
            self.update_config(name, config)
    
    def update_config(self, name: str, config: Dict[str, Any]) -> None:
        """Update configuration for existing provider"""
        if name not in self._providers:
            raise KeyError(f"Provider '{name}' not found")
        if isinstance(config, dict):
            self._configs[name] = config
        else:
            raise ValueError(f"Config must be a dictionary, got {type(config)}")

    def get_provider(self, name: str) -> Type:
        """Get a provider implementation by name."""
        return self._providers.get(name)

    def get_config(self, name: str) -> Dict[str, Any]:
        """Get provider configuration by name."""
        return self._configs.get(name, {})

    def list_providers(self) -> List[str]:
        """List all registered providers."""
        return list(self._providers.keys())