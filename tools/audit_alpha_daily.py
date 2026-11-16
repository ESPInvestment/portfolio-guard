#!/usr/bin/env python3
"""Read-only Alpha Vantage follow-up for eight Xetra ETF daily symbols."""
import datetime as dt
import json
import os
import urllib.parse
import urllib.request
from decimal import Decimal, InvalidOperation
from pathlib import Path

ASSETS = [
    ("FR0010524777", "LYM9.DEX", "PREVIOUS_PRICE"),
    ("IE00B3VWM098", "SXRG.DEX", "PREVIOUS_LIMIT"),
    ("IE00B4KBBD01", "2B7A.DEX", "PREVIOUS_LIMIT"),
    ("IE00BFMNPS42", "XZMU.DEX", "PREVIOUS_LIMIT"),
    ("IE00BGQYRS42", "XUTC.DEX", "PREVIOUS_PRICE"),
    ("IE00BMX0B631", "VDTE.DEX", "PREVIOUS_PRICE"),
    ("IE00BWBXM617", "ZPDH.DEX", "PREVIOUS_PRICE"),
    ("LU0321465469", "XFFE.DEX", "PREVIOUS_LIMIT"),
]

def classify(data, symbol):
    if not isinstance(data, dict):
        return {"status": "INVALID_RESPONSE"}
    series = data.get("Time Series (Daily)")
    if isinstance(series, dict) and series:
        meta = data.get("Meta Data") or {}
        returned = meta.get("2. Symbol")
        if not isinstance(returned, str) or returned.upper() != symbol.upper():
            return {"status": "SYMBOL_METADATA_MISMATCH", "returned_symbol": returned}
        day = max(series)
        try:
            date = dt.date.fromisoformat(day)
            close = Decimal(series[day]["4. close"])
            assert dt.date(2000, 1, 1) <= date <= dt.date.today()
            assert close.is_finite() and Decimal("0") < close < Decimal("1000000000")
        except (ValueError, InvalidOperation, TypeError, KeyError, AssertionError):
            return {"status": "INVALID_DAILY_PRICE"}
        return {"status": "PRICE_RETURNED_UNVERIFIED", "latest_date": day, "latest_close": str(close), "returned_symbol": returned, "observations": len(series)}
    message = " ".join(str(data.get(k, "")) for k in ("Information", "Note", "Error Message")).lower()
    if any(word in message for word in ("premium", "subscription", "subscribe")):
        return {"status": "PREMIUM_ACCESS_REQUIRED"}
    if any(word in message for word in ("rate limit", "api call frequency", "25 requests", "calls per day", "quota", "call volume")):
        return {"status": "RATE_LIMIT_REACHED"}
    if data.get("Error Message"):
        return {"status": "API_SYMBOL_ERROR"}
    if data.get("Information") or data.get("Note"):
        return {"status": "API_RESTRICTION_OTHER"}
    return {"status": "NO_SERIES"}

def main():
    key = os.environ.get("ALPHAVANTAGE_API_KEY", "").strip()
    if not key:
        print("Missing ALPHAVANTAGE_API_KEY secret")
        return 2
    output = []
    for isin, symbol, previous in ASSETS:
        params = urllib.parse.urlencode({"function": "TIME_SERIES_DAILY", "symbol": symbol, "outputsize": "compact", "apikey": key})
        try:
            with urllib.request.urlopen(urllib.request.Request("https://www.alphavantage.co/query?" + params, headers={"User-Agent": "PortfolioGuard-ManualAudit/1.0"}), timeout=20) as response:
                result = classify(json.loads(response.read(200000).decode("utf-8")), symbol)
        except Exception:
            result = {"status": "NETWORK_OR_PARSE_ERROR"}
        result.update({"isin": isin, "requested_symbol": symbol, "previous_status": previous, "currency": "NOT_VERIFIED", "share_class": "NOT_VERIFIED", "license_to_store_and_display": "NOT_VERIFIED"})
        output.append(result)
        print(f"{isin} {symbol} {result['status']} {result.get('latest_date', '')}")
    Path("alpha_followup_result.json").write_text(json.dumps(output, indent=2), encoding="utf-8")
    print("Read-only test complete. No Supabase writes, no daily automation.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
