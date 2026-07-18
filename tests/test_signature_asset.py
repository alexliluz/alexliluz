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
