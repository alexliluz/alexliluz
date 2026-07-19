#!/usr/bin/env python3
import argparse
import html
import re
import xml.etree.ElementTree as ET
from pathlib import Path

if __package__:
    from scripts.profile_star_history import load_history
    from scripts.svg_namespace import namespace_svg
    from scripts.validate_profile_assets import (
        MAX_SVG_BYTES,
        decode_css_escapes,
        local_name,
        validate_svg,
        validate_svg_source,
    )
else:
    from profile_star_history import load_history
    from svg_namespace import namespace_svg
    from validate_profile_assets import (
        MAX_SVG_BYTES,
        decode_css_escapes,
        local_name,
        validate_svg,
        validate_svg_source,
    )


MAX_BYTES = MAX_SVG_BYTES
SMIL_LOCAL_NAMES = {
    "animate",
    "animatecolor",
    "animatemotion",
    "animatetransform",
    "set",
}
CSS_IDENTIFIER_ESCAPE = (
    r"\\(?:[0-9a-f]{1,6}(?:\r\n|[ \t\r\n\f])?|[^\r\n\f])"
)
CSS_COMMENT = r"/\*(?:[^*]|\*(?!/))*\*/"
CSS_IGNORABLE = r"(?:\s|" + CSS_COMMENT + r")*"
CSS_DECLARATION_PATTERN = re.compile(
    r"(?P<prefix>^|[;{])"
    + CSS_IGNORABLE
    + r"(?P<property>(?:"
    + CSS_IDENTIFIER_ESCAPE
    + r"|[-_a-z0-9])+)"
    + CSS_IGNORABLE
    + r":\s*[^;{}]*(?=;|}|$)",
    re.IGNORECASE,
)
CSS_MOTION_PROPERTY_PATTERN = re.compile(
    r"(?:-[a-z]+-)?(?:animation|transition)(?:-[a-z-]+)?",
    re.IGNORECASE,
)
CSS_FIRST_KEYFRAME_PATTERN = re.compile(
    r"@(?:-[a-z]+-)?keyframes\s+"
    r"(?P<name>[-_a-z0-9]+)\s*\{\s*"
    r"(?:from|0(?:\.0+)?%)\s*\{(?P<body>[^{}]*)\}",
    re.IGNORECASE,
)
CSS_FILL_DECLARATION_PATTERN = re.compile(
    r"(?:^|;)\s*(?P<declaration>fill\s*:\s*[^;{}]+)",
    re.IGNORECASE,
)


THEMES = {
    "light": {
        "background": "#FFFFFF",
        "border": "#D0D7DE",
        "primary": "#24292F",
        "muted": "#57606A",
        "trend": "#CF222E",
        "star": "#9A6700",
    },
    "dark": {
        "background": "#080B12",
        "border": "#30363D",
        "primary": "#E6EDF3",
        "muted": "#8B949E",
        "trend": "#FF4F79",
        "star": "#E3B341",
    },
}


def read_safe_svg(path: Path) -> str:
    validate_svg(path)
    try:
        source = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as error:
        raise ValueError(f"SVG is not UTF-8 text: {path}") from error
    return source


def strip_css_motion_declarations(css: str) -> str:
    def remove_motion(match: re.Match) -> str:
        property_name = decode_css_escapes(match.group("property"))
        if CSS_MOTION_PROPERTY_PATTERN.fullmatch(property_name):
            prefix = match.group("prefix")
            return prefix if prefix == "{" else ""
        return match.group(0)

    while True:
        static = CSS_DECLARATION_PATTERN.sub(remove_motion, css)
        if static == css:
            return static
        css = static


def materialize_first_keyframe_fills(css: str) -> str:
    for keyframe in list(CSS_FIRST_KEYFRAME_PATTERN.finditer(css)):
        fill = CSS_FILL_DECLARATION_PATTERN.search(keyframe.group("body"))
        if fill is None:
            continue
        class_rule = re.compile(
            r"(?P<prefix>\."
            + re.escape(keyframe.group("name"))
            + r"\s*\{)(?P<body>[^{}]*)(?P<suffix>\})",
            re.IGNORECASE,
        )

        def add_fallback(match: re.Match) -> str:
            body = match.group("body")
            if CSS_FILL_DECLARATION_PATTERN.search(body):
                return match.group(0)
            if body and not body.rstrip().endswith(";"):
                body += ";"
            body += fill.group("declaration") + ";"
            return match.group("prefix") + body + match.group("suffix")

        css = class_rule.sub(add_fallback, css, count=1)
    return css


def static_source(source: str) -> str:
    root = ET.fromstring(source)
    for parent in root.iter():
        for child in list(parent):
            if local_name(child.tag) in SMIL_LOCAL_NAMES:
                parent.remove(child)
    for element in root.iter():
        if local_name(element.tag) == "style":
            element.text = strip_css_motion_declarations(
                materialize_first_keyframe_fills(element.text or "")
            )
        if "style" in element.attrib:
            element.attrib["style"] = strip_css_motion_declarations(
                element.attrib["style"]
            )
    static = ET.tostring(root, encoding="unicode")
    ET.fromstring(static)
    return static


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
    validate_svg_source(city_source)
    validate_svg_source(snake_source)
    if static:
        city_source = static_source(city_source)
        snake_source = static_source(snake_source)
    city_root = namespace_svg(city_source, "city")
    snake_root = namespace_svg(snake_source, "snake")
    city_markup = position_imported_svg(city_root, x=88, y=110, width=784, height=520)
    snake_markup = position_imported_svg(snake_root, x=42, y=695, width=876, height=191)
    points, total, start_date = trend_points(history)
    animation_style = "" if static else """
      .trend { stroke-dasharray: 260; stroke-dashoffset: 260; animation: draw 3s ease forwards; }
      @keyframes draw { to { stroke-dashoffset: 0; } }
    """
    source = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 900" role="img" aria-labelledby="title description">
  <title id="title">Alex contribution signal</title>
  <desc id="description">Star trend, 3D contribution city, and original contribution-grid snake.</desc>
  <style>{animation_style}</style>
  <rect x="1" y="1" width="958" height="898" rx="18" fill="{theme['background']}" stroke="{theme['border']}" stroke-width="2"/>
  <text x="28" y="38" fill="{theme['primary']}" font-family="ui-monospace, monospace" font-size="15" font-weight="600" letter-spacing="3">CONTRIBUTION SIGNAL</text>
  <text x="28" y="58" fill="{theme['muted']}" font-family="ui-monospace, monospace" font-size="10" letter-spacing="1">PUBLIC ACTIVITY · DAILY</text>
  <rect x="650" y="18" width="282" height="70" rx="10" fill="{theme['background']}" stroke="{theme['border']}"/>
  <text x="696" y="37" fill="{theme['muted']}" font-family="ui-monospace, monospace" font-size="9" letter-spacing="1">STAR TREND</text>
  <text x="910" y="37" text-anchor="end" fill="{theme['star']}" font-family="ui-monospace, monospace" font-size="12">★ {total}</text>
  <polyline class="trend" points="{points}" fill="none" stroke="{theme['trend']}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
  <text x="696" y="82" fill="{theme['muted']}" font-family="ui-monospace, monospace" font-size="8">SNAPSHOTS FROM {html.escape(start_date)}</text>
  <text x="28" y="104" fill="{theme['muted']}" font-family="ui-monospace, monospace" font-size="9" letter-spacing="1">3D CONTRIBUTION CITY</text>
  {city_markup}
  <line x1="28" y1="650" x2="932" y2="650" stroke="{theme['border']}"/>
  <text x="28" y="675" fill="{theme['muted']}" font-family="ui-monospace, monospace" font-size="9" letter-spacing="1">ORIGINAL CONTRIBUTION SNAKE</text>
  {snake_markup}
</svg>
'''
    validate_svg_source(source)
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
