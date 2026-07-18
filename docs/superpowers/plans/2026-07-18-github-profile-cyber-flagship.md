# GitHub Profile V3 Cyber Flagship Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build, verify, preview, and—only after explicit final approval—publish the approved Product Console × Midnight Aurora GitHub profile with a repository-owned animated hero, 3D contribution city, and contribution snake.

**Architecture:** Keep identity and project evidence in native GitHub Markdown, keep the accessible visual identity in `assets/profile-hero.svg`, and generate four contribution SVGs in one least-privilege GitHub Actions workflow. Publish machine output atomically to an `output` branch so scheduled jobs never touch `main`, and enforce content, workflow, security, and SVG contracts with Python standard-library tests.

**Tech Stack:** GitHub Flavored Markdown, SVG/CSS animation, GitHub Actions, Python 3 standard library, Git, GitHub CLI, `actions/checkout@v7.0.0`, `Platane/snk@v3.5.0`, `yoshi389111/github-profile-3d-contrib@v0.9.3`.

## Global Constraints

- Preserve the approved Product Console layout and Midnight Aurora blue–violet–green visual language.
- Page order is Hero 2.0, identity, Selected Systems, Contribution City, Operating Signals, Contribution Trail, and one repository link.
- Selected projects and order are exactly `planarian`, `ForkNeo`, and `api-image-neo`.
- English leads; Chinese remains concise supporting context.
- The hero is repository-owned, responsive, theme-aware, accessible, and disables nonessential motion under `prefers-reduced-motion: reduce`.
- The 3D city and snake each have a light and dark SVG on the `output` branch.
- Use native Markdown inline-code pills for stack and principles; do not add a shields.io badge matrix.
- Do not add WakaTime, visitor counters, typing widgets, generic stats cards, trophy widgets, fictional contact details, or placeholder URLs.
- Remote README images are limited to `raw.githubusercontent.com/alexliluz/alexliluz/output/`.
- Use only the repository-provided `GITHUB_TOKEN`; workflow permission is exactly `contents: write`.
- Pin third-party Actions to full commit SHAs, with release-tag comments.
- Scheduled generation never commits to `main`; a failed run preserves the last successful `output` assets.
- Do not push implementation or publish the changed profile before the user reviews the final preview and gives explicit publication approval.

## File Map

- Modify `tests/verify_profile.py`: V3 README order, content, remote-asset allowlist, Hero animation/accessibility, workflow, and public-link contract.
- Create `tests/test_validate_profile_assets.py`: unit contract for generated-SVG validation and CLI failures.
- Create `scripts/validate_profile_assets.py`: dependency-free validator used locally and in GitHub Actions.
- Create `.github/workflows/generate-profile-assets.yml`: daily/manual generation, validation, and atomic `output` publication.
- Modify `assets/profile-hero.svg`: approved Hero 2.0 with Midnight Aurora styling and reduced-motion behavior.
- Modify `README.md`: complete V3 Product Console composition.
- Use `.tmp/` only for local preview/render artifacts; never commit it.

---

### Task 1: Define the V3 Profile Contract

**Files:**
- Modify: `tests/verify_profile.py`
- Test: `tests/verify_profile.py`

**Interfaces:**
- Consumes: `README.md`, `assets/profile-hero.svg`, `.github/workflows/generate-profile-assets.yml`, `scripts/validate_profile_assets.py`, and the selected public GitHub URLs.
- Produces: `ProfileContractTests`, run with `python3 -m unittest -v tests/verify_profile.py`.

- [ ] **Step 1: Add V3 paths and generated-asset constants**

Add below the existing `HERO` constant:

```python
WORKFLOW = ROOT / ".github" / "workflows" / "generate-profile-assets.yml"
VALIDATOR = ROOT / "scripts" / "validate_profile_assets.py"
GENERATED_ASSET_BASE = (
    "https://raw.githubusercontent.com/alexliluz/alexliluz/output/"
)
GENERATED_ASSETS = (
    "profile-3d-light.svg",
    "profile-3d-dark.svg",
    "contribution-snake-light.svg",
    "contribution-snake-dark.svg",
)
```

- [ ] **Step 2: Replace V2 section and widget tests with the V3 README contract**

Replace `test_identity_and_v2_sections_are_present`, `test_readme_avoids_v1_sections_fragile_widgets_and_remote_images`, and `test_svg_is_accessible_responsive_static_and_theme_aware` with these methods:

```python
    def test_identity_and_v3_sections_are_present_in_order(self) -> None:
        text = self.read_readme()
        required = (
            "# Hi, I'm Alex / ASEnough.",
            "## Selected Systems",
            "## Contribution City",
            "## Operating Signals",
            "### Now",
            "### Core Stack",
            "### Principles",
            "## Contribution Trail",
            "[Explore all repositories →]",
        )
        positions = [text.index(fragment) for fragment in required]
        self.assertEqual(positions, sorted(positions))
        self.assertIn(
            "我在做更实用、可检查、可复现的 AI Coding 与 Agent 工作流工具。",
            text,
        )
        self.assertIn(
            "Turning agent demos into repeatable engineering workflows.",
            text,
        )
        self.assertIn(
            "`TypeScript` · `Python` · `CLI` · `GitHub Automation` · "
            "`Agent Workflows`",
            text,
        )
        self.assertIn(
            "`Inspectable artifacts` · `Reproducible workflows` · "
            "`Useful before impressive`",
            text,
        )

    def test_v3_dynamic_assets_are_theme_aware_and_repository_owned(self) -> None:
        text = self.read_readme()
        self.assertEqual(text.count("<picture>"), 2)
        self.assertEqual(text.count("</picture>"), 2)
        for asset in GENERATED_ASSETS:
            self.assertIn(f"{GENERATED_ASSET_BASE}{asset}", text)
        remote_sources = re.findall(
            r'(?:src|srcset)=["\'](https?://[^"\']+)["\']', text
        )
        self.assertEqual(len(remote_sources), 6)
        for source in remote_sources:
            self.assertTrue(source.startswith(GENERATED_ASSET_BASE), source)
        self.assertRegex(
            text,
            r'<source media="\(prefers-color-scheme: dark\)"[^>]+>',
        )
        self.assertRegex(
            text,
            r'<source media="\(prefers-color-scheme: light\)"[^>]+>',
        )
        self.assertIn("alt=\"3D contribution city generated", text)
        self.assertIn("alt=\"Animated contribution snake traversing", text)

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
            "shields.io",
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

    def test_svg_is_accessible_responsive_animated_and_theme_aware(self) -> None:
        tree = ET.parse(HERO)
        root = tree.getroot()
        namespace = "{http://www.w3.org/2000/svg}"
        self.assertEqual(root.attrib.get("role"), "img")
        self.assertEqual(root.attrib.get("viewBox"), "0 0 960 280")
        self.assertEqual(root.attrib.get("aria-labelledby"), "title description")
        self.assertTrue(root.find(f"{namespace}title").text.strip())
        self.assertTrue(root.find(f"{namespace}desc").text.strip())

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
```

- [ ] **Step 3: Add workflow and required-file contract tests**

Replace `test_required_files_exist` and add `test_generated_asset_workflow_is_hardened`:

```python
    def test_required_files_exist(self) -> None:
        for path in (README, HERO, WORKFLOW, VALIDATOR):
            self.assertTrue(path.is_file(), f"{path.relative_to(ROOT)} must exist")

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
            "scripts/validate_profile_assets.py",
            "git push origin HEAD:output",
        ):
            self.assertIn(fragment, source)
        self.assertNotIn("secrets.PAT", source)
        self.assertNotIn("|| exit 0", source)
        action_refs = re.findall(r"uses:\s+[^\s]+@([^\s#]+)", source)
        self.assertEqual(len(action_refs), 3)
        for ref in action_refs:
            self.assertRegex(ref, r"^[0-9a-f]{40}$")
```

- [ ] **Step 4: Update the local hero assertion and retain attribution/link tests**

In `test_local_hero_reference_resolves`, change the failure text to `README must reference the local V3 hero SVG`. Keep `test_selected_work_contains_exactly_the_three_owned_projects`, `test_final_action_links_to_all_repositories`, both URL tests, and their retry behavior unchanged.

- [ ] **Step 5: Run the V3 contract and verify RED**

Run:

```bash
python3 -m unittest -v tests/verify_profile.py
```

Expected: FAIL because the workflow and validator do not exist, README lacks the V3 sections and generated assets, and the Hero lacks Midnight Aurora animation and reduced-motion rules.

- [ ] **Step 6: Commit the red contract**

```bash
git add tests/verify_profile.py
git commit -m "test: define cyber flagship profile contract"
```

Expected: one commit containing only `tests/verify_profile.py`; tests remain intentionally red.

### Task 2: Add the Generated SVG Validator

**Files:**
- Create: `tests/test_validate_profile_assets.py`
- Create: `scripts/validate_profile_assets.py`

**Interfaces:**
- Produces: `validate_svg(path: pathlib.Path) -> None`, which raises `ValueError` for invalid output, and CLI `python3 scripts/validate_profile_assets.py PATH...`, which returns `0` only when every path is valid.
- Consumes: generated city and snake SVG paths from the workflow and release verification.

- [ ] **Step 1: Write validator unit tests**

Create `tests/test_validate_profile_assets.py`:

```python
import subprocess
import tempfile
import unittest
from pathlib import Path

from scripts.validate_profile_assets import validate_svg


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
                'ghp_123456789012345678901234567890123456'
                '</text></svg>',
            )
            with self.assertRaisesRegex(ValueError, "credential-like"):
                validate_svg(path)

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
```

- [ ] **Step 2: Run the validator tests and verify RED**

Run:

```bash
python3 -m unittest -v tests/test_validate_profile_assets.py
```

Expected: ERROR with `ModuleNotFoundError: No module named 'scripts.validate_profile_assets'`.

- [ ] **Step 3: Implement the dependency-free validator**

Create `scripts/validate_profile_assets.py`:

```python
#!/usr/bin/env python3
import argparse
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


SVG_TAG = "{http://www.w3.org/2000/svg}svg"
CREDENTIAL_PATTERN = re.compile(
    r"(?:gh[pousr]_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]{20,})"
)


def validate_svg(path: Path) -> None:
    if not path.is_file():
        raise ValueError("file does not exist")
    if path.stat().st_size == 0:
        raise ValueError("file is empty")

    try:
        source = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as error:
        raise ValueError("file is not UTF-8 text") from error

    if CREDENTIAL_PATTERN.search(source):
        raise ValueError("file contains credential-like text")

    try:
        root = ET.fromstring(source)
    except ET.ParseError as error:
        raise ValueError(f"invalid XML: {error}") from error

    if root.tag != SVG_TAG:
        raise ValueError(f"root element is {root.tag!r}, not SVG")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate generated profile SVGs")
    parser.add_argument("paths", nargs="+", type=Path)
    arguments = parser.parse_args()

    failures = []
    for path in arguments.paths:
        try:
            validate_svg(path)
        except ValueError as error:
            failures.append(f"{path}: {error}")

    if failures:
        print("\n".join(failures), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run validator tests and verify GREEN**

Run:

```bash
python3 -m unittest -v tests/test_validate_profile_assets.py
```

Expected: 4 tests pass.

- [ ] **Step 5: Commit the validator**

```bash
git add scripts/validate_profile_assets.py tests/test_validate_profile_assets.py
git commit -m "test: validate generated profile SVGs"
```

### Task 3: Add the Hardened Generated-Asset Workflow

**Files:**
- Create: `.github/workflows/generate-profile-assets.yml`
- Test: `tests/verify_profile.py`

**Interfaces:**
- Consumes: public contribution data for `${{ github.repository_owner }}` and `scripts/validate_profile_assets.py`.
- Produces: `profile-3d-light.svg`, `profile-3d-dark.svg`, `contribution-snake-light.svg`, and `contribution-snake-dark.svg` on the `output` branch.

- [ ] **Step 1: Create the workflow with pinned Actions and least privilege**

Create `.github/workflows/generate-profile-assets.yml`:

```yaml
name: Generate profile assets

on:
  schedule:
    - cron: "17 3 * * *"
  workflow_dispatch:

permissions:
  contents: write

concurrency:
  group: profile-assets
  cancel-in-progress: true

jobs:
  generate:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - name: Check out profile repository
        uses: actions/checkout@9c091bb21b7c1c1d1991bb908d89e4e9dddfe3e0 # v7.0.0

      - name: Generate contribution snakes
        uses: Platane/snk/svg-only@d8f6715049803e982ee5ff501b6b9b7d5deeb09b # v3.5.0
        with:
          github_user_name: ${{ github.repository_owner }}
          outputs: |
            dist/contribution-snake-light.svg?palette=github-light&color_snake=#8250DF
            dist/contribution-snake-dark.svg?palette=github-dark&color_snake=#A371F7

      - name: Generate 3D contribution city
        uses: yoshi389111/github-profile-3d-contrib@7d95e7d4cdc028dd1e1cbd957d65f35efb12ae39 # v0.9.3
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          USERNAME: ${{ github.repository_owner }}

      - name: Assemble stable output names
        shell: bash
        run: |
          set -euo pipefail
          mkdir -p .tmp/profile-output
          cp profile-3d-contrib/profile-green-animate.svg .tmp/profile-output/profile-3d-light.svg
          cp profile-3d-contrib/profile-night-rainbow.svg .tmp/profile-output/profile-3d-dark.svg
          cp dist/contribution-snake-light.svg .tmp/profile-output/contribution-snake-light.svg
          cp dist/contribution-snake-dark.svg .tmp/profile-output/contribution-snake-dark.svg

      - name: Validate generated SVGs
        run: python3 scripts/validate_profile_assets.py .tmp/profile-output/*.svg

      - name: Publish output branch atomically
        shell: bash
        run: |
          set -euo pipefail
          rm -rf .tmp/output-branch
          if git ls-remote --exit-code --heads origin output >/dev/null 2>&1; then
            git fetch origin output
            git worktree add --detach .tmp/output-branch origin/output
            git -C .tmp/output-branch rm -rf .
          else
            git worktree add --detach .tmp/output-branch
            git -C .tmp/output-branch checkout --orphan output
            git -C .tmp/output-branch rm -rf .
          fi
          cp .tmp/profile-output/*.svg .tmp/output-branch/
          touch .tmp/output-branch/.nojekyll
          git -C .tmp/output-branch add .
          if git -C .tmp/output-branch diff --cached --quiet; then
            exit 0
          fi
          git -C .tmp/output-branch config user.name github-actions[bot]
          git -C .tmp/output-branch config user.email 41898282+github-actions[bot]@users.noreply.github.com
          git -C .tmp/output-branch commit -m "chore: refresh profile assets"
          git -C .tmp/output-branch push origin HEAD:output
```

- [ ] **Step 2: Run the workflow contract tests**

Run:

```bash
python3 -m unittest -v tests/verify_profile.py
```

Expected: workflow hardening and required-file checks now pass; README and Hero V3 checks remain red.

- [ ] **Step 3: Inspect the workflow diff for token and permission mistakes**

Run:

```bash
git diff --check
rg -n "permissions:|contents:|secrets\.|uses:|git push" .github/workflows/generate-profile-assets.yml
```

Expected: exactly `contents: write`; only `secrets.GITHUB_TOKEN`; three full-SHA Action references; push target exactly `HEAD:output`.

- [ ] **Step 4: Commit the workflow before visual files**

```bash
git add .github/workflows/generate-profile-assets.yml
git commit -m "ci: generate cyber profile assets"
```

Record this commit SHA as `WORKFLOW_COMMIT`; staged publication later pushes exactly through this commit before any Hero or README commit.

### Task 4: Upgrade the Hero to Midnight Aurora

**Files:**
- Modify: `assets/profile-hero.svg`
- Test: `tests/verify_profile.py`

**Interfaces:**
- Consumes: the exact Hero assertions in `ProfileContractTests`.
- Produces: a self-contained `960 × 280` SVG that remains readable in dark/light themes and with motion disabled.

- [ ] **Step 1: Replace the Hero with the approved V3 SVG**

Set `assets/profile-hero.svg` to:

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 280" role="img" aria-labelledby="title description">
  <title id="title">Alex / ASEnough — Product OS · Agent Console</title>
  <desc id="description">Alex builds practical, inspectable tools for AI-assisted software work in a Midnight Aurora system interface.</desc>
  <defs>
    <linearGradient id="aurora" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#58A6FF"/>
      <stop offset="0.55" stop-color="#A371F7"/>
      <stop offset="1" stop-color="#3FB950"/>
    </linearGradient>
    <clipPath id="frame-clip"><rect x="1" y="1" width="958" height="278" rx="18"/></clipPath>
  </defs>
  <style>
    .surface { fill:#0D1117; stroke:#30363D; }
    .panel { fill:#161B22; stroke:#30363D; }
    .primary { fill:#F0F6FC; }
    .muted { fill:#8B949E; }
    .blue { fill:#58A6FF; }
    .violet { fill:#A371F7; }
    .green { fill:#3FB950; }
    .grid { stroke:#21262D; opacity:.7; }
    .beam { fill:url(#aurora); }
    .scan { fill:#58A6FF; opacity:0; animation:scan 8s ease-in-out infinite; }
    .node { animation:pulse 3.2s ease-in-out infinite; transform-origin:center; }
    .node.violet { animation-delay:1.1s; }
    .node.green { animation-delay:2.1s; }
    .mono { font-family:ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,"Liberation Mono",monospace; }
    .sans { font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }
    .eyebrow { font-size:13px; font-weight:700; letter-spacing:1.8px; }
    .headline { font-size:34px; font-weight:720; }
    .label { font-size:13px; font-weight:650; letter-spacing:1px; }
    .status { font-size:12px; font-weight:700; letter-spacing:.8px; }
    @keyframes scan {
      0%,18% { opacity:0; transform:translateX(-180px); }
      24% { opacity:.18; }
      55% { opacity:.06; transform:translateX(980px); }
      56%,100% { opacity:0; transform:translateX(980px); }
    }
    @keyframes pulse {
      0%,100% { opacity:.55; transform:scale(.82); }
      50% { opacity:1; transform:scale(1.18); }
    }
    @media (prefers-color-scheme: light) {
      .surface { fill:#FFFFFF; stroke:#D0D7DE; }
      .panel { fill:#F6F8FA; stroke:#D0D7DE; }
      .primary { fill:#1F2328; }
      .muted { fill:#59636E; }
      .blue { fill:#0969DA; }
      .violet { fill:#8250DF; }
      .green { fill:#1A7F37; }
      .grid { stroke:#D8DEE4; }
    }
    @media (prefers-reduced-motion: reduce) {
      .scan,.node { animation:none; }
      .scan { display:none; }
      .node { opacity:1; transform:none; }
    }
  </style>
  <rect class="surface" x="1" y="1" width="958" height="278" rx="18"/>
  <g clip-path="url(#frame-clip)">
    <path class="grid" d="M28 74H932M28 218H932M650 28V252M734 28V252M818 28V252M902 28V252"/>
    <rect class="scan" x="-180" y="1" width="180" height="278"/>
  </g>
  <text class="mono eyebrow blue" x="28" y="47">PRODUCT OS · AGENT CONSOLE</text>
  <rect class="panel" x="766" y="26" width="166" height="32" rx="16"/>
  <circle class="node green" cx="783" cy="42" r="4"/>
  <text class="mono status green" x="796" y="47">SYSTEM: ACTIVE</text>
  <text class="sans headline primary" x="28" y="116">Alex / ASEnough</text>
  <text class="sans headline primary" x="28" y="160">Building practical, inspectable tools for</text>
  <text class="sans headline primary" x="28" y="201">AI-assisted software work.</text>
  <rect class="beam" x="28" y="225" width="904" height="3" rx="1.5"/>
  <circle class="node blue" cx="38" cy="250" r="4"/>
  <circle class="node violet" cx="52" cy="250" r="4"/>
  <circle class="node green" cx="66" cy="250" r="4"/>
  <text class="mono label muted" x="86" y="255">AI CODING · AGENT WORKFLOWS · DEVELOPER TOOLS</text>
</svg>
```

- [ ] **Step 2: Run the Hero contract**

Run:

```bash
python3 -m unittest -v tests.verify_profile.ProfileContractTests.test_svg_is_accessible_responsive_animated_and_theme_aware
```

Expected: PASS.

- [ ] **Step 3: Parse and render-check the SVG**

Run:

```bash
python3 -c 'import xml.etree.ElementTree as ET; ET.parse("assets/profile-hero.svg")'
qlmanage -t -s 1200 -o .tmp assets/profile-hero.svg
```

Expected: XML parse exits `0`; `.tmp/profile-hero.svg.png` is generated and shows legible content without clipping.

- [ ] **Step 4: Commit the Hero**

```bash
git add assets/profile-hero.svg
git commit -m "feat: add Midnight Aurora profile hero"
```

### Task 5: Compose the Cyber Flagship README

**Files:**
- Modify: `README.md`
- Test: `tests/verify_profile.py`

**Interfaces:**
- Consumes: local `assets/profile-hero.svg` and the four stable filenames produced on the `output` branch.
- Produces: the complete GitHub-renderable V3 profile.

- [ ] **Step 1: Replace README with the approved composition**

Set `README.md` to:

```markdown
<img src="./assets/profile-hero.svg" alt="Alex / ASEnough builds practical, inspectable tools for AI-assisted software work" width="100%">

# Hi, I'm Alex / ASEnough.

我在做更实用、可检查、可复现的 AI Coding 与 Agent 工作流工具。

## Selected Systems

### [01 / Planarian](https://github.com/alexliluz/planarian)

`Experimental` · `Agent Workflow` · `TypeScript`

**Reproducible UI reconstruction workflows for coding agents.**

Planarian turns visual reconstruction into an inspectable process with stable artifacts, task bundles, validation commands, and explicit agent handoffs.

### [02 / ForkNeo](https://github.com/alexliluz/ForkNeo)

`Active` · `CLI` · `GitHub Automation` · `TypeScript`

**Safe fork-to-independent repository migration without losing history.**

ForkNeo preserves branches, tags, default-branch state, and Git LFS objects, then verifies the independent repository.

### [03 / api-image-neo](https://github.com/alexliluz/api-image-neo)

`Active` · `Codex Skill` · `Image Generation` · `Python`

**Provider-flexible image generation workflows for Codex.**

The skill supports generation, reference-image workflows, and editing through OpenAI-compatible providers while reusing existing Codex configuration.

## Contribution City

Daily GitHub activity, rendered as a 3D contribution city.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/alexliluz/alexliluz/output/profile-3d-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/alexliluz/alexliluz/output/profile-3d-light.svg">
  <img src="https://raw.githubusercontent.com/alexliluz/alexliluz/output/profile-3d-light.svg" alt="3D contribution city generated from Alex's GitHub contribution calendar" width="100%">
</picture>

## Operating Signals

### Now

Turning agent demos into repeatable engineering workflows.

把 Agent Demo 变成可复现、可验证、可长期维护的工程工作流。

### Core Stack

`TypeScript` · `Python` · `CLI` · `GitHub Automation` · `Agent Workflows`

### Principles

`Inspectable artifacts` · `Reproducible workflows` · `Useful before impressive`

## Contribution Trail

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/alexliluz/alexliluz/output/contribution-snake-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/alexliluz/alexliluz/output/contribution-snake-light.svg">
  <img src="https://raw.githubusercontent.com/alexliluz/alexliluz/output/contribution-snake-light.svg" alt="Animated contribution snake traversing Alex's GitHub contribution grid" width="100%">
</picture>

---

[Explore all repositories →](https://github.com/alexliluz?tab=repositories)
```

- [ ] **Step 2: Run the complete profile contract**

Run:

```bash
python3 -m unittest -v tests/verify_profile.py
```

Expected: all profile-contract tests pass, including public URL checks.

- [ ] **Step 3: Commit the README**

```bash
git add README.md
git commit -m "feat: compose cyber flagship profile"
```

### Task 6: Run the Local Completion Audit and Prepare the Preview

**Files:**
- Inspect: `README.md`
- Inspect: `assets/profile-hero.svg`
- Inspect: `.github/workflows/generate-profile-assets.yml`
- Inspect: `scripts/validate_profile_assets.py`
- Inspect: `tests/verify_profile.py`
- Inspect: `tests/test_validate_profile_assets.py`
- Create only under `.tmp/`: local render and audit artifacts.

**Interfaces:**
- Consumes: all V3 implementation commits.
- Produces: evidence for the user preview and publication decision; does not publish anything.

- [ ] **Step 1: Run all dependency-free tests**

Run:

```bash
python3 -m unittest discover -s tests -v
```

Expected: every test passes.

- [ ] **Step 2: Run static integrity and policy checks**

Run:

```bash
git diff --check origin/main...HEAD
python3 -c 'import xml.etree.ElementTree as ET; ET.parse("assets/profile-hero.svg")'
rg -n "TBD|TODO|example\.com|你的邮箱|demolab|vercel\.app|herokuapp|wakatime|shields\.io" README.md assets .github scripts tests
```

Expected: diff and XML checks exit `0`; `rg` finds only explicit forbidden-pattern assertions in tests, never production README, SVG, workflow, or scripts.

- [ ] **Step 3: Confirm commit ordering supports staged publication**

Run:

```bash
git log --reverse --format='%h %s' origin/main..HEAD
git show --name-only --format='%H %s' "$WORKFLOW_COMMIT"
```

Expected: the workflow commit precedes both Hero and README commits and contains no `README.md` or `assets/profile-hero.svg` change.

- [ ] **Step 4: Render and inspect the Hero**

Run:

```bash
mkdir -p .tmp/profile-v3-preview
qlmanage -t -s 1440 -o .tmp/profile-v3-preview assets/profile-hero.svg
```

Inspect `.tmp/profile-v3-preview/profile-hero.svg.png` for text clipping, contrast, scan-line artifacts, hierarchy, and narrow-width legibility. Also inspect the source with reduced motion enabled in a browser preview when available.

- [ ] **Step 5: Show the user the approved composition and implementation evidence**

Present the rendered Hero, exact README section sequence, workflow security summary, and passing test counts. State that live 3D and snake assets require the staged workflow publication described in Task 7. Ask for explicit publication approval; do not push during this step.

### Task 7: Stage Generated Assets and Publish Only After Approval

**Files:**
- No new source files.
- Remote mutation: `main` and generated `output` branches of `alexliluz/alexliluz`.

**Interfaces:**
- Consumes: explicit publication approval, `WORKFLOW_COMMIT`, final local `main`, GitHub CLI authentication, and the four asset names from the workflow.
- Produces: verified generated assets followed by the live Cyber Flagship profile.

- [ ] **Step 1: Reconfirm authorization and remote state**

Run only after explicit publication approval:

```bash
git status --short
git fetch origin
git rev-parse origin/main
git merge-base --is-ancestor origin/main "$WORKFLOW_COMMIT"
.tmp/gh-cli/gh_2.96.0_macOS_arm64/bin/gh auth status
```

Expected: no tracked changes; origin can fast-forward through `WORKFLOW_COMMIT`; GitHub authentication has `repo` and `workflow` scopes.

- [ ] **Step 2: Push only through the workflow commit**

```bash
git push origin "$WORKFLOW_COMMIT":main
```

Expected: remote `main` advances through the validator and workflow commit but does not yet contain the V3 Hero or README commits.

- [ ] **Step 3: Trigger and follow generated-asset workflow**

```bash
.tmp/gh-cli/gh_2.96.0_macOS_arm64/bin/gh workflow run generate-profile-assets.yml --repo alexliluz/alexliluz
RUN_ID=$(.tmp/gh-cli/gh_2.96.0_macOS_arm64/bin/gh run list \
  --repo alexliluz/alexliluz \
  --workflow generate-profile-assets.yml \
  --event workflow_dispatch \
  --limit 1 \
  --json databaseId \
  --jq '.[0].databaseId')
test -n "$RUN_ID"
.tmp/gh-cli/gh_2.96.0_macOS_arm64/bin/gh run watch "$RUN_ID" --repo alexliluz/alexliluz --exit-status
```

Expected: `RUN_ID` identifies the newly dispatched run and `Generate profile assets` completes successfully. Before watching, compare its `createdAt` from `gh run view "$RUN_ID" --json createdAt` with the dispatch time if another manual run could have started concurrently.

- [ ] **Step 4: Download and validate all four published assets**

Download each of these URLs into `.tmp/profile-v3-live-assets/` using a non-logging HTTP client, then validate them with `scripts/validate_profile_assets.py`:

```text
https://raw.githubusercontent.com/alexliluz/alexliluz/output/profile-3d-light.svg
https://raw.githubusercontent.com/alexliluz/alexliluz/output/profile-3d-dark.svg
https://raw.githubusercontent.com/alexliluz/alexliluz/output/contribution-snake-light.svg
https://raw.githubusercontent.com/alexliluz/alexliluz/output/contribution-snake-dark.svg
```

Run:

```bash
python3 scripts/validate_profile_assets.py .tmp/profile-v3-live-assets/*.svg
```

Expected: all four SVGs validate. Render and show at least one city and one snake variant to the user before the final profile push.

- [ ] **Step 5: Obtain final live-profile approval**

Show the real generated city and snake together with the Hero and complete README composition. Ask for confirmation to publish the final Hero and README commits. Do not infer this second approval from the earlier workflow-only approval.

- [ ] **Step 6: Push the complete V3 branch after final confirmation**

```bash
git push origin main
```

Expected: `origin/main` equals local `main` and the profile README now references already-existing output assets.

- [ ] **Step 7: Verify the live profile and remote invariants**

Run:

```bash
git fetch origin
test "$(git rev-parse HEAD)" = "$(git rev-parse origin/main)"
python3 -m unittest discover -s tests -v
.tmp/gh-cli/gh_2.96.0_macOS_arm64/bin/gh api repos/alexliluz/alexliluz/branches/output --jq '.name'
```

Inspect <https://github.com/alexliluz> in light, dark, desktop, and narrow layouts. Confirm Hero, city, project links, operating signals, and snake render without broken images or horizontal overflow.

- [ ] **Step 8: Report publication evidence**

Report the final commit SHA, workflow run URL, `output` branch presence, four validated asset URLs, test count, live profile URL, and any intentionally deferred items. Do not mark the overall goal complete until every acceptance criterion in the design spec has authoritative evidence.
