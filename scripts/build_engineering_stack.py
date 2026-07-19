#!/usr/bin/env python3
import argparse
from dataclasses import dataclass
from pathlib import Path
from xml.sax.saxutils import escape


@dataclass(frozen=True)
class StackNode:
    label: str
    mark: str
    x: int
    accent: str
    delay: float


@dataclass(frozen=True)
class StackGroup:
    name: str
    x: int
    width: int
    nodes: tuple[StackNode, ...]


STACK_GROUPS = (
    StackGroup("BUILD", 30, 238, (
        StackNode("TypeScript", "TS", 92, "#3178C6", 0.0),
        StackNode("Node.js", "JS", 210, "#3C873A", 0.85),
    )),
    StackGroup("AUTOMATE", 282, 266, (
        StackNode("pnpm", "pn", 350, "#F69220", 1.70),
        StackNode("GitHub Actions", "GH", 480, "#2088FF", 2.55),
    )),
    StackGroup("VERIFY", 562, 368, (
        StackNode("Vitest", "Vi", 624, "#729B1B", 3.40),
        StackNode("Playwright", "Pw", 752, "#2EAD33", 4.25),
        StackNode("Git", "G", 872, "#F05032", 5.10),
    )),
)

PALETTES = {
    "dark": {
        "surface": "#0D1117", "panel": "#10151D", "border": "#30363D",
        "text": "#F0F6FC", "muted": "#8B949E", "route": "#4B5563",
        "violet": "#A371F7", "coral": "#FF7B72", "cyan": "#39D0D8",
    },
    "light": {
        "surface": "#F6F8FA", "panel": "#FFFFFF", "border": "#D0D7DE",
        "text": "#24292F", "muted": "#57606A", "route": "#8C959F",
        "violet": "#8250DF", "coral": "#CF222E", "cyan": "#0969DA",
    },
}

OUTPUTS = (
    ("engineering-stack-dark.svg", "dark", True),
    ("engineering-stack-light.svg", "light", True),
    ("engineering-stack-dark-static.svg", "dark", False),
    ("engineering-stack-light-static.svg", "light", False),
)

MOBILE_NODE_POSITIONS = {
    "TypeScript": (16, 123),
    "Node.js": (16, 204),
    "pnpm": (247, 123),
    "GitHub Actions": (247, 204),
    "Vitest": (486, 123),
    "Playwright": (726, 123),
    "Git": (606, 204),
}


def render_node(node: StackNode, palette: dict[str, str], animated: bool) -> str:
    mobile_x, mobile_y = MOBILE_NODE_POSITIONS[node.label]
    style_declarations = [
        f"--mobile-x:{mobile_x}px",
        f"--mobile-y:{mobile_y}px",
    ]
    if animated:
        style_declarations.append(f"--delay:{node.delay:.2f}s")
    style = f' style="{";".join(style_declarations)}"'
    class_name = "stack-node animated-node" if animated else "stack-node"
    return f'''<g class="{class_name}" transform="translate({node.x - 52} 154)"{style}>
      <rect width="104" height="70" rx="14" fill="{palette['panel']}" stroke="{palette['border']}"/>
      <circle cx="20" cy="22" r="10" fill="{node.accent}" fill-opacity=".18"/>
      <text x="20" y="26" text-anchor="middle" fill="{node.accent}" font-size="10" font-weight="700">{escape(node.mark)}</text>
      <text x="52" y="52" text-anchor="middle" class="node-label">{escape(node.label)}</text>
    </g>'''


def build_svg(theme: str, animated: bool) -> str:
    if theme not in PALETTES:
        raise ValueError(f"unsupported theme: {theme}")
    palette = PALETTES[theme]
    groups = "".join(
        f'''<g class="stack-group">
          <rect x="{group.x}" y="118" width="{group.width}" height="130" rx="18" fill="{palette['panel']}" stroke="{palette['border']}"/>
          <text x="{group.x + 18}" y="142" class="group-label">{group.name}</text>
          {''.join(render_node(node, palette, animated) for node in group.nodes)}
        </g>'''
        for group in STACK_GROUPS
    )
    motion_css = "" if not animated else '''
      @keyframes node-signal { 0%,72%,100% { filter:none; } 8%,18% { filter:url(#node-glow); } }
      .animated-node { animation:node-signal 6s ease-in-out infinite; animation-delay:var(--delay); }
    '''
    motion = "" if not animated else f'''
      <circle r="5" fill="{palette['cyan']}" filter="url(#signal-glow)">
        <animateMotion dur="6s" repeatCount="indefinite"><mpath href="#engineering-route"/></animateMotion>
      </circle>
      <rect x="30" y="91" width="120" height="2" rx="1" fill="{palette['coral']}" opacity=".85">
        <animate attributeName="x" values="30;810;30" dur="6s" repeatCount="indefinite"/>
      </rect>'''
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 300" role="img" aria-labelledby="engineering-stack-title engineering-stack-description">
  <title id="engineering-stack-title">Alex engineering stack</title>
  <desc id="engineering-stack-description">A connected public toolchain: TypeScript and Node.js for building, pnpm and GitHub Actions for automation, and Vitest, Playwright, and Git for verification.</desc>
  <defs>
    <filter id="signal-glow" x="-200%" y="-200%" width="500%" height="500%"><feGaussianBlur stdDeviation="3" result="blur"/><feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
    <filter id="node-glow" x="-20%" y="-20%" width="140%" height="140%"><feDropShadow dx="0" dy="0" stdDeviation="3" flood-color="{palette['violet']}" flood-opacity=".55"/></filter>
    <style>
      text {{ font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace; }}
      .title {{ fill:{palette['text']}; font-size:24px; font-weight:700; letter-spacing:4px; }}
      .subtitle,.group-label {{ fill:{palette['muted']}; font-size:12px; font-weight:600; letter-spacing:2px; }}
      .node-label {{ fill:{palette['text']}; font-size:12px; font-weight:600; }}
      {motion_css}
      @media (max-width: 480px) {{
        .title {{ font-size:28px; letter-spacing:2px; }}
        .subtitle {{ font-size:21px; letter-spacing:1px; }}
        .group-label {{ font-size:21px; letter-spacing:1px; }}
        .node-label {{ font-size:21px; }}
        .stack-group:nth-of-type(1) > rect {{ x:8px; y:96px; width:228px; height:188px; }}
        .stack-group:nth-of-type(2) > rect {{ x:239px; y:96px; width:228px; height:188px; }}
        .stack-group:nth-of-type(3) > rect {{ x:478px; y:96px; width:474px; height:188px; }}
        .stack-group:nth-of-type(1) > .group-label {{ x:22px; y:112px; }}
        .stack-group:nth-of-type(2) > .group-label {{ x:253px; y:112px; }}
        .stack-group:nth-of-type(3) > .group-label {{ x:492px; y:112px; }}
        .stack-node {{ transform:translate(var(--mobile-x), var(--mobile-y)); }}
        .stack-node > rect {{ width:218px; height:70px; }}
        .stack-node > text:first-of-type {{ font-size:16px; }}
        .stack-node > .node-label {{ x:122px; }}
      }}
    </style>
  </defs>
  <rect x="1" y="1" width="958" height="298" rx="22" fill="{palette['surface']}" stroke="{palette['border']}" stroke-width="2"/>
  <text x="30" y="48" class="title">ENGINEERING STACK</text>
  <text x="30" y="75" class="subtitle">PUBLIC TOOLCHAIN · VERIFIED BY WORK</text>
  <path id="engineering-route" d="M92 188 H872" fill="none" stroke="{palette['route']}" stroke-width="2"/>
  {groups}
  {motion}
</svg>\n'''


def write_assets(output_dir: Path) -> tuple[Path, ...]:
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    for filename, theme, animated in OUTPUTS:
        path = output_dir / filename
        path.write_text(build_svg(theme, animated), encoding="utf-8")
        paths.append(path)
    return tuple(paths)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build Engineering Stack SVG assets")
    parser.add_argument("--output-dir", required=True, type=Path)
    arguments = parser.parse_args()
    write_assets(arguments.output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
