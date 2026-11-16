#!/usr/bin/env python3
"""One-off read-only Alpha Vantage Xetra daily-close availability check."""
import json
import os
import urllib.parse
import urllib.request
import datetime as dt

ASSETS = [
 ("FR0010524777","LYM9.DEX"),
 ("IE00B3VWM098","SXRG.DEX"),
 ("IE00B4KBBD01","2B7A.DEX"),
 ("IE00BFMNPS42","XZMU.DEX"),
 ("IE00BGQYRS42","XUTC.DEX"),
 ("IE00BMX0B631","VDTE.DEX"),
 ("IE00BWBXM617","ZPDH.DEX"),
 ("LU0321465469","XFFE.DEX"),
]
def main():
 key=os.environ.get("ALPHAVANTAGE_API_KEY","").strip()
 if not key:
  print("Missing ALPHAVANTAGE_API_KEY secret")
  return 2
 output=[]
 for isin,symbol in ASSETS:
  status="REQUEST_FAILED"
  latest_date=None
  close=None
  response_symbol=None
  try:
   url="https://www.alphavantage.co/query?"+urllib.parse.urlencode({"function":"TIME_SERIES_DAILY","symbol":symbol,"outputsize":"compact","apikey":key})
   with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"PortfolioGuardCoverageTest/1.0"}),timeout=20) as response:
    data=json.loads(response.read(200000).decode("utf-8"))
   series=data.get("Time Series (Daily)")
   if isinstance(series,dict) and series:
    dates=sorted(series.keys(),reverse=True)
    latest_date=dates[0]
    close=series[latest_date].get("4. close")
    response_symbol=(data.get("Meta Data") or {}).get("2. Symbol")
    # Future and nonsensical price guard
    day=dt.date.fromisoformat(latest_date)
    value=float(close)
    if dt.date(2000,1,1) <= day <= dt.date.today() and 0 < value < 1000000000:
     status="UNVERIFIED_PRICE_RETURNED"
    else:
     status="INVALID_PRICE_RESPONSE"
     close=None
   elif "Information" in data or "Note" in data:
    status="LIMIT_OR_ACCESS_RESTRICTION"
   elif "Error Message" in data:
    status="SYMBOL_NOT_AVAILABLE"
   else:
    status="NO_DAILY_SERIES"
  except Exception:
   status="REQUEST_FAILED"
  output.append({"isin":isin,"tested_symbol":symbol,"status":status,"response_symbol":response_symbol,"latest_date":latest_date,"latest_close":close,"currency":"NOT_VERIFIED","instrument_identity":"NOT_VERIFIED","permission_to_reuse":"NOT_VERIFIED"})
  print(f"{isin} {symbol}: {status}"+(f" date={latest_date}" if latest_date else ""))
 with open("alpha_ticker_result.json","w",encoding="utf-8") as f:
  json.dump(output,f,indent=2)
 print("Test finished: no database writes. Returned prices are not approved for import.")
 return 0
if __name__=="__main__":
 raise SystemExit(main())
