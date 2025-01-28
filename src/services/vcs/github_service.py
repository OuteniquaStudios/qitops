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
        """Get pull request with complete information."""
        try:
            repo = self.client.get_repo(repo)
            pr = repo.get_pull(pr_number)
            
            return PullRequest(
                number=pr.number,
                title=pr.title,
                description=pr.body or '',
                changes=self._get_changes(pr),
                diffs=self._get_diffs(pr),
                base_branch=pr.base.ref,
                head_branch=pr.head.ref
            )
        except Exception as e:
            self.logger.error(f"Error getting PR: {e}")
            raise

    def get_diff(self, repo: str, pr_number: int) -> Dict[str, str]:
        """Public method for getting diffs directly"""
        repository = self.client.get_repo(repo)
        pr = repository.get_pull(pr_number)
        return self._get_diffs(pr)

    def _get_diffs(self, pr) -> Dict[str, str]:
        """Get the diff content for each file in the PR."""
        try:
            files = pr.get_files()
            return {
                f.filename: f.patch if f.patch else ''
                for f in files
            }
        except Exception as e:
            self.logger.error(f"Error getting diffs: {e}")
            return {}

    def _get_changes(self, pr) -> Dict[str, List[str]]:
        files = pr.get_files()
        return {
            "added": [f.filename for f in files if f.status == "added"],
            "modified": [f.filename for f in files if f.status == "modified"],
            "removed": [f.filename for f in files if f.status == "removed"]
        }