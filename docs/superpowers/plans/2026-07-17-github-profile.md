# GitHub Profile Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a publish-ready `alexliluz/alexliluz` profile README that presents Alex as a builder of agent-ready tools for AI-assisted software work.

**Architecture:** Keep the profile dependency-free: a single Markdown document contains all essential content, while one repository-owned SVG provides the terminal visual accent. A Python standard-library test locks the content structure, project attribution rules, local asset integrity, and SVG accessibility.

**Tech Stack:** GitHub Flavored Markdown, SVG 1.1, Python 3 standard library, Git.

## Global Constraints

- English is the primary language; Chinese appears only as concise supporting context.
- Selected work is exactly `planarian`, `ForkNeo`, and `api-image-neo`.
- Do not present `linuxdo-scripts-neo` as selected personal work.
- Do not use contribution streaks, visitor counters, trophy cards, language percentages, contribution snakes, typing animations, random quotes, Spotify status, or externally hosted GitHub statistics cards.
- Essential information must remain readable as Markdown text when images do not load.
- The custom SVG must be repository-owned, accessible, responsive, and compatible with light and dark themes.
- The layout must avoid multi-column HTML tables.

---

### Task 1: Define the executable profile contract

**Files:**
- Create: `tests/verify_profile.py`

**Interfaces:**
- Consumes: the requirements in `docs/superpowers/specs/2026-07-17-github-profile-design.md`.
- Produces: a standard-library test suite run with `python3 -m unittest -v tests/verify_profile.py`.

- [ ] **Step 1: Write the failing structural tests**

Create `tests/verify_profile.py`:

```python
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
```

- [ ] **Step 2: Run the tests to verify RED**

Run:

```bash
python3 -m unittest -v tests/verify_profile.py
```

Expected: failures stating that `README.md` and `assets/builder-console.svg` do not exist.

- [ ] **Step 3: Commit the executable contract**

```bash
git add tests/verify_profile.py
git commit -m "test: define profile README contract"
```

### Task 2: Implement the Builder's Console profile

**Files:**
- Create: `README.md`
- Create: `assets/builder-console.svg`
- Create: `.gitignore`

**Interfaces:**
- Consumes: the assertions in `tests/verify_profile.py`.
- Produces: a GitHub-renderable profile README and the local SVG referenced from it.

- [ ] **Step 1: Create the accessible terminal SVG**

Create `assets/builder-console.svg`:

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 220" role="img" aria-labelledby="title description">
  <title id="title">Alex's Builder Console</title>
  <desc id="description">A terminal-style introduction describing Alex's focus on AI coding, agent workflows, and developer tools.</desc>
  <style>
    .panel { fill: #0d1117; stroke: #30363d; }
    .bar { fill: #161b22; }
    .prompt { fill: #3fb950; }
    .command { fill: #58a6ff; }
    .text { fill: #c9d1d9; }
    .muted { fill: #8b949e; }
    text { font: 18px ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace; }
    @media (prefers-color-scheme: light) {
      .panel { fill: #ffffff; stroke: #d0d7de; }
      .bar { fill: #f6f8fa; }
      .prompt { fill: #1a7f37; }
      .command { fill: #0969da; }
      .text { fill: #24292f; }
      .muted { fill: #57606a; }
    }
  </style>
  <rect class="panel" x="1" y="1" width="958" height="218" rx="14"/>
  <path class="bar" d="M15 1h930a14 14 0 0 1 14 14v27H1V15A14 14 0 0 1 15 1Z"/>
  <circle cx="23" cy="22" r="6" fill="#ff5f57"/>
  <circle cx="43" cy="22" r="6" fill="#febc2e"/>
  <circle cx="63" cy="22" r="6" fill="#28c840"/>
  <text x="28" y="78"><tspan class="prompt">alex@github:~$</tspan><tspan class="command"> ./about</tspan></text>
  <text class="text" x="28" y="116">builder.mode = "agent-ready"</text>
  <text class="text" x="28" y="152">focus = ["AI coding", "agent workflows", "developer tools"]</text>
  <text class="muted" x="28" y="188">status = "building practical things"</text>
</svg>
```

- [ ] **Step 2: Create the profile README and ignore scratch output**

Create `.gitignore`:

```gitignore
.tmp/
```

Create `README.md`:

```markdown
<img src="./assets/builder-console.svg" alt="Alex's Builder Console: AI coding, agent workflows, and developer tools" width="100%">

# Hi, I'm Alex / ASEnough.

**I build agent-ready developer tools for AI-assisted software work.**

我在做面向 AI Coding、Agent 工作流和开发者自动化的实用工具。

[Selected Work](#selected-work) · [Now](#now) · [Building Principles](#building-principles) · [Connect](#connect)

## Selected Work

### [Planarian](https://github.com/alexliluz/planarian)

`Experimental` · `Agent Workflow` · `TypeScript` · `UI Engineering`

> Repeatable UI reconstruction workflows designed for coding agents.

Planarian turns UI reconstruction into an inspectable, file-based process with stable session artifacts, task bundles, validation commands, and agent handoffs.

### [ForkNeo](https://github.com/alexliluz/ForkNeo)

`Active` · `CLI` · `GitHub Automation` · `TypeScript`

> Convert GitHub forks into independent repositories while preserving Git history.

ForkNeo safely mirrors branches, tags, default-branch state, and Git LFS objects, then verifies the resulting independent repository.

### [api-image-neo](https://github.com/alexliluz/api-image-neo)

`Active` · `Codex Skill` · `Image Generation` · `Python`

> Image generation for Codex through OpenAI-compatible providers.

The skill supports generation, reference-image workflows, and editing while keeping provider credentials in the user's existing Codex configuration.

## Now

Currently exploring reproducible agent workflows, reusable Codex skills, and practical tools that make AI-assisted development easier to inspect and maintain.

最近在探索可复现的 Agent 工作流、可复用 Codex Skills，以及更透明、更容易维护的 AI Coding 工具。

## Building Principles

- Build tools that remove repeated friction.
- AI workflows should leave inspectable artifacts.
- Useful first, impressive second.

## Working With

`TypeScript` · `Python` · `Vue` · `Node.js` · `GitHub Actions`

## Connect

[GitHub](https://github.com/alexliluz)

---

<sub>Building small tools for better human–agent collaboration.</sub>
```

- [ ] **Step 3: Run the tests to verify GREEN**

Run:

```bash
python3 -m unittest -v tests/verify_profile.py
```

Expected: all tests pass with no failures or errors.

- [ ] **Step 4: Inspect the rendered SVG**

Render the SVG to `.tmp/builder-console.svg.png` with the available macOS preview tooling and inspect the PNG for clipped text, illegible contrast, and excess empty space.

- [ ] **Step 5: Commit the profile implementation**

```bash
git add .gitignore README.md assets/builder-console.svg
git commit -m "feat: add Builder's Console profile"
```

### Task 3: Verify publish readiness

**Files:**
- Modify only if verification identifies a concrete defect: `README.md`, `assets/builder-console.svg`, `tests/verify_profile.py`.

**Interfaces:**
- Consumes: the completed profile and test suite.
- Produces: fresh evidence that the repository is safe to publish as `alexliluz/alexliluz`.

- [ ] **Step 1: Run the full local contract**

```bash
python3 -m unittest -v tests/verify_profile.py
```

Expected: all tests pass.

- [ ] **Step 2: Check Markdown and patch hygiene**

```bash
git diff --check HEAD~1..HEAD
rg -n "github-readme-stats|streak|visitor|trophy|snake|spotify" README.md assets
```

Expected: `git diff --check` exits zero; the search reports no forbidden production content.

- [ ] **Step 3: Verify public project links**

```bash
for url in \
  https://github.com/alexliluz/planarian \
  https://github.com/alexliluz/ForkNeo \
  https://github.com/alexliluz/api-image-neo; do
  curl -L --fail --silent --show-error --output /dev/null "$url"
done
```

Expected: all three requests exit zero.

- [ ] **Step 4: Audit the final repository state**

```bash
git status --short --branch
git log --oneline --decorate -5
find . -path ./.git -prune -o -path ./.tmp -prune -o -type f -print | sort
```

Expected: a clean `main` branch containing the design, plan, tests, README, and SVG; `.tmp` remains untracked or ignored and is not included in a commit.

- [ ] **Step 5: Commit any verification-only correction**

Only if Step 1–4 exposed a defect, commit the smallest correction:

```bash
git add README.md assets/builder-console.svg tests/verify_profile.py
git commit -m "fix: correct profile verification issue"
```
