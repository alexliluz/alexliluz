# Minimal Developer Profile Header Design

## Objective

Replace the verbose upper half of the GitHub profile with a compact developer introduction inspired by Anurag Hazra's profile structure, while preserving Alex's existing neon contribution city and animated contribution snake.

The profile should answer three questions within a few seconds:

1. Who is Alex / ASEnough?
2. What does he build?
3. Where can a visitor inspect the work?

## Content Structure

The README will use this order:

1. Compact greeting: `Hi, I'm Alex / ASEnough 👋`
2. One-sentence positioning statement in Chinese and English
3. `About me` with four factual bullets
4. Compact technology badges
5. One-line links to the three representative repositories
6. Existing neon 3D contribution city
7. Existing animated contribution snake
8. Link to all repositories

## Upper Profile Content

The current full-width hero SVG and the three long project descriptions will be removed from the README. The local hero asset may remain in the repository for history and possible later reuse, but it will no longer be rendered.

The introduction will avoid broad marketing language. Each line must convey a specific fact:

- Current focus: practical AI Coding and agent workflows
- Representative work: Planarian, ForkNeo, and api-image-neo
- Main tools: TypeScript, Python, Node.js, and GitHub Actions
- Engineering preference: reproducible, inspectable workflows

The bilingual positioning statement will be brief rather than repeated across several sections.

## Technology Badges

Use small, static Shields.io badges for TypeScript, Python, Node.js, GitHub Actions, and AI Agents. Badges are decorative summaries, not a comprehensive skills inventory.

No WakaTime, GitHub Readme Stats, visitor counter, typing animation, or other third-party data widget will be introduced. This keeps the page fast and avoids unreliable external dependencies.

## Project Links

The three projects will appear as a single compact line instead of full descriptions:

`Planarian` · `ForkNeo` · `api-image-neo`

Each name links directly to its public repository. The GitHub pinned-repository area remains the place for descriptions, language data, and stars.

## Preserved Dynamic Sections

The existing repository-owned assets remain unchanged:

- Light and dark 3D contribution city SVGs from the `output` branch
- Light and dark animated contribution snake SVGs from the `output` branch
- Daily and manual GitHub Actions generation workflow
- Theme-aware `<picture>` markup and accessible fallback text

The section headings may be shortened, but their asset URLs and behavior will not change.

## Verification

Automated profile contract tests will be updated to verify:

- The old hero is no longer rendered
- The compact greeting, positioning statement, and factual `About me` section exist in order
- Exactly the three approved project links remain in the featured-project line
- The five technology badges are present
- The 3D contribution city and contribution snake retain light/dark sources
- No unapproved dynamic widgets or placeholder text are introduced

The final README will also be visually checked on the live GitHub profile after publication.

## Out of Scope

- Changing GitHub profile metadata or pinned repositories
- Replacing the contribution asset workflow
- Adding WakaTime or external statistics cards
- Deleting the existing hero SVG asset
- Changing project descriptions in their individual repositories
