import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.profile_star_history import (
    REPOSITORIES,
    fetch_star_counts,
    load_history,
    update_history,
)


class Response:
    def __init__(self, payload: dict):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def read(self) -> bytes:
        return json.dumps(self.payload).encode("utf-8")


class ProfileStarHistoryTests(unittest.TestCase):
    def test_missing_history_starts_with_version_one(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            history = load_history(Path(directory) / "missing.json")
        self.assertEqual(history, {"version": 1, "snapshots": []})

    def test_load_rejects_malformed_schema(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "history.json"
            path.write_text('{"version": 2, "snapshots": []}', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "version"):
                load_history(path)

    def test_same_day_update_is_idempotent_and_retention_is_bounded(self) -> None:
        snapshots = [
            {
                "date": f"2024-01-{(index % 28) + 1:02d}",
                "repos": {repository: index for repository in REPOSITORIES},
            }
            for index in range(730)
        ]
        history = {"version": 1, "snapshots": snapshots}
        counts = {"planarian": 1, "ForkNeo": 1, "api-image-neo": 0}
        updated = update_history(history, "2026-07-19", counts)
        updated = update_history(updated, "2026-07-19", counts)
        self.assertEqual(len(updated["snapshots"]), 730)
        self.assertEqual(updated["snapshots"][-1]["date"], "2026-07-19")
        self.assertEqual(
            sum(item["date"] == "2026-07-19" for item in updated["snapshots"]),
            1,
        )

    @patch("scripts.profile_star_history.urlopen")
    def test_fetches_public_counts_and_rejects_missing_counts(self, mocked) -> None:
        mocked.side_effect = [
            Response({"stargazers_count": 1}),
            Response({"stargazers_count": 1}),
            Response({"stargazers_count": 0}),
        ]
        self.assertEqual(
            fetch_star_counts("alexliluz", REPOSITORIES, "token"),
            {"planarian": 1, "ForkNeo": 1, "api-image-neo": 0},
        )
        mocked.side_effect = [Response({})]
        with self.assertRaisesRegex(ValueError, "stargazers_count"):
            fetch_star_counts("alexliluz", ("planarian",), "token")


if __name__ == "__main__":
    unittest.main()
