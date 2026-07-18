# Minimal Profile Header Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the verbose upper profile with a compact factual developer introduction while preserving the neon 3D contribution city and animated snake.

**Architecture:** Keep the profile as a single Markdown document backed by its existing repository-owned generated SVG assets. Change only the README composition and its contract tests; retain the hero asset and asset-generation workflow unchanged so the redesign is reversible and operational risk stays low.

**Tech Stack:** GitHub-flavored Markdown, Shields.io static badges, Python `unittest`, GitHub Actions generated SVG assets

## Global Constraints

- Do not render `assets/profile-hero.svg` in `README.md`, but do not delete the asset.
- Feature exactly `Planarian`, `ForkNeo`, and `api-image-neo` with direct public GitHub links.
- Use static Shields.io badges only for TypeScript, Python, Node.js, GitHub Actions, and AI Agents.
- Do not add WakaTime, GitHub Readme Stats, visitor counters, typing animations, tables, or other third-party data widgets.
- Preserve both light and dark 3D contribution city assets.
- Preserve both light and dark animated contribution snake assets.
- Do not modify `.github/workflows/generate-profile-assets.yml` or generated asset URLs.

---

### Task 1: Replace the verbose upper profile with a compact developer card

**Files:**
- Modify: `tests/verify_profile.py`
- Modify: `README.md`

**Interfaces:**
- Consumes: Existing output-branch SVG URLs defined by `GENERATED_ASSET_BASE` and `GENERATED_ASSETS` in `tests/verify_profile.py`
- Produces: A GitHub-renderable `README.md` whose upper section is factual and compact, followed by the unchanged theme-aware contribution assets

- [ ] **Step 1: Replace the old layout assertions with the compact-profile contract**

In `tests/verify_profile.py`, replace `test_identity_and_v3_sections_are_present_in_order` with:

```python
def test_compact_identity_sections_are_present_in_order(self) -> None:
    text = self.read_readme()
    required = (
        "# Hi, I'm Alex / ASEnough 👋",
        "## About me",
        "## Tech stack",
        "## Featured work",
        "## Neon Contribution City",
        "## Contribution Snake",
        "[Explore all repositories →]",
    )
    positions = [text.index(fragment) for fragment in required]
    self.assertEqual(positions, sorted(positions))
    self.assertIn(
        "I build practical AI Coding tools and reproducible agent workflows.",
        text,
    )
    self.assertIn(
        "我专注于 AI Coding、Agent 工作流和实用开发工具。",
        text,
    )
    for fact in (
        "Building practical tools for AI-assisted software work.",
        "Planarian, ForkNeo, and api-image-neo.",
        "TypeScript, Python, Node.js, and GitHub Actions.",
        "Reproducible, inspectable workflows over opaque demos.",
    ):
        self.assertIn(fact, text)
```

Replace `test_selected_work_contains_exactly_the_three_owned_projects` with:

```python
def test_featured_work_is_one_compact_line_with_three_owned_projects(self) -> None:
    text = self.read_readme()
    repo_names = re.findall(
        r"https://github\.com/alexliluz/([A-Za-z0-9_.-]+)", text
    )
    self.assertEqual(repo_names, ["planarian", "ForkNeo", "api-image-neo"])
    self.assertIn(
        "[Planarian](https://github.com/alexliluz/planarian) · "
        "[ForkNeo](https://github.com/alexliluz/ForkNeo) · "
        "[api-image-neo](https://github.com/alexliluz/api-image-neo)",
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
```

Replace `test_local_hero_reference_resolves` with:

```python
def test_local_hero_is_retained_but_not_rendered(self) -> None:
    text = self.read_readme()
    self.assertTrue(HERO.is_file())
    self.assertNotIn("./assets/profile-hero.svg", text)
```

Add this badge contract after the compact identity test:

```python
def test_static_technology_badges_are_present(self) -> None:
    text = self.read_readme()
    expected_labels = (
        "TypeScript-3178C6",
        "Python-3776AB",
        "Node.js-339933",
        "GitHub_Actions-2088FF",
        "AI_Agents-8B5CF6",
    )
    self.assertEqual(text.count("https://img.shields.io/badge/"), 5)
    for label in expected_labels:
        self.assertIn(f"https://img.shields.io/badge/{label}", text)
```

In `test_v3_dynamic_assets_are_theme_aware_and_repository_owned`, replace the broad `remote_sources` extraction with a generated-assets-only check so the five approved static badges do not get counted as dynamic contribution assets:

```python
generated_sources = re.findall(
    rf'(?:src|srcset)=["\']({re.escape(GENERATED_ASSET_BASE)}[^"\']+)["\']',
    text,
)
self.assertEqual(len(generated_sources), 6)
for source in generated_sources:
    self.assertTrue(source.startswith(GENERATED_ASSET_BASE), source)
```

Finally, remove `"shields.io",` from the `forbidden` tuple in `test_readme_avoids_unapproved_widgets_and_placeholders`. Leave every other forbidden fragment unchanged.

- [ ] **Step 2: Run the focused contract tests and confirm they fail for the old README**

Run:

```bash
python3 -m unittest -v \
  tests.verify_profile.ProfileContractTests.test_compact_identity_sections_are_present_in_order \
  tests.verify_profile.ProfileContractTests.test_featured_work_is_one_compact_line_with_three_owned_projects \
  tests.verify_profile.ProfileContractTests.test_static_technology_badges_are_present \
  tests.verify_profile.ProfileContractTests.test_local_hero_is_retained_but_not_rendered
```

Expected: four failures because the current README renders the hero, uses the verbose section hierarchy, and has no technology badges.

- [ ] **Step 3: Replace `README.md` with the approved compact composition**

Set the complete file content to:

```markdown
# Hi, I'm Alex / ASEnough 👋

I build practical AI Coding tools and reproducible agent workflows.  
我专注于 AI Coding、Agent 工作流和实用开发工具。

## About me

- 🔭 Building practical tools for AI-assisted software work.
- 🧪 Representative projects: Planarian, ForkNeo, and api-image-neo.
- 🛠 Working mainly with TypeScript, Python, Node.js, and GitHub Actions.
- ⚙️ Reproducible, inspectable workflows over opaque demos.

## Tech stack

<p>
  <img src="https://img.shields.io/badge/TypeScript-3178C6?style=flat-square&logo=typescript&logoColor=white" alt="TypeScript">
  <img src="https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Node.js-339933?style=flat-square&logo=nodedotjs&logoColor=white" alt="Node.js">
  <img src="https://img.shields.io/badge/GitHub_Actions-2088FF?style=flat-square&logo=githubactions&logoColor=white" alt="GitHub Actions">
  <img src="https://img.shields.io/badge/AI_Agents-8B5CF6?style=flat-square&logo=openai&logoColor=white" alt="AI Agents">
</p>

## Featured work

[Planarian](https://github.com/alexliluz/planarian) · [ForkNeo](https://github.com/alexliluz/ForkNeo) · [api-image-neo](https://github.com/alexliluz/api-image-neo)

## Neon Contribution City

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/alexliluz/alexliluz/output/profile-3d-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/alexliluz/alexliluz/output/profile-3d-light.svg">
  <img src="https://raw.githubusercontent.com/alexliluz/alexliluz/output/profile-3d-light.svg" alt="3D contribution city generated from Alex's GitHub contribution calendar" width="100%">
</picture>

## Contribution Snake

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/alexliluz/alexliluz/output/contribution-snake-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/alexliluz/alexliluz/output/contribution-snake-light.svg">
  <img src="https://raw.githubusercontent.com/alexliluz/alexliluz/output/contribution-snake-light.svg" alt="Animated contribution snake traversing Alex's GitHub contribution grid" width="100%">
</picture>

---

[Explore all repositories →](https://github.com/alexliluz?tab=repositories)
```

- [ ] **Step 4: Run the focused tests and confirm the new contract passes**

Run:

```bash
python3 -m unittest -v \
  tests.verify_profile.ProfileContractTests.test_compact_identity_sections_are_present_in_order \
  tests.verify_profile.ProfileContractTests.test_featured_work_is_one_compact_line_with_three_owned_projects \
  tests.verify_profile.ProfileContractTests.test_static_technology_badges_are_present \
  tests.verify_profile.ProfileContractTests.test_local_hero_is_retained_but_not_rendered
```

Expected: `Ran 4 tests` and `OK`.

- [ ] **Step 5: Run the complete profile test suite**

Run:

```bash
python3 -m unittest -v tests/verify_profile.py tests/test_validate_profile_assets.py
```

Expected: all profile and generated-asset validator tests pass with `OK`.

- [ ] **Step 6: Perform static hygiene checks**

Run:

```bash
git diff --check
rg -n "TBD|TODO|FIXME|example\.com|你的邮箱|readme-typing-svg|wakatime" README.md tests/verify_profile.py
```

Expected: `git diff --check` produces no output and `rg` finds only deliberate forbidden-fragment assertions inside `tests/verify_profile.py`, never in `README.md`.

- [ ] **Step 7: Commit the redesign**

```bash
git add README.md tests/verify_profile.py
git commit -m "feat: simplify profile introduction"
```

Expected: one commit containing only the README composition and its contract-test updates.

- [ ] **Step 8: Publish and verify the live GitHub rendering after explicit release approval**

Push the verified commit to `main`, wait for GitHub to render the profile, and check:

```bash
git rev-parse HEAD
git ls-remote origin refs/heads/main
```

Expected: both commands report the same commit SHA. On `https://github.com/alexliluz`, the compact introduction and five badges render above the unchanged neon contribution city and contribution snake with no broken images.
