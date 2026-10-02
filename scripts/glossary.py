"""Mark glossary terms in the page and build the glossary list.

The first appearance of each term in the main text (outside headings, links, buttons,
SVG and scripts) is wrapped in a focusable span whose definition is the matching
<dd> in the glossary list, referenced with aria-describedby.
"""
import html, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP = {"a", "h1", "h2", "h3", "button", "label", "summary", "svg", "script", "style", "title", "select", "option", "th", "dt", "textarea"}
VOID = {"br", "img", "input", "meta", "link", "hr", "source", "wbr", "path", "circle", "rect", "line"}


def _wrap_first(region, phrases, key):
    """Return region with the earliest eligible match of any phrase wrapped, plus the phrase used."""
    tokens = re.split(r"(<[^>]+>)", region)
    stack, best = [], None  # stack of (tag name, is a glossary span)
    for i, tok in enumerate(tokens):
        if tok.startswith("<"):
            m = re.match(r"</?\s*([a-zA-Z0-9]+)", tok)
            name = m.group(1).lower() if m else ""
            if tok.startswith("</"):
                for j in range(len(stack) - 1, -1, -1):
                    if stack[j][0] == name:
                        del stack[j:]; break
            elif not tok.endswith("/>") and name not in VOID and not tok.startswith("<!"):
                stack.append((name, 'class="g"' in tok))
        elif tok.strip() and not any(n in SKIP or g for n, g in stack):
            for ph in phrases:
                mm = re.search(r"(?<![A-Za-z])" + re.escape(ph) + r"(?![A-Za-z])", tok)
                if mm and (best is None or (i, mm.start()) < (best[0], best[1])):
                    best = (i, mm.start(), mm.end(), ph)
    if best is None:
        return region, None
    i, a, b, ph = best
    t = tokens[i]
    tokens[i] = t[:a] + f'<span class="g" tabindex="0" data-g="{key}" aria-describedby="gdef-{key}">{t[a:b]}</span>' + t[b:]
    return "".join(tokens), ph


def apply(body):
    terms = json.loads((ROOT / "data" / "glossary.json").read_text())
    start, end = body.index('<header class="hero">'), body.index('<!--GLOSSARY-->')
    region, report = body[start:end], []
    for t in terms:
        region, used = _wrap_first(region, t["match"], t["key"])
        report.append((t["key"], used))
    items = "".join(f'<dt id="g-{t["key"]}">{html.escape(t["term"])}</dt><dd id="gdef-{t["key"]}">{html.escape(t["def"])}</dd>' for t in sorted(terms, key=lambda t: t["term"].lower()))
    gl = ('<h3 style="margin-top:8px" id="glossary">Glossary</h3>'
          '<p class="note">Terms with a dotted underline in the text show these definitions on hover, tap or keyboard focus.</p>'
          f'<dl class="gloss">{items}</dl>')
    body = body[:start] + region + body[end:]
    assert "<!--GLOSSARY-->" in body
    return body.replace("<!--GLOSSARY-->", gl), report
