"""Make web-safe marks from the Oxon Advisory logos in oxa-design-system/assets.

Lettering is converted to outlines (Times New Roman, as in the sources) so the marks
render identically everywhere, and colours come from CSS custom properties so they
reverse in dark mode.

- assets/oxai-mark.svg: footer mark from logo-oxai.svg. Keeps the three pills and the
  'OXAi' lettering; drops the 'Oxon Advisory Informatics' line and tagline, because the
  page names the division (Prevention Informatics) in text beside the mark.
- assets/oxa-wordmark.svg: header mark from logo-wordmark.svg. The full Oxon Advisory
  lockup: three overlapping pills, the wordmark and the tagline.
"""
import re
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen

ROOT = Path(__file__).resolve().parent.parent
FONTS = {"normal": "/System/Library/Fonts/Supplemental/Times New Roman.ttf",
         "italic": "/System/Library/Fonts/Supplemental/Times New Roman Italic.ttf"}


def mat(m):
    return [float(v) for v in m.split()]


def apply(m, x, y):
    a, b, c, d, e, f = m
    return a * x + c * y + e, b * x + d * y + f


def outline(text, style, size, m, bounds):
    """Glyph outlines for text drawn with the source <text> transform m; extends bounds."""
    font = TTFont(FONTS[style]); gs = font.getGlyphSet(); cmap = font.getBestCmap()
    k = size / font["head"].unitsPerEm; a, b, c, d, e, f = m; x = 0; out = []
    for ch in text:
        name = cmap[ord(ch)]
        t = (a * k, b * k, -c * k, -d * k, a * x * k + e, b * x * k + f)
        pen = SVGPathPen(gs, ntos=lambda v: ("%.2f" % v).rstrip("0").rstrip(".")); gs[name].draw(TransformPen(pen, t)); out.append(pen.getCommands())
        bp = BoundsPen(gs); gs[name].draw(TransformPen(bp, t))
        if bp.bounds:
            bounds.extend([(bp.bounds[0], bp.bounds[1]), (bp.bounds[2], bp.bounds[3])])
        x += gs[name].width
    return "".join(out)


def path_points(d, m):
    nums = [float(v) for v in re.findall(r"-?\d+(?:\.\d+)?", d)]
    return [apply(m, nums[i], nums[i + 1]) for i in range(0, len(nums) - 1, 2)]


def build(src_name, out_name, css_class, pill_classes, text_classes, label, pad=2):
    src = (ROOT / "assets" / src_name).read_text()
    gx, gy = [float(v) for v in re.search(r'<g transform="translate\(([-\d.]+) ([-\d.]+)\)"', src).groups()]
    pills = re.findall(r'<path d="([^"]+)" fill="([^"]+)" fill-rule="evenodd" fill-opacity="([\d.]+)" transform="matrix\(([^)]+)\)"', src)
    texts = re.findall(r'<text[^>]*font-style="(\w+)"[^>]*font-size="(\d+)"[^>]*transform="matrix\(([^)]+)\)">([^<]*)</text>', src)
    parts, pts = [], []
    for i, (d, fill, op, m) in enumerate(pills):
        parts.append(f'<path class="{pill_classes(i, fill, op)}" d="{d}" transform="matrix({m})"/>')
        pts += path_points(d, mat(m))
    for style, size, m, txt in texts:
        cls = text_classes(txt)
        if cls:
            parts.append(f'<path class="{cls}" d="{outline(txt, style, int(size), mat(m), pts)}"/>')
    xs = [p[0] + gx for p in pts]; ys = [p[1] + gy for p in pts]
    vb = f"{min(xs) - pad:.1f} {min(ys) - pad:.1f} {max(xs) - min(xs) + 2 * pad:.1f} {max(ys) - min(ys) + 2 * pad:.1f}"
    svg = (f'<svg class="{css_class}" viewBox="{vb}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{label}">'
           f'<g transform="translate({gx:g} {gy:g})">' + "".join(parts) + "</g></svg>")
    (ROOT / "assets" / out_name).write_text(svg)
    print(f"wrote assets/{out_name}: {len(svg)} bytes, viewBox {vb}")


# Footer: OXAi pills, ranked by opacity (1, 0.8, 0.6) as p1, p2, p3
build("logo-oxai-source.svg", "oxai-mark.svg", "oxai",
      lambda i, fill, op: {"1": "p1", "0.8": "p2", "0.6": "p3"}[op],
      lambda t: "pt" if t in ("OXA", "i") else None, "OXAi", pad=0)

# Header: Oxon Advisory lockup, pills ranked by fill colour as w1, w2, w3
build("logo-wordmark-source.svg", "oxa-wordmark.svg", "oxa-wm",
      lambda i, fill, op: {"#002046": "w1", "#3B546F": "w2", "#728296": "w3"}[fill],
      lambda t: "wt" if t == "Oxon Advisory" else ("wg" if t.startswith("working") else None), "Oxon Advisory")
