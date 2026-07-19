import re
import xml.etree.ElementTree as ET
from typing import Optional


PREFIX = re.compile(r"^[a-z][a-z0-9-]*$")
KEYFRAME = re.compile(r"(@(?:-[a-z]+-)?keyframes\s+)([-_A-Za-z][-_A-Za-z0-9]*)", re.I)
CUSTOM_PROPERTY = re.compile(r"--([-_A-Za-z][-_A-Za-z0-9]*)")
URL_FRAGMENT = re.compile(r'''(url\(\s*["']?#)([^\s"')]+)(?=\s*["']?\s*\))''', re.I)
IDREF_LIST_ATTRIBUTES = {
    "aria-activedescendant",
    "aria-controls",
    "aria-describedby",
    "aria-details",
    "aria-errormessage",
    "aria-flowto",
    "aria-labelledby",
    "aria-owns",
}


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
    if "root" in ids and root.attrib.get("id") != "root":
        raise ValueError("reserved SVG id: root")

    classes = {
        token
        for element in root.iter()
        for token in element.attrib.get("class", "").split()
    }
    styles = [element for element in root.iter() if local_name(element.tag) == "style"]
    inline_styles = [
        element.attrib["style"] for element in root.iter() if "style" in element.attrib
    ]
    keyframes = {
        match.group(2)
        for style in styles
        for match in KEYFRAME.finditer(style.text or "")
    }
    custom_properties = {
        match.group(1)
        for css in [*(style.text or "" for style in styles), *inline_styles]
        for match in CUSTOM_PROPERTY.finditer(css)
    }

    id_map = {value: f"{prefix}-{value}" for value in ids}
    if "id" in root.attrib:
        id_map[root.attrib["id"]] = f"{prefix}-root"
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
            if local_name(name) == "style":
                element.attrib[name] = _rewrite_css(
                    value, prefix, id_map, class_map, keyframe_map, property_map
                )
            else:
                element.attrib[name] = _rewrite_value(name, value, id_map)
        if local_name(element.tag) == "style":
            element.text = _rewrite_css(
                element.text or "", prefix, id_map, class_map, keyframe_map, property_map
            )

    root.attrib["id"] = f"{prefix}-root"
    root.attrib.pop("width", None)
    root.attrib.pop("height", None)
    _assert_reference_integrity(root, ids)
    return root


IDENTIFIER = r"[-_A-Za-z0-9]"
ANIMATION_KEYWORDS = {
    "alternate",
    "alternate-reverse",
    "backwards",
    "both",
    "ease",
    "ease-in",
    "ease-in-out",
    "ease-out",
    "forwards",
    "infinite",
    "linear",
    "none",
    "normal",
    "paused",
    "reverse",
    "running",
    "step-end",
    "step-start",
}


def _ordered(mapping: dict[str, str]):
    return sorted(mapping.items(), key=lambda item: len(item[0]), reverse=True)


def _rewrite_value(name: str, value: str, id_map: dict[str, str]) -> str:
    attribute_name = local_name(name)
    if attribute_name in IDREF_LIST_ATTRIBUTES:
        return " ".join(id_map.get(token, token) for token in value.split())
    if attribute_name == "href" and value.strip().startswith("#"):
        fragment = value.strip()[1:]
        return "#" + id_map.get(fragment, fragment)

    rewritten = URL_FRAGMENT.sub(
        lambda match: match.group(1) + id_map.get(match.group(2), match.group(2)), value
    )
    if attribute_name not in {"begin", "end"}:
        return rewritten
    for old, new in _ordered(id_map):
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
            rf"(?<=\.){_css_identifier_pattern(old)}(?!{IDENTIFIER}|\\)",
            _escape_css_identifier(new),
            rewritten,
        )
    rewritten = _rewrite_css_id_references(rewritten, id_map)
    rewritten = KEYFRAME.sub(
        lambda match: match.group(1) + keyframe_map[match.group(2)], rewritten
    )
    rewritten = _rewrite_animation_names(rewritten, keyframe_map)
    for old, new in _ordered(property_map):
        rewritten = re.sub(
            rf"--{re.escape(old)}(?!{IDENTIFIER})", f"--{new}", rewritten
        )
    return rewritten


def _css_identifier_pattern(identifier: str) -> str:
    """Match a CSS identifier in literal or escaped form without parsing CSS."""
    parts = []
    for character in identifier:
        codepoint = f"{ord(character):x}"
        hex_pattern = "".join(
            f"[{digit.lower()}{digit.upper()}]" if digit.isalpha() else digit
            for digit in codepoint
        )
        parts.append(
            rf"(?:{re.escape(character)}|\\{re.escape(character)}|\\0*{hex_pattern}(?:(?:\r\n|[ \t\r\n\f])|(?![0-9a-f])))"
        )
    return "".join(parts)


def _escape_css_identifier(identifier: str) -> str:
    return re.sub(r"[^-_A-Za-z0-9]", lambda match: "\\" + match.group(0), identifier)


def _rewrite_css_id_references(css: str, id_map: dict[str, str]) -> str:
    rewritten = css
    for old, new in _ordered(id_map):
        rewritten = re.sub(
            rf'''(url\(\s*["']?#){re.escape(old)}(?!{IDENTIFIER})''',
            rf"\1{new}",
            rewritten,
            flags=re.I,
        )

    def rewrite_selector(match: re.Match[str]) -> str:
        selector = match.group(1)
        for old, new in _ordered(id_map):
            selector = re.sub(
                rf"(?<=#){re.escape(old)}(?!{IDENTIFIER})", new, selector
            )
        return selector + "{"

    return re.sub(r"([^{}]+)\{", rewrite_selector, rewritten)


def _rewrite_animation_names(css: str, keyframe_map: dict[str, str]) -> str:
    name_pattern = re.compile(
        r"((?:^|[;{])\s*(?:-[a-z]+-)?animation-name\s*:\s*)([^;{}]+)", re.I
    )
    shorthand_pattern = re.compile(
        r"((?:^|[;{])\s*(?:-[a-z]+-)?animation\s*:\s*)([^;{}]+)", re.I
    )

    def rewrite_name_value(match: re.Match[str]) -> str:
        value = match.group(2)
        for old, new in _ordered(keyframe_map):
            value = re.sub(
                rf"(?<!{IDENTIFIER}){re.escape(old)}(?!{IDENTIFIER})", new, value
            )
        return match.group(1) + value

    def rewrite_shorthand(match: re.Match[str]) -> str:
        animations = _split_top_level_commas(match.group(2))
        for index, animation in enumerate(animations):
            name_match = _find_animation_name(animation, keyframe_map)
            if name_match:
                old = name_match.group(0)
                animations[index] = (
                    animation[: name_match.start()]
                    + keyframe_map[old]
                    + animation[name_match.end() :]
                )
        return match.group(1) + ",".join(animations)

    rewritten = name_pattern.sub(rewrite_name_value, css)
    return shorthand_pattern.sub(rewrite_shorthand, rewritten)


def _split_top_level_commas(value: str) -> list[str]:
    animations = []
    depth = 0
    start = 0
    for index, character in enumerate(value):
        if character == "(":
            depth += 1
        elif character == ")":
            depth -= 1
        elif character == "," and depth == 0:
            animations.append(value[start:index])
            start = index + 1
    animations.append(value[start:])
    return animations


def _find_animation_name(
    animation: str, keyframe_map: dict[str, str]
) -> Optional[re.Match[str]]:
    fallback = None
    depth = 0
    cursor = 0
    for match in re.finditer(r"[-_A-Za-z][-_A-Za-z0-9]*", animation):
        for character in animation[cursor : match.start()]:
            if character == "(":
                depth += 1
            elif character == ")":
                depth -= 1
        cursor = match.end()
        name = match.group(0)
        if depth or name not in keyframe_map:
            continue
        if animation[match.end() :].lstrip().startswith("("):
            continue
        if fallback is None:
            fallback = match
        if name.lower() not in ANIMATION_KEYWORDS:
            return match
    return fallback


def _assert_reference_integrity(root: ET.Element, old_ids: list[str]) -> None:
    for old in sorted(old_ids, key=len, reverse=True):
        fragments = (
            rf"#{re.escape(old)}(?!{IDENTIFIER})",
            rf"(?<!{IDENTIFIER}){re.escape(old)}(?=\.(?:begin|end|click|repeat))",
        )
        has_attribute_reference = any(
            (
                local_name(name) == "href" and value.strip() == f"#{old}"
            )
            or any(
                match.group(2) == old for match in URL_FRAGMENT.finditer(value)
            )
            or (
                local_name(name) in {"begin", "end"}
                and re.search(fragments[1], value)
            )
            for element in root.iter()
            for name, value in element.attrib.items()
        )
        has_idref_reference = any(
            old in value.split()
            for element in root.iter()
            for name, value in element.attrib.items()
            if local_name(name) in IDREF_LIST_ATTRIBUTES
        )
        has_css_reference = any(
            _has_css_id_reference(element.text or "", old)
            for element in root.iter()
            if local_name(element.tag) == "style"
        )
        if has_attribute_reference or has_idref_reference or has_css_reference:
            raise ValueError(f"unresolved local SVG reference: {old}")


def _has_css_id_reference(css: str, old: str) -> bool:
    if re.search(
        rf'''url\(\s*["']?#{re.escape(old)}(?!{IDENTIFIER})''', css, re.I
    ):
        return True
    return any(
        re.search(rf"(?<=#){re.escape(old)}(?!{IDENTIFIER})", match.group(1))
        for match in re.finditer(r"([^{}]+)\{", css)
    )
