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
SIGNATURE = ROOT / "assets" / "alex-signature.svg"
WORKFLOW = ROOT / ".github" / "workflows" / "generate-profile-assets.yml"
VALIDATOR = ROOT / "scripts" / "validate_profile_assets.py"
COMPOSER = ROOT / "scripts" / "compose_contribution_signal.py"
STAR_HISTORY = ROOT / "scripts" / "profile_star_history.py"
GENERATED_ASSET_BASE = (
    "https://raw.githubusercontent.com/alexliluz/alexliluz/output/"
)
SIGNAL_ASSETS = (
    "contribution-signal-light.svg",
    "contribution-signal-dark.svg",
    "contribution-signal-light-static.svg",
    "contribution-signal-dark-static.svg",
)
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
        for path in (
            README,
            HERO,
            SIGNATURE,
            WORKFLOW,
            VALIDATOR,
            COMPOSER,
            STAR_HISTORY,
        ):
            self.assertTrue(path.is_file(), f"{path.relative_to(ROOT)} must exist")

    def test_v4_sections_and_positioning_are_present_in_order(self) -> None:
        text = self.read_readme()
        required = (
            "./assets/alex-signature.svg",
            "TypeScript / Python developer focused on developer tooling, "
            "CLI automation, and reproducible systems.",
            "## Tech stack",
            "## Featured work",
            "## Contribution Signal",
            "[Explore all repositories →]",
        )
        positions = [text.index(fragment) for fragment in required]
        self.assertEqual(positions, sorted(positions))
        self.assertIn(
            "主要使用 TypeScript、Python 与 Node.js，专注开发者工具、"
            "CLI 自动化和可复现工程工作流。",
            text,
        )
        for removed in (
            "# Hi, I'm Alex / ASEnough 👋",
            "AI Coding",
            "AI_Agents",
            "## About me",
            "## Neon Contribution City",
            "## Contribution Snake",
        ):
            self.assertNotIn(removed, text)

    def test_four_technology_badges_and_three_star_badges_are_present(self) -> None:
        text = self.read_readme()
        for label in (
            "TypeScript-3178C6",
            "Python-3776AB",
            "Node.js-339933",
            "GitHub_Actions-2088FF",
        ):
            self.assertIn(f"https://img.shields.io/badge/{label}", text)
        self.assertEqual(text.count("https://img.shields.io/github/stars/"), 3)
        for repository in ("planarian", "ForkNeo", "api-image-neo"):
            self.assertIn(
                f"https://img.shields.io/github/stars/alexliluz/{repository}",
                text,
            )

    def test_featured_work_keeps_three_owned_projects_with_star_badges(self) -> None:
        text = self.read_readme()
        repo_names = re.findall(
            r"https://github\.com/alexliluz/([A-Za-z0-9_.-]+)", text
        )
        self.assertEqual(repo_names, ["planarian", "ForkNeo", "api-image-neo"])
        for label, repository in (
            ("Planarian", "planarian"),
            ("ForkNeo", "ForkNeo"),
            ("api-image-neo", "api-image-neo"),
        ):
            self.assertIn(
                f"[{label}](https://github.com/alexliluz/{repository})",
                text,
            )
            self.assertIn(
                f"https://img.shields.io/github/stars/alexliluz/{repository}",
                text,
            )
        for removed_copy in (
            "Reproducible UI reconstruction workflows for coding agents.",
            "Safe fork-to-independent repository migration without losing history.",
            "Provider-flexible image generation workflows for Codex.",
            "## Selected Systems",
            "## Operating Signals",
        ):
            self.assertNotIn(removed_copy, text)

    def test_final_action_links_to_all_repositories(self) -> None:
        text = self.read_readme()
        self.assertIn(
            "[Explore all repositories →]"
            "(https://github.com/alexliluz?tab=repositories)",
            text,
        )

    def test_contribution_signal_is_single_theme_and_motion_aware_picture(
        self,
    ) -> None:
        text = self.read_readme()
        self.assertEqual(text.count("<picture>"), 1)
        self.assertEqual(text.count("</picture>"), 1)
        for asset in SIGNAL_ASSETS:
            self.assertIn(f"{GENERATED_ASSET_BASE}{asset}", text)
        self.assertIn(
            'media="(prefers-reduced-motion: reduce) and '
            '(prefers-color-scheme: dark)"',
            text,
        )
        self.assertIn(
            'media="(prefers-reduced-motion: reduce) and '
            '(prefers-color-scheme: light)"',
            text,
        )
        self.assertIn('media="(prefers-color-scheme: dark)"', text)
        self.assertIn('media="(prefers-color-scheme: light)"', text)
        self.assertIn('alt="Alex contribution signal:', text)

    def test_readme_avoids_unapproved_widgets_and_placeholders(self) -> None:
        text = self.read_readme()
        lower_text = text.lower()
        forbidden = (
            "github-readme-stats",
            "streak-stats",
            "profile-views",
            "github-profile-trophy",
            "readme-typing-svg",
            "spotify-github-profile",
            "wakatime",
            "demolab.com",
            "vercel.app",
            "herokuapp.com",
            "你的邮箱",
            "example.com",
            "<table",
        )
        for fragment in forbidden:
            self.assertNotIn(fragment, lower_text)
        self.assertNotIn("linuxdo-scripts-neo", text)
        self.assertNotIn("## Connect", text)

    def test_old_hero_is_retained_but_signature_is_rendered(self) -> None:
        text = self.read_readme()
        self.assertTrue(HERO.is_file())
        self.assertTrue(SIGNATURE.is_file())
        self.assertNotIn("./assets/profile-hero.svg", text)
        self.assertIn("./assets/alex-signature.svg", text)

    def test_svg_is_accessible_responsive_animated_and_theme_aware(self) -> None:
        self.assertTrue(HERO.is_file(), "assets/profile-hero.svg must exist")
        tree = ET.parse(HERO)
        root = tree.getroot()
        namespace = "{http://www.w3.org/2000/svg}"
        self.assertEqual(root.attrib.get("role"), "img")
        self.assertEqual(root.attrib.get("viewBox"), "0 0 960 280")
        self.assertEqual(root.attrib.get("aria-labelledby"), "title description")
        title = root.find(f"{namespace}title")
        description = root.find(f"{namespace}desc")
        self.assertTrue(title.text.strip())
        self.assertTrue(description.text.strip())

        source = HERO.read_text(encoding="utf-8")
        for fragment in (
            "PRODUCT OS · AGENT CONSOLE",
            "SYSTEM: ACTIVE",
            "Alex / ASEnough",
            "Building practical, inspectable tools for",
            "AI-assisted software work.",
            "AI CODING · AGENT WORKFLOWS · DEVELOPER TOOLS",
            "prefers-color-scheme: light",
            "prefers-reduced-motion: reduce",
            "@keyframes scan",
            "@keyframes pulse",
            "#58A6FF",
            "#A371F7",
            "#3FB950",
        ):
            self.assertIn(fragment, source)
        self.assertNotRegex(source, r"(?:href|src)=[\"']https?://")

    def test_generated_asset_workflow_is_hardened(self) -> None:
        source = WORKFLOW.read_text(encoding="utf-8")
        for fragment in (
            "schedule:",
            "workflow_dispatch:",
            "contents: write",
            "concurrency:",
            "timeout-minutes: 15",
            "actions/checkout@9c091bb21b7c1c1d1991bb908d89e4e9dddfe3e0",
            "Platane/snk/svg-only@d8f6715049803e982ee5ff501b6b9b7d5deeb09b",
            "yoshi389111/github-profile-3d-contrib@7d95e7d4cdc028dd1e1cbd957d65f35efb12ae39",
            "profile-3d-light.svg",
            "profile-3d-dark.svg",
            "contribution-snake-light.svg",
            "contribution-snake-dark.svg",
            "scripts/validate_profile_assets.py",
            "git -C .tmp/output-branch push origin HEAD:output",
        ):
            self.assertIn(fragment, source)
        for fragment in (
            "scripts/profile_star_history.py",
            "scripts/compose_contribution_signal.py",
            "star-history.json",
            "contribution-signal-light.svg",
            "contribution-signal-dark.svg",
            "contribution-signal-light-static.svg",
            "contribution-signal-dark-static.svg",
            "GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}",
        ):
            self.assertIn(fragment, source)
        self.assertNotIn("secrets.PAT", source)
        self.assertNotIn("PROFILE_STATS_TOKEN", source)
        self.assertNotIn("|| exit 0", source)
        action_refs = re.findall(r"uses:\s+[^\s]+@([^\s#]+)", source)
        self.assertEqual(len(action_refs), 3)
        for ref in action_refs:
            self.assertRegex(ref, r"^[0-9a-f]{40}$")

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
