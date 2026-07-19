# Profile Signature and Contribution Signal Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publish a handwritten `Alex` signature, technical positioning, live project Star badges, secure daily Star snapshots, and one theme-aware Contribution Signal that preserves the existing 3D city and original contribution-grid snake.

**Architecture:** Keep the profile static and repository-owned. A standard-library Python pipeline records public Star counts, embeds the existing generated city and Platane snake SVGs into one self-contained outer SVG, and publishes animated plus reduced-motion variants atomically to the `output` branch.

**Tech Stack:** GitHub-flavored Markdown, SVG, Python 3 standard library, FontTools 4.63.0 for one-time path generation, GitHub Actions, Shields.io, Platane/snk, github-profile-3d-contrib

## Global Constraints

- The visible signature text is exactly `Alex`; do not render the old `Hi, I'm Alex / ASEnough 👋` heading.
- The subtitle is exactly `BUILDING TOOLS THAT STAY INSPECTABLE`.
- The positioning copy leads with TypeScript, Python, Node.js, developer tooling, CLI automation, and reproducible systems; do not use `AI Coding` or the `AI Agents` badge.
- Keep exactly `planarian`, `ForkNeo`, and `api-image-neo` as featured repositories.
- Do not publish a plaintext or encrypted personal access token.
- Star snapshots begin on the deployment date and retain at most 730 UTC dates.
- Preserve the existing light/dark 3D city SVGs and the original light/dark Platane contribution-grid snake SVGs.
- Generate animated and reduced-motion light/dark Contribution Signal assets.
- Do not modify GitHub's native Pinned repositories or contribution calendar.
- Generated SVGs must be UTF-8 XML, contain no scripts or external HTTP image references, and stay below 2 MiB.
- Keep the workflow at `contents: write`, `timeout-minutes: 15`, commit-pinned actions, concurrency cancellation, and atomic output publication.

---

### Task 1: Build the deterministic Alex signature asset

**Files:**
- Create: `scripts/build_signature.py`
- Create: `tests/test_signature_asset.py`
- Create: `assets/alex-signature.svg` (generated)

**Interfaces:**
- Consumes: A local `Kalam-Bold.ttf` file and an output path
- Produces: `assets/alex-signature.svg`, a self-contained accessible SVG with path-outlined `Alex`

- [ ] **Step 1: Add the failing signature asset contract**

Create `tests/test_signature_asset.py`:

```python
import re
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SIGNATURE = ROOT / "assets" / "alex-signature.svg"
SVG_NAMESPACE = "{http://www.w3.org/2000/svg}"


class SignatureAssetTests(unittest.TestCase):
    def test_signature_is_accessible_responsive_and_self_contained(self) -> None:
        self.assertTrue(SIGNATURE.is_file())
        root = ET.parse(SIGNATURE).getroot()
        self.assertEqual(root.tag, f"{SVG_NAMESPACE}svg")
        self.assertEqual(root.attrib.get("viewBox"), "0 0 960 220")
        self.assertEqual(root.attrib.get("role"), "img")
        self.assertEqual(root.attrib.get("aria-labelledby"), "title description")
        self.assertTrue(root.find(f"{SVG_NAMESPACE}title").text.strip())
        self.assertTrue(root.find(f"{SVG_NAMESPACE}desc").text.strip())

        source = SIGNATURE.read_text(encoding="utf-8")
        for fragment in (
            "Alex",
            "BUILDING TOOLS THAT STAY INSPECTABLE",
            "#F0F6FC",
            "#6D28D9",
            "#FF7B72",
            "#24292F",
            "#8250DF",
            "#CF222E",
            "prefers-color-scheme: light",
            "Generated from Kalam Bold",
        ):
            self.assertIn(fragment, source)
        self.assertGreaterEqual(source.count("<path"), 4)
        self.assertNotRegex(source, r'(?:href|src)=["\']https?://')
        self.assertNotIn("<script", source.lower())

    def test_primary_signature_is_outlined_instead_of_live_text(self) -> None:
        source = SIGNATURE.read_text(encoding="utf-8")
        self.assertIn('id="signature-outline"', source)
        self.assertNotRegex(source, r"<text[^>]*>\s*Alex\s*</text>")


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the test and confirm the missing asset fails**

Run:

```bash
python3 -m unittest -v tests/test_signature_asset.py
```

Expected: failure because `assets/alex-signature.svg` does not exist.

- [ ] **Step 3: Add the deterministic font-to-path generator**

Create `scripts/build_signature.py`:

```python
#!/usr/bin/env python3
import argparse
from pathlib import Path
from xml.sax.saxutils import escape

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont


WORD = "Alex"
SUBTITLE = "BUILDING TOOLS THAT STAY INSPECTABLE"


def outlined_word(font_path: Path, word: str) -> tuple[str, float]:
    font = TTFont(font_path)
    glyph_set = font.getGlyphSet()
    cmap = font.getBestCmap()
    metrics = font["hmtx"].metrics
    x_offset = 0
    paths = []
    for character in word:
        glyph_name = cmap.get(ord(character))
        if glyph_name is None:
            raise ValueError(f"font has no glyph for {character!r}")
        pen = SVGPathPen(glyph_set)
        glyph_set[glyph_name].draw(pen)
        paths.append(
            f'<path d="{escape(pen.getCommands())}" '
            f'transform="translate({x_offset} 0)"/>'
        )
        x_offset += metrics[glyph_name][0]
    return "".join(paths), float(x_offset)


def build_svg(font_path: Path) -> str:
    paths, advance = outlined_word(font_path, WORD)
    target_width = 330.0
    scale = target_width / advance
    x_origin = (960.0 - target_width) / 2.0
    transform = f"translate({x_origin:.3f} 132) scale({scale:.7f} {-scale:.7f})"
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 220" role="img" aria-labelledby="title description">
  <title id="title">Alex — building tools that stay inspectable</title>
  <desc id="description">Handwritten Alex signature above a technical engineering motto.</desc>
  <!-- Generated from Kalam Bold, licensed under the SIL Open Font License 1.1. -->
  <style>
    .signature {{ fill: #F0F6FC; }}
    .shadow {{ fill: #6D28D9; }}
    .subtitle {{ fill: #FF7B72; }}
    @media (prefers-color-scheme: light) {{
      .signature {{ fill: #24292F; }}
      .shadow {{ fill: #8250DF; }}
      .subtitle {{ fill: #CF222E; }}
    }}
  </style>
  <defs><g id="signature-outline">{paths}</g></defs>
  <g class="shadow" transform="translate(7 7)"><use href="#signature-outline" transform="{transform}"/></g>
  <g class="signature"><use href="#signature-outline" transform="{transform}"/></g>
  <text class="subtitle" x="480" y="190" text-anchor="middle" font-family="ui-monospace, SFMono-Regular, Menlo, monospace" font-size="24" font-weight="600" letter-spacing="5">{SUBTITLE}</text>
</svg>
'''


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--font", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    arguments = parser.parse_args()
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(build_svg(arguments.font), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Generate the committed SVG from the pinned font tooling**

Run:

```bash
python3 -m venv .tmp/fonttools
.tmp/fonttools/bin/pip install fonttools==4.63.0
curl -fsSL https://raw.githubusercontent.com/google/fonts/main/ofl/kalam/Kalam-Bold.ttf \
  -o .tmp/Kalam-Bold.ttf
printf '%s  %s\n' \
  2f6576601db015d4f6c08678120277fc8510b98c06e932ce7a6a9cbff4cbdded \
  .tmp/Kalam-Bold.ttf | shasum -a 256 -c -
.tmp/fonttools/bin/python scripts/build_signature.py \
  --font .tmp/Kalam-Bold.ttf \
  --output assets/alex-signature.svg
```

Expected: checksum reports `OK` and `assets/alex-signature.svg` is created.

- [ ] **Step 5: Run the asset contract**

Run:

```bash
python3 -m unittest -v tests/test_signature_asset.py
```

Expected: two tests pass.

- [ ] **Step 6: Commit the signature asset**

```bash
git add scripts/build_signature.py tests/test_signature_asset.py assets/alex-signature.svg
git commit -m "feat: add Alex signature banner"
```

---

### Task 2: Record secure daily Star snapshots

**Files:**
- Create: `scripts/profile_star_history.py`
- Create: `tests/test_profile_star_history.py`

**Interfaces:**
- Produces: `load_history(path) -> dict`, `fetch_star_counts(owner, repositories, token) -> dict[str, int]`, `update_history(history, snapshot_date, counts) -> dict`, and a CLI that writes version-1 JSON
- Consumed by: the profile asset workflow and Contribution Signal composer

- [ ] **Step 1: Add failing Star-history tests**

Create `tests/test_profile_star_history.py`:

```python
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.profile_star_history import (
    REPOSITORIES,
    fetch_star_counts,
    load_history,
    update_history,
)


class Response:
    def __init__(self, payload: dict):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def read(self) -> bytes:
        return json.dumps(self.payload).encode("utf-8")


class ProfileStarHistoryTests(unittest.TestCase):
    def test_missing_history_starts_with_version_one(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            history = load_history(Path(directory) / "missing.json")
        self.assertEqual(history, {"version": 1, "snapshots": []})

    def test_load_rejects_malformed_schema(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "history.json"
            path.write_text('{"version": 2, "snapshots": []}', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "version"):
                load_history(path)

    def test_same_day_update_is_idempotent_and_retention_is_bounded(self) -> None:
        snapshots = [
            {
                "date": f"2024-01-{(index % 28) + 1:02d}",
                "repos": {repository: index for repository in REPOSITORIES},
            }
            for index in range(730)
        ]
        history = {"version": 1, "snapshots": snapshots}
        counts = {"planarian": 1, "ForkNeo": 1, "api-image-neo": 0}
        updated = update_history(history, "2026-07-19", counts)
        updated = update_history(updated, "2026-07-19", counts)
        self.assertEqual(len(updated["snapshots"]), 730)
        self.assertEqual(updated["snapshots"][-1]["date"], "2026-07-19")
        self.assertEqual(
            sum(item["date"] == "2026-07-19" for item in updated["snapshots"]),
            1,
        )

    @patch("scripts.profile_star_history.urlopen")
    def test_fetches_public_counts_and_rejects_missing_counts(self, mocked) -> None:
        mocked.side_effect = [
            Response({"stargazers_count": 1}),
            Response({"stargazers_count": 1}),
            Response({"stargazers_count": 0}),
        ]
        self.assertEqual(
            fetch_star_counts("alexliluz", REPOSITORIES, "token"),
            {"planarian": 1, "ForkNeo": 1, "api-image-neo": 0},
        )
        mocked.side_effect = [Response({})]
        with self.assertRaisesRegex(ValueError, "stargazers_count"):
            fetch_star_counts("alexliluz", ("planarian",), "token")


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the tests and confirm the missing module fails**

Run:

```bash
python3 -m unittest -v tests/test_profile_star_history.py
```

Expected: import failure for `scripts.profile_star_history`.

- [ ] **Step 3: Implement the Star snapshot module and CLI**

Create `scripts/profile_star_history.py`:

```python
#!/usr/bin/env python3
import argparse
import json
import os
from copy import deepcopy
from datetime import date, timezone, datetime
from pathlib import Path
from urllib.request import Request, urlopen


REPOSITORIES = ("planarian", "ForkNeo", "api-image-neo")
MAX_SNAPSHOTS = 730


def validate_counts(counts: dict) -> dict[str, int]:
    if set(counts) != set(REPOSITORIES):
        raise ValueError("repo keys must exactly match configured repositories")
    normalized = {}
    for repository in REPOSITORIES:
        value = counts[repository]
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            raise ValueError(f"invalid star count for {repository}")
        normalized[repository] = value
    return normalized


def validate_history(history: dict) -> dict:
    if not isinstance(history, dict) or history.get("version") != 1:
        raise ValueError("history version must be 1")
    snapshots = history.get("snapshots")
    if not isinstance(snapshots, list):
        raise ValueError("history snapshots must be a list")
    for snapshot in snapshots:
        if not isinstance(snapshot, dict):
            raise ValueError("snapshot must be an object")
        date.fromisoformat(snapshot.get("date", ""))
        validate_counts(snapshot.get("repos", {}))
    return history


def load_history(path: Path) -> dict:
    if not path.is_file():
        return {"version": 1, "snapshots": []}
    try:
        history = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        raise ValueError(f"malformed history JSON: {error}") from error
    return validate_history(history)


def fetch_star_counts(
    owner: str,
    repositories: tuple[str, ...],
    token: str,
) -> dict[str, int]:
    if not token:
        raise ValueError("GITHUB_TOKEN is required")
    counts = {}
    for repository in repositories:
        request = Request(
            f"https://api.github.com/repos/{owner}/{repository}",
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {token}",
                "User-Agent": "alexliluz-profile-assets",
                "X-GitHub-Api-Version": "2026-03-10",
            },
        )
        with urlopen(request, timeout=20) as response:
            payload = json.loads(response.read().decode("utf-8"))
        count = payload.get("stargazers_count")
        if not isinstance(count, int) or isinstance(count, bool) or count < 0:
            raise ValueError(f"missing or invalid stargazers_count for {repository}")
        counts[repository] = count
    return counts


def update_history(history: dict, snapshot_date: str, counts: dict) -> dict:
    validate_history(history)
    date.fromisoformat(snapshot_date)
    normalized = validate_counts(counts)
    updated = deepcopy(history)
    updated["snapshots"] = [
        snapshot
        for snapshot in updated["snapshots"]
        if snapshot["date"] != snapshot_date
    ]
    updated["snapshots"].append({"date": snapshot_date, "repos": normalized})
    updated["snapshots"].sort(key=lambda item: item["date"])
    updated["snapshots"] = updated["snapshots"][-MAX_SNAPSHOTS:]
    return updated


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--history", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--owner", default="alexliluz")
    parser.add_argument("--date")
    arguments = parser.parse_args()
    snapshot_date = arguments.date or datetime.now(timezone.utc).date().isoformat()
    history = load_history(arguments.history)
    counts = fetch_star_counts(
        arguments.owner,
        REPOSITORIES,
        os.environ.get("GITHUB_TOKEN", ""),
    )
    updated = update_history(history, snapshot_date, counts)
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(
        json.dumps(updated, indent=2, sort_keys=False) + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run the Star-history tests**

Run:

```bash
python3 -m unittest -v tests/test_profile_star_history.py
```

Expected: four tests pass.

- [ ] **Step 5: Commit the secure Star snapshot pipeline**

```bash
git add scripts/profile_star_history.py tests/test_profile_star_history.py
git commit -m "feat: record profile star snapshots"
```

---

### Task 3: Compose and validate the unified Contribution Signal

**Files:**
- Create: `scripts/compose_contribution_signal.py`
- Create: `tests/test_compose_contribution_signal.py`
- Modify: `scripts/validate_profile_assets.py`
- Modify: `tests/test_validate_profile_assets.py`

**Interfaces:**
- Consumes: light/dark city SVG paths, light/dark Platane snake SVG paths, and version-1 Star history JSON
- Produces: four self-contained `contribution-signal-*.svg` files
- Extends: `validate_svg(path)` with script, external-reference, and 2 MiB checks

- [ ] **Step 1: Add failing composer tests**

Create `tests/test_compose_contribution_signal.py`:

```python
import base64
import json
import re
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

from scripts.compose_contribution_signal import compose_all


SVG = "http://www.w3.org/2000/svg"


class ContributionSignalComposerTests(unittest.TestCase):
    def write_svg(self, path: Path, marker: str, animated: bool = True) -> None:
        animation = (
            '<animate attributeName="opacity" values="0;1" dur="2s" '
            'repeatCount="indefinite"/>'
            if animated
            else ""
        )
        path.write_text(
            f'<svg xmlns="{SVG}" viewBox="0 0 100 40">'
            f'<style>.moving{{animation:pulse 2s infinite}}</style>'
            f'<text>{marker}</text><g class="moving">{animation}</g></svg>',
            encoding="utf-8",
        )

    def test_composes_animated_and_static_theme_variants(self) -> None:
        with tempfile.TemporaryDirectory() as directory_name:
            directory = Path(directory_name)
            city_light = directory / "city-light.svg"
            city_dark = directory / "city-dark.svg"
            snake_light = directory / "snake-light.svg"
            snake_dark = directory / "snake-dark.svg"
            self.write_svg(city_light, "ORIGINAL-CITY-LIGHT")
            self.write_svg(city_dark, "ORIGINAL-CITY-DARK")
            self.write_svg(snake_light, "ORIGINAL-SNAKE-LIGHT")
            self.write_svg(snake_dark, "ORIGINAL-SNAKE-DARK")
            history = directory / "star-history.json"
            history.write_text(
                json.dumps(
                    {
                        "version": 1,
                        "snapshots": [
                            {
                                "date": "2026-07-19",
                                "repos": {
                                    "planarian": 1,
                                    "ForkNeo": 1,
                                    "api-image-neo": 0,
                                },
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            output = directory / "output"
            compose_all(
                city_light,
                city_dark,
                snake_light,
                snake_dark,
                history,
                output,
            )

            expected = (
                "contribution-signal-light.svg",
                "contribution-signal-dark.svg",
                "contribution-signal-light-static.svg",
                "contribution-signal-dark-static.svg",
            )
            for name in expected:
                path = output / name
                self.assertTrue(path.is_file(), name)
                root = ET.parse(path).getroot()
                self.assertEqual(root.attrib["viewBox"], "0 0 960 660")
                source = path.read_text(encoding="utf-8")
                self.assertIn("CONTRIBUTION SIGNAL", source)
                self.assertIn("STAR TREND", source)
                self.assertIn("SNAPSHOTS FROM 2026-07-19", source)
                payloads = re.findall(
                    r"data:image/svg\+xml;base64,([A-Za-z0-9+/=]+)", source
                )
                self.assertEqual(len(payloads), 2)
                decoded = "\n".join(
                    base64.b64decode(payload).decode("utf-8")
                    for payload in payloads
                )
                self.assertIn("ORIGINAL-CITY", decoded)
                self.assertIn("ORIGINAL-SNAKE", decoded)
                if "-static" in name:
                    self.assertNotIn("<animate", decoded)
                    self.assertNotRegex(decoded, r"animation\s*:")
                else:
                    self.assertIn("<animate", decoded)

    def test_rejects_scripted_or_externally_referenced_inputs(self) -> None:
        with tempfile.TemporaryDirectory() as directory_name:
            directory = Path(directory_name)
            bad = directory / "bad.svg"
            bad.write_text(
                f'<svg xmlns="{SVG}"><script>alert(1)</script></svg>',
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "script"):
                compose_all(bad, bad, bad, bad, directory / "missing.json", directory)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Extend the validator tests with size, script, and external-reference cases**

Add to `GeneratedSvgValidatorTests` in `tests/test_validate_profile_assets.py`:

```python
def test_rejects_scripts_external_images_and_oversized_svg(self) -> None:
    with tempfile.TemporaryDirectory() as temporary_directory:
        directory = Path(temporary_directory)
        fixtures = (
            self.write_fixture(
                directory,
                "script.svg",
                '<svg xmlns="http://www.w3.org/2000/svg"><script>x()</script></svg>',
            ),
            self.write_fixture(
                directory,
                "external.svg",
                '<svg xmlns="http://www.w3.org/2000/svg">'
                '<image href="https://example.com/image.svg"/></svg>',
            ),
            self.write_fixture(
                directory,
                "large.svg",
                '<svg xmlns="http://www.w3.org/2000/svg"><desc>'
                + ("x" * (2 * 1024 * 1024))
                + "</desc></svg>",
            ),
        )
        for path in fixtures:
            with self.subTest(path=path), self.assertRaises(ValueError):
                validate_svg(path)
```

- [ ] **Step 3: Run the focused tests and confirm they fail**

Run:

```bash
python3 -m unittest -v \
  tests/test_compose_contribution_signal.py \
  tests/test_validate_profile_assets.py
```

Expected: composer import failure and new validator assertions fail.

- [ ] **Step 4: Implement the standard-library composer**

Create `scripts/compose_contribution_signal.py`:

```python
#!/usr/bin/env python3
import argparse
import base64
import html
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

from scripts.profile_star_history import load_history


SVG_TAG = "{http://www.w3.org/2000/svg}svg"
MAX_BYTES = 2 * 1024 * 1024
SMIL_PATTERN = re.compile(
    r"<(?:animate|animateMotion|animateTransform|set)\b[^>]*"
    r"(?:/>|>.*?</(?:animate|animateMotion|animateTransform|set)>)",
    re.IGNORECASE | re.DOTALL,
)
CSS_ANIMATION_PATTERN = re.compile(
    r"animation(?:-[a-z-]+)?\s*:[^;}]+;?",
    re.IGNORECASE,
)
EXTERNAL_REFERENCE_PATTERN = re.compile(
    r'(?:href|src)=["\']https?://',
    re.IGNORECASE,
)


THEMES = {
    "light": {
        "background": "#FFFFFF",
        "border": "#D0D7DE",
        "primary": "#24292F",
        "muted": "#57606A",
        "trend": "#CF222E",
    },
    "dark": {
        "background": "#080B12",
        "border": "#30363D",
        "primary": "#E6EDF3",
        "muted": "#8B949E",
        "trend": "#FF4F79",
    },
}


def read_safe_svg(path: Path) -> str:
    if not path.is_file():
        raise ValueError(f"missing SVG: {path}")
    source = path.read_text(encoding="utf-8")
    try:
        root = ET.fromstring(source)
    except ET.ParseError as error:
        raise ValueError(f"invalid SVG {path}: {error}") from error
    if root.tag != SVG_TAG:
        raise ValueError(f"not an SVG: {path}")
    if "<script" in source.lower():
        raise ValueError(f"script is forbidden in {path}")
    if EXTERNAL_REFERENCE_PATTERN.search(source):
        raise ValueError(f"external reference is forbidden in {path}")
    return source


def static_source(source: str) -> str:
    source = SMIL_PATTERN.sub("", source)
    return CSS_ANIMATION_PATTERN.sub("", source)


def data_uri(source: str) -> str:
    payload = base64.b64encode(source.encode("utf-8")).decode("ascii")
    return f"data:image/svg+xml;base64,{payload}"


def trend_points(history: dict) -> tuple[str, int, str]:
    snapshots = history["snapshots"]
    if not snapshots:
        raise ValueError("star history has no snapshots")
    totals = [sum(snapshot["repos"].values()) for snapshot in snapshots]
    minimum, maximum = min(totals), max(totals)
    span = max(maximum - minimum, 1)
    if len(totals) == 1:
        # Keep a visible baseline from the first deployment onward.
        points = ["700.0,55.0", "910.0,55.0"]
    else:
        denominator = len(totals) - 1
        points = []
        for index, total in enumerate(totals):
            x = 700 + (index / denominator) * 210
            y = 72 - ((total - minimum) / span) * 34
            points.append(f"{x:.1f},{y:.1f}")
    return " ".join(points), totals[-1], snapshots[0]["date"]


def compose(
    city_source: str,
    snake_source: str,
    history: dict,
    theme_name: str,
    static: bool,
) -> str:
    theme = THEMES[theme_name]
    if static:
        city_source = static_source(city_source)
        snake_source = static_source(snake_source)
    points, total, start_date = trend_points(history)
    animation_style = "" if static else """
      .trend { stroke-dasharray: 260; stroke-dashoffset: 260; animation: draw 3s ease forwards; }
      @keyframes draw { to { stroke-dashoffset: 0; } }
    """
    source = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 660" role="img" aria-labelledby="title description">
  <title id="title">Alex contribution signal</title>
  <desc id="description">Star trend, 3D contribution city, and original animated contribution-grid snake.</desc>
  <style>{animation_style}</style>
  <rect x="1" y="1" width="958" height="658" rx="18" fill="{theme['background']}" stroke="{theme['border']}" stroke-width="2"/>
  <text x="28" y="38" fill="{theme['primary']}" font-family="ui-monospace, monospace" font-size="15" font-weight="600" letter-spacing="3">CONTRIBUTION SIGNAL</text>
  <text x="28" y="58" fill="{theme['muted']}" font-family="ui-monospace, monospace" font-size="10" letter-spacing="1">PUBLIC ACTIVITY · DAILY</text>
  <rect x="680" y="18" width="252" height="70" rx="10" fill="{theme['background']}" stroke="{theme['border']}"/>
  <text x="696" y="37" fill="{theme['muted']}" font-family="ui-monospace, monospace" font-size="9" letter-spacing="1">STAR TREND</text>
  <text x="910" y="37" text-anchor="end" fill="#E3B341" font-family="ui-monospace, monospace" font-size="12">★ {total}</text>
  <polyline class="trend" points="{points}" fill="none" stroke="{theme['trend']}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
  <text x="696" y="82" fill="{theme['muted']}" font-family="ui-monospace, monospace" font-size="8">SNAPSHOTS FROM {html.escape(start_date)}</text>
  <text x="28" y="104" fill="{theme['muted']}" font-family="ui-monospace, monospace" font-size="9" letter-spacing="1">3D CONTRIBUTION CITY</text>
  <image x="20" y="110" width="920" height="350" preserveAspectRatio="xMidYMid meet" href="{data_uri(city_source)}"/>
  <line x1="28" y1="472" x2="932" y2="472" stroke="{theme['border']}"/>
  <text x="28" y="494" fill="{theme['muted']}" font-family="ui-monospace, monospace" font-size="9" letter-spacing="1">ORIGINAL CONTRIBUTION SNAKE</text>
  <image x="20" y="500" width="920" height="140" preserveAspectRatio="xMidYMid meet" href="{data_uri(snake_source)}"/>
</svg>
'''
    if len(source.encode("utf-8")) > MAX_BYTES:
        raise ValueError("composed SVG exceeds 2 MiB")
    ET.fromstring(source)
    return source


def compose_all(
    city_light: Path,
    city_dark: Path,
    snake_light: Path,
    snake_dark: Path,
    history_path: Path,
    output_directory: Path,
) -> None:
    history = load_history(history_path)
    sources = {
        "light": (read_safe_svg(city_light), read_safe_svg(snake_light)),
        "dark": (read_safe_svg(city_dark), read_safe_svg(snake_dark)),
    }
    output_directory.mkdir(parents=True, exist_ok=True)
    for theme_name, (city_source, snake_source) in sources.items():
        for static in (False, True):
            suffix = "-static" if static else ""
            path = output_directory / f"contribution-signal-{theme_name}{suffix}.svg"
            path.write_text(
                compose(city_source, snake_source, history, theme_name, static),
                encoding="utf-8",
            )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--city-light", required=True, type=Path)
    parser.add_argument("--city-dark", required=True, type=Path)
    parser.add_argument("--snake-light", required=True, type=Path)
    parser.add_argument("--snake-dark", required=True, type=Path)
    parser.add_argument("--history", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    arguments = parser.parse_args()
    compose_all(
        arguments.city_light,
        arguments.city_dark,
        arguments.snake_light,
        arguments.snake_dark,
        arguments.history,
        arguments.output_dir,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 5: Harden the generated SVG validator**

In `scripts/validate_profile_assets.py`, add these constants after `CREDENTIAL_PATTERN`:

```python
MAX_SVG_BYTES = 2 * 1024 * 1024
EXTERNAL_REFERENCE_PATTERN = re.compile(
    r'(?:href|src)=["\']https?://',
    re.IGNORECASE,
)
```

Add these checks after the empty-file check and after reading `source`:

```python
if path.stat().st_size > MAX_SVG_BYTES:
    raise ValueError("file exceeds 2 MiB")
```

```python
if "<script" in source.lower():
    raise ValueError("file contains script content")
if EXTERNAL_REFERENCE_PATTERN.search(source):
    raise ValueError("file contains an external HTTP reference")
```

- [ ] **Step 6: Run the composer and validator tests**

Run:

```bash
python3 -m unittest -v \
  tests/test_compose_contribution_signal.py \
  tests/test_validate_profile_assets.py
```

Expected: all composer and validator tests pass.

- [ ] **Step 7: Commit the composer and validation changes**

```bash
git add \
  scripts/compose_contribution_signal.py \
  scripts/validate_profile_assets.py \
  tests/test_compose_contribution_signal.py \
  tests/test_validate_profile_assets.py
git commit -m "feat: compose unified contribution signal"
```

---

### Task 4: Integrate the workflow and compact README

**Files:**
- Modify: `.github/workflows/generate-profile-assets.yml`
- Modify: `README.md`
- Modify: `tests/verify_profile.py`

**Interfaces:**
- Consumes: `assets/alex-signature.svg` and output-branch `contribution-signal-*.svg`
- Produces: the final GitHub profile composition and an atomic daily workflow that publishes source assets, composites, and `star-history.json`

- [ ] **Step 1: Replace the old README contract with the approved V4 contract**

In `tests/verify_profile.py`:

1. Add:

```python
SIGNATURE = ROOT / "assets" / "alex-signature.svg"
COMPOSER = ROOT / "scripts" / "compose_contribution_signal.py"
STAR_HISTORY = ROOT / "scripts" / "profile_star_history.py"
SIGNAL_ASSETS = (
    "contribution-signal-light.svg",
    "contribution-signal-dark.svg",
    "contribution-signal-light-static.svg",
    "contribution-signal-dark-static.svg",
)
```

2. Include `SIGNATURE`, `COMPOSER`, and `STAR_HISTORY` in `test_required_files_exist`.

3. Replace `test_compact_identity_sections_are_present_in_order` with:

```python
def test_v4_sections_and_positioning_are_present_in_order(self) -> None:
    text = self.read_readme()
    required = (
        "./assets/alex-signature.svg",
        "TypeScript / Python developer focused on developer tooling, "
        "CLI automation, and reproducible systems.",
        "## Tech stack",
        "## Featured work",
        "## Contribution Signal",
        "[Explore all repositories →]",
    )
    positions = [text.index(fragment) for fragment in required]
    self.assertEqual(positions, sorted(positions))
    self.assertIn(
        "主要使用 TypeScript、Python 与 Node.js，专注开发者工具、"
        "CLI 自动化和可复现工程工作流。",
        text,
    )
    for removed in (
        "# Hi, I'm Alex / ASEnough 👋",
        "AI Coding",
        "AI_Agents",
        "## About me",
        "## Neon Contribution City",
        "## Contribution Snake",
    ):
        self.assertNotIn(removed, text)
```

4. Replace `test_static_technology_badges_are_present` with:

```python
def test_four_technology_badges_and_three_star_badges_are_present(self) -> None:
    text = self.read_readme()
    for label in (
        "TypeScript-3178C6",
        "Python-3776AB",
        "Node.js-339933",
        "GitHub_Actions-2088FF",
    ):
        self.assertIn(f"https://img.shields.io/badge/{label}", text)
    self.assertEqual(text.count("https://img.shields.io/github/stars/"), 3)
    for repository in ("planarian", "ForkNeo", "api-image-neo"):
        self.assertIn(
            f"https://img.shields.io/github/stars/alexliluz/{repository}",
            text,
        )
```

5. Replace `test_featured_work_is_one_compact_line_with_three_owned_projects` with:

```python
def test_featured_work_keeps_three_owned_projects_with_star_badges(self) -> None:
    text = self.read_readme()
    repo_names = re.findall(
        r"https://github\.com/alexliluz/([A-Za-z0-9_.-]+)", text
    )
    self.assertEqual(repo_names, ["planarian", "ForkNeo", "api-image-neo"])
    for label, repository in (
        ("Planarian", "planarian"),
        ("ForkNeo", "ForkNeo"),
        ("api-image-neo", "api-image-neo"),
    ):
        self.assertIn(
            f"[{label}](https://github.com/alexliluz/{repository})",
            text,
        )
        self.assertIn(
            f"https://img.shields.io/github/stars/alexliluz/{repository}",
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

6. Replace `test_v3_dynamic_assets_are_theme_aware_and_repository_owned` with:

```python
def test_contribution_signal_is_single_theme_and_motion_aware_picture(self) -> None:
    text = self.read_readme()
    self.assertEqual(text.count("<picture>"), 1)
    self.assertEqual(text.count("</picture>"), 1)
    for asset in SIGNAL_ASSETS:
        self.assertIn(f"{GENERATED_ASSET_BASE}{asset}", text)
    self.assertIn(
        'media="(prefers-reduced-motion: reduce) and '
        '(prefers-color-scheme: dark)"',
        text,
    )
    self.assertIn(
        'media="(prefers-reduced-motion: reduce) and '
        '(prefers-color-scheme: light)"',
        text,
    )
    self.assertIn('media="(prefers-color-scheme: dark)"', text)
    self.assertIn('media="(prefers-color-scheme: light)"', text)
    self.assertIn('alt="Alex contribution signal:', text)
```

7. Rename `test_local_hero_is_retained_but_not_rendered` to `test_old_hero_is_retained_but_signature_is_rendered` and use:

```python
def test_old_hero_is_retained_but_signature_is_rendered(self) -> None:
    text = self.read_readme()
    self.assertTrue(HERO.is_file())
    self.assertTrue(SIGNATURE.is_file())
    self.assertNotIn("./assets/profile-hero.svg", text)
    self.assertIn("./assets/alex-signature.svg", text)
```

8. Extend `test_generated_asset_workflow_is_hardened` to require:

```python
for fragment in (
    "scripts/profile_star_history.py",
    "scripts/compose_contribution_signal.py",
    "star-history.json",
    "contribution-signal-light.svg",
    "contribution-signal-dark.svg",
    "contribution-signal-light-static.svg",
    "contribution-signal-dark-static.svg",
    "GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}",
):
    self.assertIn(fragment, source)
self.assertNotIn("secrets.PAT", source)
self.assertNotIn("PROFILE_STATS_TOKEN", source)
```

- [ ] **Step 2: Run the focused profile tests and confirm they fail for the current README and workflow**

Run:

```bash
python3 -m unittest -v \
  tests.verify_profile.ProfileContractTests.test_v4_sections_and_positioning_are_present_in_order \
  tests.verify_profile.ProfileContractTests.test_four_technology_badges_and_three_star_badges_are_present \
  tests.verify_profile.ProfileContractTests.test_contribution_signal_is_single_theme_and_motion_aware_picture \
  tests.verify_profile.ProfileContractTests.test_generated_asset_workflow_is_hardened
```

Expected: failures because the current README uses the old greeting, five generic badges, and two separate contribution pictures, while the workflow does not generate Star history or composites.

- [ ] **Step 3: Replace `README.md` with the final compact composition**

Use this complete content:

```markdown
<img src="./assets/alex-signature.svg" alt="Alex — building tools that stay inspectable" width="100%">

TypeScript / Python developer focused on developer tooling, CLI automation, and reproducible systems.  
主要使用 TypeScript、Python 与 Node.js，专注开发者工具、CLI 自动化和可复现工程工作流。

## Tech stack

<p>
  <img src="https://img.shields.io/badge/TypeScript-3178C6?style=flat-square&logo=typescript&logoColor=white" alt="TypeScript">
  <img src="https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Node.js-339933?style=flat-square&logo=nodedotjs&logoColor=white" alt="Node.js">
  <img src="https://img.shields.io/badge/GitHub_Actions-2088FF?style=flat-square&logo=githubactions&logoColor=white" alt="GitHub Actions">
</p>

## Featured work

[Planarian](https://github.com/alexliluz/planarian) <img src="https://img.shields.io/github/stars/alexliluz/planarian?style=flat-square&label=stars&color=8250DF" alt="Planarian stars"> · [ForkNeo](https://github.com/alexliluz/ForkNeo) <img src="https://img.shields.io/github/stars/alexliluz/ForkNeo?style=flat-square&label=stars&color=8250DF" alt="ForkNeo stars"> · [api-image-neo](https://github.com/alexliluz/api-image-neo) <img src="https://img.shields.io/github/stars/alexliluz/api-image-neo?style=flat-square&label=stars&color=8250DF" alt="api-image-neo stars">

## Contribution Signal

<picture>
  <source media="(prefers-reduced-motion: reduce) and (prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/alexliluz/alexliluz/output/contribution-signal-dark-static.svg">
  <source media="(prefers-reduced-motion: reduce) and (prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/alexliluz/alexliluz/output/contribution-signal-light-static.svg">
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/alexliluz/alexliluz/output/contribution-signal-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/alexliluz/alexliluz/output/contribution-signal-light.svg">
  <img src="https://raw.githubusercontent.com/alexliluz/alexliluz/output/contribution-signal-light.svg" alt="Alex contribution signal: Star trend, 3D contribution city, and original animated contribution-grid snake" width="100%">
</picture>

---

[Explore all repositories →](https://github.com/alexliluz?tab=repositories)
```

- [ ] **Step 4: Extend the workflow to preserve history and build composites**

After `Assemble stable output names`, insert:

```yaml
      - name: Restore previous Star snapshots
        shell: bash
        run: |
          set -euo pipefail
          rm -f .tmp/previous-star-history.json
          if git ls-remote --exit-code --heads origin output >/dev/null 2>&1; then
            git fetch origin output
            if git cat-file -e origin/output:star-history.json 2>/dev/null; then
              git show origin/output:star-history.json > .tmp/previous-star-history.json
            fi
          fi

      - name: Record current Star counts
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          python3 scripts/profile_star_history.py \
            --history .tmp/previous-star-history.json \
            --output .tmp/profile-output/star-history.json \
            --owner "${{ github.repository_owner }}"

      - name: Compose Contribution Signal assets
        run: |
          python3 scripts/compose_contribution_signal.py \
            --city-light .tmp/profile-output/profile-3d-light.svg \
            --city-dark .tmp/profile-output/profile-3d-dark.svg \
            --snake-light .tmp/profile-output/contribution-snake-light.svg \
            --snake-dark .tmp/profile-output/contribution-snake-dark.svg \
            --history .tmp/profile-output/star-history.json \
            --output-dir .tmp/profile-output
```

Change validation to:

```yaml
      - name: Validate generated SVGs
        run: python3 scripts/validate_profile_assets.py .tmp/profile-output/*.svg
```

In `Publish output branch atomically`, replace the copy line with:

```bash
cp .tmp/profile-output/*.svg .tmp/output-branch/
cp .tmp/profile-output/star-history.json .tmp/output-branch/
```

- [ ] **Step 5: Run the focused profile tests**

Run:

```bash
python3 -m unittest -v \
  tests.verify_profile.ProfileContractTests.test_v4_sections_and_positioning_are_present_in_order \
  tests.verify_profile.ProfileContractTests.test_four_technology_badges_and_three_star_badges_are_present \
  tests.verify_profile.ProfileContractTests.test_contribution_signal_is_single_theme_and_motion_aware_picture \
  tests.verify_profile.ProfileContractTests.test_generated_asset_workflow_is_hardened
```

Expected: four tests pass.

- [ ] **Step 6: Run the complete local test suite and hygiene checks**

Run:

```bash
python3 -m unittest -v \
  tests/verify_profile.py \
  tests/test_signature_asset.py \
  tests/test_profile_star_history.py \
  tests/test_compose_contribution_signal.py \
  tests/test_validate_profile_assets.py
git diff --check
if rg -n "你的邮箱|example\.com|readme-typing-svg|wakatime|secrets\.PAT|PROFILE_STATS_TOKEN" README.md .github scripts; then
  exit 1
fi
```

Expected: all tests pass, `git diff --check` is silent, and the forbidden-fragment scan returns no matches.

- [ ] **Step 7: Commit the workflow and README integration**

```bash
git add README.md tests/verify_profile.py .github/workflows/generate-profile-assets.yml
git commit -m "feat: publish unified profile signal"
```

- [ ] **Step 8: Run the workflow on the implementation branch before main publication**

Push the feature branch, manually dispatch `Generate profile assets`, and inspect the output branch artifacts:

```bash
git push -u origin codex/cyber-flagship
gh workflow run generate-profile-assets.yml \
  --repo alexliluz/alexliluz \
  --ref codex/cyber-flagship
gh run list --repo alexliluz/alexliluz --workflow generate-profile-assets.yml --limit 1
```

Expected: the newest run completes successfully and the output branch contains four original source SVGs, four Contribution Signal SVGs, and `star-history.json`.

- [ ] **Step 9: Publish only after explicit final approval and verify live rendering**

After approval, push the verified commit to `main`:

```bash
git push origin HEAD:main
git fetch origin main
test "$(git rev-parse HEAD)" = "$(git rev-parse origin/main)"
```

Then verify `https://github.com/alexliluz` in dark and light themes and with reduced motion. Confirm the signature, four technology badges, three Star badges, Star trend, 3D city, and original contribution-grid snake all render without broken images or horizontal overflow.
