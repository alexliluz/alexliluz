# GitHub Profile V2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build, verify, preview, and—only after final approval—publish the approved Product OS × Agent Console profile for `alexliluz`.

**Architecture:** Keep the profile static and dependency-free. `README.md` owns all selectable project and status content, `assets/profile-hero.svg` owns the theme-aware visual identity, and `tests/verify_profile.py` enforces attribution, content, local-asset, accessibility, theme, and link contracts. Visual preview artifacts are generated under ignored `.tmp/` and never committed.

**Tech Stack:** GitHub Flavored Markdown, SVG, Python 3 standard library, macOS Quick Look and `sips`, Git, GitHub CLI for the final approved publication step.

## Global Constraints

- English is the primary language; Chinese is concise supporting context.
- Selected work is exactly `planarian`, `ForkNeo`, and `api-image-neo`.
- Do not present `linuxdo-scripts-neo` as selected personal work.
- The visual mix is 60% product presentation, 25% GitHub-native typography, and 15% console personality.
- The console motif is an accent; do not reproduce a generic terminal window or traffic-light controls.
- Do not use stats cards, streaks, trophies, visitor counters, typing animations, contribution snakes, remote images, analytics, or external widget APIs.
- The layout is a GitHub-native, mobile-safe single column without HTML tables.
- The hero is repository-owned, `960 × 280`, accessible, responsive, motionless, and readable in dark and light themes.
- The V2 account name is `Alex · ASEnough` and the bio is `Building practical tools for AI-assisted software work.`
- The intended pin order is `planarian`, `ForkNeo`, `api-image-neo`.
- Do not push commits or mutate GitHub account metadata before the user sees the final preview and gives explicit publication approval.

## File Map

- Modify `tests/verify_profile.py`: executable V2 content, attribution, dependency, SVG, theme, and public-link contract.
- Modify `README.md`: complete GitHub-native V2 profile content.
- Create `assets/profile-hero.svg`: approved Product OS × Agent Console hero.
- Delete `assets/builder-console.svg`: remove the superseded V1 terminal asset.
- Create `.tmp/render_profile_themes.py` during verification: ignored helper that makes deterministic dark and light preview variants; never commit it.

---

### Task 1: Replace the V1 Contract with the V2 Contract

**Files:**
- Modify: `tests/verify_profile.py:1-88`
- Test: `tests/verify_profile.py`

**Interfaces:**
- Consumes: `README.md`, `assets/profile-hero.svg`, and the four public GitHub URLs in `PROFILE_URLS`.
- Produces: `ProfileContractTests`, run with `python3 -m unittest -v tests/verify_profile.py`.

- [ ] **Step 1: Replace the test module with the V2 contract**

Set `tests/verify_profile.py` to:

```python
import re
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
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
                with urlopen(request, timeout=15) as response:
                    self.assertLess(response.status, 400)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the V2 tests and confirm RED against V1**

Run:

```bash
python3 -m unittest -v tests/verify_profile.py
```

Expected: the URL test and project-attribution test may pass, while the suite fails on the missing `assets/profile-hero.svg`, missing `What I'm Building`, obsolete V1 sections, and old hero reference. This proves that the new contract rejects the current V1 profile for specific V2 requirements.

- [ ] **Step 3: Commit the red V2 contract**

```bash
git add tests/verify_profile.py
git commit -m "test: define GitHub profile V2 contract"
```

Expected: one commit containing only `tests/verify_profile.py`; the test suite remains intentionally red until Task 2.

### Task 2: Implement the Product OS × Agent Console Profile

**Files:**
- Create: `assets/profile-hero.svg`
- Modify: `README.md:1-59`
- Delete: `assets/builder-console.svg`
- Test: `tests/verify_profile.py`

**Interfaces:**
- Consumes: the exact assertions in `ProfileContractTests`.
- Produces: a GitHub-renderable single-column README and the local `assets/profile-hero.svg` it references.

- [ ] **Step 1: Create the accessible, theme-aware V2 hero**

Create `assets/profile-hero.svg` with this exact content:

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 280" role="img" aria-labelledby="title description">
  <title id="title">Alex / ASEnough — Product OS</title>
  <desc id="description">Alex builds practical, inspectable tools for AI-assisted software work, focused on AI coding, agent workflows, and developer tools.</desc>
  <style>
    .surface { fill: #0D1117; stroke: #30363D; }
    .accent-line { fill: #58A6FF; }
    .status-surface { fill: #161B22; stroke: #30363D; }
    .divider { stroke: #30363D; }
    .primary { fill: #F0F6FC; }
    .muted { fill: #8B949E; }
    .blue { fill: #58A6FF; }
    .green { fill: #3FB950; }
    .identity,
    .label,
    .prompt,
    .status-text {
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;
    }
    .identity { font-size: 15px; font-weight: 700; letter-spacing: 2px; }
    .headline { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; font-size: 32px; font-weight: 700; }
    .label { font-size: 13px; font-weight: 600; letter-spacing: 1.1px; }
    .prompt { font-size: 15px; }
    .status-text { font-size: 12px; font-weight: 700; letter-spacing: 0.8px; }
    @media (prefers-color-scheme: light) {
      .surface { fill: #FFFFFF; stroke: #D0D7DE; }
      .status-surface { fill: #F6F8FA; stroke: #D0D7DE; }
      .divider { stroke: #D0D7DE; }
      .primary { fill: #1F2328; }
      .muted { fill: #59636E; }
      .blue { fill: #0969DA; }
      .green { fill: #1A7F37; }
    }
  </style>
  <rect class="surface" x="1" y="1" width="958" height="278" rx="18"/>
  <rect class="accent-line" x="28" y="28" width="4" height="28" rx="2"/>
  <text class="identity primary" x="48" y="49">ALEX / ASENOUGH</text>

  <rect class="status-surface" x="782" y="27" width="150" height="32" rx="16"/>
  <rect class="green" x="798" y="40" width="7" height="7" rx="3.5"/>
  <text class="status-text green" x="815" y="48">BUILD: ACTIVE</text>

  <text class="headline primary" x="28" y="108">Building practical, inspectable tools for</text>
  <text class="headline primary" x="28" y="148">AI-assisted software work.</text>

  <text class="label blue" x="28" y="194">AI CODING</text>
  <text class="label muted" x="129" y="194">·</text>
  <text class="label blue" x="150" y="194">AGENT WORKFLOWS</text>
  <text class="label muted" x="302" y="194">·</text>
  <text class="label blue" x="323" y="194">DEVELOPER TOOLS</text>

  <line class="divider" x1="28" y1="217" x2="932" y2="217"/>
  <text class="prompt green" x="28" y="250">alex@github:~$</text>
  <text class="prompt muted" x="176" y="250">turning demos into repeatable systems_</text>
</svg>
```

- [ ] **Step 2: Replace the V1 README with the approved V2 copy**

Set `README.md` to:

```markdown
<img src="./assets/profile-hero.svg" alt="Alex / ASEnough builds practical, inspectable tools for AI-assisted software work" width="100%">

# Hi, I'm Alex / ASEnough.

我在做更实用、可检查、可复现的 AI Coding 与 Agent 工作流工具。

## What I'm Building

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

## Now

Turning agent demos into repeatable engineering workflows.

把 Agent Demo 变成可复现、可验证、可长期维护的工程工作流。

## Building Principles

`Inspectable artifacts` · `Reproducible workflows` · `Useful before impressive`

---

[Explore all repositories →](https://github.com/alexliluz?tab=repositories)
```

- [ ] **Step 3: Remove the superseded V1 hero**

Delete `assets/builder-console.svg`. Confirm that `assets/` now contains only the V2 production hero:

```bash
find assets -maxdepth 1 -type f -print | sort
```

Expected:

```text
assets/profile-hero.svg
```

- [ ] **Step 4: Run the V2 contract and confirm GREEN**

Run:

```bash
python3 -m unittest -v tests/verify_profile.py
```

Expected: eight tests pass, including the public URL checks; there are no failures or errors.

- [ ] **Step 5: Check the implementation diff**

Run:

```bash
git diff --check
git diff -- README.md assets/profile-hero.svg assets/builder-console.svg tests/verify_profile.py
```

Expected: `git diff --check` exits zero. The diff shows the V2 README and hero, deletion of the V1 hero, and no unrelated changes.

- [ ] **Step 6: Commit the V2 implementation**

```bash
git add README.md assets/profile-hero.svg assets/builder-console.svg
git commit -m "feat: upgrade GitHub profile to Product OS"
```

Expected: a focused implementation commit; `tests/verify_profile.py` is already committed by Task 1.

### Task 3: Produce Deterministic Dark, Light, and Narrow Visual Previews

**Files:**
- Create, ignored: `.tmp/render_profile_themes.py`
- Generate, ignored: `.tmp/profile-v2/profile-hero-dark.svg`
- Generate, ignored: `.tmp/profile-v2/profile-hero-light.svg`
- Generate, ignored: `.tmp/profile-v2/profile-hero-dark.svg.png`
- Generate, ignored: `.tmp/profile-v2/profile-hero-light.svg.png`
- Generate, ignored: `.tmp/profile-v2/profile-hero-dark-narrow.png`
- Generate, ignored: `.tmp/profile-v2/profile-hero-light-narrow.png`

**Interfaces:**
- Consumes: the exact `@media (prefers-color-scheme: light)` rule in `assets/profile-hero.svg`.
- Produces: forced-theme SVG variants and PNG previews without modifying production files.

- [ ] **Step 1: Create the ignored theme-variant helper**

Create `.tmp/render_profile_themes.py`:

```python
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "assets" / "profile-hero.svg"
OUTPUT = ROOT / ".tmp" / "profile-v2"
MEDIA_QUERY = "@media (prefers-color-scheme: light)"


def main() -> None:
    source = SOURCE.read_text(encoding="utf-8")
    if source.count(MEDIA_QUERY) != 1:
        raise SystemExit("profile hero must contain exactly one light-theme media query")

    OUTPUT.mkdir(parents=True, exist_ok=True)
    variants = {
        "dark": source.replace(MEDIA_QUERY, "@media not all"),
        "light": source.replace(MEDIA_QUERY, "@media all"),
    }
    for theme, content in variants.items():
        target = OUTPUT / f"profile-hero-{theme}.svg"
        target.write_text(content, encoding="utf-8")
        ET.parse(target)
        print(target)


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Generate and validate both SVG theme variants**

Run:

```bash
python3 .tmp/render_profile_themes.py
```

Expected:

```text
.tmp/profile-v2/profile-hero-dark.svg
.tmp/profile-v2/profile-hero-light.svg
```

The printed paths may be absolute. The command exits zero only after both files parse as XML.

- [ ] **Step 3: Render desktop previews with macOS Quick Look**

Run:

```bash
qlmanage -t -s 1440 -o .tmp/profile-v2 .tmp/profile-v2/profile-hero-dark.svg
qlmanage -t -s 1440 -o .tmp/profile-v2 .tmp/profile-v2/profile-hero-light.svg
```

Expected: Quick Look produces `profile-hero-dark.svg.png` and `profile-hero-light.svg.png` under `.tmp/profile-v2/`.

- [ ] **Step 4: Produce narrow previews from both rendered themes**

Run:

```bash
sips -Z 480 .tmp/profile-v2/profile-hero-dark.svg.png --out .tmp/profile-v2/profile-hero-dark-narrow.png
sips -Z 480 .tmp/profile-v2/profile-hero-light.svg.png --out .tmp/profile-v2/profile-hero-light-narrow.png
```

Expected: both commands exit zero and create the two `*-narrow.png` files.

- [ ] **Step 5: Inspect all four previews**

Open the two desktop and two narrow PNG files with the image-inspection tool. Approve the hero only if all of these statements are true:

- the identity, two-line headline, three focus labels, and status line are fully visible;
- `BUILD: ACTIVE` reads as a compact status, not as a window control;
- the layout has no traffic-light circles or simulated title bar;
- dark and light versions both have legible foreground/background contrast;
- the headline remains the strongest element and the console line remains secondary;
- the 480-pixel previews have no clipped or overlapping text;
- the frame, accent line, capsule, and divider are aligned and visually restrained.

If any statement is false, stop before Task 4, report the exact failed statement, correct only the responsible SVG coordinates or class styles, rerun `python3 -m unittest -v tests/verify_profile.py`, repeat Steps 2–5, and commit the focused correction as `fix: refine profile hero rendering`.

- [ ] **Step 6: Confirm previews remain ignored**

Run:

```bash
git status --short --ignored .tmp
git status --short
```

Expected: `.tmp/` appears only as ignored output and the production worktree is clean. Do not add any `.tmp` file to Git.

### Task 4: Audit Publish Readiness and Present the Final Preview

**Files:**
- Inspect: `README.md`
- Inspect: `assets/profile-hero.svg`
- Inspect: `tests/verify_profile.py`
- Inspect: `.tmp/profile-v2/*.png`

**Interfaces:**
- Consumes: the committed V2 implementation and verified previews.
- Produces: fresh publish-readiness evidence and a user-facing final preview; it does not publish.

- [ ] **Step 1: Run the complete executable contract again**

```bash
python3 -m unittest -v tests/verify_profile.py
```

Expected: eight tests pass with no failures or errors.

- [ ] **Step 2: Run patch, policy, XML, and link checks**

```bash
git diff --check origin/main..HEAD
python3 -c 'import xml.etree.ElementTree as ET; ET.parse("assets/profile-hero.svg")'
rg -n "github-readme-stats|streak-stats|profile-views|trophy|snake|typing-svg|spotify|<table|https?://[^\" ]+\.(png|svg|gif)" README.md assets/profile-hero.svg
for url in \
  https://github.com/alexliluz/planarian \
  https://github.com/alexliluz/ForkNeo \
  https://github.com/alexliluz/api-image-neo \
  'https://github.com/alexliluz?tab=repositories'; do
  curl -L --fail --silent --show-error --output /dev/null "$url"
done
```

Expected: the diff and XML commands exit zero; the policy search has no matches; all four URL requests exit zero.

- [ ] **Step 3: Audit the repository boundary**

```bash
git status --short --branch
git log --oneline --decorate -6
find . -path ./.git -prune -o -path ./.tmp -prune -o -type f -print | sort
```

Expected: `main` is clean and ahead of `origin/main`; production files are limited to the README, V2 hero, tests, specs, plans, and existing Git metadata/configuration. No preview artifact is tracked.

- [ ] **Step 4: Present the final unpublised result**

Show the dark and light desktop hero PNGs, link to the local `README.md`, and summarize:

- the exact V2 positioning and section order;
- the three selected project descriptions;
- the successful eight-test result;
- the successful URL, XML, and theme-render checks;
- proposed account name, bio, and pin order;
- the fact that local commits are not yet pushed.

End by asking for one explicit decision: permission to publish the V2 commits and apply the approved account metadata. Do not run Task 5 without an affirmative response.

### Task 5: Publish the Approved V2 and Verify the Public Profile

**Gate:** Execute this task only after the user explicitly approves publication in response to Task 4.

**Files and external state:**
- Push: committed `main` branch to `origin/main`.
- Update: authenticated GitHub account name and bio.
- Pin: `planarian`, `ForkNeo`, `api-image-neo`, in that order, through a supported authenticated GitHub interface.

**Interfaces:**
- Consumes: the exact local commit verified in Task 4 and explicit publication approval.
- Produces: the public V2 profile at `https://github.com/alexliluz`.

- [ ] **Step 1: Reconfirm the exact commit boundary immediately before push**

```bash
git status --short --branch
git log --oneline --decorate origin/main..HEAD
```

Expected: the worktree is clean and the outgoing commits contain the V2 design, plan, contract, and implementation only.

- [ ] **Step 2: Push the approved commits**

```bash
git push origin main
```

Expected: the push succeeds and `main` matches `origin/main`.

- [ ] **Step 3: Apply the approved display name and bio**

Use the project-local, checksum-verified GitHub CLI already stored in the ignored `.tmp/` directory and confirm authentication before mutation:

```bash
GH=.tmp/gh-cli/gh_2.96.0_macOS_arm64/bin/gh
test -x "$GH"
"$GH" auth status
"$GH" api --method PATCH /user \
  -f 'name=Alex · ASEnough' \
  -f 'bio=Building practical tools for AI-assisted software work.'
```

Expected: the JSON response contains `"name":"Alex · ASEnough"` and `"bio":"Building practical tools for AI-assisted software work."`.

- [ ] **Step 4: Apply the approved pin order through a supported interface**

Use GitHub's authenticated profile customization interface to select only `planarian`, `ForkNeo`, and `api-image-neo`, arranging them in that order. If the available GitHub connector or browser cannot safely edit profile pins, stop this step without inventing an API mutation and provide these exact manual actions:

1. Open <https://github.com/alexliluz> while signed in.
2. Choose **Customize your pins**.
3. Select `planarian`, `ForkNeo`, and `api-image-neo`; deselect unrelated repositories.
4. Save, then drag the cards into the approved order if GitHub exposes ordering controls.

- [ ] **Step 5: Verify the public repository and account state**

```bash
GH=.tmp/gh-cli/gh_2.96.0_macOS_arm64/bin/gh
git fetch origin main
test "$(git rev-parse HEAD)" = "$(git rev-parse origin/main)"
"$GH" api /user --jq '{name: .name, bio: .bio, html_url: .html_url}'
curl -L --fail --silent --show-error https://raw.githubusercontent.com/alexliluz/alexliluz/main/README.md | rg "What I'm Building|Turning agent demos|Explore all repositories"
```

Expected: local and remote commit IDs match; GitHub reports the approved name and bio; the public raw README contains all three V2 markers.

- [ ] **Step 6: Inspect the public profile and report completion**

Open <https://github.com/alexliluz> and verify the rendered hero, section order, project links, account name, bio, and pin order. Report any manual pin action still required. Mark the overarching goal complete only when the public state and every explicit V2 acceptance criterion have been verified.
