#!/usr/bin/env python3
import argparse
from pathlib import Path
from xml.sax.saxutils import escape

WORD = "Alex"
SUBTITLE = "BUILDING TOOLS THAT STAY INSPECTABLE"


def outlined_word(font_path: Path, word: str) -> tuple[str, float]:
    from fontTools.pens.svgPathPen import SVGPathPen
    from fontTools.ttLib import TTFont

    font = TTFont(font_path)
    glyph_set = font.getGlyphSet()
    cmap = font.getBestCmap()
    metrics = font["hmtx"].metrics
    x_offset = 0
    paths = []
    for character in word:
        glyph_name = cmap.get(ord(character))
        if glyph_name is None:
            raise ValueError(f"font has no glyph for {character!r}")
        pen = SVGPathPen(glyph_set)
        glyph_set[glyph_name].draw(pen)
        paths.append(
            f'<path d="{escape(pen.getCommands())}" '
            f'transform="translate({x_offset} 0)"/>'
        )
        x_offset += metrics[glyph_name][0]
    return "".join(paths), float(x_offset)


def build_svg(font_path: Path) -> str:
    paths, advance = outlined_word(font_path, WORD)
    target_width = 330.0
    scale = target_width / advance
    x_origin = (960.0 - target_width) / 2.0
    transform = f"translate({x_origin:.3f} 132) scale({scale:.7f} {-scale:.7f})"
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 220" role="img" aria-labelledby="title description">
  <title id="title">Alex — building tools that stay inspectable</title>
  <desc id="description">Handwritten Alex signature above a technical engineering motto.</desc>
  <!-- Generated from Kalam Bold, licensed under the SIL Open Font License 1.1. -->
  <style>
    .signature {{ fill: #F0F6FC; }}
    .shadow {{ fill: #6D28D9; }}
    .subtitle {{ fill: #FF7B72; }}
    @media (prefers-color-scheme: light) {{
      .signature {{ fill: #24292F; }}
      .shadow {{ fill: #8250DF; }}
      .subtitle {{ fill: #CF222E; }}
    }}
  </style>
  <defs><g id="signature-outline">{paths}</g></defs>
  <g class="shadow" transform="translate(7 7)"><use href="#signature-outline" transform="{transform}"/></g>
  <g class="signature"><use href="#signature-outline" transform="{transform}"/></g>
  <text class="subtitle" x="480" y="190" text-anchor="middle" font-family="ui-monospace, SFMono-Regular, Menlo, monospace" font-size="24" font-weight="600" letter-spacing="5">{SUBTITLE}</text>
</svg>
'''


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--font", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    arguments = parser.parse_args()
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(build_svg(arguments.font), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
