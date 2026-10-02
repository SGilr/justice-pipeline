"""Build force-level indicators and simplified boundaries for the force maps.

Inputs (data/raw):
  open-data-table-police-workforce-220726.ods  Home Office police workforce open data, 31 March 2007 to 2026
  pfatablesyemarch2026.xlsx                      ONS police force area tables, year ending March 2026
  stop-search-data-tables-summary-mar25.ods    Home Office stop and search summary tables, year ending March 2025
  police_force_areas_dec2023_bgc.geojson       ONS Police Force Areas (December 2023) generalised boundaries
Output: data/forces.json
"""
import json, math
from pathlib import Path
import pandas as pd

RAW = Path(__file__).resolve().parent.parent / "data" / "raw"
OUT = Path(__file__).resolve().parent.parent / "data" / "forces.json"

# Workforce: officer FTE by force in 2010 and 2026
wf = pd.read_excel(RAW / "open-data-table-police-workforce-220726.ods", engine="odf", sheet_name="Data")
wf["fte"] = pd.to_numeric(wf["Total (FTE)"], errors="coerce")
wf = wf[wf["Geocode"].str.startswith(("E23", "W15"))]
off = wf[wf["Worker type"] == "Police Officer"].pivot_table(index="Geocode", columns="As at 31 March", values="fte", aggfunc="sum")

# ONS: population (mid-2024) and recorded crime rate per 1,000, year ending March 2026
p3 = pd.read_excel(RAW / "pfatablesyemarch2026.xlsx", sheet_name="Table P3", header=None)
hdr = p3.index[p3[0].astype(str).str.strip() == "Area Code"][0]
p3 = p3.iloc[hdr + 1:, :5]
p3.columns = ["code", "name", "pop", "hh", "crime_rate"]
p3 = p3[p3["code"].astype(str).str.match(r"^(E23|W15)")]
p3["pop"] = pd.to_numeric(p3["pop"], errors="coerce")
p3["crime_rate"] = pd.to_numeric(p3["crime_rate"], errors="coerce")
p3 = p3.set_index("code")

# Stop and search: Black and White searches (self-defined) and Census 2021 population
ssf = RAW / "stop-search-data-tables-summary-mar25.ods"
ss = pd.read_excel(ssf, engine="odf", sheet_name="SS_05", header=None)
h = ss.index[ss[0].astype(str) == "Geocode"][0]
ss.columns = [str(c) for c in ss.iloc[h]]
ss = ss.iloc[h + 1:]
ss = ss[ss["Geocode"].astype(str).str.match(r"^(E23|W15)")].set_index("Geocode")
pp = pd.read_excel(ssf, engine="odf", sheet_name="P_1", header=None)
h = pp.index[pp[0].astype(str) == "Census Year"][0]
pp.columns = [str(c) for c in pp.iloc[h]]
pp = pp.iloc[h + 1:]
pp = pp[pp["Census Year"].astype(str).str.startswith("2021")]
pp["Population"] = pd.to_numeric(pp["Population"], errors="coerce")
pop_eth = pp.pivot_table(index="Geocode", columns="Self-defined ethnicity", values="Population", aggfunc="sum")

def col(df, key):
    return [c for c in df.columns if key in str(c)][0]

# Boundaries: project, simplify (Douglas-Peucker), emit SVG paths in a 1000-wide frame
gj = json.load(open(RAW / "police_force_areas_dec2023_bgc.geojson"))
K = math.cos(math.radians(52.5))
def proj(pt): return (pt[0] * K, -pt[1])
def dp(pts, tol):
    if len(pts) < 3: return pts
    a, b = pts[0], pts[-1]
    dx, dy = b[0] - a[0], b[1] - a[1]
    L = math.hypot(dx, dy) or 1e-12
    dmax, idx = 0, 0
    for i in range(1, len(pts) - 1):
        d = abs(dy * pts[i][0] - dx * pts[i][1] + b[0] * a[1] - b[1] * a[0]) / L
        if d > dmax: dmax, idx = d, i
    if dmax > tol:
        return dp(pts[: idx + 1], tol)[:-1] + dp(pts[idx:], tol)
    return [a, b]
rings = {}
allpts = []
for f in gj["features"]:
    code = f["properties"]["PFA23CD"]
    polys = f["geometry"]["coordinates"] if f["geometry"]["type"] == "MultiPolygon" else [f["geometry"]["coordinates"]]
    rs = []
    for poly in polys:
        for ring in poly[:1]:  # outer rings only; force areas have no meaningful holes at this scale
            pr = [proj(p) for p in ring]
            m = max(range(len(pr)), key=lambda i: (pr[i][0] - pr[0][0]) ** 2 + (pr[i][1] - pr[0][1]) ** 2)
            s = dp(pr[: m + 1], 0.004)[:-1] + dp(pr[m:], 0.004)  # split closed ring so its ends differ
            area = abs(sum(s[i][0] * s[i - 1][1] - s[i - 1][0] * s[i][1] for i in range(len(s)))) / 2
            if len(s) >= 4 and area > 2e-4 or code == "E23000034":
                rs.append(s); allpts += s
    rings[code] = rs
minx = min(p[0] for p in allpts); maxx = max(p[0] for p in allpts)
miny = min(p[1] for p in allpts); maxy = max(p[1] for p in allpts)
S = 1000 / (maxx - minx)
H = round((maxy - miny) * S)
def path(rs):
    return "".join("M" + "L".join(f"{(x - minx) * S:.1f},{(y - miny) * S:.1f}" for x, y in r) + "Z" for r in rs)
cent = {}
for code, rs in rings.items():
    big = max(rs, key=len)
    cent[code] = [round(sum((p[0] - minx) * S for p in big) / len(big), 1), round(sum((p[1] - miny) * S for p in big) / len(big), 1)]

forces = []
for f in gj["features"]:
    code, name = f["properties"]["PFA23CD"], f["properties"]["PFA23NM"]
    o10 = float(off.loc[code, 2010]); o26 = float(off.loc[code, 2026])
    pop = float(p3.loc[code, "pop"]) if code in p3.index else None
    cr = p3.loc[code, "crime_rate"] if code in p3.index else None
    rec = {"code": code, "name": name, "off2010": round(o10), "off2026": round(o26),
           "offChange": round((o26 / o10 - 1) * 100, 1), "pop": pop,
           "per100k": round(o26 / pop * 1e5, 1) if pop else None,
           "crimeRate": round(float(cr), 1) if cr is not None and not pd.isna(cr) else None,
           "path": path(rings[code]), "c": cent[code]}
    if code in ss.index and code in pop_eth.index:
        b = float(ss.loc[code, col(ss, "Black")]); w = float(ss.loc[code, col(ss, "White")])
        pb = float(pop_eth.loc[code, col(pop_eth, "Black")]); pw = float(pop_eth.loc[code, col(pop_eth, "White")])
        rec["ssBlack"], rec["ssWhite"] = int(b), int(w)
        rec["ssRatio"] = round((b / pb) / (w / pw), 1) if b >= 30 and w > 0 else None
    if code == "E23000034":  # City of London: resident population too small for per-head rates
        rec["per100k"] = None; rec["crimeRate"] = None; rec["ssRatio"] = None; rec["note"] = "Resident population too small for per-head rates"
    forces.append(rec)
json.dump({"height": H, "forces": forces}, open(OUT, "w"), separators=(",", ":"))
print(len(forces), "forces; frame 1000 x", H, "; bytes", OUT.stat().st_size)
