from dataclasses import dataclass
from typing import List

@dataclass
class TestCase:
    title: str
    description: str
    steps: List[str]
    expected_result: str