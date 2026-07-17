import re
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
HERO = ROOT / "assets" / "builder-console.svg"


class ProfileContractTests(unittest.TestCase):
    def read_readme(self) -> str:
        self.assertTrue(README.is_file(), "README.md must exist")
        return README.read_text(encoding="utf-8")

    def test_required_files_exist(self) -> None:
        self.assertTrue(README.is_file(), "README.md must exist")
        self.assertTrue(HERO.is_file(), "assets/builder-console.svg must exist")

    def test_identity_and_sections_are_present(self) -> None:
        text = self.read_readme()
        self.assertIn("# Hi, I'm Alex / ASEnough.", text)
        self.assertIn(
            "I build agent-ready developer tools for AI-assisted software work.",
            text,
        )
        for heading in (
            "## Selected Work",
            "## Now",
            "## Building Principles",
            "## Working With",
            "## Connect",
        ):
            self.assertIn(heading, text)

    def test_selected_work_contains_exactly_the_three_owned_projects(self) -> None:
        text = self.read_readme()
        repo_names = set(
            re.findall(r"https://github\.com/alexliluz/([A-Za-z0-9_.-]+)", text)
        )
        self.assertEqual(repo_names, {"planarian", "ForkNeo", "api-image-neo"})
        self.assertNotIn("linuxdo-scripts-neo", text)

    def test_readme_avoids_fragile_widgets_and_complex_layouts(self) -> None:
        text = self.read_readme().lower()
        forbidden = (
            "github-readme-stats",
            "streak-stats",
            "profile-views",
            "github-profile-trophy",
            "github-contribution-grid-snake",
            "readme-typing-svg",
            "spotify-github-profile",
            "<table",
        )
        for fragment in forbidden:
            self.assertNotIn(fragment, text)
        self.assertNotRegex(text, r"!\[[^\]]*\]\(https?://")
        self.assertNotRegex(text, r"<img[^>]+src=[\"']https?://")

    def test_local_hero_reference_resolves(self) -> None:
        text = self.read_readme()
        match = re.search(
            r'<img[^>]+src=["\'](\./assets/builder-console\.svg)["\'][^>]*>',
            text,
        )
        self.assertIsNotNone(match, "README must reference the local hero SVG")
        self.assertIn("alt=", match.group(0))
        self.assertTrue((ROOT / match.group(1)).resolve().is_file())

    def test_svg_is_accessible_responsive_and_theme_aware(self) -> None:
        self.assertTrue(HERO.is_file(), "assets/builder-console.svg must exist")
        tree = ET.parse(HERO)
        root = tree.getroot()
        namespace = "{http://www.w3.org/2000/svg}"
        self.assertEqual(root.attrib.get("role"), "img")
        self.assertEqual(root.attrib.get("viewBox"), "0 0 960 220")
        self.assertTrue(root.attrib.get("aria-labelledby"))
        self.assertIsNotNone(root.find(f"{namespace}title"))
        self.assertIsNotNone(root.find(f"{namespace}desc"))
        source = HERO.read_text(encoding="utf-8")
        self.assertIn("prefers-color-scheme: light", source)
        self.assertNotIn("<animate", source)


if __name__ == "__main__":
    unittest.main()
