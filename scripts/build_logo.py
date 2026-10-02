"""Make a web-safe footer mark from the OXAi logo (oxa-design-system/assets/logo-oxai.svg).

Keeps the three pills and the 'OXAi' lettering, converts the lettering to outlines
(Times New Roman, as in the source), and drops the 'Oxon Advisory Informatics'
line and tagline, since the page names the division in text beside the mark.
Pill colours come from CSS custom properties so the mark reverses in dark mode.
Output: assets/oxai-mark.svg
"""
import re
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

ROOT = Path(__file__).resolve().parent.parent
src = (ROOT / "assets" / "logo-oxai-source.svg").read_text()
FONTS = {"normal": "/System/Library/Fonts/Supplemental/Times New Roman.ttf",
         "italic": "/System/Library/Fonts/Supplemental/Times New Roman Italic.ttf"}

def outline(text, style, size, matrix):
    font = TTFont(FONTS[style]); gs = font.getGlyphSet(); cmap = font.getBestCmap(); upm = font["head"].unitsPerEm
    a, b, c, d, e, f = matrix; k = size / upm; x = 0; out = []
    for ch in text:
        name = cmap[ord(ch)]; pen = SVGPathPen(gs)
        # glyph units -> text space (scale, flip y, advance) -> source transform matrix
        t = (a * k, b * k, -c * k, -d * k, a * x * k + e, b * x * k + f)
        gs[name].draw(TransformPen(pen, t)); out.append(pen.getCommands()); x += gs[name].width
    return "".join(out)

pills = re.findall(r'<path d="([^"]+)" fill="#002046" fill-rule="evenodd" fill-opacity="([\d.]+)" transform="matrix\(([^)]+)\)"', src)
texts = re.findall(r'<text[^>]*font-style="(\w+)"[^>]*font-size="(\d+)"[^>]*transform="matrix\(([^)]+)\)">([^<]*)</text>', src)
order = {"1": "p1", "0.8": "p2", "0.6": "p3"}
parts = [f'<path class="{order[o]}" d="{d}" transform="matrix({m})"/>' for d, o, m in pills]
for style, size, m, txt in texts:
    if txt in ("OXA", "i"):
        parts.append(f'<path class="pt" d="{outline(txt, style, int(size), [float(v) for v in m.split()])}"/>')
svg = ('<svg class="oxai" viewBox="20 0 452 94" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="OXAi">'
       '<g transform="translate(-676 -101)">' + "".join(parts) + '</g></svg>')
(ROOT / "assets" / "oxai-mark.svg").write_text(svg)
print("wrote assets/oxai-mark.svg", len(svg), "bytes;", len(pills), "pills")
