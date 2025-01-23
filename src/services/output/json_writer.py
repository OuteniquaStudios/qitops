import json
from typing import Dict, Any
from .base import OutputProvider

class JSONWriter(OutputProvider):
    def _write_formatted(self, formatted_data: Dict[str, Any], file_path: str) -> None:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(formatted_data, f, indent=2)

    def get_format(self) -> str:
        return "json"