import os
import yaml
import logging
from typing import Dict, Any
import re

def load_config(path: str) -> Dict[str, Any]:
    logger = logging.getLogger(__name__)
    
    if not os.path.exists(path):
        logger.error(f"Config file not found: {path}")
        raise FileNotFoundError(f"Config file not found: {path}")
        
    with open(path, 'r') as f:
        config = yaml.safe_load(f)
        
    if not config:
        raise ValueError("Empty config file")
        
    # Replace environment variables
    config = _replace_env_vars(config)
    
    return config

def _replace_env_vars(config: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively replace ${VAR} with environment variable values"""
    if isinstance(config, dict):
        return {k: _replace_env_vars(v) for k, v in config.items()}
    elif isinstance(config, list):
        return [_replace_env_vars(v) for v in config]
    elif isinstance(config, str):
        pattern = r'\${([^}]+)}'
        match = re.search(pattern, config)
        if match:
            env_var = match.group(1)
            env_value = os.getenv(env_var)
            if not env_value:
                raise ValueError(f"Environment variable {env_var} not set")
            return config.replace(match.group(0), env_value)
    return config