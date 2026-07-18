import subprocess
import tempfile
import unittest
from pathlib import Path

from scripts.validate_profile_assets import validate_svg


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts" / "validate_profile_assets.py"


class GeneratedSvgValidatorTests(unittest.TestCase):
    def write_fixture(self, directory: Path, name: str, source: str) -> Path:
        path = directory / name
        path.write_text(source, encoding="utf-8")
        return path

    def test_accepts_nonempty_svg_document(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            path = self.write_fixture(
                Path(temporary_directory),
                "valid.svg",
                '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10">'
                '<rect width="10" height="10"/></svg>',
            )
            self.assertIsNone(validate_svg(path))

    def test_rejects_missing_empty_malformed_and_non_svg_files(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            fixtures = (
                directory / "missing.svg",
                self.write_fixture(directory, "empty.svg", ""),
                self.write_fixture(directory, "malformed.svg", "<svg>"),
                self.write_fixture(directory, "error.svg", "<html>failure</html>"),
            )
            for path in fixtures:
                with self.subTest(path=path), self.assertRaises(ValueError):
                    validate_svg(path)

    def test_rejects_embedded_credentials(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            path = self.write_fixture(
                Path(temporary_directory),
                "secret.svg",
                '<svg xmlns="http://www.w3.org/2000/svg"><text>'
                "ghp_123456789012345678901234567890123456"
                "</text></svg>",
            )
            with self.assertRaisesRegex(ValueError, "credential-like"):
                validate_svg(path)

    def test_cli_reports_the_invalid_path_and_returns_nonzero(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            path = self.write_fixture(Path(temporary_directory), "error.svg", "bad")
            result = subprocess.run(
                ["python3", str(VALIDATOR), str(path)],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(str(path), result.stderr)


if __name__ == "__main__":
    unittest.main()
