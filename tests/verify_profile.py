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
SIGNAL_SOURCES = (
    (
        "(prefers-reduced-motion: reduce) and (prefers-color-scheme: dark)",
        "contribution-signal-dark-static.svg",
    ),
    (
        "(prefers-reduced-motion: reduce) and (prefers-color-scheme: light)",
        "contribution-signal-light-static.svg",
    ),
    ("(prefers-color-scheme: dark)", "contribution-signal-dark.svg"),
    ("(prefers-color-scheme: light)", "contribution-signal-light.svg"),
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
        positioning = (
            "TypeScript / Python developer focused on developer tooling, "
            "CLI automation, and reproducible systems.<br>\n"
            "主要使用 TypeScript、Python 与 Node.js，专注开发者工具、"
            "CLI 自动化和可复现工程工作流。"
        )
        required = (
            "./assets/alex-signature.svg",
            positioning,
            "## Tech stack",
            "## Featured work",
            "## Contribution Signal",
            "[Explore all repositories →]",
        )
        self.assertIn(positioning, text)
        positions = [text.index(fragment) for fragment in required]
        self.assertEqual(positions, sorted(positions))
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
        technology_badges = re.findall(
            r"https://img\.shields\.io/badge/[^\"\s>]+",
            text,
        )
        self.assertEqual(
            technology_badges,
            [
                "https://img.shields.io/badge/TypeScript-3178C6"
                "?style=flat-square&logo=typescript&logoColor=white",
                "https://img.shields.io/badge/Python-3776AB"
                "?style=flat-square&logo=python&logoColor=white",
                "https://img.shields.io/badge/Node.js-339933"
                "?style=flat-square&logo=nodedotjs&logoColor=white",
                "https://img.shields.io/badge/GitHub_Actions-2088FF"
                "?style=flat-square&logo=githubactions&logoColor=white",
            ],
        )
        star_badges = re.findall(
            r"https://img\.shields\.io/github/stars/[^\"\s>]+",
            text,
        )
        self.assertEqual(len(star_badges), 3)
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
        picture_match = re.search(r"<picture>\n(.*?)\n</picture>", text, re.DOTALL)
        self.assertIsNotNone(picture_match)
        picture = picture_match.group(1)
        sources = re.findall(
            r'^[ \t]*<source media="([^"]+)" srcset="([^"]+)">$',
            picture,
            re.MULTILINE,
        )
        self.assertEqual(
            sources,
            [
                (media, f"{GENERATED_ASSET_BASE}{asset}")
                for media, asset in SIGNAL_SOURCES
            ],
        )
        fallback = re.findall(
            r'^[ \t]*<img src="([^"]+)" alt="([^"]+)" width="100%">$',
            picture,
            re.MULTILINE,
        )
        self.assertEqual(
            fallback,
            [
                (
                    f"{GENERATED_ASSET_BASE}contribution-signal-light.svg",
                    "Alex contribution signal: Star trend, 3D contribution city, "
                    "and original contribution-grid snake",
                )
            ],
        )

    def test_contribution_signal_keeps_four_stable_filenames_in_source_order(
        self,
    ) -> None:
        text = self.read_readme()
        picture = re.search(r"<picture>\n(.*?)\n</picture>", text, re.DOTALL)
        self.assertIsNotNone(picture)
        filenames = re.findall(
            r'<source media="[^"]+" srcset="[^"]+/([^"]+\.svg)">',
            picture.group(1),
        )
        self.assertEqual(
            filenames,
            [
                "contribution-signal-dark-static.svg",
                "contribution-signal-light-static.svg",
                "contribution-signal-dark.svg",
                "contribution-signal-light.svg",
            ],
        )

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
        step_prefix = "      - name: "

        def step_block(name: str) -> str:
            start = source.index(f"{step_prefix}{name}\n")
            end = source.find(f"\n{step_prefix}", start + len(step_prefix))
            return source[start:] if end == -1 else source[start:end]

        def line_position(block: str, line: str) -> int:
            match = re.search(
                rf"(?m)^[ \t]*{re.escape(line)}[ \t]*$",
                block,
            )
            self.assertIsNotNone(match, line)
            return match.start()

        def output_branch_case_arms(block: str) -> tuple[str, str, str]:
            status_init = "output_branch_status=0"
            probe = (
                "git ls-remote --exit-code --heads origin refs/heads/output "
                ">/dev/null 2>&1 || output_branch_status=$?"
            )
            case_start = 'case "$output_branch_status" in'
            self.assertEqual(block.count(status_init), 1)
            self.assertEqual(block.count(probe), 1)
            self.assertEqual(block.count(case_start), 1)
            self.assertEqual(
                [
                    line_position(block, status_init),
                    line_position(block, probe),
                    line_position(block, case_start),
                ],
                sorted(
                    (
                        line_position(block, status_init),
                        line_position(block, probe),
                        line_position(block, case_start),
                    )
                ),
            )
            match = re.search(
                r'(?ms)^[ \t]*case "\$output_branch_status" in[ \t]*\n'
                r'[ \t]*0\)[ \t]*\n(?P<exists>.*?)^[ \t]*;;[ \t]*\n'
                r'[ \t]*2\)[ \t]*\n(?P<absent>.*?)^[ \t]*;;[ \t]*\n'
                r'[ \t]*\*\)[ \t]*\n(?P<failure>.*?)^[ \t]*;;[ \t]*\n'
                r'[ \t]*esac[ \t]*$',
                block,
            )
            self.assertIsNotNone(match, "expected explicit 0/2/other status handling")
            return (
                match.group("exists"),
                match.group("absent"),
                match.group("failure"),
            )

        for fragment in (
            "schedule:",
            "workflow_dispatch:",
            "timeout-minutes: 15",
            "actions/checkout@9c091bb21b7c1c1d1991bb908d89e4e9dddfe3e0",
            "Platane/snk/svg-only@d8f6715049803e982ee5ff501b6b9b7d5deeb09b",
            "yoshi389111/github-profile-3d-contrib@7d95e7d4cdc028dd1e1cbd957d65f35efb12ae39",
        ):
            self.assertIn(fragment, source)

        permissions = source[
            source.index("permissions:") : source.index("\nconcurrency:")
        ]
        self.assertEqual(permissions, "permissions:\n  contents: write\n")
        self.assertEqual(
            re.findall(
                r"(?m)^[ \t]*permissions:[ \t]*$",
                source,
            ),
            ["permissions:"],
        )
        self.assertEqual(
            re.findall(
                r"(?m)^[ \t]*cancel-in-progress:[ \t]*(\S+)[ \t]*$",
                source,
            ),
            ["true"],
        )

        secret_expressions = re.findall(
            r"\$\{\{\s*secrets[^}]*\}\}",
            source,
        )
        self.assertTrue(secret_expressions)
        self.assertEqual(
            set(secret_expressions),
            {"${{ secrets.GITHUB_TOKEN }}"},
        )
        self.assertNotRegex(source, r"(?i)\b(?:PAT|PROFILE_STATS_TOKEN)\b")
        self.assertNotIn("|| exit 0", source)

        action_refs = re.findall(r"uses:\s+[^\s]+@([^\s#]+)", source)
        self.assertEqual(len(action_refs), 3)
        for ref in action_refs:
            self.assertRegex(ref, r"^[0-9a-f]{40}$")

        ordered_steps = (
            "Generate contribution snakes",
            "Generate 3D contribution city",
            "Assemble stable output names",
            "Restore previous Star snapshots",
            "Record current Star counts",
            "Compose Contribution Signal assets",
            "Validate generated SVGs",
            "Publish output branch atomically",
        )
        step_positions = [
            source.index(f"{step_prefix}{name}\n") for name in ordered_steps
        ]
        self.assertEqual(step_positions, sorted(step_positions))

        source_assets = (
            "profile-3d-light.svg",
            "profile-3d-dark.svg",
            "contribution-snake-light.svg",
            "contribution-snake-dark.svg",
        )
        assembled_assets = re.findall(
            r"(?m)^[ \t]*cp \S+ \.tmp/profile-output/([^\s]+\.svg)$",
            step_block("Assemble stable output names"),
        )
        self.assertEqual(assembled_assets, list(source_assets))

        star_history = step_block("Record current Star counts")
        star_history_commands = (
            "GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}",
            "python3 scripts/profile_star_history.py \\",
            "--history .tmp/previous-star-history.json \\",
            "--output .tmp/profile-output/star-history.json \\",
            '--owner "${{ github.repository_owner }}"',
        )
        star_history_positions = [
            line_position(star_history, command)
            for command in star_history_commands
        ]
        self.assertEqual(
            star_history_positions,
            sorted(star_history_positions),
        )

        composite_assets = (
            "contribution-signal-light.svg",
            "contribution-signal-dark.svg",
            "contribution-signal-light-static.svg",
            "contribution-signal-dark-static.svg",
        )
        compose = step_block("Compose Contribution Signal assets")
        self.assertNotIn(
            "python3 scripts/compose_contribution_signal.py",
            compose,
        )
        compose_commands = (
            "python3 -m scripts.compose_contribution_signal \\",
            "--city-light .tmp/profile-output/profile-3d-light.svg \\",
            "--city-dark .tmp/profile-output/profile-3d-dark.svg \\",
            "--snake-light .tmp/profile-output/contribution-snake-light.svg \\",
            "--snake-dark .tmp/profile-output/contribution-snake-dark.svg \\",
            "--history .tmp/profile-output/star-history.json \\",
            "--output-dir .tmp/profile-output",
        )
        compose_positions = [
            line_position(compose, command) for command in compose_commands
        ]
        self.assertEqual(
            compose_positions,
            sorted(compose_positions),
        )
        self.assertEqual(
            re.findall(
                r"(?m)^[ \t]*test -f \.tmp/profile-output/([^\s]+\.svg)$",
                compose,
            ),
            list(composite_assets),
        )

        restore = step_block("Restore previous Star snapshots")
        restore_exists, restore_absent, restore_failure = output_branch_case_arms(
            restore
        )
        restore_commands = (
            "git fetch origin output",
            "if git cat-file -e origin/output:star-history.json "
            "2>/dev/null; then",
            "git show origin/output:star-history.json > "
            ".tmp/previous-star-history.json",
        )
        restore_positions = [
            line_position(restore, command) for command in restore_commands
        ]
        self.assertEqual(restore_positions, sorted(restore_positions))
        self.assertEqual(restore.count("git fetch origin output"), 1)
        self.assertEqual(
            restore.count("origin/output:star-history.json"),
            2,
        )
        for command in restore_commands:
            self.assertIn(command, restore_exists)
        self.assertEqual(restore_absent.strip(), "")
        self.assertIn('exit "$output_branch_status"', restore_failure)
        self.assertNotIn("git fetch", restore_failure)

        publication = step_block("Publish output branch atomically")
        self.assertEqual(
            source.count(f"{step_prefix}Publish output branch atomically\n"),
            1,
        )
        publication_exists, publication_absent, publication_failure = (
            output_branch_case_arms(publication)
        )
        self.assertIn("git fetch origin output", publication_exists)
        self.assertIn(
            "git worktree add --detach .tmp/output-branch origin/output",
            publication_exists,
        )
        self.assertIn(
            "git worktree add --detach .tmp/output-branch",
            publication_absent,
        )
        self.assertIn(
            "git -C .tmp/output-branch checkout --orphan output",
            publication_absent,
        )
        self.assertIn('exit "$output_branch_status"', publication_failure)
        self.assertNotIn("git worktree add", publication_failure)
        self.assertEqual(
            re.findall(
                r"(?m)^[ \t]*cp \.tmp/profile-output/"
                r"(\*\.svg|star-history\.json) \.tmp/output-branch/$",
                publication,
            ),
            ["*.svg", "star-history.json"],
        )
        push_commands = re.findall(
            r"(?m)^[ \t]*(git(?: -C \S+)? push [^\n]+)$",
            source,
        )
        self.assertEqual(
            push_commands,
            ["git -C .tmp/output-branch push origin HEAD:output"],
        )

        validate = step_block("Validate generated SVGs")
        validate_command = (
            "python3 scripts/validate_profile_assets.py .tmp/profile-output/*.svg"
        )
        line_position(validate, f"run: {validate_command}")
        validate_position = source.index(validate_command)
        publish_position = step_positions[-1]
        svg_copy_position = source.index(
            "cp .tmp/profile-output/*.svg .tmp/output-branch/",
            publish_position,
        )
        json_copy_position = source.index(
            "cp .tmp/profile-output/star-history.json .tmp/output-branch/",
            publish_position,
        )
        push_position = source.index(push_commands[0], publish_position)
        self.assertLess(
            validate_position,
            publish_position,
        )
        self.assertEqual(
            [svg_copy_position, json_copy_position, push_position],
            sorted((svg_copy_position, json_copy_position, push_position)),
        )

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
