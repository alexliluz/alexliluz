# Professional Engineering Stack Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the generic technology badges with a self-hosted, theme-aware Engineering Stack SVG that presents Alex's publicly verified toolchain as one animated engineering route.

**Architecture:** Add a deterministic Python generator that owns the stack data, SVG layout, theme palette, and animated/static rendering from one source. Commit its four generated assets under `assets/`, select them through a local README `<picture>`, and extend the existing profile contracts and SVG-security checks without changing the Contribution Signal workflow.

**Tech Stack:** Python 3 standard library, SVG/CSS/SMIL, GitHub-flavored Markdown, `xml.etree.ElementTree`, `unittest`, existing SVG validator, Git, GitHub pull requests

## Global Constraints

- SVG viewBox must be exactly `0 0 960 300`.
- Show exactly three groups: `BUILD`, `AUTOMATE`, and `VERIFY`.
- Show exactly seven technologies: TypeScript, Node.js, pnpm, GitHub Actions, Vitest, Playwright, and Git.
- Do not add Python or any other technology to the Engineering Stack panel.
- Use an animated route loop between 5.8 and 6.2 seconds; select exactly `6s` in the implementation.
- Animated panels may move only the route signal, node illumination, and heading scan accent.
- The heading scan travels left-to-right once per 6-second cycle, hides, and resets instantaneously; it never scans back from right to left.
- Narrow viewports use a dedicated connected route and signal through the centers of the two-row mobile nodes; desktop keeps the straight route.
- At 380 px and below, required secondary and technology text grows to 27 SVG units and heading baselines separate so 320/360/375 px renderings remain at least 9 px without clipping or overlap.
- TypeScript and Node.js are explicit primary nodes with slightly stronger stroke, label, and mark weight.
- Validate the exact required groups and technology labels before rendering or writing any asset.
- Static variants must contain no SMIL animation elements and no CSS animation or transition declarations.
- Generate light, dark, animated, and static assets from one deterministic repository script.
- Keep all SVG resources self-contained and below the existing 2 MiB asset limit.
- Do not add remote fonts, scripts, stylesheets, runtime images, Skill Icons, GitHub Stats, streak, trophy, WakaTime, or visitor-count dependencies.
- Preserve Featured Work, all three live Star badges, Star trend, 3D city, original contribution grid, and Platane snake.
- Do not modify `.github/workflows/generate-profile-assets.yml` or the `output` branch.
- Use test-first development and commit each independently reviewable task.

## File Map

- Create `scripts/build_engineering_stack.py`: own the approved stack model and deterministically render four safe SVG assets.
- Create `tests/test_engineering_stack_asset.py`: test exact scope, layout, accessibility, motion/static contracts, determinism, CLI output, and SVG safety.
- Create `assets/engineering-stack-dark.svg`: generated animated dark asset.
- Create `assets/engineering-stack-light.svg`: generated animated light asset.
- Create `assets/engineering-stack-dark-static.svg`: generated reduced-motion dark asset.
- Create `assets/engineering-stack-light-static.svg`: generated reduced-motion light asset.
- Modify `README.md`: replace the old Shields technology row with the four-source local Engineering Stack `<picture>`.
- Modify `tests/verify_profile.py`: add the new assets to the profile contract, update section ordering, isolate both `<picture>` contracts, and reject generic technology badges.
- Do not modify `scripts/compose_contribution_signal.py`, `scripts/profile_star_history.py`, or `.github/workflows/generate-profile-assets.yml`.

---

### Task 1: Deterministic Engineering Stack generator and assets

**Files:**
- Create: `scripts/build_engineering_stack.py`
- Create: `tests/test_engineering_stack_asset.py`
- Create: `assets/engineering-stack-dark.svg`
- Create: `assets/engineering-stack-light.svg`
- Create: `assets/engineering-stack-dark-static.svg`
- Create: `assets/engineering-stack-light-static.svg`

**Interfaces:**
- Consumes: `theme` equal to `"dark"` or `"light"`, and `animated: bool`.
- Produces: `build_svg(theme: str, animated: bool) -> str` and `write_assets(output_dir: pathlib.Path) -> tuple[pathlib.Path, ...]`.
- CLI: `python3 -m scripts.build_engineering_stack --output-dir assets` writes the four stable filenames.
- Guarantees: identical inputs produce byte-identical UTF-8 SVG; every output is accepted by `scripts.validate_profile_assets.validate_svg_source`.

- [ ] **Step 1: Write failing generator, scope, and safety tests**

Create `tests/test_engineering_stack_asset.py`:

```python
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
```

- [ ] **Step 2: Run the focused test and confirm the missing-module failure**

```bash
python3 -m unittest -v tests/test_engineering_stack_asset.py
```

Expected: FAIL with `ImportError: cannot import name 'build_engineering_stack' from 'scripts'`.

- [ ] **Step 3: Implement the stack model and deterministic renderer**

Create `scripts/build_engineering_stack.py` with these concrete public data types and coordinates:

```python
#!/usr/bin/env python3
import argparse
from dataclasses import dataclass
from pathlib import Path
from xml.sax.saxutils import escape


@dataclass(frozen=True)
class StackNode:
    label: str
    mark: str
    x: int
    accent: str
    delay: float
    primary: bool


@dataclass(frozen=True)
class StackGroup:
    name: str
    x: int
    width: int
    nodes: tuple[StackNode, ...]


STACK_GROUPS = (
    StackGroup("BUILD", 30, 238, (
        StackNode("TypeScript", "TS", 92, "#3178C6", 0.0, True),
        StackNode("Node.js", "JS", 210, "#3C873A", 0.85, True),
    )),
    StackGroup("AUTOMATE", 282, 266, (
        StackNode("pnpm", "pn", 350, "#F69220", 1.70, False),
        StackNode("GitHub Actions", "GH", 480, "#2088FF", 2.55, False),
    )),
    StackGroup("VERIFY", 562, 368, (
        StackNode("Vitest", "Vi", 624, "#729B1B", 3.40, False),
        StackNode("Playwright", "Pw", 752, "#2EAD33", 4.25, False),
        StackNode("Git", "G", 872, "#F05032", 5.10, False),
    )),
)

REQUIRED_STACK = (
    ("BUILD", ("TypeScript", "Node.js")),
    ("AUTOMATE", ("pnpm", "GitHub Actions")),
    ("VERIFY", ("Vitest", "Playwright", "Git")),
)

PALETTES = {
    "dark": {
        "surface": "#0D1117", "panel": "#10151D", "border": "#30363D",
        "text": "#F0F6FC", "muted": "#8B949E", "route": "#4B5563",
        "violet": "#A371F7", "coral": "#FF7B72", "cyan": "#39D0D8",
    },
    "light": {
        "surface": "#F6F8FA", "panel": "#FFFFFF", "border": "#D0D7DE",
        "text": "#24292F", "muted": "#57606A", "route": "#8C959F",
        "violet": "#8250DF", "coral": "#CF222E", "cyan": "#0969DA",
    },
}

OUTPUTS = (
    ("engineering-stack-dark.svg", "dark", True),
    ("engineering-stack-light.svg", "light", True),
    ("engineering-stack-dark-static.svg", "dark", False),
    ("engineering-stack-light-static.svg", "light", False),
)
```

Implement `render_node`, `build_svg`, and `write_assets` with these exact structural contracts:

```python
def render_node(node: StackNode, palette: dict[str, str], animated: bool) -> str:
    classes = ["stack-node"]
    if node.primary:
        classes.append("primary-node")
    if animated:
        classes.append("animated-node")
    class_name = " ".join(classes)
    style = f' style="--delay:{node.delay:.2f}s"' if animated else ""
    return f'''<g class="{class_name}" transform="translate({node.x - 52} 154)"{style}>
      <rect width="104" height="70" rx="14" fill="{palette['panel']}" stroke="{palette['border']}"/>
      <circle cx="20" cy="22" r="10" fill="{node.accent}" fill-opacity=".18"/>
      <text x="20" y="26" text-anchor="middle" fill="{node.accent}" font-size="10" font-weight="700">{escape(node.mark)}</text>
      <text x="52" y="52" text-anchor="middle" class="node-label">{escape(node.label)}</text>
    </g>'''


def build_svg(theme: str, animated: bool) -> str:
    validate_stack_model(STACK_GROUPS)
    if theme not in PALETTES:
        raise ValueError(f"unsupported theme: {theme}")
    palette = PALETTES[theme]
    mobile_route = mobile_route_path(STACK_GROUPS)
    groups = "".join(
        f'''<g class="stack-group">
          <rect x="{group.x}" y="118" width="{group.width}" height="130" rx="18" fill="{palette['panel']}" stroke="{palette['border']}"/>
          <text x="{group.x + 18}" y="142" class="group-label">{group.name}</text>
          {''.join(render_node(node, palette, animated) for node in group.nodes)}
        </g>'''
        for group in STACK_GROUPS
    )
    motion_css = "" if not animated else '''
      @keyframes node-signal { 0%,72%,100% { filter:none; } 8%,18% { filter:url(#node-glow); } }
      .animated-node { animation:node-signal 6s ease-in-out infinite; animation-delay:var(--delay); }
    '''
    motion = "" if not animated else f'''
      <circle class="route-signal desktop-only" r="5" fill="{palette['cyan']}" filter="url(#signal-glow)">
        <animateMotion dur="6s" repeatCount="indefinite"><mpath href="#engineering-route-desktop"/></animateMotion>
      </circle>
      <circle class="route-signal mobile-only" r="5" fill="{palette['cyan']}" filter="url(#signal-glow)">
        <animateMotion dur="6s" repeatCount="indefinite"><mpath href="#engineering-route-mobile"/></animateMotion>
      </circle>
      <rect x="30" y="91" width="120" height="2" rx="1" fill="{palette['coral']}" opacity=".85">
        <animate attributeName="x" values="30;810;810;30" keyTimes="0;.72;.999;1" dur="6s" repeatCount="indefinite"/>
        <animate attributeName="opacity" values=".85;.85;0;0" keyTimes="0;.72;.721;1" dur="6s" repeatCount="indefinite"/>
      </rect>'''
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 300" role="img" aria-labelledby="engineering-stack-title engineering-stack-description">
  <title id="engineering-stack-title">Alex engineering stack</title>
  <desc id="engineering-stack-description">A connected public toolchain: TypeScript and Node.js for building, pnpm and GitHub Actions for automation, and Vitest, Playwright, and Git for verification.</desc>
  <defs>
    <filter id="signal-glow" x="-200%" y="-200%" width="500%" height="500%"><feGaussianBlur stdDeviation="3" result="blur"/><feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
    <filter id="node-glow" x="-20%" y="-20%" width="140%" height="140%"><feDropShadow dx="0" dy="0" stdDeviation="3" flood-color="{palette['violet']}" flood-opacity=".55"/></filter>
    <style>
      text {{ font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace; }}
      .title {{ fill:{palette['text']}; font-size:24px; font-weight:700; letter-spacing:4px; }}
      .subtitle,.group-label {{ fill:{palette['muted']}; font-size:12px; font-weight:600; letter-spacing:2px; }}
      .node-label {{ fill:{palette['text']}; font-size:12px; font-weight:600; }}
      {motion_css}
    </style>
  </defs>
  <rect x="1" y="1" width="958" height="298" rx="22" fill="{palette['surface']}" stroke="{palette['border']}" stroke-width="2"/>
  <text x="30" y="48" class="title">ENGINEERING STACK</text>
  <text x="30" y="75" class="subtitle">PUBLIC TOOLCHAIN · VERIFIED BY WORK</text>
  <path id="engineering-route-desktop" class="engineering-route desktop-only" d="M92 188 H872" fill="none" stroke="{palette['route']}" stroke-width="2"/>
  <path id="engineering-route-mobile" class="engineering-route mobile-only" d="{mobile_route}" fill="none" stroke="{palette['route']}" stroke-width="2"/>
  {groups}
  {motion}
</svg>\n'''


def write_assets(output_dir: Path) -> tuple[Path, ...]:
    validate_stack_model(STACK_GROUPS)
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    for filename, theme, animated in OUTPUTS:
        path = output_dir / filename
        path.write_text(build_svg(theme, animated), encoding="utf-8")
        paths.append(path)
    return tuple(paths)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build Engineering Stack SVG assets")
    parser.add_argument("--output-dir", required=True, type=Path)
    arguments = parser.parse_args()
    write_assets(arguments.output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Generate the four committed assets**

```bash
python3 -m scripts.build_engineering_stack --output-dir assets
```

Expected: the command exits 0 and writes exactly the four `engineering-stack-*.svg` files named in the file map.

- [ ] **Step 5: Run focused generator and security tests**

```bash
python3 -m unittest -v \
  tests/test_engineering_stack_asset.py \
  tests/test_validate_profile_assets.py
python3 scripts/validate_profile_assets.py assets/engineering-stack-*.svg
```

Expected: all focused tests PASS and the validator exits 0 without output.

- [ ] **Step 6: Commit the generator, tests, and generated assets**

```bash
git add scripts/build_engineering_stack.py tests/test_engineering_stack_asset.py assets/engineering-stack-*.svg
git commit -m "feat: add professional engineering stack assets"
```

---

### Task 2: README integration and profile contracts

**Files:**
- Modify: `README.md`
- Modify: `tests/verify_profile.py`

**Interfaces:**
- Consumes: the four stable local filenames produced by `write_assets` in Task 1.
- Produces: a theme- and reduced-motion-aware Engineering Stack `<picture>` before Featured Work.
- Preserves: the existing Contribution Signal `<picture>` source order, URLs, alternative text, and all Featured Work Star badge URLs.

- [ ] **Step 1: Replace the old badge expectations with failing Engineering Stack contracts**

In `tests/verify_profile.py`, add:

```python
ENGINEERING_ASSETS = (
    ROOT / "assets" / "engineering-stack-dark.svg",
    ROOT / "assets" / "engineering-stack-light.svg",
    ROOT / "assets" / "engineering-stack-dark-static.svg",
    ROOT / "assets" / "engineering-stack-light-static.svg",
)
ENGINEERING_SOURCES = (
    (
        "(prefers-reduced-motion: reduce) and (prefers-color-scheme: dark)",
        "./assets/engineering-stack-dark-static.svg",
    ),
    (
        "(prefers-reduced-motion: reduce) and (prefers-color-scheme: light)",
        "./assets/engineering-stack-light-static.svg",
    ),
    ("(prefers-color-scheme: dark)", "./assets/engineering-stack-dark.svg"),
    ("(prefers-color-scheme: light)", "./assets/engineering-stack-light.svg"),
)
```

Add every `ENGINEERING_ASSETS` path to `test_required_files_exist`. Change the ordered heading fragment from `## Tech stack` to `## Engineering Stack`. Replace `test_four_technology_badges_and_three_star_badges_are_present` with:

```python
def test_engineering_stack_replaces_generic_technology_badges(self) -> None:
    text = self.read_readme()
    self.assertNotIn("## Tech stack", text)
    self.assertNotRegex(text, r"https://img\.shields\.io/badge/")
    self.assertEqual(
        len(re.findall(r"https://img\.shields\.io/github/stars/", text)),
        3,
    )

def test_engineering_stack_picture_selects_four_local_variants(self) -> None:
    text = self.read_readme()
    section = text[text.index("## Engineering Stack"):text.index("## Featured work")]
    sources = re.findall(
        r'<source media="([^"]+)" srcset="([^"]+)">',
        section,
    )
    self.assertEqual(sources, list(ENGINEERING_SOURCES))
    fallback = re.findall(
        r'<img src="([^"]+)" alt="([^"]+)" width="100%">',
        section,
    )
    self.assertEqual(
        fallback,
        [(
            "./assets/engineering-stack-light.svg",
            "Alex engineering stack: TypeScript, Node.js, pnpm, GitHub Actions, Vitest, Playwright, and Git",
        )],
    )
```

Change the Contribution Signal picture test to slice only its section before applying its existing source and fallback assertions:

```python
section = text[text.index("## Contribution Signal"):text.index("\n---", text.index("## Contribution Signal"))]
self.assertEqual(section.count("<picture>"), 1)
self.assertEqual(section.count("</picture>"), 1)
picture_match = re.search(r"<picture>\n(.*?)\n</picture>", section, re.DOTALL)
```

Add this overall count assertion to the Engineering Stack picture test:

```python
self.assertEqual(text.count("<picture>"), 2)
self.assertEqual(text.count("</picture>"), 2)
```

- [ ] **Step 2: Run the profile contract and confirm it fails on the old badge section**

```bash
python3 -m unittest -v tests.verify_profile.ProfileContractTests.test_engineering_stack_replaces_generic_technology_badges tests.verify_profile.ProfileContractTests.test_engineering_stack_picture_selects_four_local_variants
```

Expected: FAIL because README still contains `## Tech stack` and has no Engineering Stack picture.

- [ ] **Step 3: Replace the README technology section**

Replace the complete block from `## Tech stack` through its closing `</p>` with:

```markdown
## Engineering Stack

<picture>
  <source media="(prefers-reduced-motion: reduce) and (prefers-color-scheme: dark)" srcset="./assets/engineering-stack-dark-static.svg">
  <source media="(prefers-reduced-motion: reduce) and (prefers-color-scheme: light)" srcset="./assets/engineering-stack-light-static.svg">
  <source media="(prefers-color-scheme: dark)" srcset="./assets/engineering-stack-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="./assets/engineering-stack-light.svg">
  <img src="./assets/engineering-stack-light.svg" alt="Alex engineering stack: TypeScript, Node.js, pnpm, GitHub Actions, Vitest, Playwright, and Git" width="100%">
</picture>
```

Do not change the bilingual positioning statement, Featured Work line, Contribution Signal picture, separator, or repository link.

- [ ] **Step 4: Run README and existing Contribution Signal contracts**

```bash
python3 -m unittest -v tests.verify_profile.ProfileContractTests
```

Expected: all profile contract tests PASS, including the unchanged workflow-hardening and Contribution Signal assertions.

- [ ] **Step 5: Commit README integration**

```bash
git add README.md tests/verify_profile.py
git commit -m "feat: integrate engineering stack into profile"
```

---

### Task 3: Full regression and visual verification

**Files:**
- Verify: `assets/engineering-stack-dark.svg`
- Verify: `assets/engineering-stack-light.svg`
- Verify: `assets/engineering-stack-dark-static.svg`
- Verify: `assets/engineering-stack-light-static.svg`
- Verify: `README.md`
- Do not commit `.tmp/` preview artifacts or screenshots.

**Interfaces:**
- Consumes: the generated assets and README contract from Tasks 1 and 2.
- Produces: objective test evidence and visual approval evidence for the feature branch.

- [ ] **Step 1: Confirm the generator is reproducible without changing tracked files**

```bash
python3 -m scripts.build_engineering_stack --output-dir assets
git diff --exit-code -- assets/engineering-stack-*.svg
```

Expected: both commands exit 0; the second command prints no diff.

- [ ] **Step 2: Run every local test and asset validator**

```bash
python3 -m unittest discover -s tests -v
python3 scripts/validate_profile_assets.py assets/*.svg
git diff --check
```

Expected: the suite reports at least 87 tests with `OK`; the validator and whitespace check exit 0 without output.

- [ ] **Step 3: Render all four variants locally**

Start a local server from the repository root:

```bash
python3 -m http.server 61975
```

Open these exact URLs in a browser capable of displaying SVG animation:

```text
http://localhost:61975/assets/engineering-stack-dark.svg
http://localhost:61975/assets/engineering-stack-light.svg
http://localhost:61975/assets/engineering-stack-dark-static.svg
http://localhost:61975/assets/engineering-stack-light-static.svg
```

Verify all seven technology labels are unclipped at 960 px and 420 px viewport widths. For animated variants, observe one complete 6-second loop and confirm the route dot moves, nodes illuminate in left-to-right order, and the heading scan remains restrained. Observe each static variant for at least 6 seconds and confirm no element moves or disappears.

- [ ] **Step 4: Confirm the protected profile elements are byte-unchanged**

```bash
git diff origin/main -- .github/workflows/generate-profile-assets.yml scripts/compose_contribution_signal.py scripts/profile_star_history.py
git diff origin/main -- README.md
```

Expected: the first command prints no diff. The README diff contains only replacement of the old Tech stack badge block with the Engineering Stack picture; Featured Work and Contribution Signal lines are unchanged.

- [ ] **Step 5: Confirm the branch is clean and review its commit series**

```bash
git status --short --branch
git log --oneline --decorate origin/main..HEAD
```

Expected: status has no modified or untracked files. The log contains the approved design and implementation-plan commits followed by one asset-generator commit and one README-integration commit.

---

### Task 4: Publish for GitHub review

**Files:**
- Publish branch: `codex/profile-professional-stack`
- Create pull request against: `main`

**Interfaces:**
- Consumes: a clean feature branch with all Task 3 checks passing.
- Produces: a reviewable GitHub pull request; does not merge it.

- [ ] **Step 1: Push the exact tested branch**

```bash
git push -u origin codex/profile-professional-stack
```

Expected: push succeeds and GitHub reports the remote branch is up to date.

- [ ] **Step 2: Open the pull request**

```bash
gh pr create \
  --base main \
  --head codex/profile-professional-stack \
  --title "Add professional engineering stack to profile" \
  --body $'## Summary\n- replace generic technology badges with a custom engineering workflow panel\n- add light, dark, animated, and reduced-motion SVG variants\n- preserve Featured Work, Star trend, 3D city, and original contribution snake\n\n## Verification\n- python3 -m unittest discover -s tests -v\n- python3 scripts/validate_profile_assets.py assets/*.svg\n- visual inspection at desktop and mobile widths'
```

Expected: GitHub returns one pull-request URL targeting `main`.

- [ ] **Step 3: Verify GitHub rendering and stop before merge**

Open the pull request's changed `README.md` preview and each rendered asset. Confirm GitHub displays the correct theme asset, animated variants visibly move, static variants remain complete, all three Featured Work Star badges load, and Contribution Signal still contains the Star trend, 3D city, and original moving snake.

Report the pull-request URL and verification results to the user. Do not merge until the user explicitly approves final publication.
