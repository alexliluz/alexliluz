import re
import unittest
import xml.etree.ElementTree as ET
from contextlib import nullcontext
from pathlib import Path
from unittest.mock import patch
from urllib.error import URLError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
HERO = ROOT / "assets" / "profile-hero.svg"
PROFILE_URLS = (
    "https://github.com/alexliluz/planarian",
    "https://github.com/alexliluz/ForkNeo",
    "https://github.com/alexliluz/api-image-neo",
    "https://github.com/alexliluz?tab=repositories",
)


class ProfileContractTests(unittest.TestCase):
    def read_readme(self) -> str:
        self.assertTrue(README.is_file(), "README.md must exist")
        return README.read_text(encoding="utf-8")

    def test_required_files_exist(self) -> None:
        self.assertTrue(README.is_file(), "README.md must exist")
        self.assertTrue(HERO.is_file(), "assets/profile-hero.svg must exist")

    def test_identity_and_v2_sections_are_present(self) -> None:
        text = self.read_readme()
        self.assertIn("# Hi, I'm Alex / ASEnough.", text)
        self.assertIn(
            "我在做更实用、可检查、可复现的 AI Coding 与 Agent 工作流工具。",
            text,
        )
        self.assertIn("## What I'm Building", text)
        self.assertIn("## Now", text)
        self.assertIn("## Building Principles", text)
        self.assertIn(
            "Turning agent demos into repeatable engineering workflows.",
            text,
        )
        self.assertIn(
            "`Inspectable artifacts` · `Reproducible workflows` · "
            "`Useful before impressive`",
            text,
        )

    def test_selected_work_contains_exactly_the_three_owned_projects(self) -> None:
        text = self.read_readme()
        repo_names = set(
            re.findall(r"https://github\.com/alexliluz/([A-Za-z0-9_.-]+)", text)
        )
        self.assertEqual(repo_names, {"planarian", "ForkNeo", "api-image-neo"})
        self.assertNotIn("linuxdo-scripts-neo", text)
        for lead in (
            "Reproducible UI reconstruction workflows for coding agents.",
            "Safe fork-to-independent repository migration without losing history.",
            "Provider-flexible image generation workflows for Codex.",
        ):
            self.assertIn(lead, text)

    def test_final_action_links_to_all_repositories(self) -> None:
        text = self.read_readme()
        self.assertIn(
            "[Explore all repositories →]"
            "(https://github.com/alexliluz?tab=repositories)",
            text,
        )

    def test_readme_avoids_v1_sections_fragile_widgets_and_remote_images(self) -> None:
        text = self.read_readme()
        lower_text = text.lower()
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
            self.assertNotIn(fragment, lower_text)
        for obsolete in (
            "## Selected Work",
            "## Working With",
            "## Connect",
            "builder-console.svg",
        ):
            self.assertNotIn(obsolete, text)
        self.assertNotRegex(text, r"!\[[^\]]*\]\(https?://")
        self.assertNotRegex(text, r"<img[^>]+src=[\"']https?://")

    def test_local_hero_reference_resolves(self) -> None:
        text = self.read_readme()
        match = re.search(
            r'<img[^>]+src=["\'](\./assets/profile-hero\.svg)["\'][^>]*>',
            text,
        )
        self.assertIsNotNone(match, "README must reference the local V2 hero SVG")
        self.assertIn("alt=", match.group(0))
        self.assertIn('width="100%"', match.group(0))
        self.assertTrue((ROOT / match.group(1)).resolve().is_file())

    def test_svg_is_accessible_responsive_static_and_theme_aware(self) -> None:
        self.assertTrue(HERO.is_file(), "assets/profile-hero.svg must exist")
        tree = ET.parse(HERO)
        root = tree.getroot()
        namespace = "{http://www.w3.org/2000/svg}"
        self.assertEqual(root.attrib.get("role"), "img")
        self.assertEqual(root.attrib.get("viewBox"), "0 0 960 280")
        self.assertEqual(root.attrib.get("aria-labelledby"), "title description")
        title = root.find(f"{namespace}title")
        description = root.find(f"{namespace}desc")
        self.assertIsNotNone(title)
        self.assertIsNotNone(description)
        self.assertTrue(title.text.strip())
        self.assertTrue(description.text.strip())

        source = HERO.read_text(encoding="utf-8")
        self.assertIn("prefers-color-scheme: light", source)
        self.assertNotIn("<animate", source)
        self.assertNotRegex(source, r"(?:href|src)=[\"']https?://")
        self.assertIn("ALEX / ASENOUGH", source)
        self.assertIn("BUILD: ACTIVE", source)
        self.assertIn("Building practical, inspectable tools for", source)
        self.assertIn("AI-assisted software work.", source)
        self.assertIn("turning demos into repeatable systems_", source)
        for color in (
            "#0D1117",
            "#30363D",
            "#F0F6FC",
            "#8B949E",
            "#58A6FF",
            "#3FB950",
            "#FFFFFF",
            "#D0D7DE",
            "#1F2328",
            "#59636E",
            "#0969DA",
            "#1A7F37",
        ):
            self.assertIn(color, source)

    def test_selected_project_urls_are_public(self) -> None:
        for url in PROFILE_URLS:
            with self.subTest(url=url):
                request = Request(
                    url,
                    headers={"User-Agent": "alexliluz-profile-verifier"},
                )
                for attempt in range(3):
                    try:
                        with urlopen(request, timeout=15) as response:
                            self.assertLess(response.status, 400)
                        break
                    except URLError:
                        if attempt == 2:
                            raise

    def test_public_url_check_retries_one_transient_failure(self) -> None:
        class SuccessfulResponse:
            status = 200

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc_value, traceback):
                return False

        outcomes = [URLError("transient TLS EOF")]
        outcomes.extend(SuccessfulResponse() for _ in PROFILE_URLS)

        def flaky_urlopen(*args, **kwargs):
            outcome = outcomes.pop(0)
            if isinstance(outcome, Exception):
                raise outcome
            return outcome

        with patch.object(
            self,
            "subTest",
            side_effect=lambda **kwargs: nullcontext(),
        ), patch(f"{__name__}.urlopen", side_effect=flaky_urlopen) as mocked:
            try:
                self.test_selected_project_urls_are_public()
            except URLError as error:
                self.fail(f"public URL verification did not retry: {error}")

        self.assertEqual(mocked.call_count, len(PROFILE_URLS) + 1)


if __name__ == "__main__":
    unittest.main()
