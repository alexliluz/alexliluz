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


def _rewrite_css_id_references(css: str, id_map: dict[str, str]) -> str:
    rewritten = css
    for old, new in _ordered(id_map):
        rewritten = re.sub(
            rf"(url\(\s*#){re.escape(old)}(?!{IDENTIFIER})",
            rf"\1{new}",
            rewritten,
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
        animations = match.group(2).split(",")
        for index, animation in enumerate(animations):
            for old, new in _ordered(keyframe_map):
                rewritten, count = re.subn(
                    rf"(?<!{IDENTIFIER}){re.escape(old)}(?!{IDENTIFIER})",
                    new,
                    animation,
                    count=1,
                )
                if count:
                    animations[index] = rewritten
                    break
        return match.group(1) + ",".join(animations)

    rewritten = name_pattern.sub(rewrite_name_value, css)
    return shorthand_pattern.sub(rewrite_shorthand, rewritten)


def _assert_reference_integrity(root: ET.Element, old_ids: list[str]) -> None:
    for old in sorted(old_ids, key=len, reverse=True):
        fragments = (
            rf"#{re.escape(old)}(?!{IDENTIFIER})",
            rf"(?<!{IDENTIFIER}){re.escape(old)}(?=\.(?:begin|end|click|repeat))",
        )
        attribute_values = tuple(
            value for element in root.iter() for value in element.attrib.values()
        )
        has_attribute_reference = any(
            re.search(pattern, value) for pattern in fragments for value in attribute_values
        )
        has_css_reference = any(
            _has_css_id_reference(element.text or "", old)
            for element in root.iter()
            if local_name(element.tag) == "style"
        )
        if has_attribute_reference or has_css_reference:
            raise ValueError(f"unresolved local SVG reference: {old}")


def _has_css_id_reference(css: str, old: str) -> bool:
    if re.search(rf"url\(\s*#{re.escape(old)}(?!{IDENTIFIER})", css):
        return True
    return any(
        re.search(rf"(?<=#){re.escape(old)}(?!{IDENTIFIER})", match.group(1))
        for match in re.finditer(r"([^{}]+)\{", css)
    )
