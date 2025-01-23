import json
from typing import Dict, Any
from .base import OutputProvider

class JSONWriter(OutputProvider):
    def write(self, data: Dict[str, Any], file_path: str) -> None:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def get_format(self) -> str:
        return "json"