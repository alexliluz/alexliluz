# GitHub Profile: Builder's Console Design

## Purpose

Create a GitHub profile README for `alexliluz` that presents Alex as a builder of practical tools for AI-assisted software work. A visitor should understand the identity, focus, and strongest work within five seconds.

## Audience

- Developers interested in AI coding, Codex skills, agent workflows, and developer automation.
- Potential collaborators evaluating Alex's current work.
- Recruiters or clients who need concise evidence of technical direction and project ownership.

## Positioning

Primary statement:

> I build agent-ready developer tools for AI-assisted software work.

Chinese supporting statement:

> 我在做面向 AI Coding、Agent 工作流和开发者自动化的实用工具。

The page uses English as the primary language for international accessibility and Chinese as concise supporting context.

## Content Architecture

The README contains these sections in order:

1. A terminal-inspired hero with the primary and Chinese positioning statements.
2. A compact navigation row linking to selected work, current focus, and contact.
3. `Selected Work`, featuring exactly three clearly attributable projects.
4. `Now`, describing current areas of exploration.
5. `Building Principles`, expressing engineering judgment in three short statements.
6. `Working With`, listing evidenced technologies without proficiency percentages.
7. `Connect`, linking to the GitHub profile and omitting channels that do not yet have confirmed URLs.

## Selected Work

### Planarian

- URL: `https://github.com/alexliluz/planarian`
- Value: repeatable UI reconstruction workflows designed for coding agents.
- Labels: Agent Workflow, TypeScript, UI Engineering.
- Status: Experimental.

### ForkNeo

- URL: `https://github.com/alexliluz/ForkNeo`
- Value: converts GitHub forks into independent repositories while preserving Git history.
- Labels: CLI, GitHub Automation, TypeScript.
- Status: Active.

### api-image-neo

- URL: `https://github.com/alexliluz/api-image-neo`
- Value: provides a Codex image-generation skill for OpenAI-compatible providers.
- Labels: Codex Skill, Image Generation, Python.
- Status: Active.

`linuxdo-scripts-neo` is intentionally excluded from selected work because most of its history belongs to upstream contributors. The profile must not imply ownership of work that is primarily attributable to others.

## Visual System

- Use a small repository-owned SVG hero rather than remote decorative widgets.
- Use a transparent background for GitHub light and dark theme compatibility.
- Keep all essential information as selectable HTML text in the README; the SVG is decorative and must have useful alt text.
- Use GitHub blue `#58A6FF`, green `#3FB950`, muted gray `#8B949E`, and theme-aware text through CSS media queries in the SVG.
- Keep the README left-aligned and avoid multi-column HTML tables so it remains readable on narrow screens.
- Avoid animation in the first version.

## Excluded Patterns

The first version must not include contribution streaks, visitor counters, trophy cards, language percentages, contribution snakes, typing animations, random quotes, Spotify status, or externally hosted GitHub statistics cards. These distract from project evidence and introduce fragile third-party dependencies.

## Profile Metadata Recommendations

These GitHub account settings are documented for manual application because they are outside the repository:

- Display name: `Alex · ASEnough`
- Bio: `Building agent-ready tools for AI-assisted software work.`
- Pin, in order: `planarian`, `ForkNeo`, `api-image-neo`.

## Repository Structure

- `README.md`: complete profile content and navigation.
- `assets/builder-console.svg`: decorative terminal-inspired hero owned by the repository.
- `tests/verify_profile.py`: dependency-free structural and policy checks.
- `docs/superpowers/specs/2026-07-17-github-profile-design.md`: this design record.
- `docs/superpowers/plans/2026-07-17-github-profile.md`: implementation plan.

## Acceptance Criteria

- The README identifies Alex and states the AI-assisted developer tooling focus above the fold.
- It links to Planarian, ForkNeo, and api-image-neo with accurate one-line descriptions.
- It contains `Now`, `Building Principles`, `Working With`, and `Connect` sections.
- It does not contain forbidden third-party profile widgets or unconfirmed contact links.
- The SVG is valid XML, uses a transparent canvas, and contains accessible title and description elements.
- All repository-owned paths referenced by the README exist.
- All referenced public GitHub project URLs return a successful HTTP response.
