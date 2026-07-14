from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class FileChange(BaseModel):
    path: str
    additions: int = 0
    deletions: int = 0
    changeType: str = "modified"  # added, modified, deleted, renamed


class GitCommit(BaseModel):
    sha: str
    shortSha: str
    author: str
    authorEmail: str
    message: str
    timestamp: datetime
    service: str
    filesChanged: List[FileChange] = []
    totalAdditions: int = 0
    totalDeletions: int = 0


class GitDeployment(BaseModel):
    id: str
    version: str
    service: str
    environment: str = "production"
    timestamp: datetime
    deployer: str = "ci-bot"
    commitSha: str
    status: str = "success"  # success, failed, in_progress
    duration: str = "PT2M30S"


class GitRollback(BaseModel):
    id: str
    fromVersion: str
    toVersion: str
    service: str
    timestamp: datetime
    initiator: str
    reason: str


class GitResponse(BaseModel):
    recentCommits: List[GitCommit] = []
    recentDeployments: List[GitDeployment] = []
    rollbacks: List[GitRollback] = []
