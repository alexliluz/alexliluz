import subprocess
import tempfile
import unittest
from pathlib import Path

from scripts.validate_profile_assets import MAX_SVG_BYTES, validate_svg, validate_svg_source


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

    def test_rejects_scripts_remote_runtime_references_and_size_boundary(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            prefix = '<svg xmlns="http://www.w3.org/2000/svg"><desc>'
            suffix = "</desc></svg>"
            fixtures = (
                self.write_fixture(
                    directory,
                    "script.svg",
                    '<svg xmlns="http://www.w3.org/2000/svg"><script>x()</script></svg>',
                ),
                self.write_fixture(
                    directory,
                    "namespaced-script.svg",
                    '<svg xmlns="http://www.w3.org/2000/svg" '
                    'xmlns:s="http://www.w3.org/2000/svg"><s:script>x()</s:script></svg>',
                ),
                self.write_fixture(
                    directory,
                    "external.svg",
                    '<svg xmlns="http://www.w3.org/2000/svg">'
                    '<image href="https://example.com/image.svg"/></svg>',
                ),
                self.write_fixture(
                    directory,
                    "encoded-external.svg",
                    '<svg xmlns="http://www.w3.org/2000/svg">'
                    '<image href="https&#x3a;//example.com/image.svg"/></svg>',
                ),
                self.write_fixture(
                    directory,
                    "protocol-relative.svg",
                    '<svg xmlns="http://www.w3.org/2000/svg">'
                    '<image href="//example.com/image.svg"/></svg>',
                ),
                self.write_fixture(
                    directory,
                    "xml-base.svg",
                    '<svg xmlns="http://www.w3.org/2000/svg" '
                    'xml:base="https://example.com/"><image href="image.svg"/></svg>',
                ),
                self.write_fixture(
                    directory,
                    "css-remote.svg",
                    '<svg xmlns="http://www.w3.org/2000/svg">'
                    '<style>.x{fill:url(//example.com/image.svg)}</style></svg>',
                ),
                self.write_fixture(
                    directory,
                    "large.svg",
                    '<svg xmlns="http://www.w3.org/2000/svg"><desc>'
                    + ("x" * (2 * 1024 * 1024))
                    + "</desc></svg>",
                ),
            )
            for path in fixtures:
                with self.subTest(path=path), self.assertRaises(ValueError):
                    validate_svg(path)

            equal_limit = self.write_fixture(
                directory,
                "equal-limit.svg",
                prefix + ("x" * (MAX_SVG_BYTES - len(prefix) - len(suffix))) + suffix,
            )
            with self.assertRaisesRegex(ValueError, "2 MiB"):
                validate_svg(equal_limit)
            with self.assertRaisesRegex(ValueError, "2 MiB"):
                validate_svg_source(equal_limit.read_text(encoding="utf-8"))

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
