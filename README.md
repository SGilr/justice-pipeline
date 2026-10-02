# The Justice Pipeline

An interactive account of police numbers, crime, courts, prisons and children in custody in England and Wales, 2000 to 2026, with force-level maps. Produced by Oxon Advisory as part of Prevention Works (howpreventionworks.com).

## Build

```
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python scripts/build_forces.py   # force indicators and simplified boundaries -> data/forces.json
.venv/bin/python scripts/build_page.py     # inlines data into src/page.html -> site/index.html
```

`site/` is the deployable static site. `justice-pipeline.html` is the same page without the document wrapper, used for the Claude artifact preview.

## Data

Raw source files are in `data/raw/`, unchanged from publication:

- Home Office, Police workforce open data tables, 31 March 2007 to 2026
- ONS, Crime in England and Wales: police force area data tables and appendix tables, year ending March 2026
- Home Office, Crime outcomes in England and Wales, year ending March 2026 data tables
- Ministry of Justice, Criminal court statistics quarterly, January to March 2026 tables
- Home Office, Stop and search summary tables, year ending March 2025
- ONS Open Geography Portal, Police Force Areas (December 2023) generalised boundaries. Contains OS data © Crown copyright and database right 2023

National series that predate these tables (officers and PCSOs before 2007, remand before 2018, children in custody before 2010, stop and search before 2018, and the real-terms funding index) are approximate reconstructions and are marked ≈ on the page. The notes section of the page lists every caveat.

Contains public sector information licensed under the Open Government Licence v3.0.

## Deploy

Hosted on Cloudflare Pages (project `justice-pipeline`, direct upload), to be served at justice.howpreventionworks.com.

```
wrangler pages deploy site --project-name justice-pipeline --branch main
```
