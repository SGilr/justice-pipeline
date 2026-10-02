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

# ---------- legitimacy: components, groups, contact quality, relating ----------
def cell(sheet, r, c):
    return f"{POL.name}, {sheet}, cell {get_column_letter(c + 1)}{r + 1}"

comp_rows = [("Police doing a good/excellent job", "good job"), ("Police can be relied upon", "can be relied on when needed"),
             ("Police would treat you with respect", "would treat you with respect"), ("Police would treat you fairly", "would treat you fairly"),
             ("Police understand local concerns", "understand local concerns"), ("Police deal with local concerns", "deal with local concerns"),
             ("Police in this area can be trusted", "can be trusted"), ("Overall confidence", "overall confidence")]
components = []
for start, label in comp_rows:
    s = series(POL, "Table 4", lambda x, r, st=start: x.startswith(st))
    components.append({"label": label, "y2016": s["values"].get(2016), "y2020": s["values"].get(2020), "y2026": s["values"][2026], "source": s["source"]})

t5 = pd.read_excel(POL, sheet_name="Table 5", header=None)
hdr5 = [" ".join(str(c).split()) for c in t5.iloc[7]]
cF, cC, cB = hdr5.index("Police would treat you fairly (%)"), hdr5.index("Overall confidence in local police (%)"), [i for i, h in enumerate(hdr5) if h.startswith("Unweighted base")][0]
want = [("All people", "All adults"), ("Men", "Men"), ("Women", "Women"), ("White", "White"), ("Asian/Asian British", "Asian"),
        ("Black/African/Caribbean/Black British", "Black"), ("African", "Black African"), ("Caribbean", "Black Caribbean"),
        ("Mixed/Multiple", "Mixed"), ("White and Black Caribbean", "White and Black Caribbean"),
        ("Disabled", "Disabled"), ("Not disabled", "Not disabled"), ("Heterosexual", "Heterosexual"), ("Gay or Lesbian", "Gay or lesbian"), ("Bisexual", "Bisexual"),
        ("Victim", "Victim of crime in the past year"), ("Not a victim", "Not a victim"),
        ("Have ever experienced homelessness", "Ever homeless"), ("Have experienced care", "Care-experienced as a child")]
groups = []
for key, label in want:
    rows = [i for i in range(8, len(t5)) if " ".join(str(t5.iat[i, 1]).split()) == key]
    i = rows[0]
    groups.append({"label": label, "fair": round(float(t5.iat[i, cF]), 1), "confidence": round(float(t5.iat[i, cC]), 1), "base": int(t5.iat[i, cB]),
                   "source": f"{cell('Table 5', i, cF)} and {get_column_letter(cC + 1)}{i + 1}, base {get_column_letter(cB + 1)}{i + 1}"})

t17 = pd.read_excel(POL, sheet_name="Table 17", header=None)
def t17v(factor, answer):
    i = [k for k in range(len(t17)) if str(t17.iat[k, 0]).startswith(factor) and str(t17.iat[k, 1]).strip() == answer][0]
    return {"pct": round(float(t17.iat[i, 2]), 1), "base": int(t17.iat[i, 3]), "source": cell("Table 17", i, 2)}
contact = [{"label": "Treated fairly", "yes": t17v("Treated fairly", "Yes"), "no": t17v("Treated fairly", "No")},
           {"label": "Treated with respect", "yes": t17v("Treated with respect", "Yes"), "no": t17v("Treated with respect", "No")},
           {"label": "Kept well informed", "yes": t17v("How well police kept", "Well"), "no": t17v("How well police kept", "Not well")}]

t20 = pd.read_excel(POL, sheet_name="Table 20", header=None)
relating = []
for k in range(len(t20)):
    lab = " ".join(str(t20.iat[k, 0]).split())
    if lab.startswith("I would") or lab.startswith("The police show"):
        relating.append({"label": lab, "pct": round(float(t20.iat[k, 1]), 1), "source": cell("Table 20", k, 1)})

S2 = json.load(open(out)); S2["legitimacy"] = {"components": components, "groups": groups, "contact": contact, "relating": relating}
json.dump(S2, open(out, "w"), indent=1)
print("\nlegitimacy:")
for c in components: print(f"  {c['label']:30} 2016 {c['y2016']}  2026 {c['y2026']}")
for g in groups: print(f"  {g['label']:32} fair {g['fair']:5} conf {g['confidence']:5} n={g['base']}")
for c in contact: print(f"  {c['label']:22} yes {c['yes']['pct']} (n={c['yes']['base']}) no {c['no']['pct']} (n={c['no']['base']})")
for r in relating: print(f"  {r['label']:50} {r['pct']}")
