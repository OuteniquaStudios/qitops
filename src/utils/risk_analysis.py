from enum import Enum
from typing import Dict, List, Any
import re

class RiskLevel(Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"

class RiskFactor(Enum):
    DEPENDENCY = "Dependency Changes"
    SECURITY = "Security Impact"
    BREAKING = "Breaking Changes"
    COVERAGE = "Test Coverage"

def analyze_risk(changes: Dict[str, List[str]], diffs: Dict[str, str]) -> Dict[str, Any]:
    risk_factors = []
    
    # Check dependency changes
    if any('requirements.txt' in file or 'package.json' in file for file in changes.get('modified', [])):
        risk_factors.append(RiskFactor.DEPENDENCY.value)
    
    # Check security patterns
    security_patterns = [
        r'auth[orization]*',
        r'password',
        r'secret',
        r'token',
        r'crypt'
    ]
    
    if any(re.search('|'.join(security_patterns), diff, re.I) for diff in diffs.values()):
        risk_factors.append(RiskFactor.SECURITY.value)
    
    # Determine risk level
    risk_level = RiskLevel.LOW
    if len(risk_factors) >= 2:
        risk_level = RiskLevel.HIGH
    elif len(risk_factors) == 1:
        risk_level = RiskLevel.MEDIUM
    
    return {
        "level": risk_level.value,
        "factors": risk_factors
    }