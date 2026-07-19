# Animated Contribution Signal V2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace nested data-URI assets with a top-level animated SVG composition that makes the 3D city, Star signal, and original Platane contribution snake larger and unmistakably dynamic on GitHub.

**Architecture:** Add a focused SVG namespace importer that rewrites imported IDs, classes, keyframes, custom properties, and local references before city and snake nodes enter the outer SVG DOM. Keep the existing composer and workflow interfaces, but render a `960 × 900` panel, normalize approved motion timings, and generate motion-free variants from the same imported sources.

**Tech Stack:** Python 3 standard library, `xml.etree.ElementTree`, regular expressions, GitHub-flavored Markdown, SVG/CSS/SMIL animation, GitHub Actions, `unittest`, Git, GitHub CLI

## Global Constraints

- Preserve one unified Contribution Signal panel.
- Preserve the original Platane contribution grid, snake path, and theme-specific cell colors.
- Keep stable README-facing filenames and the existing light/dark/reduced-motion `<picture>` selection.
- Use panel viewBox `0 0 960 900`.
- Use city viewport `x=88`, `y=110`, `width=784`, `height=520` with source viewBox `0 0 1280 850`.
- Use snake viewport `x=42`, `y=695`, `width=876`, `height=191` with source viewBox `-16 -32 880 192`.
- Use dark city rainbow duration `6.5s`, light city sweep duration `6.5s`, active-building breath duration `3.25s`, city entrance duration `1.8s`, snake duration `8500ms`, trend draw duration `1.6s`, and trend signal duration `3.2s`.
- Animated outputs must not contain city or snake `data:image/svg+xml` payloads or remote runtime references.
- Static outputs must contain no SMIL animation elements and no CSS animation or transition declarations.
- Preserve the existing 2 MiB input/output limit and atomic `output` branch publication.
- Do not change profile content outside Contribution Signal.
- Use test-first development and commit each independently reviewable task.

## File Map

- Create `scripts/svg_namespace.py`: parse and namespace one validated SVG document for safe insertion into another SVG DOM.
- Create `tests/test_svg_namespace.py`: focused namespacing, reference-integrity, and rejection tests.
- Modify `scripts/compose_contribution_signal.py`: replace data-URI embedding, position imported DOMs, normalize motion, and render the Star signal.
- Modify `tests/test_compose_contribution_signal.py`: layout, flattening, timing, staticization, and upstream-drift contract tests.
- Modify `tests/verify_profile.py`: assert the stable README contract and top-level composer architecture without changing README copy.
- Do not modify `README.md` or `.github/workflows/generate-profile-assets.yml` unless a failing contract proves that the stable invocation cannot be preserved.

---

### Task 1: Safe SVG namespace importer

**Files:**
- Create: `scripts/svg_namespace.py`
- Create: `tests/test_svg_namespace.py`

**Interfaces:**
- Consumes: a UTF-8 SVG source string already accepted by `validate_svg_source` and a lowercase namespace prefix.
- Produces: `namespace_svg(source: str, prefix: str) -> xml.etree.ElementTree.Element`.
- Guarantees: the returned root has ID `<prefix>-root`; imported IDs, classes, CSS keyframes, custom properties, fragment URLs, hrefs, and SMIL timing references are namespaced; no unresolved old local references remain.

- [ ] **Step 1: Write the failing namespace and reference-integrity tests**

Create `tests/test_svg_namespace.py` with a fixture that exercises every required reference type:

```python
import unittest
import xml.etree.ElementTree as ET

from scripts.svg_namespace import namespace_svg


SVG = "http://www.w3.org/2000/svg"


class SvgNamespaceTests(unittest.TestCase):
    def sample(self) -> str:
        return f'''<svg xmlns="{SVG}" viewBox="0 0 100 40">
          <style>
            :root{{--tone:#8250df}}
            .tile{{fill:var(--tone);animation:pulse 10s linear infinite}}
            #layer{{filter:url(#glow)}}
            @keyframes pulse{{from{{opacity:.8}}to{{opacity:1}}}}
          </style>
          <defs><filter id="glow"/></defs>
          <g id="layer" class="tile">
            <animate attributeName="opacity" begin="layer.end" dur="1s"/>
            <use href="#layer"/>
          </g>
        </svg>'''

    def test_namespaces_css_dom_and_local_references(self) -> None:
        root = namespace_svg(self.sample(), "city")
        source = ET.tostring(root, encoding="unicode")
        self.assertEqual(root.attrib["id"], "city-root")
        for expected in (
            'id="city-layer"',
            'id="city-glow"',
            'class="city-tile"',
            '@keyframes city-pulse',
            'animation:city-pulse 10s',
            '--city-tone',
            'var(--city-tone)',
            'url(#city-glow)',
            'href="#city-layer"',
            'begin="city-layer.end"',
            '#city-layer',
        ):
            self.assertIn(expected, source)

    def test_rejects_invalid_prefix(self) -> None:
        with self.assertRaisesRegex(ValueError, "prefix"):
            namespace_svg(self.sample(), "City Signal")

    def test_rejects_duplicate_ids_before_rewrite(self) -> None:
        source = f'<svg xmlns="{SVG}"><g id="x"/><g id="x"/></svg>'
        with self.assertRaisesRegex(ValueError, "duplicate SVG id: x"):
            namespace_svg(source, "city")

    def test_preserves_viewbox_and_removes_fixed_dimensions(self) -> None:
        source = f'<svg xmlns="{SVG}" viewBox="0 0 100 40" width="100" height="40"/>'
        root = namespace_svg(source, "snake")
        self.assertEqual(root.attrib["viewBox"], "0 0 100 40")
        self.assertNotIn("width", root.attrib)
        self.assertNotIn("height", root.attrib)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the new tests and confirm the missing-module failure**

```bash
python3 -m unittest -v tests/test_svg_namespace.py
```

Expected: FAIL with `ModuleNotFoundError: No module named 'scripts.svg_namespace'`.

- [ ] **Step 3: Implement the minimal importer**

Create `scripts/svg_namespace.py` with these public and private interfaces:

```python
import re
import xml.etree.ElementTree as ET


PREFIX = re.compile(r"^[a-z][a-z0-9-]*$")
KEYFRAME = re.compile(r"(@(?:-[a-z]+-)?keyframes\s+)([-_A-Za-z][-_A-Za-z0-9]*)", re.I)
CUSTOM_PROPERTY = re.compile(r"--([-_A-Za-z][-_A-Za-z0-9]*)")


def local_name(name: str) -> str:
    return name.rsplit("}", 1)[-1].lower()


def namespace_svg(source: str, prefix: str) -> ET.Element:
    if not PREFIX.fullmatch(prefix):
        raise ValueError(f"invalid SVG namespace prefix: {prefix}")
    root = ET.fromstring(source)
    ids = [element.attrib["id"] for element in root.iter() if "id" in element.attrib]
    duplicate = next((value for value in ids if ids.count(value) > 1), None)
    if duplicate:
        raise ValueError(f"duplicate SVG id: {duplicate}")

    classes = {
        token
        for element in root.iter()
        for token in element.attrib.get("class", "").split()
    }
    styles = [element for element in root.iter() if local_name(element.tag) == "style"]
    keyframes = {
        match.group(2)
        for style in styles
        for match in KEYFRAME.finditer(style.text or "")
    }
    custom_properties = {
        match.group(1)
        for style in styles
        for match in CUSTOM_PROPERTY.finditer(style.text or "")
    }

    id_map = {value: f"{prefix}-{value}" for value in ids}
    class_map = {value: f"{prefix}-{value}" for value in classes}
    keyframe_map = {value: f"{prefix}-{value}" for value in keyframes}
    property_map = {value: f"{prefix}-{value}" for value in custom_properties}

    for element in root.iter():
        if "id" in element.attrib:
            element.attrib["id"] = id_map[element.attrib["id"]]
        if "class" in element.attrib:
            element.attrib["class"] = " ".join(
                class_map[token] for token in element.attrib["class"].split()
            )
        for name, value in list(element.attrib.items()):
            element.attrib[name] = _rewrite_value(value, id_map)
        if local_name(element.tag) == "style":
            element.text = _rewrite_css(
                element.text or "", prefix, id_map, class_map, keyframe_map, property_map
            )

    root.attrib["id"] = f"{prefix}-root"
    root.attrib.pop("width", None)
    root.attrib.pop("height", None)
    _assert_reference_integrity(root, ids)
    return root
```

Use these complete helper implementations after `namespace_svg`:

```python
IDENTIFIER = r"[-_A-Za-z0-9]"


def _ordered(mapping: dict[str, str]):
    return sorted(mapping.items(), key=lambda item: len(item[0]), reverse=True)


def _rewrite_value(value: str, id_map: dict[str, str]) -> str:
    rewritten = value
    for old, new in _ordered(id_map):
        rewritten = re.sub(
            rf"(?<=#){re.escape(old)}(?!{IDENTIFIER})",
            new,
            rewritten,
        )
        rewritten = re.sub(
            rf"(?<!{IDENTIFIER}){re.escape(old)}(?=\.(?:begin|end|click|repeat))",
            new,
            rewritten,
        )
    return rewritten


def _rewrite_css(
    css: str,
    prefix: str,
    id_map: dict[str, str],
    class_map: dict[str, str],
    keyframe_map: dict[str, str],
    property_map: dict[str, str],
) -> str:
    rewritten = re.sub(r"(?<![-_A-Za-z0-9]):root(?![-_A-Za-z0-9])", f"#{prefix}-root", css)
    for old, new in _ordered(class_map):
        rewritten = re.sub(
            rf"(?<=\.){re.escape(old)}(?!{IDENTIFIER})", new, rewritten
        )
    for old, new in _ordered(id_map):
        rewritten = re.sub(
            rf"(?<=#){re.escape(old)}(?!{IDENTIFIER})", new, rewritten
        )
    for old, new in _ordered(keyframe_map):
        rewritten = re.sub(
            rf"(?<!{IDENTIFIER}){re.escape(old)}(?!{IDENTIFIER})", new, rewritten
        )
    for old, new in _ordered(property_map):
        rewritten = re.sub(
            rf"--{re.escape(old)}(?!{IDENTIFIER})", f"--{new}", rewritten
        )
    return rewritten


def _assert_reference_integrity(root: ET.Element, old_ids: list[str]) -> None:
    source = ET.tostring(root, encoding="unicode")
    for old in sorted(old_ids, key=len, reverse=True):
        fragments = (
            rf"#{re.escape(old)}(?!{IDENTIFIER})",
            rf"(?<!{IDENTIFIER}){re.escape(old)}(?=\.(?:begin|end|click|repeat))",
        )
        if any(re.search(pattern, source) for pattern in fragments):
            raise ValueError(f"unresolved local SVG reference: {old}")
```

These helpers rewrite `:root`, class and ID selectors, keyframe declarations and animation-name occurrences, custom-property declarations/usages, `url(#...)`, exact fragment hrefs, and SMIL `id.begin`/`id.end` references.

- [ ] **Step 4: Run focused and security tests**

```bash
python3 -m unittest -v \
  tests/test_svg_namespace.py \
  tests/test_validate_profile_assets.py
```

Expected: all namespace tests and existing SVG-security tests PASS.

- [ ] **Step 5: Commit the importer**

```bash
git add scripts/svg_namespace.py tests/test_svg_namespace.py
git commit -m "feat: add safe svg namespace importer"
```

---

### Task 2: Flatten city and snake into the outer SVG and correct layout

**Files:**
- Modify: `scripts/compose_contribution_signal.py`
- Modify: `tests/test_compose_contribution_signal.py`

**Interfaces:**
- Consumes: `namespace_svg(source: str, prefix: str) -> ET.Element` from Task 1.
- Produces: `position_imported_svg(root: ET.Element, *, x: int, y: int, width: int, height: int) -> str` and flattened animated/static output documents.
- Preserves: `compose(...) -> str`, `compose_all(...) -> None`, and both CLI entry points.

- [ ] **Step 1: Replace old payload assertions with failing flattening and layout assertions**

In `tests/test_compose_contribution_signal.py`, change the main composition test to assert:

```python
source = path.read_text(encoding="utf-8")
self.assertNotIn("data:image/svg+xml", source)
root = ET.fromstring(source)
self.assertEqual(root.attrib["viewBox"], "0 0 960 900")

city = next(element for element in root.iter() if element.attrib.get("id") == "city-root")
snake = next(element for element in root.iter() if element.attrib.get("id") == "snake-root")
self.assertEqual(
    {key: city.attrib[key] for key in ("x", "y", "width", "height")},
    {"x": "88", "y": "110", "width": "784", "height": "520"},
)
self.assertEqual(
    {key: snake.attrib[key] for key in ("x", "y", "width", "height")},
    {"x": "42", "y": "695", "width": "876", "height": "191"},
)
self.assertIn("ORIGINAL-CITY-", source)
self.assertIn("ORIGINAL-SNAKE-", source)
```

Add a test that the Star card is exactly `x=650`, `y=18`, `width=282`, `height=70`, and the outer border is `width=958`, `height=898`.

- [ ] **Step 2: Run the focused test and confirm the old architecture fails**

```bash
python3 -m unittest -v \
  tests.test_compose_contribution_signal.ContributionSignalComposerTests.test_composes_byte_preserving_animated_and_valid_static_theme_variants
```

Expected: FAIL because the output still contains `data:image/svg+xml` and `viewBox="0 0 960 660"`.

- [ ] **Step 3: Implement top-level insertion and approved coordinates**

Extend the composer's existing package/direct-script import split so both supported CLI entry points can find the importer:

```python
if __package__:
    from scripts.svg_namespace import namespace_svg
else:
    from svg_namespace import namespace_svg


def position_imported_svg(
    root: ET.Element,
    *,
    x: int,
    y: int,
    width: int,
    height: int,
) -> str:
    root.attrib.update(
        {
            "x": str(x),
            "y": str(y),
            "width": str(width),
            "height": str(height),
            "preserveAspectRatio": "xMidYMid meet",
        }
    )
    return ET.tostring(root, encoding="unicode")
```

In `compose`, staticize source strings first when requested, then call:

```python
city_root = namespace_svg(city_source, "city")
snake_root = namespace_svg(snake_source, "snake")
city_markup = position_imported_svg(city_root, x=88, y=110, width=784, height=520)
snake_markup = position_imported_svg(snake_root, x=42, y=695, width=876, height=191)
```

Delete `data_uri`. Insert `city_markup` and `snake_markup` directly into the outer source. Change the outer viewBox and border to `960 × 900`, set the Star card to the approved `650/18/282/70` box, move the separator to `y=650`, and move the snake label baseline to `y=675`.

- [ ] **Step 4: Run composer and validator tests**

```bash
python3 -m unittest -v \
  tests/test_svg_namespace.py \
  tests/test_compose_contribution_signal.py \
  tests/test_validate_profile_assets.py
```

Expected: all tests PASS; no generated test output contains `data:image/svg+xml`.

- [ ] **Step 5: Commit the flattened layout**

```bash
git add scripts/compose_contribution_signal.py tests/test_compose_contribution_signal.py
git commit -m "feat: flatten and enlarge contribution signal assets"
```

---

### Task 3: Normalize city and snake motion and add the live Star signal

**Files:**
- Modify: `scripts/compose_contribution_signal.py`
- Modify: `tests/test_compose_contribution_signal.py`

**Interfaces:**
- Produces: `tune_city_motion(root: ET.Element, theme_name: str) -> None`.
- Produces: `tune_snake_motion(root: ET.Element) -> None`.
- Produces: immutable `TrendGeometry(points: str, motion_path: str, final_x: float, final_y: float, total: int, start_date: str)`.
- Raises: `ValueError` when expected upstream city or snake animation contracts are absent.

- [ ] **Step 1: Write failing timing, Star geometry, and drift tests**

Add these concrete tests and import `namespace_svg`, `trend_geometry`, `tune_city_motion`, and `tune_snake_motion`:

```python
def test_motion_uses_approved_durations_and_preserves_snake_percentages(self):
    city_source = f'''<svg xmlns="{SVG}">
      <style>
        .rb-l1-top{{animation:rb-l1-top 10s linear infinite}}
        @keyframes rb-l1-top{{0%{{fill:red}}100%{{fill:blue}}}}
      </style>
      <rect class="rb-l1-top">
        <animate attributeName="height" values="2;10" dur="3s"/>
      </rect>
    </svg>'''
    snake_source = f'''<svg xmlns="{SVG}">
      <style>
        .c{{animation:none 18500ms linear infinite}}
        @keyframes path{{62.69%{{fill:green}}62.71%{{fill:black}}}}
      </style>
    </svg>'''
    city = namespace_svg(city_source, "city")
    snake = namespace_svg(snake_source, "snake")
    tune_city_motion(city, "dark")
    tune_snake_motion(snake)
    city_text = ET.tostring(city, encoding="unicode")
    snake_text = ET.tostring(snake, encoding="unicode")
    self.assertIn("6.5s", city_text)
    self.assertIn('dur="1.8s"', city_text)
    self.assertIn("8500ms", snake_text)
    self.assertIn("62.69%", snake_text)

def test_single_snapshot_trend_has_a_repeating_signal_path(self):
    geometry = trend_geometry(self.sample_history())
    self.assertEqual(geometry.points, "700.0,55.0 910.0,55.0")
    self.assertEqual(geometry.motion_path, "M 700.0 55.0 L 910.0 55.0")
    self.assertEqual((geometry.final_x, geometry.final_y), (910.0, 55.0))

def test_rejects_upstream_snake_without_shared_duration(self):
    root = ET.fromstring(f'<svg xmlns="{SVG}"><style>.c{{animation:x 5s}}</style></svg>')
    with self.assertRaisesRegex(ValueError, "18500ms"):
        tune_snake_motion(root)
```

Also assert the animated outer SVG contains a trend signal `<circle>` with an `<animateMotion dur="3.2s" repeatCount="indefinite">`, and the trend draw CSS contains `animation: draw 1.6s ease forwards`.

- [ ] **Step 2: Run focused tests and confirm old durations fail**

```bash
python3 -m unittest -v tests/test_compose_contribution_signal.py
```

Expected: FAIL because city remains 10 seconds, snake remains 18.5 seconds, and no moving Star signal exists.

- [ ] **Step 3: Implement deterministic motion normalization**

Add:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class TrendGeometry:
    points: str
    motion_path: str
    final_x: float
    final_y: float
    total: int
    start_date: str
```

`trend_geometry` builds both the polyline points and `M/L` motion path from the same coordinate list, preventing the signal dot from diverging from the visible line.

Implement it as:

```python
def trend_geometry(history: dict) -> TrendGeometry:
    snapshots = history["snapshots"]
    if not snapshots:
        raise ValueError("star history has no snapshots")
    totals = [sum(snapshot["repos"].values()) for snapshot in snapshots]
    minimum, maximum = min(totals), max(totals)
    span = max(maximum - minimum, 1)
    if len(totals) == 1:
        coordinates = [(700.0, 55.0), (910.0, 55.0)]
    else:
        denominator = len(totals) - 1
        coordinates = [
            (
                700 + (index / denominator) * 210,
                72 - ((total - minimum) / span) * 34,
            )
            for index, total in enumerate(totals)
        ]
    points = " ".join(f"{x:.1f},{y:.1f}" for x, y in coordinates)
    motion_path = " ".join(
        ("M" if index == 0 else "L") + f" {x:.1f} {y:.1f}"
        for index, (x, y) in enumerate(coordinates)
    )
    final_x, final_y = coordinates[-1]
    return TrendGeometry(
        points=points,
        motion_path=motion_path,
        final_x=final_x,
        final_y=final_y,
        total=totals[-1],
        start_date=snapshots[0]["date"],
    )
```

`tune_snake_motion` must replace every `18500ms` occurrence in imported `<style>` text with `8500ms`, require at least one replacement, and leave all percentage keyframes byte-for-byte unchanged.

`tune_city_motion` must:

- replace every dark-city `10s` rainbow duration with `6.5s` and require at least one replacement for the dark theme;
- replace city entrance SMIL `dur="3s"` with `dur="1.8s"` for `height`, `transform`, `points`, and `fill-opacity` animations;
- find active contribution elements by imported class tokens ending in `cont-*-1` through `cont-*-4` or `rb-l1-*` through `rb-l4-*`;
- append an opacity `<animate values="0.88;1;0.88" dur="3.25s" repeatCount="indefinite">` to active elements;
- for light theme only, append a staggered `<animate attributeName="fill-opacity" values="0.65;1;0.65" dur="6.5s" repeatCount="indefinite">` whose negative begin offset is derived from the element index modulo 24.

Implement both tuners with explicit upstream-contract counts:

```python
SVG_NAMESPACE = "http://www.w3.org/2000/svg"
ACTIVE_CITY_CLASS = re.compile(
    r"city-(?:cont-(?:top|left|right)-[1-4]|rb-l[1-4]-(?:top|left|right))$"
)


def tune_snake_motion(root: ET.Element) -> None:
    replacements = 0
    for element in root.iter():
        if local_name(element.tag) != "style":
            continue
        element.text, count = re.subn(r"(?<![0-9])18500ms(?![0-9])", "8500ms", element.text or "")
        replacements += count
    if replacements == 0:
        raise ValueError("upstream snake CSS no longer contains 18500ms")


def _append_smil(element: ET.Element, **attributes: str) -> None:
    ET.SubElement(element, f"{{{SVG_NAMESPACE}}}animate", attributes)


def tune_city_motion(root: ET.Element, theme_name: str) -> None:
    rainbow_replacements = 0
    entrance_replacements = 0
    active = []
    for element in root.iter():
        if local_name(element.tag) == "style" and theme_name == "dark":
            element.text, count = re.subn(
                r"(?<![0-9.])10s(?![0-9.])", "6.5s", element.text or ""
            )
            rainbow_replacements += count
        if (
            local_name(element.tag) in SMIL_LOCAL_NAMES
            and element.attrib.get("dur") == "3s"
            and element.attrib.get("attributeName")
            in {"height", "transform", "points", "fill-opacity"}
        ):
            element.attrib["dur"] = "1.8s"
            entrance_replacements += 1
        if any(ACTIVE_CITY_CLASS.fullmatch(token) for token in element.attrib.get("class", "").split()):
            active.append(element)
    if theme_name == "dark" and rainbow_replacements == 0:
        raise ValueError("upstream dark city CSS no longer contains 10s")
    if entrance_replacements == 0:
        raise ValueError("upstream city SMIL no longer contains 3s entrance motion")
    if not active:
        raise ValueError("upstream city no longer exposes active contribution classes")
    for index, element in enumerate(active):
        phase = (index % 24) * (6.5 / 24)
        _append_smil(
            element,
            attributeName="opacity",
            values="0.88;1;0.88",
            dur="3.25s",
            begin=f"-{phase:.2f}s",
            repeatCount="indefinite",
        )
        if theme_name == "light":
            _append_smil(
                element,
                attributeName="fill-opacity",
                values="0.65;1;0.65",
                dur="6.5s",
                begin=f"-{phase:.2f}s",
                repeatCount="indefinite",
            )
```

Call motion tuning only for animated variants, after namespacing and before serialization.

Generate the animated Star signal as:

```xml
<circle id="signal-trend-dot" r="4" fill="THEME_TREND" filter="url(#signal-trend-glow)">
  <animateMotion path="GENERATED_PATH" dur="3.2s" repeatCount="indefinite"/>
</circle>
```

Keep the trend glow radius at or below 4 pixels.

- [ ] **Step 4: Run motion and namespace tests**

```bash
python3 -m unittest -v \
  tests/test_svg_namespace.py \
  tests/test_compose_contribution_signal.py
```

Expected: all tests PASS, including upstream-drift rejection.

- [ ] **Step 5: Commit motion changes**

```bash
git add scripts/compose_contribution_signal.py tests/test_compose_contribution_signal.py
git commit -m "feat: accelerate contribution signal motion"
```

---

### Task 4: Preserve complete reduced-motion outputs and harden contracts

**Files:**
- Modify: `scripts/compose_contribution_signal.py`
- Modify: `tests/test_compose_contribution_signal.py`
- Modify: `tests/verify_profile.py`

**Interfaces:**
- Preserves: `static_source(source: str) -> str` and four stable output filenames.
- Adds: static Star signal at `(TrendGeometry.final_x, TrendGeometry.final_y)` with no animation child.

- [ ] **Step 1: Write failing static-output and README-contract tests**

Add tests that compose all four variants and assert:

```python
for theme_name in ("light", "dark"):
    animated = output / f"contribution-signal-{theme_name}.svg"
    static = output / f"contribution-signal-{theme_name}-static.svg"
    self.assertNotEqual(animated.read_bytes(), static.read_bytes())
    self.assert_static_payload(static.read_text())
    root = ET.parse(static).getroot()
    signal = next(
        element for element in root.iter()
        if element.attrib.get("id") == "signal-trend-dot"
    )
    self.assertEqual(signal.attrib["cx"], "910.0")
    self.assertEqual(signal.attrib["cy"], "55.0")
    self.assertFalse(
        any(local_name(child.tag) == "animatemotion" for child in signal)
    )
```

Update `tests/verify_profile.py` to assert that README still lists reduced-motion dark/light sources before animated dark/light sources and still references exactly the four stable Contribution Signal filenames.

- [ ] **Step 2: Run focused static tests and confirm the missing static-dot failure**

```bash
python3 -m unittest -v \
  tests/test_compose_contribution_signal.py \
  tests/verify_profile.py
```

Expected: FAIL because the new static signal dot contract is not yet implemented.

- [ ] **Step 3: Implement the static Star state and post-transform validation**

When `static=True`, emit:

```xml
<circle id="signal-trend-dot" cx="FINAL_X" cy="FINAL_Y" r="4" fill="THEME_TREND"/>
```

When `static=False`, emit the same ID with `<animateMotion>` instead of fixed `cx/cy`.

After assembling every outer document:

1. call `validate_svg_source(source)`;
2. parse the final document;
3. reject duplicate IDs;
4. reject unresolved `url(#...)`, `href="#..."`, and SMIL timing references;
5. verify imported roots `city-root` and `snake-root` each appear exactly once.

Add and call this final integrity gate after `validate_svg_source(source)`:

```python
LOCAL_FRAGMENT = re.compile(r"url\(\s*#([A-Za-z_][\w:.-]*)\s*\)")
SMIL_TARGET = re.compile(
    r"(?<![-_A-Za-z0-9])([-_A-Za-z][-_A-Za-z0-9]*)(?=\.(?:begin|end|click|repeat))"
)


def assert_composed_integrity(source: str) -> None:
    root = ET.fromstring(source)
    ids = [element.attrib["id"] for element in root.iter() if "id" in element.attrib]
    duplicate = next((value for value in ids if ids.count(value) > 1), None)
    if duplicate:
        raise ValueError(f"duplicate composed SVG id: {duplicate}")
    known = set(ids)
    referenced = set()
    for element in root.iter():
        for name, value in element.attrib.items():
            referenced.update(LOCAL_FRAGMENT.findall(value))
            if local_name(name) == "href" and value.startswith("#"):
                referenced.add(value[1:])
            if local_name(name) in {"begin", "end"}:
                referenced.update(SMIL_TARGET.findall(value))
        if local_name(element.tag) == "style":
            referenced.update(LOCAL_FRAGMENT.findall(element.text or ""))
    missing = sorted(referenced - known)
    if missing:
        raise ValueError(f"unresolved composed SVG reference: {missing[0]}")
    for required in ("city-root", "snake-root"):
        if ids.count(required) != 1:
            raise ValueError(f"composed SVG requires exactly one {required}")
```

Do not weaken existing static CSS/SMIL stripping or the first-keyframe city fallback.

- [ ] **Step 4: Run the full unit suite and both CLI entry points**

```bash
python3 -m unittest -v \
  tests/verify_profile.py \
  tests/test_signature_asset.py \
  tests/test_profile_star_history.py \
  tests/test_svg_namespace.py \
  tests/test_compose_contribution_signal.py \
  tests/test_validate_profile_assets.py
python3 -m scripts.compose_contribution_signal --help
python3 scripts/compose_contribution_signal.py --help
git diff --check
```

Expected: all tests PASS, both help commands exit 0, and `git diff --check` prints nothing.

- [ ] **Step 5: Commit reduced-motion and contract hardening**

```bash
git add scripts/compose_contribution_signal.py tests/test_compose_contribution_signal.py tests/verify_profile.py
git commit -m "test: harden animated signal contracts"
```

---

### Task 5: Real-asset rendering and visual motion verification

**Files:**
- Modify only if verification exposes a defect: `scripts/compose_contribution_signal.py`, `scripts/svg_namespace.py`, or their focused tests.
- Generate ignored scratch artifacts under: `.tmp/animated-signal-v2/`

**Interfaces:**
- Consumes: exact `origin/output` city, snake, and Star-history assets.
- Produces: four locally generated Contribution Signal SVGs and paired frame captures for animated/static verification.

- [ ] **Step 1: Fetch and extract the current output branch into scratch space**

```bash
git fetch origin output
mkdir -p .tmp/animated-signal-v2/source .tmp/animated-signal-v2/rendered
git archive origin/output | tar -x -C .tmp/animated-signal-v2/source
```

Expected: source directory contains light/dark city, light/dark snake, and `star-history.json`.

- [ ] **Step 2: Compose and validate all real-asset variants**

```bash
python3 scripts/compose_contribution_signal.py \
  --city-light .tmp/animated-signal-v2/source/profile-3d-light.svg \
  --city-dark .tmp/animated-signal-v2/source/profile-3d-dark.svg \
  --snake-light .tmp/animated-signal-v2/source/contribution-snake-light.svg \
  --snake-dark .tmp/animated-signal-v2/source/contribution-snake-dark.svg \
  --history .tmp/animated-signal-v2/source/star-history.json \
  --output-dir .tmp/animated-signal-v2/rendered
python3 scripts/validate_profile_assets.py .tmp/animated-signal-v2/rendered/*.svg
```

Expected: four valid SVGs, each below 2 MiB; animated files contain no data URI; static files contain no SMIL/CSS motion.

- [ ] **Step 3: Prove persistent animation and static stability with browser frames**

Use the Browser skill against a local HTTP server rooted at `.tmp/animated-signal-v2/rendered`.

For each animated theme:

1. capture a full-panel PNG after the 1.8-second entrance completes;
2. wait 3.4 seconds;
3. capture a second PNG;
4. compute SHA-256 hashes and require them to differ.

For each static theme, repeat the same pair and require identical hashes. Save captures in `.tmp/animated-signal-v2/frames/` and inspect light/dark animated second frames visually.

Expected visual result: city uses the full 784 × 520 viewport, snake uses the full 876 × 191 viewport, no text or chart is clipped, inactive cells do not glow, and the Star signal remains smaller than the Star total text.

- [ ] **Step 4: If verification finds a defect, reproduce it with a failing test before fixing**

Add the narrowest failing test to `tests/test_svg_namespace.py` or `tests/test_compose_contribution_signal.py`, run it to confirm RED, implement one minimal fix, and rerun Task 4 plus Steps 2–3 of this task. Commit only after the real-asset defect is gone:

```bash
git add scripts/svg_namespace.py scripts/compose_contribution_signal.py tests/test_svg_namespace.py tests/test_compose_contribution_signal.py
git commit -m "fix: correct real contribution signal rendering"
```

Skip this commit when no defect is found.

- [ ] **Step 5: Record verification evidence without committing scratch files**

```bash
git status --short
git diff --check
```

Expected: `.tmp/` artifacts remain ignored; source worktree is clean after any required fix commit.

---

### Task 6: Safe review, publication, and public-profile verification

**Files:**
- No source changes expected.

**Interfaces:**
- Consumes: clean `codex/animated-signal` branch with all tests and real-asset checks passing.
- Produces: Draft PR first; live `output` and `main` changes only after explicit final publication approval.

- [ ] **Step 1: Run the final pre-push verification gate**

```bash
python3 -m unittest -v \
  tests/verify_profile.py \
  tests/test_signature_asset.py \
  tests/test_profile_star_history.py \
  tests/test_svg_namespace.py \
  tests/test_compose_contribution_signal.py \
  tests/test_validate_profile_assets.py
git diff --check
git status --short --branch
```

Expected: zero failures, no diff-check output, and a clean branch.

- [ ] **Step 2: Push the feature branch and open a Draft PR**

```bash
git push -u origin codex/animated-signal
gh pr create --draft \
  --base main \
  --head codex/animated-signal \
  --title "Make Contribution Signal visibly animated" \
  --body "Flattens city and snake SVGs into one top-level document, corrects their aspect-ratio viewports, accelerates approved motion, and preserves reduced-motion variants."
```

Do not dispatch the workflow from the feature branch: `output` is live and would change the public profile before final approval.

- [ ] **Step 3: Request explicit final publication approval**

Provide the Draft PR, test count, real-asset frame hashes, and light/dark preview captures. Wait for the exact publication decision before merging or changing `output`.

- [ ] **Step 4: After approval, merge and regenerate from `main`**

```bash
gh pr ready
gh pr merge --squash
git fetch origin main
gh workflow run generate-profile-assets.yml --ref main
```

Capture the new workflow run ID and verify its head SHA equals `origin/main`.

- [ ] **Step 5: Verify the live output branch and public README**

```bash
git fetch origin output
mkdir -p .tmp/animated-signal-v2/live-output
git archive origin/output | tar -x -C .tmp/animated-signal-v2/live-output
python3 scripts/validate_profile_assets.py .tmp/animated-signal-v2/live-output/*.svg
gh api repos/alexliluz/alexliluz/contents/README.md --jq .sha
git rev-parse origin/main:README.md
```

Expected: workflow succeeds, all live SVGs validate, API README blob equals `origin/main:README.md`, and GitHub's rendered README contains the four stable Contribution Signal sources.

- [ ] **Step 6: Perform final public visual verification**

Verify the public profile in light and dark themes. Confirm obvious persistent city motion after the entrance, an 8.5-second original snake traversal, the 3.2-second Star signal, correct enlarged proportions, no clipping, and static behavior when reduced motion is enabled.
