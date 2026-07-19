# Animated Contribution Signal V2 Design

## Summary

The current Contribution Signal is technically animated, but its motion is too slow and visually subtle on GitHub. The 3D city and contribution snake are also placed inside boxes whose aspect ratios do not match their source SVGs, so `preserveAspectRatio="xMidYMid meet"` shrinks both focal elements and creates excessive empty space.

V2 keeps the approved single-panel composition and the original Platane contribution-grid snake, but makes motion unmistakable and professional. It replaces data-URI image nesting with one top-level SVG document, gives the city and snake aspect-ratio-correct viewports, and shortens their animation cycles without introducing aggressive flashing.

## Goals

- Keep one unified Contribution Signal panel.
- Make the 3D neon city and original contribution-grid snake visibly animate on GitHub.
- Enlarge both focal elements without cropping their source content.
- Preserve light, dark, animated, and reduced-motion variants.
- Keep Star history in the same panel and make its live signal apparent even while the history contains only one snapshot.
- Preserve the existing repository-owned, atomic `output` branch publication flow.

## Non-goals

- Replacing the original Platane snake path or contribution grid with a custom imitation.
- Converting the panel to GIF, APNG, video, or another raster animation format.
- Adding WakaTime, new statistics providers, or additional README sections.
- Changing the signature, technology badges, featured repositories, or surrounding profile copy.
- Adding fast flashes, large glow blooms, or continuous movement outside the Contribution Signal panel.

## Root Cause

The upstream source dimensions are:

- 3D city: `1280 × 850`
- contribution snake: `880 × 192`

The current outer layout places them in:

- city: `920 × 350`
- snake: `920 × 140`

Because both sources use aspect-preserving `meet` behavior, the city renders at approximately `527 × 350` and the snake at approximately `642 × 140`. Their visible widths are therefore much smaller than the boxes around them.

The upstream city rainbow cycle is 10 seconds. The upstream Platane snake cycle is 18.5 seconds. Frame-difference diagnostics confirm that the city, snake, and combined SVG all change over time, but these long cycles and small rendered subjects make the public profile feel static.

The current composer also embeds both source SVGs as base64 data URIs inside `<image>` elements. Although this works in local Chromium diagnostics, it introduces an unnecessary nested image boundary. V2 removes that boundary so every animated element belongs to the top-level SVG document GitHub loads.

## Selected Approach

### Top-level vector composition

The composer parses each validated source SVG and inserts its drawable nodes into nested `<svg>` viewports within the outer Contribution Signal document. These nested viewports are part of the same XML DOM; they are not `<image>` elements and do not use data URIs.

Before insertion, the composer namespaces each imported document so its styles cannot collide with the outer panel or the other imported document:

- prefix element IDs and rewrite fragment references;
- prefix class tokens and their CSS selectors;
- prefix keyframe names and matching animation declarations;
- scope source `:root` custom properties to the imported wrapper;
- rewrite local SMIL timing references when they target renamed IDs.

If the upstream SVG contains a construct that cannot be namespaced safely, composition fails with a path-specific error. The workflow must not silently fall back to data-URI embedding or publish a partially composed panel.

## Layout

The panel viewBox changes from `0 0 960 660` to `0 0 960 900`.

### Header and Star signal

- Keep the `CONTRIBUTION SIGNAL` title and `PUBLIC ACTIVITY · DAILY` subtitle in the upper-left.
- Keep the Star total and snapshot start date in the upper-right signal card.
- Preserve the current GitHub-compatible dark and light surface colors.
- Set the Star card to `x=650`, `y=18`, `width=282`, `height=70` so the moving signal dot has a fixed, testable viewport without changing the panel's outer width.

### 3D contribution city

- Label baseline: approximately `y=104`.
- Viewport: `x=88`, `y=110`, `width=784`, `height=520`.
- Source viewBox remains `0 0 1280 850`.
- Use `preserveAspectRatio="xMidYMid meet"` with the matching viewport ratio, so the complete city fills approximately 784 pixels of horizontal space.
- The visible city width increases by roughly 49 percent compared with V1.
- The upstream radar, language ring, totals, and contribution buildings remain part of the city asset; they are secondary to the contribution grid but are not removed or clipped.

### Original contribution snake

- Separator: approximately `y=650`.
- Label baseline: approximately `y=675`.
- Viewport: `x=42`, `y=695`, `width=876`, `height=191`.
- Source viewBox remains `-16 -32 880 192`.
- The visible snake width increases by roughly 36 percent compared with V1.
- Preserve the original contribution cells, original path, purple snake coloring, and theme-specific contribution colors generated by Platane/snk.

The exact label and separator coordinates may move by no more than 8 pixels during implementation to prevent clipping after real-asset rendering. The city and snake viewport dimensions are acceptance requirements and must not shrink.

## Motion Design

The selected motion character is “A+”: clearly visible, restrained, and slightly faster than the original recommended professional setting.

### City

- Dark-theme rainbow neon cycle: 6.5 seconds, linear, infinite.
- Light-theme active-building sweep: 6.5 seconds, linear, infinite, using the existing green contribution scale rather than a full rainbow.
- Initial building-rise sequence: 1.8 seconds, runs once.
- Keep existing stagger/delay relationships so the city reads as a coordinated field rather than a single flashing block.
- Add a 3.25-second alternating luminance breath only to active contribution buildings; no full-panel opacity pulse.

### Contribution snake

- Full original snake traversal: 8.5 seconds, linear, infinite.
- Preserve the original Platane keyframe percentages and path; change only the shared duration.
- Keep the purple head/body readable against both theme backgrounds.
- Apply a restrained glow only to the moving snake accent, never to inactive contribution cells.

### Star trend

- Initial line draw: 1.6 seconds, runs once.
- Add a small signal dot that follows the generated trend path every 3.2 seconds.
- When only one Star snapshot exists and the trend is a horizontal baseline, the dot still moves from left to right so the signal is visibly alive.
- The signal dot uses the existing theme trend color and a small glow; it must not obscure the line or Star total.

### Reduced motion

The existing README `<picture>` selection remains unchanged. Visitors with `prefers-reduced-motion: reduce` receive static light or dark output.

Static variants:

- contain no SMIL animation elements;
- contain no CSS animation or transition declarations;
- materialize a visible city color from the first keyframe;
- show the full contribution grid and snake at a meaningful resting state;
- show the trend line completely drawn with the signal dot at the latest point.

## Data Flow

1. The workflow generates the upstream light/dark city and snake SVGs.
2. The validator rejects unsafe or remote runtime references before composition.
3. The Star-history recorder restores prior snapshots and appends the current counts idempotently.
4. The composer parses and namespaces the city and snake documents.
5. The composer adjusts approved animation durations and inserts both documents into aspect-ratio-correct top-level viewports.
6. The composer generates animated and static light/dark Contribution Signal SVGs.
7. The validator checks the four final SVGs, including all imported nodes.
8. The workflow atomically publishes the same stable filenames to `output`.

README-facing filenames remain:

- `contribution-signal-light.svg`
- `contribution-signal-dark.svg`
- `contribution-signal-light-static.svg`
- `contribution-signal-dark-static.svg`

No README URL migration is required.

## Safety and Failure Handling

- Validate each input before parsing or transformation.
- Do not add external fonts, scripts, stylesheets, or runtime resource URLs.
- Reject duplicate IDs after namespacing.
- Reject unresolved fragment, CSS, or SMIL references after transformation.
- Enforce the existing 2 MiB SVG size boundary on inputs and outputs.
- Stop publication if animation-duration normalization does not find the expected city or snake rules; an upstream generator format change must be visible rather than silently producing a slow or static result.
- Preserve atomic publication: validation failure leaves the existing `output` branch assets untouched.

## Testing

### Unit and contract tests

- Animated outputs contain no `data:image/svg+xml` payloads for city or snake.
- Imported city and snake nodes exist in the top-level document.
- Namespaced IDs, classes, keyframes, custom properties, and references remain internally consistent.
- Dark city rainbow and light city active-building sweep use 6.5-second cycles.
- Active city buildings use a 3.25-second alternating luminance breath.
- City SMIL introduction uses 1.8-second timing where applicable.
- Snake animation rules use an 8.5-second shared cycle while preserving original keyframe percentages.
- Star trend line uses a 1.6-second draw and the signal dot uses a 3.2-second repeated path.
- Animated and static variants preserve the existing accessibility title and description.
- Static variants contain no executable motion and retain visible city/snake fallback states.
- The four output files validate and remain under the size limit.
- Existing README, Star-history, signature, workflow-hardening, and SVG-security tests continue to pass.

### Real-asset verification

- Generate all variants from actual workflow city and snake assets.
- Render light and dark animated outputs at an interval after the 1.8-second intro; frame hashes must continue to differ, proving infinite city/snake motion rather than only an entrance animation.
- Render the reduced-motion light and dark outputs twice; frame hashes must remain identical.
- Visually inspect the full panel for clipping, excessive blank space, text overlap, and low-contrast glow.
- Confirm the city occupies its approved 784 × 520 viewport and the snake occupies its approved 876 × 191 viewport.

### GitHub verification

- Publish the feature branch and run the workflow manually from its exact head SHA.
- Validate the generated `output` branch files before merging.
- After final approval and merge, confirm GitHub's rendered README contains the four stable theme/motion sources.

## Acceptance Criteria

- The public profile still shows one unified Contribution Signal panel.
- The city is visibly larger and fills its intended viewport.
- The dark city cycles through neon colors in 6.5 seconds; the light city runs a green active-building sweep over the same duration.
- Contribution buildings complete their entrance in 1.8 seconds.
- The original Platane contribution-grid snake visibly traverses the grid in 8.5 seconds.
- The Star trend line draws once and a signal dot continues to travel every 3.2 seconds.
- Light, dark, animated, and reduced-motion variants all remain legible and valid.
- Reduced-motion variants are fully static but visually complete.
- No city or snake is embedded through a data URI or external runtime reference.
- The workflow refuses to publish if upstream asset structure changes incompatibly.
- Existing profile content outside Contribution Signal is unchanged.
