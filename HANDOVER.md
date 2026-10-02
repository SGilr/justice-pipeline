# The Justice Pipeline: project handover

Updated 2 October 2026 (court and charge refresh on branch refresh-2026-10).

## What it is

An interactive, single-page data story about police numbers, crime, courts, prisons and children in custody in England and Wales, 2000 to 2026. It is produced by Prevention Informatics, a division of Oxon Advisory, and hosted at justice.howpreventionworks.com. It follows Stan Gilmour's house style: UK English, sentence case headings, no em dashes, and an analytical register.

## Where things are

- Local folder: `/Users/stangilmour/justice-pipeline`
- Live site: https://justice.howpreventionworks.com (Cloudflare Pages project `justice-pipeline`, direct upload; DNS is a DNS-only CNAME `justice` pointing to `justice-pipeline.pages.dev`)
- Repository: https://github.com/SGilr/justice-pipeline (public)
- Claude artifact preview: https://claude.ai/artifact/CLWH5MU6MHpoLtvaJg8p5K (private)

## Structure

- `src/page.html`: the page source (HTML, CSS and vanilla JS with hand-built SVG charts). Edit this file.
- `scripts/build_forces.py`: builds `data/forces.json` (43 force indicators and simplified boundaries) from the raw tables.
- `scripts/fetch_weekly.py`: downloads the HMPPS weekly prison population and capacity bulletins (2024 to 2026) to `data/raw/weekly/` and writes `data/weekly_capacity.json`.
- `scripts/build_page.py`: inlines `forces.json` and `weekly_capacity.json` into the page. It writes `site/index.html` (the deployable site) and `justice-pipeline.html` (the artifact version, with no document wrapper).
- `data/raw/`: every source table, unchanged from publication.
- `.venv/`: Python environment (pandas, odfpy, openpyxl, xlrd, pypdf). Not committed.

## Update and deploy

```
cd /Users/stangilmour/justice-pipeline
.venv/bin/python scripts/build_forces.py      # only if force tables change
.venv/bin/python scripts/fetch_weekly.py      # refresh weekly prison capacity
.venv/bin/python scripts/build_page.py
wrangler pages deploy site --project-name justice-pipeline --branch main
git add -A && git commit -m "..." && git push
```

To update the artifact, republish `justice-pipeline.html` to the artifact URL above.

## Page sections

1. Hero with headline figures and a sticky year scrubber that drives every timeline chart.
2. One timeline: small multiples on a shared 2000 to 2026 axis covering police officers, PCSOs, officers per 100,000, real-terms funding, crime survey against recorded crime, charge rate, stop and search, Crown Court and magistrates' open cases, prison population, remand and children in custody. It shows government bands and event markers (unrest, policy, shock).
3. Relative change: every series indexed to a chosen base year (2000, 2010 or 2019).
4. Police and crime: a connected scatter of officers per 100,000 against CSEW crime.
5. Pipeline since 2019: change at each stage, with the release figures (SDS40, ECSL, headroom, cases open a year or more).
6. The release valve: the progression model early release from 1 October 2026, with weekly headroom, tranche estimates, MoJ supply and demand projections with and without the Sentencing Act, and criticisms and safeguards.
7. Forces: a choropleth of the 43 force areas with a ranked list. Measures are change in officers since 2010, officers per 100,000, recorded crime per 1,000, and the Black to White stop and search ratio.
8. Children and disproportionality: youth custody, first-time entrants, ethnic minority share, and the stop and search ratio over time.
9. Context: the events list.
10. Data and notes: a table view, caveats and sources.

## Data status

Every series has been verified against published source tables (Home Office, ONS, MoJ, YJB, HMPPS).

Points marked ≈ on the page are official figures on a slightly different basis:
- prison population for 2000 and 2001 (annual averages)
- CSEW for 2000 (calendar year 1999)
- funding for 2000/01 and 2005/06 (IFS figures spliced to the Home Office Table 5 series)
- child first-time entrants, which break from financial years to calendar years in 2014

Officer numbers before 2003 are omitted because no comparable published series was available.

Corrections made during verification:
- Police recorded crime excluding fraud is 5.24m in 2025/26, not 6.6m (6.6m included fraud).
- Police funding fell 13% in real terms to a low in 2014/15 and was 4% above 2010/11 by 2025/26.
- The ethnic minority share of children in custody is about half (YJB), not 59%.
- The stop and search denominator switched to Census 2021 from 2020/21.
- ECSL releases are 13,325, not 13,395.

Prison Reform Trust factfile figures have been checked against MoJ tables. These still rest on secondary sources:
- the events list
- policy narrative from the House of Commons Library briefing CBP-10974
- the 41-day median time to charge (Institute for Government)

## Latest key figures

- Officers: 145,886 FTE (March 2026). That is 235 per 100,000 residents, against 258 in 2010 and 207 in 2018.
- Recorded crime excluding fraud: 5.24m (2025/26). CSEW excluding fraud and computer misuse: 4.3m, down 78% since 1995.
- Charge rate: 8.5% (2025/26), against 15.5% in 2014/15. Charges or summonses: 550,778 in the year to March 2026, up 15.5% (MoJ CJSQ Table Q1.2).
- Open cases: Crown Court 80,829 (23,706 open a year or more, 7,255 two years or more, median age 203 days); magistrates' courts 380,230 (June 2026, MoJ CCSQ April to June 2026, which revised March 2026 Crown Court to 80,437).
- Prison population: 85,858; remand 15,386, or 18% (June 2026). Headroom was 1,556 on 28 September 2026.
- SDS40 releases: 70,065 (September 2024 to March 2026).
- Progression model: about 700 released on 1 October 2026, and about 4,500 first-day releases across ten tranches to June 2027. MoJ projections (January 2026, before the exclusions) put the saving at about 7,700 places by November 2027. Central demand then grows again to 95,900 by November 2032; the high scenario exceeds supply in 2027 and 2028 and again from 2030.
- Children in custody: 418 (2024/25), down 86% since 2007/08.
- Political context: Andy Burnham has been Prime Minister since 20 July 2026, and the Justice Secretary is Alex Norris.

## Possible next steps

- Refresh with the stop and search release for the year ending March 2026, when it is published (expected late 2026).
- Track actual tranche releases and weekly headroom through to June 2027.
- Add force-level charge rates from the Home Office outcomes open data.
- Consider OS basemap tiles for sub-force zoom; this would need an API key proxied through Cloudflare.
- Run an accessibility review (WCAG 2.1 AA).
