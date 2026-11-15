"""Generate original, product-specific JARVIS listing copy and vector cover artwork."""
from __future__ import annotations
import argparse
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "ai-agents" / "products"
PALETTES = {
    "rankmaster-ai": "#55D6BE", "leadscout-bot": "#7AA8FF",
    "tradetrend-analyst": "#E7BC68", "docusense-support": "#B79CFF",
    "socialsync-ai": "#F08AB7", "mailforge-pro": "#71D5E6",
    "contentflip-ai": "#FF9D72", "estateguard-ai": "#A6D48A",
    "codesentinel": "#F28A83", "marketmind-ai": "#D2B3FF",
}
ICONS = {
    "rankmaster-ai": '<circle cx="0" cy="0" r="76"/><path d="M54 54 L112 112 M-44 26 L-12 -8 L18 10 L52 -42 M-44 54 H52"/>',
    "leadscout-bot": '<circle cx="-42" cy="-18" r="26"/><circle cx="42" cy="-18" r="26"/><circle cx="0" cy="48" r="26"/><path d="M-20 -4 L-6 24 M20 -4 L6 24 M-16 -18 H16"/>',
    "tradetrend-analyst": '<path d="M-110 48 L-64 8 L-22 26 L24 -42 L62 -16 L110 -88 M-110 74 H110 M-110 -74 V74"/><circle cx="110" cy="-88" r="10"/>',
    "docusense-support": '<path d="M-72 -104 H34 L76 -62 V104 H-72 Z M34 -104 V-62 H76 M-42 -20 H44 M-42 12 H30 M-42 44 H18"/><circle cx="50" cy="48" r="30"/><path d="M72 70 L100 98"/>',
    "socialsync-ai": '<circle cx="-66" cy="-48" r="25"/><circle cx="66" cy="-48" r="25"/><circle cx="0" cy="66" r="25"/><path d="M-44 -32 L-14 42 M44 -32 L14 42 M-40 -48 H40"/>',
    "mailforge-pro": '<rect x="-104" y="-70" width="208" height="140" rx="18"/><path d="M-96 -56 L0 18 L96 -56 M-96 56 L-28 0 M96 56 L28 0"/>',
    "contentflip-ai": '<rect x="-106" y="-76" width="212" height="152" rx="20"/><path d="M-28 -42 L54 0 L-28 42 Z M-70 102 H70 M-54 122 H54"/>',
    "estateguard-ai": '<path d="M0 -112 L88 -78 V-8 C88 48 48 94 0 118 C-48 94 -88 48 -88 -8 V-78 Z M-42 0 L-10 32 L48 -34"/>',
    "codesentinel": '<path d="M-26 -88 L-94 0 L-26 88 M26 -88 L94 0 L26 88 M12 -112 L-12 112"/>',
    "marketmind-ai": '<circle cx="0" cy="0" r="92"/><path d="M0 -120 L24 -18 L120 0 L24 18 L0 120 L-24 18 L-120 0 L-24 -18 Z"/><circle cx="0" cy="0" r="18"/>',
}

def esc(value: object) -> str:
    return html.escape(str(value), quote=True)

def wrap(text: str, width: int = 48) -> list[str]:
    words = text.split()
    lines, current = [], ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if len(candidate) > width and current:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines[:3]

def cover_svg(product: dict, square: bool = False) -> str:
    slug, name = product["slug"], product["name"]
    accent, icon = PALETTES[slug], ICONS[slug]
    if square:
        title_y, title_size, subtitle_y, width, height = 535, 62, 610, 800, 800
        subtitle, label = "INTELLIGENT BUSINESS AGENT", "JARVIS COLLECTION"
        title_x, icon_x, icon_y, icon_scale = 80, 400, 300, 1.45
    else:
        title_y, title_size, subtitle_y, width, height = 570, 82, 660, 1600, 1000
        subtitle, label = product["hero"].upper(), "JARVIS  /  INTELLIGENT BUSINESS AGENTS"
        title_x, icon_x, icon_y, icon_scale = 120, 1190, 470, 2.2
    lines = wrap(subtitle, 30 if square else 46)
    subtitle_markup = "".join(f'<tspan x="{title_x}" dy="{0 if i == 0 else 38}">{esc(line)}</tspan>' for i, line in enumerate(lines))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">
<title id="title">{esc(name)} — JARVIS AI Agent</title><desc id="desc">{esc(product["hero"])}</desc>
<defs>
<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#101A2B"/><stop offset="1" stop-color="#202C40"/></linearGradient>
<linearGradient id="glow" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{accent}" stop-opacity=".34"/><stop offset="1" stop-color="{accent}" stop-opacity="0"/></linearGradient>
<filter id="soft"><feGaussianBlur stdDeviation="36"/></filter>
</defs>
<rect width="100%" height="100%" fill="url(#bg)"/>
<circle cx="{icon_x}" cy="{icon_y}" r="290" fill="url(#glow)" filter="url(#soft)"/>
<path d="M0 820 C360 720 560 1060 980 880 S1420 780 1600 860" fill="none" stroke="{accent}" stroke-opacity=".13" stroke-width="2"/>
<path d="M0 870 C360 770 560 1110 980 930 S1420 830 1600 910" fill="none" stroke="#FFFFFF" stroke-opacity=".06" stroke-width="2"/>
<g transform="translate({icon_x} {icon_y}) scale({icon_scale})" fill="none" stroke="{accent}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round">{icon}</g>
<circle cx="{icon_x}" cy="{icon_y}" r="{205 if square else 250}" fill="none" stroke="{accent}" stroke-opacity=".26" stroke-width="2"/>
<circle cx="{icon_x}" cy="{icon_y}" r="{245 if square else 300}" fill="none" stroke="#FFFFFF" stroke-opacity=".08" stroke-width="2" stroke-dasharray="8 18"/>
<text x="{title_x}" y="110" fill="{accent}" font-family="Inter,Arial,sans-serif" font-size="26" font-weight="700" letter-spacing="5">{esc(label)}</text>
<text x="{title_x}" y="{title_y}" fill="#F4F0E7" font-family="Inter,Arial,sans-serif" font-size="{title_size}" font-weight="750">{esc(name)}</text>
<text x="{title_x}" y="{subtitle_y}" fill="#C2CBD8" font-family="Inter,Arial,sans-serif" font-size="{22 if square else 28}" font-weight="500">{subtitle_markup}</text>
<rect x="{title_x}" y="{height-100}" width="90" height="5" rx="2.5" fill="{accent}"/>
<text x="{title_x}" y="{height-52}" fill="#9AA4B2" font-family="Inter,Arial,sans-serif" font-size="20" letter-spacing="3">ZUBAIR DIGITAL KITS</text>
<text x="{width-80}" y="{height-52}" fill="#9AA4B2" font-family="Inter,Arial,sans-serif" font-size="18" text-anchor="end">LOCAL-FIRST EDITION</text>
</svg>'''

def listing_markdown(product: dict) -> str:
    lines = [
        f"# {product['name']}", "", f"> {product['hero']}", "",
        f"**SEO title:** {product['seo_title']}  ",
        f"**Meta description:** {product['meta_description']}  ",
        f"**Primary keyword:** {product['primary_keyword']}  ",
        f"**Tags:** {', '.join(product['tags'])}", "",
        "## The problem", "", product["problem"], "",
        "## What this product does", "", product["solution"], "",
        "## What is included", "",
    ]
    lines.extend(f"- {item}" for item in product["included"])
    lines += ["", "## Frequently asked questions", ""]
    for question, answer in product["faq"]:
        lines += [f"### {question}", "", answer, ""]
    lines += ["## Next step", "", product["cta"], "", "---", "", "Published by Zubair Digital Kits · JARVIS Intelligent Business & Productivity Agents", ""]
    return "\n".join(lines)

def build(output: Path) -> int:
    manifest = json.loads((ROOT / "ai-agents" / "runtime" / "seo-listings.json").read_text(encoding="utf-8"))
    products = manifest["listings"]
    output.mkdir(parents=True, exist_ok=True)
    for product in products:
        directory = output / product["slug"]
        assets = directory / "assets"
        assets.mkdir(parents=True, exist_ok=True)
        (directory / "listing.md").write_text(listing_markdown(product), encoding="utf-8")
        (assets / "cover.svg").write_text(cover_svg(product), encoding="utf-8")
        (assets / "thumbnail.svg").write_text(cover_svg(product, square=True), encoding="utf-8")
    return len(products)

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    count = build(args.output)
    print(f"Generated listing copy and two original SVG assets for {count} products in {args.output}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
