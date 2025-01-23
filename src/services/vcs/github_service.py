from github import Github
from models.pull_request import PullRequest
from services.base.vcs_provider import VCSProvider
from typing import Dict, List

class GitHubService(VCSProvider):
    def __init__(self, token: str):
        self.client = Github(token)

    def get_pull_request(self, repo: str, pr_number: int) -> PullRequest:
        repo = self.client.get_repo(repo)
        pr = repo.get_pull(pr_number)
        return PullRequest(
            number=pr_number,
            title=pr.title,
            description=pr.body or "",
            changes=self._get_changes(pr),
            diffs=self._get_diffs(pr),
            base_branch=pr.base.ref,
            head_branch=pr.head.ref
        )

    def get_diff(self, repo: str, pr_number: int) -> Dict[str, str]:
        """Implement the abstract method get_diff"""
        repo = self.client.get_repo(repo)
        pr = repo.get_pull(pr_number)
        return {f.filename: f.patch for f in pr.get_files()}

    def _get_changes(self, pr) -> Dict[str, List[str]]:
        files = pr.get_files()
        return {
            "added": [f.filename for f in files if f.status == "added"],
            "modified": [f.filename for f in files if f.status == "modified"],
            "removed": [f.filename for f in files if f.status == "removed"]
        }

    def _get_diffs(self, pr) -> Dict[str, str]:
        return {f.filename: f.patch for f in pr.get_files()}