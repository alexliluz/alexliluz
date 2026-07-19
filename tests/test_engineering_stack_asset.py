import re
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

from scripts import build_engineering_stack
from scripts.validate_profile_assets import validate_svg_source


ROOT = Path(__file__).resolve().parents[1]
ASSET_NAMES = (
    "engineering-stack-dark.svg",
    "engineering-stack-light.svg",
    "engineering-stack-dark-static.svg",
    "engineering-stack-light-static.svg",
)
GROUPS = ("BUILD", "AUTOMATE", "VERIFY")
TECHNOLOGIES = (
    "TypeScript",
    "Node.js",
    "pnpm",
    "GitHub Actions",
    "Vitest",
    "Playwright",
    "Git",
)
SVG = "{http://www.w3.org/2000/svg}"


class EngineeringStackAssetTests(unittest.TestCase):
    def test_model_contains_only_the_approved_public_toolchain(self) -> None:
        self.assertEqual(
            tuple(group.name for group in build_engineering_stack.STACK_GROUPS),
            GROUPS,
        )
        self.assertEqual(
            tuple(
                node.label
                for group in build_engineering_stack.STACK_GROUPS
                for node in group.nodes
            ),
            TECHNOLOGIES,
        )

    def test_all_variants_are_accessible_safe_and_responsive(self) -> None:
        for name in ASSET_NAMES:
            with self.subTest(name=name):
                path = ROOT / "assets" / name
                self.assertTrue(path.is_file())
                source = path.read_text(encoding="utf-8")
                root = validate_svg_source(source)
                self.assertEqual(root.attrib["viewBox"], "0 0 960 300")
                self.assertEqual(root.attrib["role"], "img")
                self.assertEqual(
                    root.attrib["aria-labelledby"],
                    "engineering-stack-title engineering-stack-description",
                )
                self.assertTrue(root.find(f"{SVG}title").text.strip())
                self.assertTrue(root.find(f"{SVG}desc").text.strip())
                for label in GROUPS + TECHNOLOGIES:
                    self.assertEqual(source.count(f">{label}<"), 1)
                self.assertNotIn(">Python<", source)
                self.assertLess(path.stat().st_size, 2 * 1024 * 1024)

    def test_all_variants_define_legible_two_row_narrow_viewport_layout(self) -> None:
        scale_at_420_px = 420 / 960
        minimum_rendered_sizes = {
            ".title": 12,
            ".subtitle": 9,
            ".group-label": 9,
            ".node-label": 9,
        }

        for name, theme, animated in build_engineering_stack.OUTPUTS:
            with self.subTest(name=name):
                source = (ROOT / "assets" / name).read_text(encoding="utf-8")
                self.assertEqual(
                    source,
                    build_engineering_stack.build_svg(theme, animated),
                    "committed asset must match the responsive generator output",
                )
                media_start = source.find("@media (max-width: 480px)")
                self.assertNotEqual(
                    media_start,
                    -1,
                    "narrow SVG viewports need a dedicated responsive layout",
                )
                mobile_css = source[media_start : source.index("</style>")]

                for selector, minimum in minimum_rendered_sizes.items():
                    match = re.search(
                        rf"{re.escape(selector)}\s*\{{[^}}]*font-size:(\d+)px",
                        mobile_css,
                    )
                    self.assertIsNotNone(match, f"missing mobile size for {selector}")
                    self.assertGreaterEqual(
                        int(match.group(1)) * scale_at_420_px,
                        minimum,
                        f"{selector} renders below {minimum}px at 420px",
                    )

                positions = re.findall(
                    r"--mobile-x:(\d+)px;--mobile-y:(\d+)px", source
                )
                self.assertEqual(len(positions), len(TECHNOLOGIES))
                self.assertEqual({int(y) for _, y in positions}, {123, 204})

    def test_motion_exists_only_in_animated_variants(self) -> None:
        for theme in ("dark", "light"):
            animated = (ROOT / "assets" / f"engineering-stack-{theme}.svg").read_text()
            static = (
                ROOT / "assets" / f"engineering-stack-{theme}-static.svg"
            ).read_text()
            self.assertIn('dur="6s"', animated)
            self.assertIn("@keyframes node-signal", animated)
            self.assertIn("<animateMotion", animated)
            self.assertIn("<animate ", animated)
            for forbidden in (
                "<animate ",
                "<animateMotion",
                "<animateTransform",
                "@keyframes",
                "animation:",
                "transition:",
            ):
                self.assertNotIn(forbidden, static)

    def test_build_is_deterministic_and_cli_writes_stable_names(self) -> None:
        self.assertEqual(
            build_engineering_stack.build_svg("dark", True),
            build_engineering_stack.build_svg("dark", True),
        )
        with tempfile.TemporaryDirectory() as directory:
            paths = build_engineering_stack.write_assets(Path(directory))
            self.assertEqual(tuple(path.name for path in paths), ASSET_NAMES)
            for path in paths:
                validate_svg_source(path.read_text(encoding="utf-8"))

    def test_invalid_theme_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "unsupported theme"):
            build_engineering_stack.build_svg("neon", True)


if __name__ == "__main__":
    unittest.main()
