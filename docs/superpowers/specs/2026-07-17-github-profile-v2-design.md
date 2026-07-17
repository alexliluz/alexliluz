# GitHub Profile V2: Product OS × Agent Console

## Status

The visual direction and information architecture were approved on 2026-07-17. This document is the implementation contract for the V2 profile and is awaiting written-spec review before implementation planning begins.

## Purpose

Upgrade `github.com/alexliluz` from the V1 Builder's Console into a distinctive, product-led profile that explains Alex's work within five seconds and rewards a deeper read without becoming a widget dashboard.

The profile should communicate four things in order:

1. Alex builds practical tools for AI-assisted software work.
2. The work focuses on AI coding, agent workflows, and developer tooling.
3. Planarian, ForkNeo, and api-image-neo are the strongest current examples.
4. A visitor can open one of those projects or browse the rest of the work.

## Audience

- Developers interested in AI coding, Codex skills, agent workflows, and developer automation.
- Potential collaborators evaluating Alex's technical direction and project judgment.
- Recruiters or clients who need concise evidence of ownership and practical output.

English remains the primary language for international reach. Chinese provides a concise second layer of personality and context rather than duplicating every paragraph.

## Research Basis

The design combines three durable patterns observed in strong current profiles:

- product-led identity and release-oriented work presentation, as seen in `tw93`;
- restraint and strong navigation hierarchy, as seen in `antfu`;
- maintainable, source-backed updates, as seen in `simonw`.

The design intentionally rejects the common template stack of stats cards, streaks, trophies, visitor counters, typing animations, and contribution snakes. Those components compete with project evidence, introduce third-party availability risk, and date the page quickly.

Reference URLs:

- <https://github.com/tw93>
- <https://github.com/antfu>
- <https://github.com/simonw>
- <https://devbio.me/blogs/github-profile-readme-examples-2026>
- <https://github.com/abhisheknaiidu/awesome-github-profile-readme>
- <https://docs.github.com/en/account-and-profile/how-tos/profile-customization/managing-your-profile-readme>

## Design Direction

The visual language is **Product OS × Agent Console**:

- 60% product-oriented presentation: outcome-led project descriptions and deliberate visual hierarchy;
- 25% GitHub-native typography: readable Markdown, restrained labels, and mobile-safe single-column flow;
- 15% console personality: monospace accents, a build-state motif, and one terminal-style status line.

The console motif is an accent, not the page metaphor. V2 must not look like a generic macOS terminal template or require visitors to decode command-line jokes before understanding the work.

## Page Architecture

The README uses a single-column sequence:

1. Theme-aware hero.
2. Identity and positioning copy.
3. `What I'm Building` with exactly three projects.
4. `Now` with one current-direction statement in English and Chinese.
5. `Building Principles` compressed into one short line.
6. One final link to all repositories.

The V1 anchor navigation, standalone `Working With`, and self-referential `Connect` sections are removed. Project-specific labels already provide technical context, and a GitHub link that points back to the current profile has no navigational value.

## Hero Component

Create a repository-owned SVG at `assets/profile-hero.svg` and replace the V1 `builder-console.svg` reference.

### Content

The hero presents this hierarchy:

```text
ALEX / ASENOUGH                              BUILD: ACTIVE

Building practical, inspectable tools for
AI-assisted software work.

AI CODING  ·  AGENT WORKFLOWS  ·  DEVELOPER TOOLS

alex@github:~$ turning demos into repeatable systems_
```

The Chinese supporting line remains native Markdown directly below the hero:

> 我在做更实用、可检查、可复现的 AI Coding 与 Agent 工作流工具。

### Visual Rules

- Canvas: `960 × 280` view box, responsive at `width="100%"`.
- Layout: left-aligned content with generous vertical spacing; no simulated window controls.
- Shape language: one quiet rounded frame, a compact build-status capsule, and a thin accent rule.
- Palette: GitHub-compatible neutral surfaces with blue and green accents.
- Default dark colors: surface `#0D1117`, border `#30363D`, primary `#F0F6FC`, muted `#8B949E`, blue `#58A6FF`, green `#3FB950`.
- Light-theme colors use `prefers-color-scheme: light`: surface `#FFFFFF`, border `#D0D7DE`, primary `#1F2328`, muted `#59636E`, blue `#0969DA`, green `#1A7F37`.
- Typography: system sans-serif for identity and headline, system monospace for labels and status. No remote fonts.
- Motion: none.
- Accessibility: include `<title>`, `<desc>`, `role="img"`, and meaningful README alt text. The Chinese positioning and all project evidence remain selectable Markdown.

If GitHub or a client ignores the light-theme media query, the SVG's default dark palette remains legible and complete.

## README Copy

### Identity

The hero is followed by:

```markdown
# Hi, I'm Alex / ASEnough.

我在做更实用、可检查、可复现的 AI Coding 与 Agent 工作流工具。
```

The English positioning sentence lives in the hero and its accessible description. The heading provides a searchable, selectable identity without repeating the full headline.

### What I'm Building

Use `## What I'm Building`. Each project is a native Markdown block consisting of a linked heading, compact labels, an outcome-led sentence, one supporting sentence, and no fabricated metrics.

#### 01 / Planarian

- URL: <https://github.com/alexliluz/planarian>
- Labels: `Experimental` · `Agent Workflow` · `TypeScript`
- Lead: `Reproducible UI reconstruction workflows for coding agents.`
- Support: `Planarian turns visual reconstruction into an inspectable process with stable artifacts, task bundles, validation commands, and explicit agent handoffs.`

#### 02 / ForkNeo

- URL: <https://github.com/alexliluz/ForkNeo>
- Labels: `Active` · `CLI` · `GitHub Automation` · `TypeScript`
- Lead: `Safe fork-to-independent repository migration without losing history.`
- Support: `ForkNeo preserves branches, tags, default-branch state, and Git LFS objects, then verifies the independent repository.`

#### 03 / api-image-neo

- URL: <https://github.com/alexliluz/api-image-neo>
- Labels: `Active` · `Codex Skill` · `Image Generation` · `Python`
- Lead: `Provider-flexible image generation workflows for Codex.`
- Support: `The skill supports generation, reference-image workflows, and editing through OpenAI-compatible providers while reusing existing Codex configuration.`

`linuxdo-scripts-neo` remains excluded because its history is primarily attributable to upstream contributors. The profile must not imply ownership of work that is not substantially Alex's.

### Now

```markdown
## Now

Turning agent demos into repeatable engineering workflows.

把 Agent Demo 变成可复现、可验证、可长期维护的工程工作流。
```

This statement is manually maintained. V2 does not add scheduled automation merely to make the profile appear active.

### Building Principles

```markdown
## Building Principles

`Inspectable artifacts` · `Reproducible workflows` · `Useful before impressive`
```

### Final Action

End with one deliberate browse action:

```markdown
[Explore all repositories →](https://github.com/alexliluz?tab=repositories)
```

Project headings remain direct links because they are evidence, not competing promotional calls to action.

## Profile Metadata

The README and account metadata should read as one composition:

- Display name: `Alex · ASEnough`
- Bio: `Building practical tools for AI-assisted software work.`
- Pinned repositories, in order: `planarian`, `ForkNeo`, `api-image-neo`

Metadata changes are a separate release action. They must be previewed alongside the README and require final publication approval. If pinning cannot be performed safely through the available GitHub interface, provide exact manual steps instead of using unsupported automation.

## Dependencies and Data Flow

V2 is intentionally static:

```text
README.md ──references──> assets/profile-hero.svg
    │
    ├──links──> three selected public repositories
    └──links──> the account repositories tab
```

- The profile has no runtime JavaScript, remote images, analytics, counters, or external widget APIs.
- Project status and `Now` copy are maintained in `README.md`.
- Theme behavior is self-contained in the SVG.
- Account metadata lives in GitHub settings and is documented separately from repository content.

## Reliability and Failure Handling

- A missing local hero is a release-blocking error.
- Malformed SVG XML is a release-blocking error.
- A selected project URL that does not resolve successfully is a release-blocking error.
- If theme detection fails, the default dark SVG remains readable.
- If metadata automation is unavailable, README publication can proceed only after the user decides whether to apply metadata manually; no fragile workaround is introduced.
- No future dynamic section may erase the last known-good profile content when an update job fails.

## Verification Strategy

Extend `tests/verify_profile.py` so the V2 contract verifies:

- required identity, `What I'm Building`, `Now`, and `Building Principles` content;
- exact links to Planarian, ForkNeo, api-image-neo, and the repositories tab;
- the presence of `assets/profile-hero.svg` and the absence of the V1 asset reference;
- absence of `Working With`, self-referential `Connect`, and forbidden widget patterns;
- no remote image dependencies;
- valid SVG XML with accessible title and description;
- successful responses from all selected public repository URLs.

Before publication, also run:

- the dependency-free test suite;
- `git diff --check`;
- an SVG render check at desktop and narrow widths;
- a visual inspection in both light and dark themes;
- a final GitHub-rendered preview or an equivalent local preview before pushing.

Tests prove structure and policy compliance; visual inspection proves hierarchy, spacing, theme contrast, and narrow-screen readability. Neither substitutes for the other.

## Release Boundaries

Implementation is performed locally first. The sequence is:

1. Implement the README, SVG, and tests.
2. Run structural, link, XML, render, and visual checks.
3. Show the final preview and summarize account-metadata changes.
4. Wait for explicit final publication approval.
5. Only then push README changes and apply approved metadata changes.

The design-spec commit itself may remain local until publication approval; approval of this design does not authorize publishing the new profile.

## Long-Term Evolution

V2 favors stable, manual truth over decorative automation. A later release may add one bounded `Latest Shipping` section only when repositories have meaningful releases or changelog entries to surface. Any such automation must:

- use GitHub-owned data or repository files as the source of truth;
- update only a delimited README region;
- preserve the last good content on failure;
- run no more often than necessary;
- avoid external badge or card services.

A personal website, writing feed, or contact link should be added only after a confirmed canonical URL exists. Stats dashboards remain out of scope unless the profile's audience and purpose materially change.

## Acceptance Criteria

- A first-time visitor can identify Alex's field and three strongest projects within five seconds.
- The page uses the approved Product OS × Agent Console direction without resembling a stock terminal template.
- The hero is self-hosted, theme-aware, accessible, responsive, and legible without remote assets.
- All project claims are attributable, current, and free of fabricated metrics.
- The README is readable as a single column on desktop and mobile.
- There is no third-party profile-widget dependency.
- Account metadata recommendations are explicit and handled as a separately approved publication action.
- Automated checks and visual inspection pass before the final preview is presented.
- No V2 profile or metadata change is published before explicit final approval.
