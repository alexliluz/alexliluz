# GitHub Profile V3: Cyber Flagship

## Status

The layout, visual language, content architecture, automation model, and acceptance standards were approved on 2026-07-18. This document is the implementation contract for the V3 profile and is awaiting written-spec review before implementation planning begins.

## Purpose

Evolve the existing **Product OS × Agent Console** profile into a more memorable **Cyber Flagship** without losing the credibility, project focus, and maintainability established in V2.

The intended first impression is:

> Alex builds practical, inspectable tools for AI-assisted software work.

The 3D contribution city and contribution snake reinforce that identity as supporting visuals. They must not replace the explanation of Alex's work or become the primary reason the page exists.

## Approved Direction

### Layout: Product Console

The approved layout preserves a single-column, product-led reading order. It introduces one large contribution visualization after the selected projects and one animated footer detail after the operating signals.

This direction was selected over:

- **Neon Cinema**, which created a stronger first-frame spectacle but reduced space for project evidence;
- **Dense Dashboard**, which exposed more information but increased scanning cost and weakened mobile readability.

### Visual Skin: Midnight Aurora

The approved palette combines:

- GitHub blue for primary interaction and system structure;
- agent violet for ambient depth and generative-tool character;
- status green for active-state signals;
- GitHub-compatible dark and light neutral surfaces.

The visual treatment should feel like a polished developer product interface, not a generic cyberpunk poster. Glow, scanning, and pulse effects remain subtle and subordinate to text.

## Audience and Content Principles

The primary audience remains developers, collaborators, clients, and recruiters interested in AI coding, agent workflows, and developer tooling.

The profile follows these rules:

1. Project evidence appears before contribution spectacle.
2. Every technical claim is traceable to public work.
3. English leads for international readability; Chinese adds concise identity and context.
4. Dynamic sections use repository-owned generated assets rather than best-effort public widget endpoints.
5. Decorative components are limited to one hero, one 3D contribution visualization, and one contribution snake.
6. Empty metrics, fabricated contact details, visitor counters, trophy walls, generic statistics cards, and large badge matrices are excluded.

WakaTime is explicitly excluded from V3 because Alex does not currently use it. The design must not display empty activity data or require public time-tracking settings merely to fill a section.

## Page Architecture

The README uses this exact sequence:

1. Theme-aware **Hero 2.0**.
2. Native Markdown identity and mission.
3. **Selected Systems** with Planarian, ForkNeo, and api-image-neo.
4. Theme-aware **3D Contribution City**.
5. **Operating Signals** for Now, Core Stack, and Principles.
6. Theme-aware **Contribution Snake**.
7. One minimal link to all repositories.

The page remains a mobile-safe single column. HTML is used only where GitHub Markdown requires theme-aware `<picture>` elements or centered image treatment.

## Hero 2.0

The existing repository-owned `assets/profile-hero.svg` is evolved rather than replaced with a remote typing widget.

### Content hierarchy

```text
PRODUCT OS · AGENT CONSOLE                    SYSTEM: ACTIVE

Alex / ASEnough
Building practical, inspectable tools for
AI-assisted software work.

AI CODING · AGENT WORKFLOWS · DEVELOPER TOOLS
```

The Chinese mission remains selectable Markdown immediately below the hero:

> 我在做更实用、可检查、可复现的 AI Coding 与 Agent 工作流工具。

### Visual behavior

- Preserve the current responsive SVG approach and repository ownership.
- Use the Midnight Aurora blue–violet–green accent beam.
- Add a restrained scanning highlight, two or three node pulses, and a quiet active-state indicator.
- Keep all motion within the SVG; do not add JavaScript.
- Include `prefers-color-scheme` styles for light and dark GitHub themes.
- Include `prefers-reduced-motion: reduce` rules that disable nonessential animation.
- Retain `<title>`, `<desc>`, `role="img"`, and meaningful README alt text.
- Use system fonts only and remain legible when animation or theme detection is unavailable.

The hero may not simulate a full terminal window, use fake traffic-light controls, or introduce a typing animation. Its personality comes from system hierarchy and restrained motion.

## Selected Systems

The three V2 projects remain the core evidence and preserve their approved order:

1. **Planarian** — experimental agent workflow tooling for reproducible UI reconstruction.
2. **ForkNeo** — active CLI and GitHub automation for safe fork-to-independent repository migration.
3. **api-image-neo** — active Codex skill for provider-flexible image generation workflows.

Each item remains native Markdown with a linked heading, compact status/domain labels, an outcome-led sentence, and one supporting sentence. V3 may strengthen spacing and visual separators but must not replace these explanations with repository-stat cards.

No fabricated metrics, release counts, star claims, or ownership implications are added.

## 3D Contribution City

The 3D city is the only large contribution-data visual and appears after Selected Systems.

### Assets

Generate two repository-owned SVGs on the `output` branch:

```text
profile-3d-light.svg
profile-3d-dark.svg
```

Publish upstream `profile-night-rainbow.svg` as the dark asset and `profile-green-animate.svg` as the light asset. Implementation may rename those upstream output files while publishing them, but README-facing names remain stable.

### Presentation

- Heading: `## Contribution City`.
- One short supporting line explains that the city is generated from Alex's GitHub contribution calendar.
- A `<picture>` element selects the correct light or dark asset.
- The image uses a meaningful alt description and fills the available README width.
- The city must not appear before the projects or carry exaggerated claims about productivity.

The generator is `yoshi389111/github-profile-3d-contrib`; the incorrect `yoshi386` identifier from the rejected proposal must not appear.

## Operating Signals

This compact section combines information that is stable and useful:

### Now

```text
Turning agent demos into repeatable engineering workflows.
把 Agent Demo 变成可复现、可验证、可长期维护的工程工作流。
```

### Core Stack

Only publicly supportable areas are listed:

```text
TypeScript · Python · CLI · GitHub Automation · Agent Workflows
```

### Principles

```text
Inspectable artifacts · Reproducible workflows · Useful before impressive
```

These remain native Markdown text rendered as small inline-code pills, not a large shields.io badge matrix.

## Contribution Snake

The contribution snake is retained as a page-end visual reward rather than a headline component.

### Assets

Generate two SVGs on the `output` branch:

```text
contribution-snake-light.svg
contribution-snake-dark.svg
```

Colors should reuse Midnight Aurora accents where supported. A `<picture>` element selects the visitor's light or dark theme.

### Presentation

- Heading: `## Contribution Trail`.
- The image appears after Operating Signals and before the final repository link.
- Alt text describes the animated snake traversing the contribution grid.
- The section must remain intelligible when animation is paused or unsupported.

The generator is the SVG-only mode of `Platane/snk` when compatible with the pinned release.

## Minimal Connect

V3 ends with one deliberate action:

```markdown
[Explore all repositories →](https://github.com/alexliluz?tab=repositories)
```

No email, social network, website, or messaging link is added until Alex provides a confirmed canonical destination. The profile does not link back to its own overview page as a social button.

## Generated-Asset Architecture

Use one workflow at `.github/workflows/generate-profile-assets.yml` with daily scheduled and manual triggers.

```text
GitHub contribution data
          │
          ├──> 3D contribution generator ──> light/dark city SVGs
          │
          └──> contribution-snake generator ──> light/dark snake SVGs
                                         │
                                         v
                              validate generated SVGs
                                         │
                                         v
                         atomically publish output directory
                                  to `output` branch
                                         │
                                         v
                         README light/dark `<picture>` sources
```

### Workflow boundaries

- Grant only `contents: write` at workflow or job scope.
- Use the repository-provided `GITHUB_TOKEN`; do not require a personal access token.
- Do not request private contribution details beyond what Alex exposes on the public contribution calendar.
- Pin every third-party Action to a full immutable commit SHA. A comment may record the corresponding release tag for maintainability.
- Add a concurrency group with cancellation of superseded runs.
- Add a bounded job timeout.
- Generate into a temporary build directory before publishing.
- Validate that all four expected files exist, are nonempty, parse as SVG XML, and contain no obvious error document.
- Publish only after every generation and validation step succeeds.
- Keep machine-generated files on the `output` branch so scheduled runs do not create daily commits on `main`.
- Preserve stable README-facing filenames even if an upstream generator changes its native output names.

The implementation must not combine a generated `dist` directory with unrelated files from the checked-out branch, push generated content back to `main`, or hide generation errors with unconditional success commands such as `|| exit 0`.

## Failure Handling

- If either generator fails, the publish step does not run and the last successful `output` branch remains available.
- If validation fails, the workflow reports a failed run and preserves the last successful assets.
- If the `output` branch or an asset is temporarily unavailable, the self-hosted hero, native project descriptions, and operating signals still communicate the complete profile identity.
- A failed scheduled run never edits README content.
- Workflow logs must identify whether failure occurred during city generation, snake generation, validation, or publication.
- Upstream breaking changes are handled by updating one pinned Action reference and any corresponding filename mapping; they do not require restructuring the README.

## Security and Privacy

- No WakaTime API key, personal access token, analytics script, visitor tracker, or third-party profile-data endpoint is added.
- The workflow receives only the minimum GitHub repository permission needed to publish generated assets.
- Secrets and tokens must never be written into generated SVGs, logs, README URLs, or committed configuration.
- Remote images are limited to raw assets from the `alexliluz/alexliluz` repository's generated `output` branch.
- Generated SVGs are treated as untrusted build output and validated before publication.

## Verification Strategy

Extend `tests/verify_profile.py` to cover the V3 contract.

### Static structure

- required Hero, Selected Systems, Contribution City, Operating Signals, Contribution Snake, and repository-link sequence;
- exact project links and project order;
- absence of WakaTime, visitor counters, typing widgets, generic stats cards, trophy widgets, placeholder domains, and fabricated contact text;
- README image sources restricted to local assets and the repository-owned `output` branch;
- valid `<picture>` light/dark source structure and meaningful alt text;
- accessible, parseable Hero SVG with reduced-motion and theme rules;
- valid workflow YAML and the expected trigger, concurrency, timeout, permission, generation, validation, and publish stages;
- full-SHA pinning for third-party Actions and absence of broad permissions or PAT references.

### Generated assets

- manually trigger the workflow before publication;
- confirm that the run succeeds and publishes four nonempty SVG files to `output`;
- fetch and parse each published SVG;
- inspect the 3D city and snake in GitHub light and dark themes;
- confirm that narrow-width rendering does not introduce horizontal overflow or unreadable text.

### Release checks

- run the complete dependency-free test suite;
- run `git diff --check`;
- render and inspect the Hero at desktop and narrow widths with animation enabled and reduced;
- preview the complete GitHub-rendered README before pushing;
- confirm that `main` contains no generated daily assets.

## Release Sequence

Design approval does not itself authorize implementation or publication. The implementation sequence is:

1. Approve and commit this design specification.
2. Create and approve a detailed implementation plan.
3. Implement Hero, README, workflow, and tests locally.
4. Run static, render, security, link, and workflow syntax checks.
5. Push the workflow and README changes only after explicit publication approval.
6. Manually trigger the asset workflow and verify the four `output` assets.
7. Inspect the live profile in light, dark, desktop, and narrow layouts.

If generated assets are not ready at publication time, README references to them must not be published until a successful workflow run has created the stable files.

## Research Basis

- GitHub profile README behavior and public-profile elements: <https://docs.github.com/en/account-and-profile/concepts/personal-profile>
- GitHub profile README management: <https://docs.github.com/en/account-and-profile/how-tos/profile-customization/managing-your-profile-readme>
- Contribution snake generator and current SVG workflow: <https://github.com/Platane/snk>
- 3D contribution generator and current workflow: <https://github.com/yoshi389111/github-profile-3d-contrib>
- GitHub Readme Stats reliability notice and static-generation recommendation, used to justify exclusion of its public endpoint: <https://github.com/anuraghazra/github-readme-stats>

## Acceptance Criteria

- A first-time visitor can identify Alex's field and three selected projects before encountering contribution visuals.
- The profile looks recognizably more ambitious than V2 while preserving Product OS × Agent Console continuity.
- Midnight Aurora is applied consistently across Hero, city selection, operating accents, and snake colors.
- Hero motion is restrained, theme-aware, accessible, and disabled under reduced-motion preferences.
- The 3D city and snake each have working light and dark SVG assets owned by the profile repository.
- Dynamic assets are regenerated daily without scheduled commits to `main`.
- A failed generation cannot replace the last successful assets or erase core profile content.
- All project and technology claims remain attributable and current.
- No WakaTime, visitor counter, generic stats card, typing widget, trophy wall, placeholder URL, or fictional contact detail is present.
- The automated suite, generated-asset checks, and final visual inspection pass before release completion.
