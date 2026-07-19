# Professional Engineering Stack Design

## Summary

The profile already has two strong custom visual anchors: the Alex signature and the animated Contribution Signal. The current `Tech stack` section between them is a row of generic Shields badges. It communicates the right basic technologies, but its visual language does not match the rest of the profile and it presents tools as an unstructured list.

This design replaces that badge row with a repository-owned Engineering Stack SVG. The new panel presents a small, publicly verifiable toolchain as one connected engineering workflow. It adopts only the profile-appropriate ideas from the referenced GitHub-profile beautification guide: a concise visual technology section and selective live repository signals. It deliberately excludes generic stats, streak, and trophy cards because the existing Contribution Signal already communicates public activity, trends, and contributions.

Reference: <https://www.cnblogs.com/aopstudio/p/19094889>

## Goals

- Make the technology section feel designed as part of the same profile as the Alex signature and Contribution Signal.
- Show only technologies that are supported by Alex's public repositories.
- Explain how the tools relate to one another instead of displaying an undifferentiated icon wall.
- Keep the profile compact, professional, responsive, accessible, and GitHub-compatible.
- Provide light, dark, animated, and reduced-motion variants without third-party runtime dependencies.
- Preserve the existing Featured Work, live Star badges, Star trend, 3D contribution city, and original contribution snake.

## Non-goals

- Adding GitHub Stats, streak, trophy, WakaTime, visitor-count, or language-percentage cards.
- Adding technologies that are familiar to the profile owner but not clearly demonstrated by current public work.
- Replacing or redesigning the existing Alex signature or Contribution Signal.
- Changing the Star-history data model, Contribution Signal generation workflow, or Platane snake animation.
- Embedding third-party Skill Icons, remote fonts, scripts, stylesheets, or runtime image resources.
- Turning the profile into a maximal dashboard.

## Evidence-based Technology Scope

The selected stack is limited to technologies directly supported by public work:

- **TypeScript and Node.js:** primary implementation platform for Planarian and ForkNeo.
- **pnpm:** declared package manager and command runner in Planarian.
- **Playwright:** direct Planarian dependency and browser-backed workflow component.
- **Vitest:** Planarian's declared test runner.
- **Git:** core migration layer documented by ForkNeo.
- **GitHub Actions:** used by the profile repository's published automation workflows.

Python is removed from this first version of the visual stack. Although it appears in the current profile copy and the profile repository contains Python-based asset tooling, the approved rule is to prioritize the clearest representative-project signal rather than maximize the number of technologies shown. It can be added later when it becomes a primary, clearly documented part of a featured public project.

## Information Architecture

The README order becomes:

1. Alex signature artwork.
2. One concise bilingual technical-positioning statement.
3. Engineering Stack panel.
4. Featured Work with the existing live Star badges.
5. Contribution Signal containing the 3D city, Star trend, and original animated contribution snake.
6. `Explore all repositories` link.

The old Shields-based `Tech stack` badge row is removed. The surrounding sections remain concise so the Contribution Signal continues to be the primary visual climax.

## Selected Visual Approach

### Canvas and hierarchy

- SVG viewBox: `0 0 960 300`.
- README display width: `100%` so GitHub can scale the panel responsively.
- Heading: `ENGINEERING STACK`.
- Supporting label: `PUBLIC TOOLCHAIN · VERIFIED BY WORK`.
- The panel uses one connected left-to-right engineering route rather than a logo grid.

### Workflow groups

The route has three semantic groups:

1. **BUILD** — TypeScript → Node.js
2. **AUTOMATE** — pnpm → GitHub Actions
3. **VERIFY** — Vitest → Playwright → Git

TypeScript and Node.js are the primary nodes and receive slightly more visual weight. The remaining nodes are smaller operational capabilities. Group labels, connecting lines, and consistent node geometry make the relationship legible even if brand colors are unavailable.

### Visual language

- Rounded outer frame and subtle inner rails align with the existing signature and Contribution Signal.
- Dark variant uses a GitHub-dark-compatible surface with restrained violet and coral accents plus a small cyan signal color.
- Light variant uses a pale GitHub-compatible surface, dark text, and lower-saturation accents.
- Each technology uses a text label and a small locally defined symbolic mark. The design does not depend on external logo CDNs.
- Monospaced uppercase labels carry the cyber/engineering character; technology names remain immediately readable.
- Glow is confined to active signal elements and never applied to entire text blocks.
- All essential meaning remains available through labels, contrast, and ordering rather than color alone.

## Motion Design

The motion character is precise and subordinate to Contribution Signal.

- Total loop: approximately 6 seconds, linear and continuous.
- A small signal point travels along the engineering route.
- Nodes illuminate briefly as the signal reaches them, using staggered timing.
- A narrow scan accent passes once through the heading rule during each loop.
- The panel itself does not translate, scale, bounce, flicker, or pulse as a whole.
- No rapid flashing, large blur blooms, or competing simultaneous loops are permitted.
- The signal remains visible at GitHub's normal profile width and does not rely on a one-time entrance animation.

Exact node delays may move by up to 150 milliseconds during implementation to make the route feel continuous. The total loop must remain between 5.8 and 6.2 seconds.

## Theme and Reduced-motion Variants

Four repository-owned SVG assets are required:

- `engineering-stack-dark.svg`
- `engineering-stack-light.svg`
- `engineering-stack-dark-static.svg`
- `engineering-stack-light-static.svg`

README uses a `<picture>` element with motion preference evaluated before theme preference, matching the existing profile pattern. Visitors with `prefers-reduced-motion: reduce` receive a fully static theme-appropriate asset.

Static variants:

- contain no CSS animation or transition declarations;
- contain no executable SMIL animation elements;
- show the complete route and every node in a meaningful resting state;
- preserve the same labels, layout, contrast, title, and description as the animated variants.

## Accessibility and Responsive Behavior

- Every SVG includes a concise `<title>` and `<desc>`.
- README provides descriptive alternative text that names the engineering stack rather than saying only "image" or "banner".
- Light and dark text, borders, and primary node states meet normal-text contrast expectations where applicable.
- The 960 × 300 composition remains readable when scaled to the GitHub profile column and a narrow mobile viewport.
- Essential labels do not use animated opacity values that disappear at any point in the loop.
- The layout avoids text smaller than the existing Contribution Signal's secondary labels.

## Integration and Data Flow

The Engineering Stack is a stable profile asset, not a daily data visualization:

1. A deterministic repository script generates the four SVG variants from one approved layout definition.
2. Tests validate structure, dimensions, technology labels, animation timing, staticization, accessibility metadata, and runtime-reference safety.
3. Generated files are committed under `assets/` because they change only when the public technology scope changes.
4. README selects the correct variant through `<picture>`.
5. Existing Contribution Signal workflows continue generating and publishing their current output assets without modification.

The generator must produce byte-identical output for identical inputs. It must not fetch assets during generation or at README render time.

## Safety and Failure Handling

- Reject scripts, event handlers, remote URLs, CSS imports, embedded credentials, and non-approved data resources.
- Reject duplicate IDs and unresolved local fragment references.
- Keep the SVG self-contained and below the repository's existing generated-asset size boundary.
- Fail generation if a required group or technology label is missing.
- Do not silently substitute a third-party Skill Icons or Shields image when generation fails.
- A failure in the Engineering Stack generator must not alter or republish Contribution Signal output.

## Testing and Verification

### Automated checks

- Generator reproduces identical files for identical inputs.
- All four files parse as valid SVG/XML and use `viewBox="0 0 960 300"`.
- Every approved group and technology appears exactly once.
- No unapproved technology appears.
- Animated variants use a route loop between 5.8 and 6.2 seconds and retain visibly changing frames after the initial render.
- Static variants contain no executable CSS or SMIL motion.
- All variants contain matching accessible title and description content.
- All variants contain no remote runtime references.
- README contains the four-source `<picture>` selection in the approved order.
- Existing profile, signature, Star-history, Contribution Signal, SVG-security, and workflow tests continue to pass.

### Visual checks

- Render light and dark animated variants at multiple timestamps; confirm the signal moves and nodes illuminate in route order.
- Render static variants twice; confirm identical frames.
- Inspect at full width and a narrow mobile width for clipping, unreadable labels, or collapsed spacing.
- Compare the panel with the signature above and Contribution Signal below; the three assets must feel related without having equal visual intensity.

### GitHub checks

- Verify the branch README renders the correct light and dark sources on GitHub.
- Verify reduced-motion sources remain complete and static.
- Confirm Featured Work Star badges still load.
- Confirm the existing Star trend, 3D contribution city, and original contribution snake remain animated and unchanged.

## Publishing Strategy

- Work in an isolated worktree based on the latest `origin/main` so the stale local main checkout and its untracked files remain untouched.
- Implement on a `codex/` feature branch.
- Review generated assets and test output before publishing the branch.
- Merge through a pull request only after user approval.
- Do not change the `output` branch or run the Contribution Signal publication workflow as part of this feature unless verification uncovers an unrelated live regression.

## Alternatives Considered

### Skill Icons strip

This is easy to add and is recommended by the referenced guide, but it depends on a third-party renderer, looks similar to many other profiles, and does not communicate relationships between tools.

### Expanded Shields badge matrix

This is reliable and accessible, but it is only an incremental extension of the current section and does not match the custom visual quality of the rest of the profile.

### Generic profile statistics suite

GitHub Stats, streak, and trophy cards are valid profile widgets, but they repeat information already expressed more distinctly by Featured Work and Contribution Signal. Adding them would lengthen the profile and weaken the selected professional hierarchy.

## Acceptance Criteria

- The generic Shields technology row is replaced by one custom Engineering Stack panel.
- The panel presents exactly the approved public toolchain in BUILD, AUTOMATE, and VERIFY groups.
- The design visually aligns with the Alex signature and Contribution Signal while remaining quieter than the latter.
- Light, dark, animated, and reduced-motion variants are valid, accessible, responsive, and self-contained.
- Animated variants show a clear approximately 6-second engineering-route signal; static variants contain no executable motion.
- No third-party runtime image, font, script, stylesheet, stats, streak, trophy, or Skill Icons dependency is added.
- Featured Work, live Star badges, Star trend, 3D city, and original contribution snake are preserved.
- Existing test suites pass and GitHub renders all intended variants correctly.
