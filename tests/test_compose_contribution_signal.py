import base64
import json
import re
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

from scripts.compose_contribution_signal import (
    MAX_BYTES,
    compose,
    compose_all,
    static_source,
)


SVG = "http://www.w3.org/2000/svg"
SMIL_NAMES = {"animate", "animatecolor", "animatemotion", "animatetransform", "set"}
CSS_MOTION = re.compile(
    r"(?:-[a-z]+-)?(?:animation|transition)(?:-[a-z-]+)?\s*:",
    re.IGNORECASE,
)
ROOT = Path(__file__).resolve().parents[1]
COMPOSER = ROOT / "scripts" / "compose_contribution_signal.py"


def local_name(name: str) -> str:
    return name.rsplit("}", maxsplit=1)[-1].lower()


class ContributionSignalComposerTests(unittest.TestCase):
    def write_svg(self, path: Path, marker: str) -> str:
        source = (
            f'<svg xmlns="{SVG}" xmlns:s="{SVG}" viewBox="0 0 100 40">'
            '<style>.moving{animation:pulse 2s infinite}</style>'
            '<g style="animation-delay:0.000s"><text>'
            f'{marker}</text><g class="moving">'
            '<animate attributeName="opacity" values="0;1" dur="2s" '
            'repeatCount="indefinite"/>'
            '<s:animateTransform attributeName="transform" type="rotate" '
            'from="0" to="360" dur="2s"/></g></g></svg>'
        )
        path.write_text(source, encoding="utf-8")
        return source

    def write_history(self, path: Path) -> None:
        path.write_text(
            json.dumps(
                {
                    "version": 1,
                    "snapshots": [
                        {
                            "date": "2026-07-19",
                            "repos": {
                                "planarian": 1,
                                "ForkNeo": 1,
                                "api-image-neo": 0,
                            },
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )

    def payloads(self, path: Path) -> list[str]:
        source = path.read_text(encoding="utf-8")
        encoded = re.findall(r"data:image/svg\+xml;base64,([A-Za-z0-9+/=]+)", source)
        self.assertEqual(len(encoded), 2)
        return [base64.b64decode(payload).decode("utf-8") for payload in encoded]

    def assert_static_payload(self, source: str) -> None:
        root = ET.fromstring(source)
        for element in root.iter():
            self.assertNotIn(local_name(element.tag), SMIL_NAMES)
            if local_name(element.tag) == "style":
                self.assertNotRegex(element.text or "", CSS_MOTION)
            self.assertNotRegex(element.attrib.get("style", ""), CSS_MOTION)

    def contrast_ratio(self, first: str, second: str) -> float:
        def luminance(color: str) -> float:
            channels = [int(color[index : index + 2], 16) / 255 for index in (1, 3, 5)]
            linear = [
                channel / 12.92
                if channel <= 0.04045
                else ((channel + 0.055) / 1.055) ** 2.4
                for channel in channels
            ]
            return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]

        lighter, darker = sorted((luminance(first), luminance(second)), reverse=True)
        return (lighter + 0.05) / (darker + 0.05)

    def sample_history(self) -> dict:
        return {
            "snapshots": [
                {"date": "2026-07-19", "repos": {"planarian": 1}},
            ]
        }

    def test_composes_byte_preserving_animated_and_valid_static_theme_variants(self) -> None:
        with tempfile.TemporaryDirectory() as directory_name:
            directory = Path(directory_name)
            city_light = directory / "city-light.svg"
            city_dark = directory / "city-dark.svg"
            snake_light = directory / "snake-light.svg"
            snake_dark = directory / "snake-dark.svg"
            inputs = {
                "light": (
                    self.write_svg(city_light, "ORIGINAL-CITY-LIGHT"),
                    self.write_svg(snake_light, "ORIGINAL-SNAKE-LIGHT"),
                ),
                "dark": (
                    self.write_svg(city_dark, "ORIGINAL-CITY-DARK"),
                    self.write_svg(snake_dark, "ORIGINAL-SNAKE-DARK"),
                ),
            }
            history = directory / "star-history.json"
            self.write_history(history)
            output = directory / "output"
            compose_all(city_light, city_dark, snake_light, snake_dark, history, output)

            for theme_name, expected_payloads in inputs.items():
                for suffix in ("", "-static"):
                    path = output / f"contribution-signal-{theme_name}{suffix}.svg"
                    self.assertTrue(path.is_file(), path.name)
                    root = ET.parse(path).getroot()
                    self.assertEqual(root.attrib["viewBox"], "0 0 960 660")
                    source = path.read_text(encoding="utf-8")
                    self.assertIn("CONTRIBUTION SIGNAL", source)
                    self.assertIn("STAR TREND", source)
                    self.assertIn("SNAPSHOTS FROM 2026-07-19", source)
                    polyline = root.find(f"{{{SVG}}}polyline")
                    self.assertIsNotNone(polyline)
                    self.assertEqual(len(polyline.attrib["points"].split()), 2)
                    payloads = self.payloads(path)
                    if suffix:
                        for payload in payloads:
                            self.assert_static_payload(payload)
                    else:
                        self.assertEqual(payloads, list(expected_payloads))
                        for payload in payloads:
                            self.assertIn("<animate", payload)
                            self.assertRegex(payload, CSS_MOTION)

    def test_star_total_meets_text_contrast_for_each_theme(self) -> None:
        minimal_svg = f'<svg xmlns="{SVG}" viewBox="0 0 1 1"/>'
        fills = {}
        for theme_name in ("light", "dark"):
            with self.subTest(theme=theme_name):
                root = ET.fromstring(
                    compose(
                        minimal_svg,
                        minimal_svg,
                        self.sample_history(),
                        theme_name,
                        False,
                    )
                )
                background = next(
                    element.attrib["fill"]
                    for element in root
                    if local_name(element.tag) == "rect"
                )
                star = next(
                    element
                    for element in root
                    if local_name(element.tag) == "text"
                    and (element.text or "").startswith("★")
                )
                fills[theme_name] = star.attrib["fill"]
                self.assertGreaterEqual(
                    self.contrast_ratio(star.attrib["fill"], background),
                    4.5,
                )
        self.assertEqual(fills["dark"], "#E3B341")
        self.assertNotEqual(fills["light"], fills["dark"])

    def test_generated_description_is_motion_neutral_for_all_variants(self) -> None:
        minimal_svg = f'<svg xmlns="{SVG}" viewBox="0 0 1 1"/>'
        for static in (False, True):
            with self.subTest(static=static):
                root = ET.fromstring(
                    compose(
                        minimal_svg,
                        minimal_svg,
                        self.sample_history(),
                        "light",
                        static,
                    )
                )
                description = root.find(f"{{{SVG}}}desc")
                self.assertEqual(
                    description.text,
                    "Star trend, 3D contribution city, and original "
                    "contribution-grid snake.",
                )

    def test_staticization_removes_animate_color(self) -> None:
        source = (
            f'<svg xmlns="{SVG}"><rect fill="red">'
            '<animateColor attributeName="fill" values="red;blue" dur="1s"/>'
            "</rect></svg>"
        )
        static = static_source(source)
        self.assert_static_payload(static)
        ET.fromstring(static)

    def test_staticization_preserves_first_keyframe_fill_as_fallback(self) -> None:
        source = (
            f'<svg xmlns="{SVG}">'
            "<style>"
            ".rainbow{animation:rainbow 10s linear infinite;}"
            "@keyframes rainbow{"
            "0.00%{fill:rgb(115, 38, 38)}"
            "50.00%{fill:rgb(38, 115, 115)}"
            "100.00%{fill:rgb(115, 38, 38)}}"
            "</style>"
            '<rect class="rainbow" width="10" height="10"/>'
            "</svg>"
        )

        static = static_source(source)

        self.assert_static_payload(static)
        root = ET.fromstring(static)
        style = next(
            element.text or ""
            for element in root.iter()
            if local_name(element.tag) == "style"
        )
        fallback_rule = re.search(r"\.rainbow\s*\{([^{}]*)\}", style)
        self.assertIsNotNone(fallback_rule)
        self.assertIn("fill:rgb(115, 38, 38)", fallback_rule.group(1))

    def test_staticization_removes_vendor_prefixed_animation_declarations(self) -> None:
        source = (
            f'<svg xmlns="{SVG}">'
            "<style>.moving{-webkit-animation:pulse 1s;fill:red}</style>"
            '<rect class="moving" style="-moz-animation-delay:1s;stroke:blue"/>'
            "</svg>"
        )
        static = static_source(source)
        self.assert_static_payload(static)
        self.assertIn("fill:red", static)
        self.assertIn("stroke:blue", static)
        ET.fromstring(static)

    def test_staticization_removes_transition_declarations(self) -> None:
        source = (
            f'<svg xmlns="{SVG}">'
            "<style>.moving{transition:transform 1s;fill:red}</style>"
            '<rect class="moving" style="-webkit-transition-delay:1s;stroke:blue"/>'
            "</svg>"
        )
        static = static_source(source)
        self.assert_static_payload(static)
        self.assertIn("fill:red", static)
        self.assertIn("stroke:blue", static)
        ET.fromstring(static)

    def test_staticization_removes_consecutive_motion_declarations(self) -> None:
        source = (
            f'<svg xmlns="{SVG}"><style>.moving{{'
            "-webkit-animation:pulse 1s;transition:transform 1s;fill:red}"
            "</style></svg>"
        )
        static = static_source(source)
        self.assert_static_payload(static)
        self.assertIn("fill:red", static)
        ET.fromstring(static)

    def test_staticization_removes_css_escaped_motion_declarations(self) -> None:
        source = (
            f'<svg xmlns="{SVG}"><style>.moving{{'
            "\\61nimation:pulse 1s;tr\\61nsition:transform 1s;fill:red}"
            "</style></svg>"
        )
        static = static_source(source)
        self.assertNotIn(r"\61nimation", static)
        self.assertNotIn(r"tr\61nsition", static)
        self.assertIn("fill:red", static)
        ET.fromstring(static)

    def test_staticization_removes_motion_after_nonmotion_declaration(self) -> None:
        source = (
            f'<svg xmlns="{SVG}"><style>'
            ".moving{fill:red;animation-name:pulse}"
            "</style></svg>"
        )
        static = static_source(source)
        self.assert_static_payload(static)
        self.assertIn("fill:red", static)
        ET.fromstring(static)

    def test_staticization_removes_comment_delimited_motion_declarations(
        self,
    ) -> None:
        source = (
            f'<svg xmlns="{SVG}"><style>.moving{{'
            "animation/**/:pulse 1s;fill:red;transition/**/:transform 1s}"
            "</style></svg>"
        )
        static = static_source(source)
        self.assertNotIn("animation/**/", static)
        self.assertNotIn("transition/**/", static)
        self.assert_static_payload(static)
        self.assertIn("fill:red", static)
        ET.fromstring(static)

    def test_help_succeeds_for_module_and_direct_script_entry_points(self) -> None:
        commands = (
            [sys.executable, "-m", "scripts.compose_contribution_signal", "--help"],
            [sys.executable, str(COMPOSER), "--help"],
        )
        for command in commands:
            with self.subTest(command=command):
                result = subprocess.run(
                    command,
                    cwd=ROOT,
                    check=False,
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn("usage:", result.stdout)

    def test_rejects_script_and_remote_runtime_references_in_inputs(self) -> None:
        fixtures = (
            f'<svg xmlns="{SVG}" xmlns:s="{SVG}"><s:script>x()</s:script></svg>',
            f'<svg xmlns="{SVG}"><image href="//example.com/image.svg"/></svg>',
            f'<svg xmlns="{SVG}" xml:base="https://example.com/"><image href="image.svg"/></svg>',
            f'<svg xmlns="{SVG}"><style>.x{{fill:url(https://example.com/a.svg)}}</style></svg>',
            f'<svg xmlns="{SVG}"><style>.x{{fill:url(//example.com/a.svg)}}</style></svg>',
        )
        with tempfile.TemporaryDirectory() as directory_name:
            directory = Path(directory_name)
            for index, source in enumerate(fixtures):
                path = directory / f"bad-{index}.svg"
                path.write_text(source, encoding="utf-8")
                with self.subTest(source=source), self.assertRaises(ValueError):
                    compose_all(path, path, path, path, directory / "missing.json", directory)

    def test_compose_rejects_unsafe_source_strings_before_embedding(self) -> None:
        unsafe = f'<svg xmlns="{SVG}" xmlns:s="{SVG}"><s:script>x()</s:script></svg>'
        history = {
            "snapshots": [
                {"date": "2026-07-19", "repos": {"planarian": 0}},
            ]
        }
        with self.assertRaisesRegex(ValueError, "script"):
            compose(unsafe, unsafe, history, "light", False)

    def test_rejects_inputs_at_and_outputs_above_the_size_limit(self) -> None:
        with tempfile.TemporaryDirectory() as directory_name:
            directory = Path(directory_name)
            prefix = f'<svg xmlns="{SVG}"><desc>'
            suffix = "</desc></svg>"
            equal_limit = prefix + ("x" * (MAX_BYTES - len(prefix) - len(suffix))) + suffix
            path = directory / "equal-limit.svg"
            path.write_text(equal_limit, encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "2 MiB"):
                compose_all(path, path, path, path, directory / "missing.json", directory)

        large_source = f'<svg xmlns="{SVG}"><desc>' + ("x" * 800_000) + "</desc></svg>"
        with self.assertRaisesRegex(ValueError, "2 MiB"):
            compose(
                large_source,
                large_source,
                {
                    "snapshots": [
                        {"date": "2026-07-19", "repos": {"planarian": 0}},
                    ]
                },
                "light",
                False,
            )


if __name__ == "__main__":
    unittest.main()
