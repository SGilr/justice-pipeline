"""Download HMPPS weekly population and capacity bulletins (2024 to 2026) and extract
total population, useable operational capacity and headroom for each Monday.
Output: data/weekly_capacity.json
"""
import json, re, datetime, urllib.request
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw" / "weekly"; RAW.mkdir(parents=True, exist_ok=True)
PAGES = ["prison-population-figures-2024", "prison-population-weekly-estate-figures-2025", "prison-population-weekly-estate-figures-2026"]

def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    return urllib.request.urlopen(req, timeout=60).read()

rows = []
for page in PAGES:
    d = json.loads(get(f"https://www.gov.uk/api/content/government/publications/{page}"))
    for a in d["details"].get("attachments", []):
        url = a.get("url", "")
        if not url.endswith((".ods", ".xlsx", ".xls")): continue
        fn = RAW / url.rsplit("/", 2)[-2] + "_" + url.rsplit("/", 1)[-1] if False else RAW / (url.rsplit("/", 2)[-2] + "_" + url.rsplit("/", 1)[-1])
        if not fn.exists(): fn.write_bytes(get(url))
        try:
            x = pd.read_excel(fn, sheet_name=0, header=None, engine="odf" if fn.suffix == ".ods" else None)
        except Exception as e:
            print("skip", fn.name, e); continue
        cells = x.astype(str)
        def val(label):
            for i in range(min(len(x), 15)):
                for j in range(x.shape[1]):
                    if cells.iat[i, j].strip().lower().startswith(label):
                        for k in range(j + 1, x.shape[1]):
                            v = pd.to_numeric(x.iat[i, k], errors="coerce")
                            if pd.notna(v): return int(v)
            return None
        title = " ".join(cells.iloc[:5].values.ravel())
        m = re.search(r"(\d{1,2})(?:st|nd|rd|th)?\s+([A-Za-z]+)\s+(\d{4})", title) or re.search(r"(\d{1,2})(?:st|nd|rd|th)?\s+([A-Za-z]+)\s+(\d{4})", a.get("title", ""))
        try:
            date = datetime.datetime.strptime(f"{m.group(1)} {m.group(2)[:3]} {m.group(3)}", "%d %b %Y").date().isoformat()
        except Exception:
            print("no date", fn.name, a.get("title")); continue
        pop, cap = val("population"), val("useable operational capacity")
        if pop and cap:
            rows.append({"date": date, "pop": pop, "cap": cap, "headroom": cap - pop})
        else:
            print("no values", fn.name)
rows = sorted({r["date"]: r for r in rows}.values(), key=lambda r: r["date"])
json.dump(rows, open(ROOT / "data" / "weekly_capacity.json", "w"), indent=0)
print(len(rows), "weeks", rows[0]["date"], "to", rows[-1]["date"])
