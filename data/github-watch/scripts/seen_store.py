"""
Gestion des repos deja vus pour GitHub Watch.
Stocke dans ~/.openclaw/data/github-watch/seen.json
"""

import json
import os
from pathlib import Path
from datetime import datetime

DEFAULT_PATH = os.path.expanduser("~/.openclaw/data/github-watch/seen.json")


class GitHubStore:
    def __init__(self, filepath=DEFAULT_PATH):
        self.filepath = Path(filepath)
        self.data = {}
        self.load()

    def load(self):
        if self.filepath.exists():
            try:
                with open(self.filepath) as f:
                    self.data = json.load(f)
            except Exception:
                self.data = {}
        else:
            self.data = {}

    def save(self):
        self.filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(self.filepath, "w") as f:
            json.dump(self.data, f, indent=2)

    def mark_seen(self, repo_name):
        """Mark a repo as seen. Call AFTER agent selection, not during filtering."""
        self.data[repo_name] = datetime.utcnow().isoformat()
        self.save()

    def is_seen(self, repo_name):
        return repo_name in self.data

    def filter_unseen(self, repos, key_fn=None):
        """
        Return (repos_unseen, nb_skipped).
        Does NOT mark repos as seen - call mark_seen() explicitly after agent selection.
        key_fn: extract key from repo dict (default: repo["name"])
        """
        if key_fn is None:
            key_fn = lambda r: r

        unseen = []
        skipped = 0
        for repo in repos:
            key = key_fn(repo)
            if self.is_seen(key):
                skipped += 1
            else:
                unseen.append(repo)

        return unseen, skipped


# Singleton global
github_store = GitHubStore()
