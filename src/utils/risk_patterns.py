from enum import Enum
from typing import List, Pattern
import re

class RiskPatternType(Enum):
    SECURITY = "security"
    BREAKING = "breaking"
    PERFORMANCE = "performance"
    COMPLEXITY = "complexity"

class RiskPattern:
    def __init__(self, pattern: str, risk_type: RiskPatternType, weight: int = 1):
        self.pattern = re.compile(pattern, re.IGNORECASE)
        self.type = risk_type
        self.weight = weight

RISK_PATTERNS = [
    RiskPattern(r'auth|login|password|secret|token', RiskPatternType.SECURITY, 3),
    RiskPattern(r'break.*change|deprecat|remove[d]?\s+\w+', RiskPatternType.BREAKING, 2),
    RiskPattern(r'performance|optimize|slow|fast', RiskPatternType.PERFORMANCE, 2),
    RiskPattern(r'complex|complicated|confusing', RiskPatternType.COMPLEXITY, 1)
]