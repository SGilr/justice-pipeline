"""Assemble the page: inline force data into src/page.html.

Writes justice-pipeline.html (the Claude artifact body) and site/index.html (a full standalone document for hosting).
"""
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
src = (ROOT / "src" / "page.html").read_text()
forces = (ROOT / "data" / "forces.json").read_text()
weekly = (ROOT / "data" / "weekly_capacity.json").read_text()
body = src.replace("/*FORCES*/null", forces).replace("/*WEEKLY*/null", weekly.replace("\n", ""))
logo = (ROOT / "assets" / "oxai-mark.svg").read_text()
body = body.replace("<!--LOGO-->", logo)
assert "/*FORCES*/" not in body and "<!--LOGO-->" not in body and "/*WEEKLY*/" not in body, "placeholder not found"
(ROOT / "justice-pipeline.html").write_text(body)
title = "The Justice Pipeline"
desc = "Police numbers, crime, courts, prisons and children in custody in England and Wales, 2000 to 2026, on one interactive timeline with force-level maps."
head = f"""<!doctype html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="description" content="{desc}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="website">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3E%3Crect x='1' y='9' width='3' height='6' fill='%232a78d6'/%3E%3Crect x='6.5' y='5' width='3' height='10' fill='%23008300'/%3E%3Crect x='12' y='1' width='3' height='14' fill='%23eda100'/%3E%3C/svg%3E">
<style>html{{-webkit-text-size-adjust:100%}}body{{margin:0}}img{{max-width:100%}}[hidden]{{display:none!important}}</style>
</head>
<body>
"""
page = body.replace('<meta charset="utf-8">\n', "", 1)
(ROOT / "site" / "index.html").write_text(head + page + "\n</body>\n</html>\n")
print("wrote justice-pipeline.html and site/index.html")
