#!/usr/bin/env python3
import argparse
import base64
import binascii
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


SVG_TAG = "{http://www.w3.org/2000/svg}svg"
XML_BASE_ATTRIBUTE = "{http://www.w3.org/XML/1998/namespace}base"
CREDENTIAL_PATTERN = re.compile(
    r"(?:gh[pousr]_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]{20,})"
)
APPROVED_DATA_IMAGE_PATTERN = re.compile(
    r"data:image/svg\+xml;base64,([A-Za-z0-9+/]+={0,2})",
    re.IGNORECASE,
)
CSS_URL_PATTERN = re.compile(
    r"url\(\s*(['\"]?)(.*?)\1\s*\)",
    re.IGNORECASE | re.DOTALL,
)
CSS_IMPORT_PATTERN = re.compile(r"@import\b", re.IGNORECASE)
CSS_ESCAPE_PATTERN = re.compile(
    r"\\(?:"
    r"(?P<hex>[0-9a-f]{1,6})(?:\r\n|[ \t\r\n\f])?"
    r"|(?P<char>[^\r\n\f])"
    r")",
    re.IGNORECASE,
)
URI_ATTRIBUTE_NAMES = {
    "action",
    "background",
    "cite",
    "data",
    "formaction",
    "href",
    "longdesc",
    "manifest",
    "ping",
    "poster",
    "src",
    "usemap",
}
COMPOUND_URI_ATTRIBUTE_NAMES = {"imagesrcset", "srcset"}
SMIL_LOCAL_NAMES = {
    "animate",
    "animatecolor",
    "animatemotion",
    "animatetransform",
    "discard",
    "set",
}
SMIL_VALUE_ATTRIBUTE_NAMES = {"by", "from", "to", "values"}
SMIL_TIMING_ATTRIBUTE_NAMES = {"begin", "end"}
MAX_SVG_BYTES = 2 * 1024 * 1024


def local_name(name: str) -> str:
    return name.rsplit("}", maxsplit=1)[-1].lower()


def is_remote_url(value: str) -> bool:
    return value.strip().lower().startswith(("http://", "https://", "//"))


def is_executable_url(value: str) -> bool:
    normalized = "".join(value.split()).lower()
    return normalized.startswith(("javascript:", "vbscript:"))


def decode_css_escapes(value: str) -> str:
    def replace(match: re.Match) -> str:
        hexadecimal = match.group("hex")
        if hexadecimal is None:
            return match.group("char")
        codepoint = int(hexadecimal, 16)
        if (
            codepoint == 0
            or codepoint > 0x10FFFF
            or 0xD800 <= codepoint <= 0xDFFF
        ):
            return "\N{REPLACEMENT CHARACTER}"
        return chr(codepoint)

    return CSS_ESCAPE_PATTERN.sub(replace, value)


def is_allowed_resource_reference(
    value: str, *, allow_embedded_svg: bool = False
) -> bool:
    normalized = value.strip()
    if re.fullmatch(r"#[^\s]+", normalized):
        return True

    if not allow_embedded_svg:
        return False
    match = APPROVED_DATA_IMAGE_PATTERN.fullmatch(normalized)
    if match is None:
        return False
    try:
        embedded = base64.b64decode(match.group(1), validate=True).decode("utf-8")
        validate_svg_source(embedded)
    except (binascii.Error, UnicodeDecodeError, ValueError):
        return False
    return True


def css_resource_references(css: str):
    for match in CSS_URL_PATTERN.finditer(css):
        yield match.group(2).strip()


def has_remote_css_reference(css: str) -> bool:
    normalized = decode_css_escapes(css)
    return bool(CSS_IMPORT_PATTERN.search(normalized)) or any(
        not is_allowed_resource_reference(reference)
        for reference in css_resource_references(normalized)
    )


def has_xml_stylesheet_instruction(source: str) -> bool:
    parser = ET.XMLPullParser(events=("pi",))
    parser.feed(source)
    parser.close()
    for _, instruction in parser.read_events():
        fields = (instruction.text or "").split(maxsplit=1)
        if fields and fields[0].lower() == "xml-stylesheet":
            return True
    return False


def has_executable_svg_content(root: ET.Element) -> bool:
    for element in root.iter():
        for attribute, value in element.attrib.items():
            if local_name(attribute).startswith("on") or is_executable_url(value):
                return True
    return False


def contains_external_smil_value(value: str) -> bool:
    normalized = "".join(value.split()).lower()
    return any(
        fragment in normalized
        for fragment in ("http://", "https://", "//", "javascript:", "vbscript:", "data:")
    )


def has_unapproved_smil_reference(element: ET.Element) -> bool:
    if local_name(element.tag) not in SMIL_LOCAL_NAMES:
        return False
    attributes = {local_name(name): value for name, value in element.attrib.items()}
    target_name = (
        local_name(attributes.get("attributename", ""))
        .rsplit(":", maxsplit=1)[-1]
        .strip()
    )

    for attribute_name in SMIL_VALUE_ATTRIBUTE_NAMES:
        if attribute_name not in attributes:
            continue
        value = attributes[attribute_name]
        if target_name in URI_ATTRIBUTE_NAMES:
            candidates = value.split(";") if attribute_name == "values" else (value,)
            if any(
                not is_allowed_resource_reference(candidate)
                for candidate in candidates
            ):
                return True
        elif contains_external_smil_value(value):
            return True

    return any(
        contains_external_smil_value(attributes[attribute_name])
        for attribute_name in SMIL_TIMING_ATTRIBUTE_NAMES
        if attribute_name in attributes
    )


def has_remote_runtime_reference(root: ET.Element) -> bool:
    for element in root.iter():
        if local_name(element.tag) == "style" and has_remote_css_reference(
            element.text or ""
        ):
            return True
        if has_unapproved_smil_reference(element):
            return True
        for attribute, value in element.attrib.items():
            attribute_name = local_name(attribute)
            if attribute == XML_BASE_ATTRIBUTE or attribute_name == "base":
                return True
            if attribute_name in COMPOUND_URI_ATTRIBUTE_NAMES:
                return True
            allow_embedded_svg = (
                local_name(element.tag) == "image" and attribute_name == "href"
            )
            if attribute_name in URI_ATTRIBUTE_NAMES and not is_allowed_resource_reference(
                value,
                allow_embedded_svg=allow_embedded_svg,
            ):
                return True
            if has_remote_css_reference(value):
                return True
    return False


def validate_svg_source(source: str) -> ET.Element:
    if len(source.encode("utf-8")) >= MAX_SVG_BYTES:
        raise ValueError("file exceeds 2 MiB")
    if CREDENTIAL_PATTERN.search(source):
        raise ValueError("file contains credential-like text")
    try:
        root = ET.fromstring(source)
    except ET.ParseError as error:
        raise ValueError(f"invalid XML: {error}") from error
    if root.tag != SVG_TAG:
        raise ValueError(f"root element is {root.tag!r}, not SVG")
    if has_xml_stylesheet_instruction(source):
        raise ValueError("file contains an xml-stylesheet processing instruction")
    if any(local_name(element.tag) == "script" for element in root.iter()):
        raise ValueError("file contains script content")
    if has_executable_svg_content(root):
        raise ValueError("file contains executable SVG content")
    if has_remote_runtime_reference(root):
        raise ValueError("file contains an external runtime reference")
    return root


def validate_svg(path: Path) -> None:
    if not path.is_file():
        raise ValueError("file does not exist")
    if path.stat().st_size == 0:
        raise ValueError("file is empty")
    if path.stat().st_size >= MAX_SVG_BYTES:
        raise ValueError("file exceeds 2 MiB")

    try:
        source = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as error:
        raise ValueError("file is not UTF-8 text") from error
    validate_svg_source(source)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate generated profile SVGs")
    parser.add_argument("paths", nargs="+", type=Path)
    arguments = parser.parse_args()

    failures = []
    for path in arguments.paths:
        try:
            validate_svg(path)
        except ValueError as error:
            failures.append(f"{path}: {error}")

    if failures:
        print("\n".join(failures), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
