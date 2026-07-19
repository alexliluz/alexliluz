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
    @staticmethod
    def history_with_snapshots(*snapshots: dict) -> dict:
        return {"version": 1, "snapshots": list(snapshots)}

    @staticmethod
    def snapshot(snapshot_date: object = "2024-01-01", repos: object = None) -> dict:
        if repos is None:
            repos = {repository: 0 for repository in REPOSITORIES}
        return {"date": snapshot_date, "repos": repos}

    def assert_history_is_rejected(self, history: object) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "history.json"
            path.write_text(json.dumps(history), encoding="utf-8")
            with self.assertRaises(ValueError) as caught:
                load_history(path)
            self.assertIn(str(path), str(caught.exception))

    def test_missing_history_starts_with_version_one(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            history = load_history(Path(directory) / "missing.json")
        self.assertEqual(history, {"version": 1, "snapshots": []})

    def test_load_requires_integer_version_one(self) -> None:
        for version in (True, False, 1.0, "1", 0, 2):
            with self.subTest(version=version):
                self.assert_history_is_rejected({"version": version, "snapshots": []})

    def test_load_requires_exact_root_keys(self) -> None:
        for history in (
            {"version": 1},
            {"snapshots": []},
            {"version": 1, "snapshots": [], "extra": None},
        ):
            with self.subTest(history=history):
                self.assert_history_is_rejected(history)

    def test_load_requires_an_object_root_and_snapshot_list(self) -> None:
        for history in (
            None,
            [],
            {"version": 1, "snapshots": None},
            {"version": 1, "snapshots": {}},
        ):
            with self.subTest(history=history):
                self.assert_history_is_rejected(history)

    def test_load_requires_exact_snapshot_keys(self) -> None:
        valid_repos = {repository: 0 for repository in REPOSITORIES}
        for snapshot in (
            {"date": "2024-01-01"},
            {"repos": valid_repos},
            {"date": "2024-01-01", "repos": valid_repos, "extra": None},
        ):
            with self.subTest(snapshot=snapshot):
                self.assert_history_is_rejected(self.history_with_snapshots(snapshot))

    def test_load_requires_snapshot_objects(self) -> None:
        for snapshot in (None, [], "2024-01-01"):
            with self.subTest(snapshot=snapshot):
                self.assert_history_is_rejected(self.history_with_snapshots(snapshot))

    def test_load_requires_canonical_iso_dates(self) -> None:
        for snapshot_date in (
            None,
            20240101,
            "20240101",
            "2024-1-1",
            "2024-W01-1",
            "2024-02-30",
        ):
            with self.subTest(snapshot_date=snapshot_date):
                self.assert_history_is_rejected(
                    self.history_with_snapshots(self.snapshot(snapshot_date))
                )

    def test_load_rejects_duplicate_dates(self) -> None:
        self.assert_history_is_rejected(
            self.history_with_snapshots(
                self.snapshot("2024-01-01"),
                self.snapshot("2024-01-01"),
            )
        )

    def test_load_rejects_out_of_order_dates(self) -> None:
        self.assert_history_is_rejected(
            self.history_with_snapshots(
                self.snapshot("2024-01-02"),
                self.snapshot("2024-01-01"),
            )
        )

    def test_load_rejects_more_than_maximum_snapshots(self) -> None:
        first_date = date(2024, 1, 1)
        snapshots = [
            self.snapshot((first_date + timedelta(days=index)).isoformat())
            for index in range(731)
        ]
        self.assert_history_is_rejected(self.history_with_snapshots(*snapshots))

    def test_load_requires_exact_repository_keys(self) -> None:
        valid_repos = {repository: 0 for repository in REPOSITORIES}
        missing = dict(valid_repos)
        missing.pop(REPOSITORIES[0])
        extra = {**valid_repos, "other": 0}
        wrong_case = dict(valid_repos)
        wrong_case["forkneo"] = wrong_case.pop("ForkNeo")
        for repos in (None, missing, extra, wrong_case):
            with self.subTest(repos=repos):
                snapshot = {"date": "2024-01-01", "repos": repos}
                self.assert_history_is_rejected(self.history_with_snapshots(snapshot))

    def test_load_requires_non_negative_integer_repository_counts(self) -> None:
        for invalid_count in (True, False, 1.0, "1", -1):
            with self.subTest(invalid_count=invalid_count):
                repos = {repository: 0 for repository in REPOSITORIES}
                repos[REPOSITORIES[0]] = invalid_count
                self.assert_history_is_rejected(
                    self.history_with_snapshots(self.snapshot(repos=repos))
                )

    def test_load_errors_include_path_and_useful_cause(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            cases = (
                ("malformed.json", b"{", "Expecting property name"),
                ("unicode.json", b'\xff', "utf-8"),
                (
                    "schema.json",
                    json.dumps({"version": 2, "snapshots": []}).encode("utf-8"),
                    "version",
                ),
            )
            for filename, payload, cause in cases:
                path = Path(directory) / filename
                path.write_bytes(payload)
                with self.subTest(filename=filename), self.assertRaises(
                    ValueError
                ) as caught:
                    load_history(path)
                message = str(caught.exception)
                self.assertIn(str(path), message)
                self.assertIn(cause, message)

    def test_update_requires_a_canonical_iso_date(self) -> None:
        history = {"version": 1, "snapshots": []}
        counts = {repository: 0 for repository in REPOSITORIES}
        for snapshot_date in (None, 20240101, "20240101", "2024-1-1"):
            with self.subTest(snapshot_date=snapshot_date), self.assertRaises(
                ValueError
            ):
                update_history(history, snapshot_date, counts)

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
