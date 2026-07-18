# Profile Signature and Contribution Signal Design

## Objective

Evolve Alex's GitHub profile into a compact technical identity with three distinctive elements:

1. A deterministic handwritten `Alex` signature banner
2. A factual TypeScript/Python/Node.js introduction with project Star counts
3. One theme-aware `Contribution Signal` panel that preserves both the existing 3D contribution city and the original contribution-grid snake animation

The redesign must remain fast, inspectable, repository-owned, and safe to publish without exposing a personal access token.

## GitHub Layout Boundary

GitHub controls the native `Pinned` and `contributions in the last year` areas outside the profile README. Their order and layout cannot be changed by README Markdown.

The redesign only controls the profile README above those native areas. It reduces duplication within the README by replacing two separate contribution sections with one unified `Contribution Signal` section. GitHub's native Pinned repositories and contribution calendar remain unchanged below it.

## Page Structure

The README will use this order:

1. `Alex` signature banner
2. Two-line technical positioning statement
3. Compact technology badges
4. Three featured repository links with live Star-count badges
5. One `Contribution Signal` picture
6. Link to all repositories

The current `About me` bullet list will be removed. Its useful information is compressed into the positioning statement and technology badges.

## Signature Banner

Create `assets/alex-signature.svg` with a `960 × 220` responsive viewBox.

The banner contains exactly:

- Primary text: `Alex`
- Subtitle: `BUILDING TOOLS THAT STAY INSPECTABLE`

The primary word uses the open-licensed `Kalam Bold` handwriting style converted to SVG path outlines. Converting the letters to paths prevents font substitution and guarantees that `Alex` renders identically on every platform. The subtitle uses a compact monospace treatment.

Theme colors:

- Dark: white signature `#F0F6FC`, purple offset shadow `#6D28D9`, coral subtitle `#FF7B72`
- Light: charcoal signature `#24292F`, violet offset shadow `#8250DF`, red subtitle `#CF222E`

The SVG includes `<title>`, `<desc>`, `role="img"`, a responsive viewBox, and no external font or image dependency. The supplied Anurag-style screenshot is a visual reference only; no pixels are copied into the final asset.

## Technical Positioning

Replace the current AI Coding copy with:

> TypeScript / Python developer focused on developer tooling, CLI automation, and reproducible systems.  
> 主要使用 TypeScript、Python 与 Node.js，专注开发者工具、CLI 自动化和可复现工程工作流。

The technology badges remain limited to:

- TypeScript
- Python
- Node.js
- GitHub Actions

Remove the generic `AI Agents` badge. The page may describe concrete agent-related projects through repository links, but the identity copy must lead with engineering technologies and capabilities.

## Featured Repositories and Star Counts

Keep the three approved repositories:

- `planarian`
- `ForkNeo`
- `api-image-neo`

Each link has a small Shields.io `github/stars` badge showing the current public count. These are live counts, not historical charts.

The combined panel also includes one quiet `Star Trend` inset representing the sum of Stars across the same three fixed repositories.

## Secure Star Snapshot History

Do not use Star History's token-based embed and do not publish any encrypted or plaintext personal access token.

Instead, extend the existing daily profile workflow to read each repository's public `stargazers_count` from `GET /repos/alexliluz/{repository}`. This endpoint exposes the current count without requesting the restricted list of individual stargazers.

Persist snapshots on the `output` branch as `star-history.json`:

```json
{
  "version": 1,
  "snapshots": [
    {
      "date": "2026-07-19",
      "repos": {
        "planarian": 1,
        "ForkNeo": 1,
        "api-image-neo": 0
      }
    }
  ]
}
```

Rules:

- Start history on the deployment date; do not invent or backfill unavailable history.
- Store at most 730 daily snapshots.
- Re-running on the same UTC date replaces that date rather than adding a duplicate.
- If a count request fails, fail the generation job and leave the previous output branch untouched.
- Never replace a previously positive count with a failure-derived zero.
- Use only the existing repository-scoped `GITHUB_TOKEN`; no new repository secret or user-scoped token is required.

The trend inset labels its starting date so visitors understand the available time window.

## Contribution Signal Composition

Generate these new stable assets on the `output` branch:

- `contribution-signal-light.svg`
- `contribution-signal-dark.svg`
- `contribution-signal-light-static.svg`
- `contribution-signal-dark-static.svg`

Each animated asset is one outer SVG with:

1. A framed `CONTRIBUTION SIGNAL` header
2. A small Star Trend inset in the upper-right corner
3. The matching existing 3D contribution city in the upper content area
4. A divider
5. The matching original `Platane/snk` SVG in the lower content area, including its GitHub contribution grid and animated snake

The original city and snake SVG documents are embedded as self-contained SVG data images inside the outer SVG. This isolates their IDs and CSS while preserving their existing animations. The outer document contains no remote runtime dependency.

The four existing source assets remain published for inspection and fallback:

- `profile-3d-light.svg`
- `profile-3d-dark.svg`
- `contribution-snake-light.svg`
- `contribution-snake-dark.svg`

The static variants use the same embedded source documents after removing SMIL animation nodes and CSS animation declarations. README `<picture>` sources select the static variant when `prefers-reduced-motion: reduce` is active, then select light or dark animated variants for other visitors.

## Visual Hierarchy and Motion

The 3D city remains the primary contribution visualization. The original snake grid is a shorter lower band rather than a second full-page section. The Star Trend inset stays visually quiet so it does not compete with contribution activity.

Motion principles:

- Preserve the existing city and Platane snake animations
- Add only subtle outer-frame glow and Star-line drawing
- Avoid continuous large-area movement
- Provide the four static assets for reduced-motion visitors
- Keep light and dark palettes legible against GitHub's native themes

## Workflow Architecture

The existing `.github/workflows/generate-profile-assets.yml` remains the single daily and manually dispatchable workflow.

Its pipeline becomes:

1. Generate the original light/dark snake assets
2. Generate the original light/dark 3D city assets
3. Read the previous `star-history.json` from the `output` branch when it exists
4. Fetch current public Star counts
5. Update the snapshot history
6. Compose four `Contribution Signal` assets
7. Validate the original and composed SVGs
8. Atomically publish all assets and `star-history.json` to `output`

The job retains `contents: write`, a 15-minute timeout, concurrency cancellation, commit-pinned third-party actions, and atomic output publication.

## Failure Handling

- Missing or malformed generated city/snake SVG: fail before publishing.
- Malformed history JSON: fail with the path and parsing error; do not silently reset history.
- Star API request failure: fail and retain the previous output branch.
- Composed SVG exceeding 2 MiB: fail validation to avoid an excessively heavy profile.
- Embedded SVG containing scripts or external HTTP references: fail validation.
- No previous history file: create version 1 with the current UTC date.

## Testing and Verification

Add focused tests for:

- Signature SVG accessibility, exact copy, theme colors, responsive viewBox, and absence of external dependencies
- Removal of `AI Coding`, `AI Agents`, the old greeting heading, and the old separate contribution headings
- Exact technical positioning copy and four technology badges
- Three featured repository links and Star badges
- Snapshot schema, same-day idempotency, 730-day retention, and failure preservation
- Composite SVG structure, embedded city and snake payloads, original Contribution Snake preservation, Star Trend label, and 2 MiB size limit
- Static variants containing no SMIL or CSS animation declarations
- README `<picture>` ordering for reduced-motion and light/dark sources
- Workflow permissions, pinned actions, timeout, atomic publication, and absence of PAT secrets

Before publication, render the README on GitHub and visually verify:

- Correct `Alex` spelling and signature appearance
- No broken technology or Star badges
- Star inset label and line
- Animated city and original Contribution Snake grid
- Static reduced-motion variants
- No horizontal overflow in the GitHub profile column

## Out of Scope

- Moving or restyling GitHub's native Pinned or contribution sections
- Publishing a personal access token, encrypted or otherwise
- Backfilling Star history from individual stargazer timestamps
- Changing which repositories are pinned in GitHub's native UI
- Adding WakaTime, visitor counters, GitHub Readme Stats, or typing widgets
