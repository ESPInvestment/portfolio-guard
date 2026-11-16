#!/usr/bin/env python3
"""Validate independently obtained daily prices before optional manual CSV import.

No network, secret access, scheduling or Supabase writes. Refuses instruments not
explicitly verified in provider_coverage.csv. It never invents missing prices.
"""
import argparse
import csv
import datetime as dt
import decimal
import io
import json
import pathlib
import re
import sys

FIELDS = ("isin", "date", "price", "currency", "price_type", "source", "symbol", "exchange")

def read_manifest(text):
    entries={}
    for row in csv.DictReader(io.StringIO(text)):
        isin=row["isin"].strip()
        if isin in entries:
            raise ValueError("Duplicate ISIN in manifest")
        entries[isin]=row
    return entries

def validate(observations, manifest, current_date=None):
    current_date=current_date or dt.date.today()
    errors=[]
    accepted=[]
    unique=set()
    if not isinstance(observations,list):
        return [], ["Expected JSON array"]
    for idx, data in enumerate(observations, start=1):
        label=f"Row {idx}"
        if not isinstance(data,dict):
            errors.append(label+": not an object");continue
        if any(k not in data for k in FIELDS):
            errors.append(label+": missing required field");continue
        isin=str(data["isin"]).strip()
        setting=manifest.get(isin)
        if not setting:
            errors.append(label+": ISIN not in manifest");continue
        if setting["verified"].strip().lower()!="true":
            errors.append(label+": provider mapping NOT VERIFIED; import blocked");continue
        date=str(data["date"])
        try:
            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}",date):
                raise ValueError()
            parsed=dt.date.fromisoformat(date)
            if parsed>current_date:
                raise ValueError()
        except ValueError:
            errors.append(label+": invalid or future date");continue
        if (isin,date) in unique:
            errors.append(label+": duplicate observation");continue
        unique.add((isin,date))
        raw_price=str(data["price"])
        try:
            if not re.fullmatch(r"\d+(\.\d{1,6})?",raw_price):
                raise ValueError()
            price=decimal.Decimal(raw_price)
            if not decimal.Decimal("0")<price<=decimal.Decimal("1000000000"):
                raise ValueError()
        except (ValueError,decimal.InvalidOperation):
            errors.append(label+": invalid price");continue
        expected_type=setting["price_type"].strip().upper()
        actual_type=str(data["price_type"]).upper()
        if actual_type!=expected_type or actual_type not in ("NAV","CLOSE"):
            errors.append(label+": NAV and exchange close may not be mixed");continue
        for field in ("currency","provider_symbol","exchange"):
            if not setting[field].strip():
                errors.append(label+": manifest missing "+field);break
        else:
            mismatch=(
                str(data["currency"]).upper()!=setting["currency"].upper() or
                str(data["symbol"])!=setting["provider_symbol"] or
                str(data["exchange"]).upper()!=setting["exchange"].upper()
            )
            if mismatch:
                errors.append(label+": symbol/exchange/currency mismatch");continue
            source=str(data["source"]).strip()
            if not 3<=len(source)<=200 or any(c in source for c in "\r\n"):
                errors.append(label+": source invalid");continue
            accepted.append((isin,date,str(price),source))
    return accepted,errors

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_json",type=pathlib.Path)
    parser.add_argument("--manifest",type=pathlib.Path,default=pathlib.Path("data/provider_coverage.csv"))
    parser.add_argument("--out",type=pathlib.Path,default=pathlib.Path("validated_daily_prices.csv"))
    args=parser.parse_args()
    try:
        observations=json.loads(args.input_json.read_text(encoding="utf-8"))
        manifest=read_manifest(args.manifest.read_text(encoding="utf-8"))
        accepted,errors=validate(observations,manifest)
    except (OSError,ValueError,KeyError,json.JSONDecodeError) as exc:
        print("Validation failed:",exc,file=sys.stderr)
        return 2
    if errors:
        for err in errors:
            print("ERROR:",err,file=sys.stderr)
        print("Blocked; no output generated",file=sys.stderr)
        return 1
    if not accepted:
        print("No price observations. No CSV generated.")
        return 0
    with args.out.open("w",newline="",encoding="utf-8") as file:
        writer=csv.writer(file)
        writer.writerow(("isin","date","price","source"))
        writer.writerows(sorted(accepted,key=lambda x:(x[1],x[0])))
    print(f"Validated {len(accepted)} observations into {args.out}; manual import still required.")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
