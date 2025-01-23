from dataclasses import dataclass
from typing import List

@dataclass
class TestCase:
    id: str
    title: str
    priority: str
    description: str
    steps: List[str]
    expected_result: str