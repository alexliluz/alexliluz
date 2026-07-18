import base64
import json
import re
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

from scripts.compose_contribution_signal import compose_all


SVG = "http://www.w3.org/2000/svg"


class ContributionSignalComposerTests(unittest.TestCase):
    def write_svg(self, path: Path, marker: str, animated: bool = True) -> None:
        animation = (
            '<animate attributeName="opacity" values="0;1" dur="2s" '
            'repeatCount="indefinite"/>'
            if animated
            else ""
        )
        path.write_text(
            f'<svg xmlns="{SVG}" viewBox="0 0 100 40">'
            f'<style>.moving{{animation:pulse 2s infinite}}</style>'
            f'<text>{marker}</text><g class="moving">{animation}</g></svg>',
            encoding="utf-8",
        )

    def test_composes_animated_and_static_theme_variants(self) -> None:
        with tempfile.TemporaryDirectory() as directory_name:
            directory = Path(directory_name)
            city_light = directory / "city-light.svg"
            city_dark = directory / "city-dark.svg"
            snake_light = directory / "snake-light.svg"
            snake_dark = directory / "snake-dark.svg"
            self.write_svg(city_light, "ORIGINAL-CITY-LIGHT")
            self.write_svg(city_dark, "ORIGINAL-CITY-DARK")
            self.write_svg(snake_light, "ORIGINAL-SNAKE-LIGHT")
            self.write_svg(snake_dark, "ORIGINAL-SNAKE-DARK")
            history = directory / "star-history.json"
            history.write_text(
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
            output = directory / "output"
            compose_all(
                city_light,
                city_dark,
                snake_light,
                snake_dark,
                history,
                output,
            )

            expected = (
                "contribution-signal-light.svg",
                "contribution-signal-dark.svg",
                "contribution-signal-light-static.svg",
                "contribution-signal-dark-static.svg",
            )
            for name in expected:
                path = output / name
                self.assertTrue(path.is_file(), name)
                root = ET.parse(path).getroot()
                self.assertEqual(root.attrib["viewBox"], "0 0 960 660")
                source = path.read_text(encoding="utf-8")
                self.assertIn("CONTRIBUTION SIGNAL", source)
                self.assertIn("STAR TREND", source)
                self.assertIn("SNAPSHOTS FROM 2026-07-19", source)
                payloads = re.findall(
                    r"data:image/svg\+xml;base64,([A-Za-z0-9+/=]+)", source
                )
                self.assertEqual(len(payloads), 2)
                decoded = "\n".join(
                    base64.b64decode(payload).decode("utf-8")
                    for payload in payloads
                )
                self.assertIn("ORIGINAL-CITY", decoded)
                self.assertIn("ORIGINAL-SNAKE", decoded)
                if "-static" in name:
                    self.assertNotIn("<animate", decoded)
                    self.assertNotRegex(decoded, r"animation\s*:")
                else:
                    self.assertIn("<animate", decoded)

    def test_rejects_scripted_or_externally_referenced_inputs(self) -> None:
        with tempfile.TemporaryDirectory() as directory_name:
            directory = Path(directory_name)
            bad = directory / "bad.svg"
            bad.write_text(
                f'<svg xmlns="{SVG}"><script>alert(1)</script></svg>',
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "script"):
                compose_all(bad, bad, bad, bad, directory / "missing.json", directory)


if __name__ == "__main__":
    unittest.main()
