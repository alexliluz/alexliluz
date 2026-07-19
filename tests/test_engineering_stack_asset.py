import re
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from unittest.mock import patch

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
PLAN = (
    ROOT
    / "docs"
    / "superpowers"
    / "plans"
    / "2026-07-19-professional-engineering-stack.md"
)
EXPECTED_MOBILE_CENTERS = (
    (125, 158),
    (125, 239),
    (356, 158),
    (356, 239),
    (595, 158),
    (835, 158),
    (715, 239),
)


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

    def test_required_text_stays_legible_in_bounds_and_separated_at_mobile_widths(
        self,
    ) -> None:
        widths = (320, 360, 375, 420)
        text_layouts = {
            "wide_mobile": (
                ("title", "ENGINEERING STACK", 30, 48, 28, "start"),
                (
                    "subtitle",
                    "PUBLIC TOOLCHAIN · VERIFIED BY WORK",
                    30,
                    75,
                    21,
                    "start",
                ),
                ("group-build", "BUILD", 22, 112, 21, "start"),
                ("group-automate", "AUTOMATE", 253, 112, 21, "start"),
                ("group-verify", "VERIFY", 492, 112, 21, "start"),
            ),
            "narrow_mobile": (
                ("title", "ENGINEERING STACK", 30, 42, 28, "start"),
                (
                    "subtitle",
                    "PUBLIC TOOLCHAIN · VERIFIED BY WORK",
                    30,
                    78,
                    27,
                    "start",
                ),
                ("group-build", "BUILD", 22, 112, 27, "start"),
                ("group-automate", "AUTOMATE", 253, 112, 27, "start"),
                ("group-verify", "VERIFY", 492, 112, 27, "start"),
            ),
        }
        node_positions = tuple(
            (
                f"node-{node.label}",
                node.label,
                build_engineering_stack.MOBILE_NODE_POSITIONS[node.label][0] + 122,
                build_engineering_stack.MOBILE_NODE_POSITIONS[node.label][1] + 52,
            )
            for group in build_engineering_stack.STACK_GROUPS
            for node in group.nodes
        )

        for name, theme, animated in build_engineering_stack.OUTPUTS:
            with self.subTest(name=name):
                source = (ROOT / "assets" / name).read_text(encoding="utf-8")
                self.assertEqual(
                    source, build_engineering_stack.build_svg(theme, animated)
                )
                self.assertIn("@media (max-width: 380px)", source)
                self.assertIn(
                    ".subtitle,.group-label,.node-label { font-size:27px; }",
                    source,
                )
                self.assertIn(".title { y:42px; }", source)
                self.assertIn(".subtitle { y:78px; }", source)

                for width in widths:
                    scale = width / 960
                    narrow = width <= 380
                    layout = list(
                        text_layouts[
                            "narrow_mobile" if narrow else "wide_mobile"
                        ]
                    )
                    node_size = 27 if narrow else 21
                    layout.extend(
                        (*position, node_size, "middle")
                        for position in node_positions
                    )
                    boxes = []
                    for label, text, x, y, font_size, anchor in layout:
                        self.assertGreaterEqual(
                            font_size * scale,
                            9,
                            f"{label} is below 9px at {width}px",
                        )
                        text_width = len(text) * font_size * 0.65
                        left = x - text_width / 2 if anchor == "middle" else x
                        right = left + text_width
                        top = y - font_size * 0.9
                        bottom = y + font_size * 0.25
                        self.assertGreaterEqual(left, 0, f"{label} clips at {width}px")
                        self.assertLessEqual(right, 960, f"{label} clips at {width}px")
                        self.assertGreaterEqual(top, 0, f"{label} clips at {width}px")
                        self.assertLessEqual(bottom, 300, f"{label} clips at {width}px")
                        boxes.append((label, left, top, right, bottom))

                    for index, first in enumerate(boxes):
                        for second in boxes[index + 1 :]:
                            overlaps = not (
                                first[3] <= second[1]
                                or second[3] <= first[1]
                                or first[4] <= second[2]
                                or second[4] <= first[2]
                            )
                            self.assertFalse(
                                overlaps,
                                f"{first[0]} overlaps {second[0]} at {width}px",
                            )

    def test_mobile_route_follows_every_node_center_in_approved_order(self) -> None:
        expected_path = "M" + " L".join(
            f"{x} {y}" for x, y in EXPECTED_MOBILE_CENTERS
        )
        model_centers = tuple(
            (
                build_engineering_stack.MOBILE_NODE_POSITIONS[node.label][0] + 109,
                build_engineering_stack.MOBILE_NODE_POSITIONS[node.label][1] + 35,
            )
            for group in build_engineering_stack.STACK_GROUPS
            for node in group.nodes
        )
        self.assertEqual(model_centers, EXPECTED_MOBILE_CENTERS)

        for name, _, animated in build_engineering_stack.OUTPUTS:
            with self.subTest(name=name):
                source = (ROOT / "assets" / name).read_text(encoding="utf-8")
                root = ET.fromstring(source)
                desktop_route = root.find(f"{SVG}path[@id='engineering-route-desktop']")
                mobile_route = root.find(f"{SVG}path[@id='engineering-route-mobile']")
                self.assertIsNotNone(desktop_route)
                self.assertIsNotNone(mobile_route)
                self.assertEqual(desktop_route.attrib["d"], "M92 188 H872")
                self.assertEqual(mobile_route.attrib["d"], expected_path)
                self.assertIn("desktop-only", desktop_route.attrib["class"].split())
                self.assertIn("mobile-only", mobile_route.attrib["class"].split())
                self.assertIn(".mobile-only { display:none; }", source)
                self.assertRegex(
                    source,
                    r"(?s)@media \(max-width: 480px\).*?"
                    r"\.desktop-only \{ display:none; \}.*?"
                    r"\.mobile-only \{ display:inline; \}",
                )

                signals = [
                    element
                    for element in root.findall(f"{SVG}circle")
                    if "route-signal" in element.attrib.get("class", "").split()
                ]
                self.assertEqual(len(signals), 2 if animated else 0)
                if animated:
                    route_targets = []
                    for signal in signals:
                        motion = signal.find(f"{SVG}animateMotion")
                        self.assertIsNotNone(motion)
                        route_targets.append(
                            motion.find(f"{SVG}mpath").attrib["href"]
                        )
                    self.assertEqual(
                        route_targets,
                        ["#engineering-route-desktop", "#engineering-route-mobile"],
                    )
                    self.assertIn("desktop-only", signals[0].attrib["class"].split())
                    self.assertIn("mobile-only", signals[1].attrib["class"].split())

    def test_heading_scan_moves_left_to_right_once_then_hides(self) -> None:
        for theme in ("dark", "light"):
            with self.subTest(theme=theme):
                source = build_engineering_stack.build_svg(theme, True)
                self.assertNotIn('values="30;810;30"', source)
                self.assertIn(
                    'attributeName="x" values="30;810;810;30" '
                    'keyTimes="0;.72;.999;1" dur="6s"',
                    source,
                )
                self.assertIn(
                    'attributeName="opacity" values=".85;.85;0;0" '
                    'keyTimes="0;.72;.721;1" dur="6s"',
                    source,
                )

        plan = PLAN.read_text(encoding="utf-8")
        self.assertNotIn('values="30;810;30"', plan)
        self.assertIn('values="30;810;810;30"', plan)

    def test_typescript_and_node_are_the_only_primary_nodes(self) -> None:
        self.assertEqual(
            tuple(
                node.label
                for group in build_engineering_stack.STACK_GROUPS
                for node in group.nodes
                if node.primary
            ),
            ("TypeScript", "Node.js"),
        )
        for name, _, _ in build_engineering_stack.OUTPUTS:
            with self.subTest(name=name):
                source = (ROOT / "assets" / name).read_text(encoding="utf-8")
                root = ET.fromstring(source)
                primary_nodes = [
                    element
                    for element in root.findall(f".//{SVG}g")
                    if "primary-node" in element.attrib.get("class", "").split()
                ]
                self.assertEqual(len(primary_nodes), 2)
                self.assertEqual(
                    tuple(node.find(f"{SVG}text[2]").text for node in primary_nodes),
                    ("TypeScript", "Node.js"),
                )
                self.assertIn(".primary-node > rect { stroke-width:2; }", source)
                self.assertIn(
                    ".primary-node > .node-label { font-weight:700; }", source
                )
                self.assertIn(
                    ".primary-node > text:first-of-type { font-weight:800; }",
                    source,
                )

    def test_model_validation_rejects_a_missing_required_group_before_output(self) -> None:
        incomplete = build_engineering_stack.STACK_GROUPS[:-1]
        with patch.object(build_engineering_stack, "STACK_GROUPS", incomplete):
            with self.assertRaisesRegex(
                ValueError, r"missing required stack group: VERIFY"
            ):
                build_engineering_stack.build_svg("dark", True)
            with tempfile.TemporaryDirectory() as directory:
                output_dir = Path(directory)
                with self.assertRaisesRegex(
                    ValueError, r"missing required stack group: VERIFY"
                ):
                    build_engineering_stack.write_assets(output_dir)
                self.assertEqual(tuple(output_dir.iterdir()), ())

    def test_model_validation_rejects_a_missing_technology_label(self) -> None:
        verify = build_engineering_stack.STACK_GROUPS[-1]
        incomplete = (
            *build_engineering_stack.STACK_GROUPS[:-1],
            build_engineering_stack.StackGroup(
                verify.name, verify.x, verify.width, verify.nodes[:-1]
            ),
        )
        with self.assertRaisesRegex(
            ValueError, r"missing required technology label: Git"
        ):
            build_engineering_stack.validate_stack_model(incomplete)

    def test_model_validation_rejects_a_duplicate_technology_label(self) -> None:
        build = build_engineering_stack.STACK_GROUPS[0]
        duplicate = (
            build_engineering_stack.StackGroup(
                build.name, build.x, build.width, (*build.nodes, build.nodes[0])
            ),
            *build_engineering_stack.STACK_GROUPS[1:],
        )
        with self.assertRaisesRegex(
            ValueError, r"duplicate technology label: TypeScript"
        ):
            build_engineering_stack.validate_stack_model(duplicate)

    def test_model_validation_rejects_an_unapproved_technology_label(self) -> None:
        verify = build_engineering_stack.STACK_GROUPS[-1]
        python = build_engineering_stack.StackNode(
            "Python", "Py", 900, "#3776AB", 5.5, False
        )
        extra = (
            *build_engineering_stack.STACK_GROUPS[:-1],
            build_engineering_stack.StackGroup(
                verify.name, verify.x, verify.width, (*verify.nodes, python)
            ),
        )
        with self.assertRaisesRegex(
            ValueError, r"unexpected technology label: Python"
        ):
            build_engineering_stack.validate_stack_model(extra)

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
