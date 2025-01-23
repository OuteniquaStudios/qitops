import yaml
from typing import Dict, Any
from .base import OutputProvider

class YAMLWriter(OutputProvider):
    def write(self, data: Dict[str, Any], file_path: str) -> None:
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, sort_keys=False, allow_unicode=True)

    def get_format(self) -> str:
        return "yaml"