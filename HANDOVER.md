# The Justice Pipeline: project handover

Updated 2 October 2026, after the court and charge refresh (commit 21686e2, deployed the same day).

## What it is

An interactive, single-page data story about police numbers, crime, courts, prisons and children in custody in England and Wales, 2000 to 2026. It is produced by Prevention Informatics, a division of Oxon Advisory, and hosted at justice.howpreventionworks.com. It follows Stan Gilmour's house style: UK English, sentence case headings, no em dashes, and an analytical register.

## Where things are

- Local folder: `/Users/stangilmour/justice-pipeline`
- Live site: https://justice.howpreventionworks.com (Cloudflare Pages project `justice-pipeline`, direct upload; DNS is a DNS-only CNAME `justice` pointing to `justice-pipeline.pages.dev`)
- Repository: https://github.com/SGilr/justice-pipeline (public)
- Claude artifact preview: https://claude.ai/artifact/CLWH5MU6MHpoLtvaJg8p5K (private). Republished on 3 October 2026 (version 14), so it matches the live site.

## Structure

- `src/page.html`: the page source (HTML, CSS and vanilla JS with hand-built SVG charts). Edit this file.
- `scripts/build_forces.py`: builds `data/forces.json` (43 force indicators and simplified boundaries) from the raw tables.
- `scripts/fetch_weekly.py`: downloads the HMPPS weekly prison population and capacity bulletins (2024 to 2026) to `data/raw/weekly/` and writes `data/weekly_capacity.json`.
- `scripts/build_perceptions.py`: extracts the CSEW confidence and fear series from the ONS tables to `data/perceptions.json`, recording the table and row for each.
- `scripts/build_page.py`: inlines `forces.json`, `weekly_capacity.json` and `perceptions.json` into the page. It writes `site/index.html` (the deployable site) and `justice-pipeline.html` (the artifact version, with no document wrapper).
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

Deployment is manual. The Pages project has no Git connection and the repo has no GitHub Action, so pushing to GitHub does not change the live site; only `wrangler pages deploy` does. The site sends `cache-control: max-age=0, must-revalidate`, so a deploy shows immediately.

Working practice: make data changes on a branch, show the diff, and deploy only after approval. Every figure is taken from the official table itself (GOV.UK, ONS, MoJ or Home Office, not press reports), with the table and cell recorded, and is updated everywhere it appears: hero, chart data, table view, notes and sources.

## Page sections

1. Hero with headline figures and a sticky year scrubber that drives every timeline chart.
2. One timeline: small multiples on a shared 2000 to 2026 axis covering police officers, PCSOs, officers per 100,000, real-terms funding, crime survey against recorded crime, charge rate, stop and search, Crown Court and magistrates' open cases, prison population, remand and children in custody. It shows government bands and event markers (unrest, policy, shock).
3. Relative change: every series indexed to a chosen base year (2000, 2010 or 2019).
4. Police and crime: a connected scatter of officers per 100,000 against CSEW crime.
5. Confidence and fear: six CSEW charts covering confidence in local police, trust in the police, foot patrol visibility, perceived national crime trend, worry about violent crime, and women's safety after dark. It is followed by a legitimacy subsection:
   - components of confidence, 2015/16 against 2025/26
   - victim satisfaction by quality of contact
   - confidence and fair treatment by group
   - willingness to cooperate
   - a cautious reading of what these suggest
6. Pipeline since 2019: change at each stage, with the release figures (SDS40, ECSL, headroom, charge volume, median time to charge, cases open a year or more).
7. The release valve: the progression model early release from 1 October 2026, with weekly headroom, tranche estimates, MoJ supply and demand projections with and without the Sentencing Act, and criticisms and safeguards.
8. Forces: a choropleth of the 43 force areas with a ranked list. Measures are change in officers since 2010, officers per 100,000, recorded crime per 1,000, and the Black to White stop and search ratio.
9. Children and disproportionality: youth custody, first-time entrants, ethnic minority share, and the stop and search ratio over time.
10. Context: the events list.
11. Data and notes: a table view, caveats and sources.

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
- MoJ revised the court series in the April to June 2026 release; for example, end of March 2026 Crown Court open cases is 80,437, not the 80,061 first published. The notes record this.
- Charges in the year to March 2026 are the most since the year ending March 2016, not 2017 as some press reports say (CJSQ Table Q1.2: 556,829 in the year to March 2016).

Prison Reform Trust factfile figures have been checked against MoJ tables. These still rest on secondary sources:
- the events list
- policy narrative from the House of Commons Library briefing CBP-10974
- the 41-day median time to charge (Institute for Government)

## Latest key figures

- Officers: 145,886 FTE (March 2026). That is 235 per 100,000 residents using the mid-2025 population, against 258 in 2010 and 207 in 2018. The Home Office gives 236 (Table H4) because it uses mid-2024; note 4 explains the difference.
- Recorded crime excluding fraud: 5.24m (2025/26). CSEW excluding fraud and computer misuse: 4.3m, down 78% since 1995.
- Charge rate: 8.5% (2025/26), against 15.5% in 2014/15. Charges or summonses: 550,778 in the year to March 2026, up 15.5% (MoJ CJSQ Table Q1.2).
- Open cases: Crown Court 80,829 (23,706 open a year or more, 7,255 two years or more, median age 203 days); magistrates' courts 380,230 (June 2026, MoJ CCSQ April to June 2026, which revised March 2026 Crown Court to 80,437).
- Prison population: 85,858; remand 15,386, or 18% (June 2026). Headroom was 1,556 on 28 September 2026.
- SDS40 releases: 70,065 (September 2024 to March 2026).
- Progression model: about 700 released on 1 October 2026, and about 4,500 first-day releases across ten tranches to June 2027. MoJ projections (January 2026, before the exclusions) put the saving at about 7,700 places by November 2027. Central demand then grows again to 95,900 by November 2032; the high scenario exceeds supply in 2027 and 2028 and again from 2030.
- Children in custody: 418 (2024/25), down 86% since 2007/08. 44% were on remand in 2024/25, against 21% in 2016/17 (YJB Table 6.3). 62% of children remanded in custody whose cases ended in 2024/25 were acquitted or given a non-custodial sentence (YJB Table 6.6).
- Confidence and fear (CSEW, 2025/26):
  - overall confidence in local police 67% (peak 79% in 2015/16)
  - trust in the police 74% (87% in 2017/18 and 2018/19)
  - weekly foot patrol sightings 12.5% (39% in 2010/11)
  - 80% think crime has risen nationally, 52% locally
  - high worry about violent crime 9%
  - feeling safe after dark: women 68%, men 88%
- Political context: Andy Burnham has been Prime Minister since 20 July 2026, and the Justice Secretary is Alex Norris.

## Change log

### 3 October 2026: deployment evidence

- The police and crime text now explains that a national headcount says nothing about where officers are or what they do. It cites hot spots policing (Braga et al., 2019, Campbell Systematic Reviews 15(3) e1046: a small but consistent fall in crime, with diffusion of benefits more likely than displacement) and problem-oriented policing (Hinkle et al., 2020, Campbell Systematic Reviews 16(2) e1089: a 33.8% reduction relative to comparison areas, no significant displacement), and links to the College of Policing Crime Reduction Toolkit.
- Wording was checked against the review abstracts via Crossref. Harvard references were added to the sources list.
- Not yet used: Hinkle et al. found limited impacts of problem-oriented policing on fear of crime, legitimacy and collective efficacy, which could inform the legitimacy reading.
- Deployed (commit f61ce37); artifact republished as version 14.

### 3 October 2026: force map outlines

- Force areas now have a thin outline (`--map-edge`): #474d55 in light mode, giving 4.0 to 6.6:1 against the pale and neutral shades; #8a9097 in dark mode.
- The dark-mode neutral shade (`--mid`) is lightened to #6e7378, 3.6:1 against the card. Legend swatches use the same outline.
- This closes the last open audit finding apart from touch targets and screen reader testing. axe-core reports no violations.
- Deployed (commit 8ce2b35); artifact republished as version 13.

### 3 October 2026: accessibility fixes

- A WCAG 2.1 AA audit of the live site found 13 issues: 7 major and 6 minor. Fixes:
  - darker muted text (#646a71, 4.9:1)
  - darker light-mode prison, remand and crime survey colours (3.5:1 or more)
  - a main landmark and skip links
  - event marker focus rings and Enter/Space
  - map buttons as plain toggle buttons, and map areas with an image role
  - a focusable ranked list
  - Escape closes tooltips
  - the slider describes the year in place of a live region
  - tables for the hover-only charts
- After deploy, axe-core 4.10 on the live site reports no violations in light or dark mode.
- Not done at the time: the pale map bins (fixed later the same day by outlining force areas), touch target sizes (advisory under 2.1), and real screen reader testing (VoiceOver, NVDA).
- The legitimacy reading now dates its comparisons: 2015/16 to 2025/26 for the falls, 2025/26 for satisfaction.
- Deployed (commit bb66d05); artifact republished as version 12.
- Deploy note: the custom domain can take 10 to 30 seconds after `wrangler pages deploy` to serve the new version. Re-check before concluding a deploy failed.

### 3 October 2026: police legitimacy panels

- Added to section 04 from ONS perceptions tables, year ending March 2026:
  - Table 4: components of confidence. Respect fell 4 points since 2015/16; "deal with local concerns" fell 13.5 and "good job" 13.8.
  - Table 17: victim satisfaction 77% if treated fairly against 12% if not, and about four times as high for respect and for being kept informed.
  - Table 5: 19 groups. The lowest are the ever homeless (53%), care-experienced (57%) and Black Caribbean adults (52%, from 249 respondents).
  - Table 20: willingness to cooperate. 92% would help and 91% would call the police; 69% would follow an order and 70% say standards of behaviour are good.
- The copy stresses association, not causation. The user asked how the data can inform current calls to improve police legitimacy; the specific announcement was not identified or cited.
- Grid items are now prevented from widening the page on phones.
- Deployed (commit 5e81d9b); artifact republished as version 11.

### 3 October 2026: confidence and fear

- New section 04 (Confidence and fear) from ONS, Perception and experience of police and criminal justice system, year ending March 2026 (Tables 1, 2, 4, 10 and 21) and the annual supplementary tables (B1, B4 and B7). Later sections are renumbered.
- Series breaks noted by ONS are drawn as dashed joins. Force-level confidence is not shown, because ONS advises extreme caution.
- An ethnicity callout was added on ratings of local police: Black Caribbean 35%, Black African 62%, White 47%, with a small-sample caveat.
- The revised-figure note no longer quotes 80,061.
- Deployed (commit 2b1182e); artifact republished as version 10.

### 3 October 2026: logo link

- The header logo links to https://www.oxonadvisory.com/ (oxonadvisory.com redirects there), opening in the same tab, with a hover fade and a visible keyboard focus outline. Deployed (commit c4abbb6); artifact republished as version 9.

### 3 October 2026: header logo

- The full Oxon Advisory lockup (pills, wordmark and tagline) now sits at the top left of the hero, above the eyebrow: 92px tall on desktop and 68px on phones. `scripts/build_logo.py` builds it as `assets/oxa-wordmark.svg` from `assets/logo-wordmark-source.svg`, a copy of `~/code/oxa-design-system/assets/logo-wordmark.svg`, with outlined lettering and token colours that reverse in dark mode.
- Deployed (commit 5cf8b09); artifact republished as version 8.

### 3 October 2026: footer mark

- The footer now carries the OXAi pill mark with "Prevention Informatics, a division of Oxon Advisory" in text beside it. The mark is built by `scripts/build_logo.py` from `assets/logo-oxai-source.svg`, a copy of `~/code/oxa-design-system/assets/logo-oxai.svg`. The lettering is outlined from Times New Roman, the "Oxon Advisory Informatics" line and tagline are dropped, and colours come from CSS tokens, using the reverse palette in dark mode.
- Deployed (commit 89e8566); artifact republished as version 7.

### 2 October 2026: court and charge refresh

Sources: MoJ Criminal court statistics quarterly, April to June 2026 (Tables C1, M1, O1, O3); MoJ Criminal Justice Statistics quarterly, March 2026 (Table Q1.2); YJB Youth justice statistics 2024 to 2025 (Tables 6.3, 6.6); Home Office police workforce tables, Table H4.

- Crown Court open cases: 80,061 (March 2026) became 80,829 (June 2026). The whole 2016 to 2025 series was replaced with MoJ's revised figures (2019: 38,341; 2025: 80,462). "More than double the end-2019 level" still holds (2.11 times).
- Cases open a year or more: 22,124 (March 2026) became 23,706 (June 2026), with 7,255 open two years or more and a median open case age of 203 days. The early-2016 comparator is 5,248, up from 5,209.
- Magistrates' open cases: 370,722 (March 2026) became 380,230 (June 2026), with the series revised (2019: 223,577). The page now says up 70% since 2019, replacing "up two thirds".
- New pipeline stat: 550,778 charges or summonses in the year to March 2026, up 15.5%.
- Children on remand changed from 43% to 44% (2024/25, against 21% in 2016/17). The remand outcomes year changed from 2023/24 to 2024/25; the value stays at 62%.
- Data notes: court dates now say end of June 2026; the prison note says the pipeline uses June 2026; note 4 explains 235 against the Home Office's 236; there is a dated refresh line; two sources were added (CCSQ April to June 2026, CJSQ March 2026) and the OMSQ January to March 2026 source.
- Branding: "Prevention Works" is retired. The README, this handover and the GitHub repo description now say "Prevention Informatics, a division of Oxon Advisory". The domain is unchanged, and the page itself never used the old brand.
- Mobile: the scrubber's instruction label is hidden below 640px, so the sticky bar is about 96px tall on phones. There is no horizontal scroll at 375px.
- Checked and unchanged:
  - The remand share (17.9% in June 2026, 11.1% in 2019, peak 20.3% in 2025).
  - The tranche figures (MoJ report of 30 August 2026, no updates).
  - The Prime Minister wording, verified on the GOV.UK role page (appointed 20 July 2026) and the GOV.UK news release of 4 August 2026.
- Not updated: weekly spare places. No HMPPS bulletin after the 1 October tranche existed yet; the latest was 28 September (1,556).
- Link check: 27 of 29 sources return 200. The two Commons Library links (CBP-10974 and the CDP-2025-0031 PDF) return 403 to automated requests but load in a browser.

## Possible next steps

- Run `scripts/fetch_weekly.py` after the HMPPS bulletin of Monday 5 October 2026, the first after the first tranche, then rebuild and redeploy.
- Update prison and remand figures from the offender management statistics for April to June 2026 (expected around 29 October 2026).
- Update court caseloads from criminal court statistics for July to September 2026 (expected December 2026).

- Refresh with the stop and search release for the year ending March 2026, when it is published (expected late 2026).
- Track actual tranche releases and weekly headroom through to June 2027.
- Add force-level charge rates from the Home Office outcomes open data.
- Consider OS basemap tiles for sub-force zoom; this would need an API key proxied through Cloudflare.
- Test with VoiceOver and NVDA.
