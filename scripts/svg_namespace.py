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
