import base64
import json
import re
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

from scripts.compose_contribution_signal import MAX_BYTES, compose, compose_all


SVG = "http://www.w3.org/2000/svg"
SMIL_NAMES = {"animate", "animatemotion", "animatetransform", "set"}
CSS_ANIMATION = re.compile(r"animation(?:-[a-z-]+)?\s*:", re.IGNORECASE)


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
                self.assertNotRegex(element.text or "", CSS_ANIMATION)
            self.assertNotRegex(element.attrib.get("style", ""), CSS_ANIMATION)

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
                            self.assertRegex(payload, CSS_ANIMATION)

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
