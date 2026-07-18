#!/usr/bin/env python3
import argparse
import json
import os
from copy import deepcopy
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen


REPOSITORIES = ("planarian", "ForkNeo", "api-image-neo")
MAX_SNAPSHOTS = 730
HISTORY_KEYS = {"version", "snapshots"}
SNAPSHOT_KEYS = {"date", "repos"}


def validate_counts(counts: dict) -> dict[str, int]:
    if not isinstance(counts, dict) or set(counts) != set(REPOSITORIES):
        raise ValueError("repo keys must exactly match configured repositories")
    normalized = {}
    for repository in REPOSITORIES:
        value = counts[repository]
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            raise ValueError(f"invalid star count for {repository}")
        normalized[repository] = value
    return normalized


def validate_snapshot_date(value: object) -> date:
    if not isinstance(value, str):
        raise ValueError("snapshot date must be a string in YYYY-MM-DD form")
    try:
        parsed = date.fromisoformat(value)
    except ValueError as error:
        raise ValueError(f"invalid snapshot date {value!r}: {error}") from error
    if parsed.isoformat() != value:
        raise ValueError(f"snapshot date must use canonical YYYY-MM-DD form: {value!r}")
    return parsed


def validate_history(history: dict) -> dict:
    if not isinstance(history, dict):
        raise ValueError("history root must be an object")
    if set(history) != HISTORY_KEYS:
        raise ValueError("history root keys must exactly match the version-1 schema")
    version = history["version"]
    if not isinstance(version, int) or isinstance(version, bool) or version != 1:
        raise ValueError("history version must be the integer 1")
    snapshots = history["snapshots"]
    if not isinstance(snapshots, list):
        raise ValueError("history snapshots must be a list")
    if len(snapshots) > MAX_SNAPSHOTS:
        raise ValueError(f"history cannot contain more than {MAX_SNAPSHOTS} snapshots")
    previous_date = None
    for index, snapshot in enumerate(snapshots):
        if not isinstance(snapshot, dict):
            raise ValueError(f"snapshot {index} must be an object")
        if set(snapshot) != SNAPSHOT_KEYS:
            raise ValueError(
                f"snapshot {index} keys must exactly match the version-1 schema"
            )
        snapshot_date = validate_snapshot_date(snapshot["date"])
        if previous_date is not None:
            if snapshot_date == previous_date:
                raise ValueError(f"duplicate snapshot date: {snapshot['date']}")
            if snapshot_date < previous_date:
                raise ValueError("history snapshots must be ordered by ascending date")
        validate_counts(snapshot["repos"])
        previous_date = snapshot_date
    return history


def load_history(path: Path) -> dict:
    if not path.is_file():
        return {"version": 1, "snapshots": []}
    try:
        history = json.loads(path.read_text(encoding="utf-8"))
        return validate_history(history)
    except ValueError as error:
        raise ValueError(f"invalid Star history at {path}: {error}") from error


def fetch_star_counts(
    owner: str,
    repositories: tuple[str, ...],
    token: str,
) -> dict[str, int]:
    if not token:
        raise ValueError("GITHUB_TOKEN is required")
    counts = {}
    for repository in repositories:
        request = Request(
            f"https://api.github.com/repos/{owner}/{repository}",
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {token}",
                "User-Agent": "alexliluz-profile-assets",
                "X-GitHub-Api-Version": "2026-03-10",
            },
        )
        with urlopen(request, timeout=20) as response:
            payload = json.loads(response.read().decode("utf-8"))
        count = payload.get("stargazers_count")
        if not isinstance(count, int) or isinstance(count, bool) or count < 0:
            raise ValueError(f"missing or invalid stargazers_count for {repository}")
        counts[repository] = count
    return counts


def update_history(history: dict, snapshot_date: str, counts: dict) -> dict:
    validate_history(history)
    validate_snapshot_date(snapshot_date)
    normalized = validate_counts(counts)
    updated = deepcopy(history)
    updated["snapshots"] = [
        snapshot
        for snapshot in updated["snapshots"]
        if snapshot["date"] != snapshot_date
    ]
    updated["snapshots"].append({"date": snapshot_date, "repos": normalized})
    updated["snapshots"].sort(key=lambda item: item["date"])
    updated["snapshots"] = updated["snapshots"][-MAX_SNAPSHOTS:]
    return updated


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--history", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--owner", default="alexliluz")
    parser.add_argument("--date")
    arguments = parser.parse_args()
    snapshot_date = arguments.date or datetime.now(timezone.utc).date().isoformat()
    history = load_history(arguments.history)
    counts = fetch_star_counts(
        arguments.owner,
        REPOSITORIES,
        os.environ.get("GITHUB_TOKEN", ""),
    )
    updated = update_history(history, snapshot_date, counts)
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(
        json.dumps(updated, indent=2, sort_keys=False) + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
