# Candidate: Official Deutsche Börse MiFID II delayed Xetra files
Research date: 2026-11-16. Status: unverified candidate, no feed activated.

Primary sources:
- https://www.mds.deutsche-boerse.com/mds-en/real-time-data/Delayed-data
- https://mfs.deutsche-boerse.com/DETR-posttrade

Official Xetra post-trade data is offered as free-to-access 15-minute delayed gzipped JSON. Publication is roughly once per minute; files are available until midnight of the following business day. The official service requires accepting its terms. The licence is free for non-commercial use only. Commercial downstream services require a separate licence.

Caveats:
- This is a trade-print file service, NOT a validated daily ETF closing-price endpoint.
- A last trade is not necessarily the official closing auction price.
- Sparse trading means a single minute file might not include an ETF.
- The eight ETF ISINs have not yet been found within a genuine downloaded source file.
- Two mutual funds DE0009770206 and LU1799928095 require a separate NAV workflow.
- No automation should bypass the terms acceptance or assert usage rights.

Optional private inspection: after personally accepting the terms and downloading a JSON/GZ file, run: python tools/inspect_xetra_file.py file.json.gz
That command only reports record counts and JSON keys for the eight target ISINs. It does not save prices, contact Supabase, or run on any schedule.
Nothing here is authorized for automatic ingestion until coverage, mapping, timing, price semantics and rights are verified.