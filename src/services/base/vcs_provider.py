from abc import ABC, abstractmethod
from models.pull_request import PullRequest
from typing import Dict

class VCSProvider(ABC):
    @abstractmethod
    def get_pull_request(self, repo: str, pr_number: int) -> PullRequest:
        pass
    
    @abstractmethod
    def get_diff(self, repo: str, pr_number: int) -> Dict[str, str]:
        pass