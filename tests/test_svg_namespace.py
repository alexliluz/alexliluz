import unittest
import xml.etree.ElementTree as ET

from scripts.svg_namespace import namespace_svg


SVG = "http://www.w3.org/2000/svg"


class SvgNamespaceTests(unittest.TestCase):
    def sample(self) -> str:
        return f'''<svg xmlns="{SVG}" viewBox="0 0 100 40">
          <style>
            :root{{--tone:#8250df}}
            .tile{{fill:var(--tone);animation:pulse 10s linear infinite}}
            #layer{{filter:url(#glow)}}
            @keyframes pulse{{from{{opacity:.8}}to{{opacity:1}}}}
          </style>
          <defs><filter id="glow"/></defs>
          <g id="layer" class="tile">
            <animate attributeName="opacity" begin="layer.end" dur="1s"/>
            <use href="#layer"/>
          </g>
        </svg>'''

    def test_namespaces_css_dom_and_local_references(self) -> None:
        root = namespace_svg(self.sample(), "city")
        source = ET.tostring(root, encoding="unicode")
        self.assertEqual(root.attrib["id"], "city-root")
        for expected in (
            'id="city-layer"',
            'id="city-glow"',
            'class="city-tile"',
            '@keyframes city-pulse',
            'animation:city-pulse 10s',
            '--city-tone',
            'var(--city-tone)',
            'url(#city-glow)',
            'href="#city-layer"',
            'begin="city-layer.end"',
            '#city-layer',
        ):
            self.assertIn(expected, source)

    def test_rejects_invalid_prefix(self) -> None:
        with self.assertRaisesRegex(ValueError, "prefix"):
            namespace_svg(self.sample(), "City Signal")

    def test_rejects_duplicate_ids_before_rewrite(self) -> None:
        source = f'<svg xmlns="{SVG}"><g id="x"/><g id="x"/></svg>'
        with self.assertRaisesRegex(ValueError, "duplicate SVG id: x"):
            namespace_svg(source, "city")

    def test_preserves_viewbox_and_removes_fixed_dimensions(self) -> None:
        source = f'<svg xmlns="{SVG}" viewBox="0 0 100 40" width="100" height="40"/>'
        root = namespace_svg(source, "snake")
        self.assertEqual(root.attrib["viewBox"], "0 0 100 40")
        self.assertNotIn("width", root.attrib)
        self.assertNotIn("height", root.attrib)

    def test_rewrites_root_id_references_to_the_guaranteed_root_id(self) -> None:
        source = f'<svg xmlns="{SVG}" id="scene"><use href="#scene"/></svg>'
        root = namespace_svg(source, "city")
        rendered = ET.tostring(root, encoding="unicode")
        self.assertEqual(root.attrib["id"], "city-root")
        self.assertIn('href="#city-root"', rendered)
        self.assertNotIn("city-scene", rendered)

    def test_rewrites_css_id_selectors_without_rewriting_hex_colors(self) -> None:
        source = f'''<svg xmlns="{SVG}">
          <style>#fff{{fill:#fff;filter:url(#fff)}}</style>
          <g id="fff"/>
        </svg>'''
        rendered = ET.tostring(namespace_svg(source, "city"), encoding="unicode")
        self.assertIn("#city-fff{fill:#fff;filter:url(#city-fff)}", rendered)

    def test_rewrites_only_animation_names_that_match_keyframes(self) -> None:
        source = f'''<svg xmlns="{SVG}">
          <style>@keyframes linear{{to{{opacity:1}}}}.tile{{animation:linear 1s linear}}</style>
        </svg>'''
        rendered = ET.tostring(namespace_svg(source, "city"), encoding="unicode")
        self.assertIn("@keyframes city-linear", rendered)
        self.assertIn("animation:city-linear 1s linear", rendered)

    def test_rewrites_quoted_css_fragment_urls(self) -> None:
        source = f'''<svg xmlns="{SVG}">
          <style>.tile{{filter:url("#glow");mask:url('#glow')}}</style>
          <filter id="glow"/>
        </svg>'''
        rendered = ET.tostring(namespace_svg(source, "city"), encoding="unicode")
        self.assertIn('url("#city-glow")', rendered)
        self.assertIn("url('#city-glow')", rendered)

    def test_rewrites_shorthand_name_without_rewriting_keyframe_timing_keyword(self) -> None:
        source = f'''<svg xmlns="{SVG}">
          <style>
            @keyframes linear{{to{{opacity:1}}}}
            @keyframes pulse{{to{{opacity:.5}}}}
            .tile{{animation:pulse 1s linear}}
          </style>
        </svg>'''
        rendered = ET.tostring(namespace_svg(source, "city"), encoding="unicode")
        self.assertIn("@keyframes city-linear", rendered)
        self.assertIn("@keyframes city-pulse", rendered)
        self.assertIn("animation:city-pulse 1s linear", rendered)


if __name__ == "__main__":
    unittest.main()
