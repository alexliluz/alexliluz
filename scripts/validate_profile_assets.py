#!/usr/bin/env python3
import argparse
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


SVG_TAG = "{http://www.w3.org/2000/svg}svg"
CREDENTIAL_PATTERN = re.compile(
    r"(?:gh[pousr]_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]{20,})"
)
MAX_SVG_BYTES = 2 * 1024 * 1024
EXTERNAL_REFERENCE_PATTERN = re.compile(
    r'(?:href|src)\s*=\s*["\']\s*https?://',
    re.IGNORECASE,
)


def has_external_http_reference(source: str, root: ET.Element) -> bool:
    if EXTERNAL_REFERENCE_PATTERN.search(source):
        return True
    for element in root.iter():
        for attribute, value in element.attrib.items():
            if attribute.rsplit("}", maxsplit=1)[-1].lower() in {"href", "src"}:
                if value.strip().lower().startswith(("http://", "https://")):
                    return True
    return False


def validate_svg(path: Path) -> None:
    if not path.is_file():
        raise ValueError("file does not exist")
    if path.stat().st_size == 0:
        raise ValueError("file is empty")
    if path.stat().st_size > MAX_SVG_BYTES:
        raise ValueError("file exceeds 2 MiB")

    try:
        source = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as error:
        raise ValueError("file is not UTF-8 text") from error

    if CREDENTIAL_PATTERN.search(source):
        raise ValueError("file contains credential-like text")
    if "<script" in source.lower():
        raise ValueError("file contains script content")
    if EXTERNAL_REFERENCE_PATTERN.search(source):
        raise ValueError("file contains an external HTTP reference")

    try:
        root = ET.fromstring(source)
    except ET.ParseError as error:
        raise ValueError(f"invalid XML: {error}") from error

    if root.tag != SVG_TAG:
        raise ValueError(f"root element is {root.tag!r}, not SVG")
    if has_external_http_reference(source, root):
        raise ValueError("file contains an external HTTP reference")


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
