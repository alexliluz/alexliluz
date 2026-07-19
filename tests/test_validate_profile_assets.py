import base64
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
                    "event-handler.svg",
                    '<svg xmlns="http://www.w3.org/2000/svg"><rect onload="x()"/></svg>',
                ),
                self.write_fixture(
                    directory,
                    "namespaced-event-handler.svg",
                    '<svg xmlns="http://www.w3.org/2000/svg" '
                    'xmlns:s="http://www.w3.org/2000/svg"><rect s:onclick="x()"/></svg>',
                ),
                self.write_fixture(
                    directory,
                    "javascript-link.svg",
                    '<svg xmlns="http://www.w3.org/2000/svg">'
                    '<a href=" \nJaVaScRiPt&#x3a;alert(1)"><text>x</text></a></svg>',
                ),
                self.write_fixture(
                    directory,
                    "vbscript-link.svg",
                    '<svg xmlns="http://www.w3.org/2000/svg">'
                    '<a href="vbscript:msgbox(1)"><text>x</text></a></svg>',
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
                    "css-import-https.svg",
                    '<svg xmlns="http://www.w3.org/2000/svg">'
                    '<style>@import "https://example.com/theme.css";</style></svg>',
                ),
                self.write_fixture(
                    directory,
                    "css-import-protocol-relative.svg",
                    '<svg xmlns="http://www.w3.org/2000/svg">'
                    '<style>@import \'//example.com/theme.css\';</style></svg>',
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

    def test_accepts_fragment_and_approved_embedded_svg_references(self) -> None:
        embedded = (
            '<svg xmlns="http://www.w3.org/2000/svg">'
            '<defs><path id="embedded" d="M0 0"/></defs>'
            '<use href="#embedded"/></svg>'
        )
        encoded = base64.b64encode(embedded.encode("utf-8")).decode("ascii")
        source = (
            '<svg xmlns="http://www.w3.org/2000/svg" '
            'xmlns:xlink="http://www.w3.org/1999/xlink">'
            '<defs><linearGradient id="paint"/></defs>'
            '<rect id="local" fill="url(#paint)"/>'
            '<use href="#local"/>'
            '<use xlink:href="#local"/>'
            '<set attributeName="href" to="#local"/>'
            f'<image href="data:image/svg+xml;base64,{encoded}"/>'
            "</svg>"
        )
        self.assertIsNotNone(validate_svg_source(source))

    def test_rejects_relative_runtime_resource_references(self) -> None:
        fixtures = (
            '<image href="image.svg"/>',
            '<use href="sprite.svg#icon"/>',
            '<image src="./image.svg"/>',
            '<object data="../asset.svg"/>',
            '<use xmlns:xlink="http://www.w3.org/1999/xlink" '
            'xlink:href="icons.svg#icon"/>',
            '<rect fill="url(patterns.svg#paint)"/>',
            '<style>.x{mask:url(../masks.svg#mask)}</style>',
            '<style>@import "theme.css";</style>',
        )
        for fixture in fixtures:
            source = f'<svg xmlns="http://www.w3.org/2000/svg">{fixture}</svg>'
            with self.subTest(fixture=fixture), self.assertRaisesRegex(
                ValueError, "runtime reference"
            ):
                validate_svg_source(source)

    def test_rejects_nonapproved_data_images_and_all_css_imports(self) -> None:
        safe_embedded = '<svg xmlns="http://www.w3.org/2000/svg"/>'
        safe_encoded = base64.b64encode(safe_embedded.encode("utf-8")).decode(
            "ascii"
        )
        unsafe_embedded = (
            '<svg xmlns="http://www.w3.org/2000/svg">'
            '<image href="https://example.com/image.svg"/></svg>'
        )
        unsafe_encoded = base64.b64encode(unsafe_embedded.encode("utf-8")).decode(
            "ascii"
        )
        fixtures = (
            '<image href="data:image/png;base64,eA=="/>',
            f'<a href="data:image/svg+xml;base64,{safe_encoded}"/>',
            '<style>@import url(#local);</style>',
            f'<style>@import url(data:image/svg+xml;base64,{safe_encoded});</style>',
            f'<image href="data:image/svg+xml;base64,{unsafe_encoded}"/>',
        )
        for fixture in fixtures:
            source = (
                '<svg xmlns="http://www.w3.org/2000/svg">'
                '<g id="local"/>'
                f"{fixture}</svg>"
            )
            with self.subTest(fixture=fixture), self.assertRaises(ValueError):
                validate_svg_source(source)

    def test_rejects_smil_uri_rewrites(self) -> None:
        fixtures = (
            '<set attributeName="href" to="https://example.com/image.svg"/>',
            '<set attributeName="href" to="image.svg"/>',
            '<set attributeName=" href " to="image.svg"/>',
            '<set attributeName="xlink:href" to="image.svg"/>',
            '<set attributeName="href" to="javascript:alert(1)"/>',
            '<set attributeName="href" to="data:image/png;base64,eA=="/>',
            '<animate attributeName="href" from="#local" '
            'to="//example.com/image.svg"/>',
            '<animate attributeName="href" '
            'values="#local;https://example.com/image.svg"/>',
            '<animate attributeName="href" '
            'values="#local;icons.svg#remote"/>',
            '<animate attributeName="fill" '
            'values="red;url(https://example.com/paint.svg#paint)"/>',
            '<animate attributeName="opacity" '
            'begin="https://example.com/timing.svg#event"/>',
        )
        for fixture in fixtures:
            source = (
                '<svg xmlns="http://www.w3.org/2000/svg">'
                '<g id="local"/>'
                f"{fixture}</svg>"
            )
            with self.subTest(fixture=fixture), self.assertRaises(ValueError):
                validate_svg_source(source)

    def test_rejects_srcdoc_attributes_by_local_name(self) -> None:
        fixtures = (
            '<foreignObject><iframe xmlns="http://www.w3.org/1999/xhtml" '
            'srcdoc="&lt;script&gt;alert(1)&lt;/script&gt;"/></foreignObject>',
            '<foreignObject xmlns:xhtml="http://www.w3.org/1999/xhtml" '
            'xhtml:srcdoc="&lt;img src=&quot;https://example.com/a.png&quot;&gt;">'
            '<xhtml:iframe/></foreignObject>',
        )
        for fixture in fixtures:
            source = f'<svg xmlns="http://www.w3.org/2000/svg">{fixture}</svg>'
            with self.subTest(fixture=fixture), self.assertRaisesRegex(
                ValueError, "runtime reference"
            ):
                validate_svg_source(source)

    def test_rejects_path_shaped_smil_timing_references(self) -> None:
        fixtures = (
            ("begin", "timing.svg#event.begin"),
            ("end", "../timing.svg#event.begin"),
            ("begin", "/timing.svg#event.begin"),
            ("end", "./timing.svg#event.end"),
            ("begin", "assets/timing.svg#event.begin"),
            ("end", r"C:\timing.svg#event.end"),
        )
        for attribute_name, value in fixtures:
            source = (
                '<svg xmlns="http://www.w3.org/2000/svg">'
                f'<animate attributeName="opacity" {attribute_name}="{value}"/>'
                "</svg>"
            )
            with self.subTest(attribute=attribute_name, value=value), self.assertRaises(
                ValueError
            ):
                validate_svg_source(source)

    def test_accepts_local_smil_timing_grammar(self) -> None:
        source = (
            '<svg xmlns="http://www.w3.org/2000/svg">'
            '<g id="local-event"/>'
            '<animate id="local-animation" attributeName="opacity" '
            'begin="local-event.click;local-animation.end+1s;2s;'
            'wallclock(2026-07-19T00:00:00Z);accessKey(/)+250ms" '
            'end="local-event.mouseout;local-animation.begin+2s;indefinite"/>'
            "</svg>"
        )
        self.assertIsNotNone(validate_svg_source(source))

    def test_rejects_css_escaped_remote_references(self) -> None:
        fixtures = (
            r'<style>.x{fill:u\72l(https://example.com/image.svg)}</style>',
            r'<style>@\69mport "https://example.com/theme.css";</style>',
        )
        for fixture in fixtures:
            source = f'<svg xmlns="http://www.w3.org/2000/svg">{fixture}</svg>'
            with self.subTest(fixture=fixture), self.assertRaisesRegex(
                ValueError, "runtime reference"
            ):
                validate_svg_source(source)

    def test_rejects_xml_stylesheet_processing_instructions(self) -> None:
        for stylesheet in ("https://example.com/theme.css", "theme.css"):
            source = (
                f'<?xml-stylesheet href="{stylesheet}"?>'
                '<svg xmlns="http://www.w3.org/2000/svg"/>'
            )
            with self.subTest(stylesheet=stylesheet), self.assertRaisesRegex(
                ValueError, "stylesheet"
            ):
                validate_svg_source(source)

    def test_rejects_compound_uri_attributes(self) -> None:
        fixtures = (
            '<img xmlns="http://www.w3.org/1999/xhtml" '
            'srcset="https://example.com/image.png 1x"/>',
            '<img xmlns="http://www.w3.org/1999/xhtml" srcset="image.png 1x"/>',
            '<link xmlns="http://www.w3.org/1999/xhtml" '
            'imagesrcset="image.png 1x"/>',
        )
        for fixture in fixtures:
            source = (
                '<svg xmlns="http://www.w3.org/2000/svg"><foreignObject>'
                f"{fixture}</foreignObject></svg>"
            )
            with self.subTest(fixture=fixture), self.assertRaisesRegex(
                ValueError, "runtime reference"
            ):
                validate_svg_source(source)

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
