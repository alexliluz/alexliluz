#!/usr/bin/env python3
import argparse
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


SVG_TAG = "{http://www.w3.org/2000/svg}svg"
XML_BASE_ATTRIBUTE = "{http://www.w3.org/XML/1998/namespace}base"
CREDENTIAL_PATTERN = re.compile(
    r"(?:gh[pousr]_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]{20,})"
)
CSS_REMOTE_URL_PATTERN = re.compile(
    r"url\(\s*(?:['\"]\s*)?(?:(?:https?:)?//)",
    re.IGNORECASE,
)
CSS_REMOTE_IMPORT_PATTERN = re.compile(
    r"@import\s+(?:['\"]\s*)?(?:(?:https?:)?//)",
    re.IGNORECASE,
)
MAX_SVG_BYTES = 2 * 1024 * 1024


def local_name(name: str) -> str:
    return name.rsplit("}", maxsplit=1)[-1].lower()


def is_remote_url(value: str) -> bool:
    return value.strip().lower().startswith(("http://", "https://", "//"))


def is_executable_url(value: str) -> bool:
    normalized = "".join(value.split()).lower()
    return normalized.startswith(("javascript:", "vbscript:"))


def has_remote_css_reference(css: str) -> bool:
    return bool(
        CSS_REMOTE_URL_PATTERN.search(css) or CSS_REMOTE_IMPORT_PATTERN.search(css)
    )


def has_executable_svg_content(root: ET.Element) -> bool:
    for element in root.iter():
        for attribute, value in element.attrib.items():
            if local_name(attribute).startswith("on") or is_executable_url(value):
                return True
    return False


def has_remote_runtime_reference(root: ET.Element) -> bool:
    for element in root.iter():
        if local_name(element.tag) == "style" and has_remote_css_reference(
            element.text or ""
        ):
            return True
        for attribute, value in element.attrib.items():
            attribute_name = local_name(attribute)
            if attribute == XML_BASE_ATTRIBUTE and is_remote_url(value):
                return True
            if attribute_name in {"href", "src"} and is_remote_url(value):
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
