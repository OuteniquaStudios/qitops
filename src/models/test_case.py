from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime

@dataclass
class TestCase:
    id: str
    title: str
    priority: str
    description: str
    steps: List[str]
    expected_result: str
    generated_at: datetime = datetime.now()
    approved: bool = False
    approved_by: Optional[str] = None
    risk_factors: List[str] = None