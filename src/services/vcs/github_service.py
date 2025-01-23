from github import Github
from models.pull_request import PullRequest
from services.base.vcs_provider import VCSProvider
from typing import Dict, List
import logging

class GitHubService(VCSProvider):
    def __init__(self, token: str):
        self.client = Github(token)
        self.logger = logging.getLogger(__name__)

    def get_pull_request(self, repo: str, pr_number: int) -> PullRequest:
        try:
            repository = self.client.get_repo(repo)
            pr = repository.get_pull(pr_number)
            
            return PullRequest(
                number=pr_number,
                title=pr.title,
                description=pr.body or "",
                changes=self._get_changes(pr),
                diffs=self._get_diffs(pr),  # Use private method
                base_branch=pr.base.ref,
                head_branch=pr.head.ref
            )
        except Exception as e:
            self.logger.error(f"Error fetching PR {pr_number} from {repo}: {str(e)}")
            raise

    def get_diff(self, repo: str, pr_number: int) -> Dict[str, str]:
        """Public method for getting diffs directly"""
        repository = self.client.get_repo(repo)
        pr = repository.get_pull(pr_number)
        return self._get_diffs(pr)

    def _get_diffs(self, pr) -> Dict[str, str]:
        """Private method for getting diffs from PR object"""
        return {f.filename: f.patch for f in pr.get_files()}

    def _get_changes(self, pr) -> Dict[str, List[str]]:
        files = pr.get_files()
        return {
            "added": [f.filename for f in files if f.status == "added"],
            "modified": [f.filename for f in files if f.status == "modified"],
            "removed": [f.filename for f in files if f.status == "removed"]
        }