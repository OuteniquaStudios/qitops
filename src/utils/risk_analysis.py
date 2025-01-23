from enum import Enum

class RiskLevel(Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"

def analyze_diff(diff_content):
    """Analyze diff content for risk patterns."""
    risk_patterns = {
        "sql": "Database changes",
        "await": "Async flow changes",
        "try": "Error handling changes",
        "import": "Dependency changes",
        "class": "Class structure changes",
        "function": "Function signature changes"
    }

    found_patterns = []
    for pattern, risk in risk_patterns.items():
        if pattern in diff_content.lower():
            found_patterns.append(risk)

    return found_patterns