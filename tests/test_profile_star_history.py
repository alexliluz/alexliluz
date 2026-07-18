import json
import sys
import tempfile
import unittest
from datetime import date, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

from scripts.profile_star_history import (
    REPOSITORIES,
    fetch_star_counts,
    load_history,
    main,
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

    def test_load_rejects_null_snapshot_date_and_repositories(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "history.json"
            for snapshot in (
                {"date": None, "repos": {repository: 0 for repository in REPOSITORIES}},
                {"date": "2024-01-01", "repos": None},
            ):
                path.write_text(
                    json.dumps({"version": 1, "snapshots": [snapshot]}),
                    encoding="utf-8",
                )
                with self.subTest(snapshot=snapshot), self.assertRaises(ValueError):
                    load_history(path)

    def test_update_evicts_oldest_distinct_date_and_is_idempotent(self) -> None:
        first_date = date(2024, 1, 1)
        snapshots = [
            {
                "date": (first_date + timedelta(days=index)).isoformat(),
                "repos": {repository: index for repository in REPOSITORIES},
            }
            for index in range(730)
        ]
        history = {"version": 1, "snapshots": snapshots}
        counts = {"planarian": 1, "ForkNeo": 1, "api-image-neo": 0}
        newest_date = (first_date + timedelta(days=730)).isoformat()
        updated = update_history(history, newest_date, counts)
        updated = update_history(updated, newest_date, counts)

        self.assertEqual(len(updated["snapshots"]), 730)
        self.assertNotIn(first_date.isoformat(), [item["date"] for item in updated["snapshots"]])
        self.assertEqual(updated["snapshots"][-1]["date"], newest_date)
        self.assertEqual(
            sum(item["date"] == newest_date for item in updated["snapshots"]),
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

    def test_fetch_rejects_an_empty_token(self) -> None:
        with self.assertRaisesRegex(ValueError, "GITHUB_TOKEN"):
            fetch_star_counts("alexliluz", REPOSITORIES, "")

    @patch("scripts.profile_star_history.fetch_star_counts")
    @patch("scripts.profile_star_history.datetime")
    def test_cli_defaults_snapshot_date_to_utc(self, mocked_datetime, mocked_fetch) -> None:
        counts = {"planarian": 1, "ForkNeo": 1, "api-image-neo": 0}
        mocked_datetime.now.return_value.date.return_value.isoformat.return_value = (
            "2026-07-19"
        )
        mocked_fetch.return_value = counts
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "history.json"
            with patch.object(
                sys,
                "argv",
                ["profile_star_history.py", "--history", str(output), "--output", str(output)],
            ):
                self.assertEqual(main(), 0)

            self.assertEqual(json.loads(output.read_text(encoding="utf-8"))["snapshots"], [
                {"date": "2026-07-19", "repos": counts}
            ])
        mocked_datetime.now.assert_called_once_with(timezone.utc)


if __name__ == "__main__":
    unittest.main()
