"""Extract public perception series from ONS Crime Survey for England and Wales tables.

Inputs (data/raw):
  perceptionsofpolicetablesyemarch2026.xlsx   ONS, Perception and experience of police and criminal justice system, YE March 2026
  annualsupplementarytablesyemarch2026.xlsx   ONS, Crime in England and Wales: annual supplementary tables, YE March 2026
Output: data/perceptions.json. Each series is keyed by the year the survey year ends
(April 2025 to March 2026 is 2026; calendar-year surveys keep their year) and records its table and row.
"""
import json, re
from pathlib import Path
import pandas as pd
from openpyxl.utils import get_column_letter

RAW = Path(__file__).resolve().parent.parent / "data" / "raw"
POL = RAW / "perceptionsofpolicetablesyemarch2026.xlsx"
SUP = RAW / "annualsupplementarytablesyemarch2026.xlsx"


def year_of(h):
    h = " ".join(str(h).split())
    m = re.search(r"(?:Apr|April)\w* (\d{4}) to (?:Mar|March)\w* (\d{4})", h)
    if m: return int(m.group(2))
    m = re.search(r"Jan\w* (\d{4}) to Dec\w* (\d{4})", h)
    if m: return int(m.group(2))
    return None


def series(path, sheet, row_match, label_col=0, extra=None):
    v = pd.read_excel(path, sheet_name=sheet, header=None)
    hdr = next(i for i in range(len(v)) if sum(year_of(c) is not None for c in v.iloc[i]) > 3)
    rows = [i for i in range(hdr + 1, len(v)) if row_match(str(v.iat[i, label_col]), v.iloc[i])]
    assert len(rows) == 1, (sheet, rows)
    r = rows[0]; out = {}; seen = set(); cols = []
    for j, h in enumerate(v.iloc[hdr]):
        y = year_of(h)
        if y is None or y in seen: continue  # later duplicate columns are significance tests
        val = pd.to_numeric(v.iat[r, j], errors="coerce")
        if pd.notna(val):
            out[y] = round(float(val), 1); seen.add(y); cols.append(get_column_letter(j + 1))
    return {"values": out, "source": f"{path.name}, {sheet}, row {r + 1} ({' '.join(str(v.iat[r, label_col]).split())[:70]}), columns {cols[0]} to {cols[-1]}"}


S = {}
S["confidence"] = series(POL, "Table 4", lambda s, r: s.startswith("Overall confi"))
S["trust"] = series(POL, "Table 21", lambda s, r: s.startswith("England and W"))
S["patrol"] = series(POL, "Table 10", lambda s, r: s.startswith("High visibili"))
rating = series(POL, "Table 1", lambda s, r: s.strip() == "Excellent")
good = series(POL, "Table 1", lambda s, r: s.strip() == "Good")
S["rating"] = {"values": {y: round(rating["values"][y] + good["values"][y], 1) for y in rating["values"]},
               "source": rating["source"] + " plus 'Good' row; summed"}
S["risingNational"] = series(SUP, "Table B1", lambda s, r: s.startswith("Crime has g") and str(r.iloc[1]).strip() == "National")
S["risingLocal"] = series(SUP, "Table B1", lambda s, r: s.startswith("Crime has g") and str(r.iloc[1]).strip() == "Local")
S["worryViolent"] = series(SUP, "Table B4", lambda s, r: s.startswith("Violent cri"))
S["safeWomen"] = series(SUP, "Table B7", lambda s, r: s.strip() == "Females")
S["safeMen"] = series(SUP, "Table B7", lambda s, r: s.strip() == "Males")

out = Path(__file__).resolve().parent.parent / "data" / "perceptions.json"
json.dump(S, open(out, "w"), indent=1)
for k, s in S.items():
    ys = sorted(s["values"]); print(f"{k:15} {ys[0]}..{ys[-1]} n={len(ys)} first={s['values'][ys[0]]} last={s['values'][ys[-1]]}\n   {s['source']}")
