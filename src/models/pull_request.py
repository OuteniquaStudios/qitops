from dataclasses import dataclass
from typing import Dict, List

@dataclass
class PullRequest:
    number: int
    title: str
    description: str
    changes: Dict[str, List[str]]
    diffs: Dict[str, str]
    base_branch: str
    head_branch: str