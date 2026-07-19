#!/usr/bin/env python3
import argparse
import html
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
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
SVG_NAMESPACE = "http://www.w3.org/2000/svg"
SMIL_LOCAL_NAMES = {
    "animate",
    "animatecolor",
    "animatemotion",
    "animatetransform",
    "discard",
    "set",
}
ACTIVE_CITY_CLASS = re.compile(
    r"city-(?:cont-(?:top|left|right)-[1-4]|rb-l[1-4]-(?:top|left|right))$"
)
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
LOCAL_FRAGMENT = re.compile(
    r'''url\(\s*["']?\s*#([A-Za-z_][\w:.-]*)\s*["']?\s*\)''',
    re.IGNORECASE,
)
SMIL_TARGET = re.compile(
    r"(?<![-_A-Za-z0-9])([-_A-Za-z][-_A-Za-z0-9]*)(?=\.(?:begin|end|click|repeat))"
)
SNAKE_ACCENT_GLOW_ID = "snake-accent-glow"


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


@dataclass(frozen=True)
class TrendGeometry:
    points: str
    motion_path: str
    final_x: float
    final_y: float
    total: int
    start_date: str


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


def assert_static_integrity(source: str) -> None:
    root = ET.fromstring(source)
    for element in root.iter():
        name = local_name(element.tag)
        if name in SMIL_LOCAL_NAMES:
            raise ValueError(f"static SVG contains executable SMIL element: {name}")
        if name == "style" and strip_css_motion_declarations(element.text or "") != (
            element.text or ""
        ):
            raise ValueError("static SVG contains CSS motion declaration")
        if "style" in element.attrib and strip_css_motion_declarations(
            element.attrib["style"]
        ) != element.attrib["style"]:
            raise ValueError("static SVG contains CSS motion declaration")


def _append_smil(element: ET.Element, **attributes: str) -> None:
    ET.SubElement(element, f"{{{SVG_NAMESPACE}}}animate", attributes)


def tune_snake_motion(root: ET.Element) -> None:
    replacements = 0
    for element in root.iter():
        if local_name(element.tag) != "style":
            continue
        element.text, count = re.subn(
            r"(?<![0-9])18500ms(?![0-9])", "8500ms", element.text or ""
        )
        replacements += count
    if replacements == 0:
        raise ValueError("upstream snake CSS no longer contains 18500ms")
    _add_snake_accent_glow(root)


def _add_snake_accent_glow(root: ET.Element) -> None:
    accents = [
        element
        for element in root.iter()
        if _is_platane_snake_accent(element)
    ]
    if not accents:
        return
    if any(element.attrib.get("id") == SNAKE_ACCENT_GLOW_ID for element in root.iter()):
        raise ValueError(f"upstream snake reserves generated id: {SNAKE_ACCENT_GLOW_ID}")
    if any("filter" in element.attrib for element in accents):
        raise ValueError("upstream snake moving accent already defines a filter")

    defs = next(
        (element for element in root if local_name(element.tag) == "defs"), None
    )
    if defs is None:
        defs = ET.Element(f"{{{SVG_NAMESPACE}}}defs")
        root.insert(0, defs)
    glow = ET.SubElement(
        defs,
        f"{{{SVG_NAMESPACE}}}filter",
        {
            "id": SNAKE_ACCENT_GLOW_ID,
            "x": "-35%",
            "y": "-35%",
            "width": "170%",
            "height": "170%",
        },
    )
    ET.SubElement(
        glow,
        f"{{{SVG_NAMESPACE}}}feGaussianBlur",
        {"stdDeviation": "0.65"},
    )
    for accent in accents:
        accent.attrib["filter"] = f"url(#{SNAKE_ACCENT_GLOW_ID})"


def _is_platane_snake_accent(element: ET.Element) -> bool:
    classes = element.attrib.get("class", "").split()
    return "snake-s" in classes and any(
        re.fullmatch(r"snake-s[0-9]+", token) for token in classes
    )


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
        if any(
            ACTIVE_CITY_CLASS.fullmatch(token)
            for token in element.attrib.get("class", "").split()
        ):
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


def trend_points(history: dict) -> tuple[str, int, str]:
    geometry = trend_geometry(history)
    return geometry.points, geometry.total, geometry.start_date


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
            if local_name(name) == "href" and value.strip().startswith("#"):
                referenced.add(value.strip()[1:])
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
        try:
            city_source = static_source(city_source)
        except ValueError as error:
            raise ValueError(f"city transform: {error}") from error
        try:
            snake_source = static_source(snake_source)
        except ValueError as error:
            raise ValueError(f"snake transform: {error}") from error
    try:
        city_root = namespace_svg(city_source, "city")
    except ValueError as error:
        raise ValueError(f"city import: {error}") from error
    try:
        snake_root = namespace_svg(snake_source, "snake")
    except ValueError as error:
        raise ValueError(f"snake import: {error}") from error
    if not static:
        try:
            tune_city_motion(city_root, theme_name)
        except ValueError as error:
            raise ValueError(f"city transform: {error}") from error
        try:
            tune_snake_motion(snake_root)
        except ValueError as error:
            raise ValueError(f"snake transform: {error}") from error
    city_markup = position_imported_svg(city_root, x=88, y=110, width=784, height=520)
    snake_markup = position_imported_svg(snake_root, x=42, y=695, width=876, height=191)
    geometry = trend_geometry(history)
    signal_markup = ""
    animation_style = "" if static else """
      .trend { stroke-dasharray: 260; stroke-dashoffset: 260; animation: draw 1.6s ease forwards; }
      @keyframes draw { to { stroke-dashoffset: 0; } }
    """
    if not static:
        signal_markup = f'''<defs>
    <filter id="signal-trend-glow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="3"/>
    </filter>
  </defs>
  <circle id="signal-trend-dot" r="4" fill="{theme['trend']}" filter="url(#signal-trend-glow)">
    <animateMotion path="{geometry.motion_path}" dur="3.2s" repeatCount="indefinite"/>
  </circle>'''
    else:
        signal_markup = (
            f'<circle id="signal-trend-dot" cx="{geometry.final_x:.1f}" '
            f'cy="{geometry.final_y:.1f}" r="4" fill="{theme["trend"]}"/>'
        )
    source = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 900" role="img" aria-labelledby="title description">
  <title id="title">Alex contribution signal</title>
  <desc id="description">Star trend, 3D contribution city, and original contribution-grid snake.</desc>
  <style>{animation_style}</style>
  <rect x="1" y="1" width="958" height="898" rx="18" fill="{theme['background']}" stroke="{theme['border']}" stroke-width="2"/>
  <text x="28" y="38" fill="{theme['primary']}" font-family="ui-monospace, monospace" font-size="15" font-weight="600" letter-spacing="3">CONTRIBUTION SIGNAL</text>
  <text x="28" y="58" fill="{theme['muted']}" font-family="ui-monospace, monospace" font-size="10" letter-spacing="1">PUBLIC ACTIVITY · DAILY</text>
  <rect x="650" y="18" width="282" height="70" rx="10" fill="{theme['background']}" stroke="{theme['border']}"/>
  <text x="696" y="37" fill="{theme['muted']}" font-family="ui-monospace, monospace" font-size="9" letter-spacing="1">STAR TREND</text>
  <text x="910" y="37" text-anchor="end" fill="{theme['star']}" font-family="ui-monospace, monospace" font-size="12">★ {geometry.total}</text>
  <polyline class="trend" points="{geometry.points}" fill="none" stroke="{theme['trend']}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
  {signal_markup}
  <text x="696" y="82" fill="{theme['muted']}" font-family="ui-monospace, monospace" font-size="8">SNAPSHOTS FROM {html.escape(geometry.start_date)}</text>
  <text x="28" y="104" fill="{theme['muted']}" font-family="ui-monospace, monospace" font-size="9" letter-spacing="1">3D CONTRIBUTION CITY</text>
  {city_markup}
  <line x1="28" y1="650" x2="932" y2="650" stroke="{theme['border']}"/>
  <text x="28" y="675" fill="{theme['muted']}" font-family="ui-monospace, monospace" font-size="9" letter-spacing="1">ORIGINAL CONTRIBUTION SNAKE</text>
  {snake_markup}
</svg>
'''
    validate_svg_source(source)
    assert_composed_integrity(source)
    if static:
        assert_static_integrity(source)
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
        "light": (read_safe_svg(city_light), read_safe_svg(snake_light), city_light, snake_light),
        "dark": (read_safe_svg(city_dark), read_safe_svg(snake_dark), city_dark, snake_dark),
    }
    output_directory.mkdir(parents=True, exist_ok=True)
    for theme_name, (city_source, snake_source, city_path, snake_path) in sources.items():
        for static in (False, True):
            suffix = "-static" if static else ""
            path = output_directory / f"contribution-signal-{theme_name}{suffix}.svg"
            try:
                composed = compose(city_source, snake_source, history, theme_name, static)
            except ValueError as error:
                message = str(error)
                if message.startswith("city "):
                    raise ValueError(f"city source ({city_path}): {message}") from error
                if message.startswith("snake "):
                    raise ValueError(f"snake source ({snake_path}): {message}") from error
                raise
            path.write_text(composed, encoding="utf-8")


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
