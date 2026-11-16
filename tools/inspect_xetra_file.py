#!/usr/bin/env python3
"""Read-only, OFFLINE inspection of user-downloaded Xetra delayed data."""
import argparse, gzip, json, pathlib
from collections import Counter
EXPECTED={"FR0010524777","IE00B3VWM098","IE00B4KBBD01","IE00BFMNPS42","IE00BGQYRS42","IE00BMX0B631","IE00BWBXM617","LU0321465469"}
def json_records(text):
    content=text.strip()
    if not content:return []
    try:
        x=json.loads(content)
        if isinstance(x,list):return [e for e in x if isinstance(e,dict)]
        if isinstance(x,dict):return [x]
    except json.JSONDecodeError:pass
    return [json.loads(line) for line in content.splitlines() if line.strip()]
def inspect(records):
    matched=Counter();samples={}
    for record in records:
        document=json.dumps(record,ensure_ascii=False)
        for isin in EXPECTED:
            if isin in document:
                matched[isin]+=1
                samples.setdefault(isin,sorted(record.keys()))
    return matched,samples
def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file",type=pathlib.Path)
    args=parser.parse_args()
    if args.file.stat().st_size>25_000_000:parser.error("Input >25 MB")
    try:
        if args.file.suffix==".gz":
            with gzip.open(args.file,"rt",encoding="utf-8") as handle:data=handle.read(40_000_001)
        else:data=args.file.read_text(encoding="utf-8")
        if len(data)>40_000_000:parser.error("Decompressed file >40 MB")
        records=json_records(data)
    except (OSError,UnicodeError,ValueError,json.JSONDecodeError) as e:parser.error("Could not parse: "+str(e))
    found,keys=inspect(records)
    print("Records:",len(records))
    for isin in sorted(EXPECTED):
        print(isin,found[isin],"matching records; keys:",",".join(keys.get(isin,[])) or "-")
    print("No prices extracted. Match does not prove official close, currency, or licence.")
    return 0
if __name__=="__main__":raise SystemExit(main())
