#!/usr/bin/env python3
"""Read-only Alpha Vantage ISIN discovery; never writes to Supabase."""
import json
import os
import urllib.parse
import urllib.request
import time

INSTRUMENTS = [
    ("DE0009770206", "ODDO BHF Money Market"),
    ("FR0010524777", "Amundi MSCI New Energy"),
    ("IE00B3VWM098", "iShares MSCI USA Small Cap"),
    ("IE00B4KBBD01", "iShares S&P 500 Utilities"),
    ("IE00BFMNPS42", "Xtrackers MSCI USA ESG"),
    ("IE00BGQYRS42", "Xtrackers MSCI USA Information Technology"),
    ("IE00BMX0B631", "Vanguard USD Treasury EUR Hedged"),
    ("IE00BWBXM617", "SPDR US Health Care"),
    ("LU0321465469", "Xtrackers USD Overnight Rate"),
    ("LU1799928095", "DWS Vorsorge Geldmarkt TFC"),
]

def main():
    key = os.environ.get("ALPHAVANTAGE_API_KEY", "").strip()
    if not key:
        print("ERROR: GitHub Secret ALPHAVANTAGE_API_KEY is missing.")
        return 2
    print("Alpha Vantage read-only ISIN search; no writes and no daily schedule.")
    print("Note: search results are candidates only. They do not prove ISIN match or prices.")
    results = []
    for index, (isin, name) in enumerate(INSTRUMENTS):
        params = urllib.parse.urlencode({"function":"SYMBOL_SEARCH","keywords":isin,"apikey":key})
        url = "https://www.alphavantage.co/query?" + params
        status="NO_MATCH"
        found=[]
        try:
            req=urllib.request.Request(url,headers={"User-Agent":"PortfolioGuard-CoverageCheck/1.0"})
            with urllib.request.urlopen(req,timeout=20) as response:
                raw=response.read(150_000)
            data=json.loads(raw.decode("utf-8"))
            if any(k in data for k in ("Information","Note","Error Message")):
                status="API_LIMIT_OR_UNAVAILABLE"
            elif "bestMatches" not in data or not isinstance(data["bestMatches"],list):
                status="UNEXPECTED_RESPONSE"
            else:
                found=[{
                    "symbol":item.get("1. symbol",""),
                    "name":item.get("2. name",""),
                    "type":item.get("3. type",""),
                    "region":item.get("4. region",""),
                    "currency":item.get("8. currency",""),
                } for item in data["bestMatches"][:3]]
                status="CANDIDATES_UNVERIFIED" if found else "NO_MATCH"
        except Exception as exc:
            # Do not print exception: URLs may contain API keys.
            status="REQUEST_FAILED"
        results.append({"isin":isin,"name":name,"status":status,"candidates":found})
        print(f"{index+1}/10 {isin} {status}")
        if index<9:
            time.sleep(2)
    with open("alpha_coverage_result.json","w",encoding="utf-8") as handle:
        json.dump(results,handle,ensure_ascii=False,indent=2)
    print("Finished. Download the alpha-coverage-result artifact from the workflow run.")
    print("Even a matching name needs verification of share class, currency, exchange, timestamps and license.")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
