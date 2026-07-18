#!/usr/bin/env python3
import argparse
import base64
import html
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
    r'(?:href|src)\s*=\s*["\']\s*https?://',
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


def has_external_http_reference(source: str, root: ET.Element) -> bool:
    if EXTERNAL_REFERENCE_PATTERN.search(source):
        return True
    for element in root.iter():
        for attribute, value in element.attrib.items():
            if attribute.rsplit("}", maxsplit=1)[-1].lower() in {"href", "src"}:
                if value.strip().lower().startswith(("http://", "https://")):
                    return True
    return False


def read_safe_svg(path: Path) -> str:
    if not path.is_file():
        raise ValueError(f"missing SVG: {path}")
    if path.stat().st_size > MAX_BYTES:
        raise ValueError(f"SVG exceeds 2 MiB: {path}")
    try:
        source = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as error:
        raise ValueError(f"SVG is not UTF-8 text: {path}") from error
    try:
        root = ET.fromstring(source)
    except ET.ParseError as error:
        raise ValueError(f"invalid SVG {path}: {error}") from error
    if root.tag != SVG_TAG:
        raise ValueError(f"not an SVG: {path}")
    if "<script" in source.lower():
        raise ValueError(f"script is forbidden in {path}")
    if has_external_http_reference(source, root):
        raise ValueError(f"external HTTP reference is forbidden in {path}")
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
    if "<script" in source.lower():
        raise ValueError("composed SVG contains script content")
    try:
        root = ET.fromstring(source)
    except ET.ParseError as error:
        raise ValueError(f"invalid composed SVG: {error}") from error
    if has_external_http_reference(source, root):
        raise ValueError("composed SVG contains an external HTTP reference")
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
