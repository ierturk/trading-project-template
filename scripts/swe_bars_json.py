"""Build the Trading Desk "swe_bars" dataset: daily OHLC of the SWE ETFs since the SIM start, kept across runs.
Usage: python3 swe_bars_json.py <bars_dir> <out.json> [previous swe_bars.json]
Reads every <SYMBOL>.csv in bars_dir (date,open,high,low,close; the Close Loop's step 1 files), merges them over the
previous file (new values win for the same date and symbol), keeps dates from START on, and writes rows
{date, symbol, open, high, low, close} sorted by date then symbol. The page uses it for the SWE equity curve,
the fill check (OPG fill vs that day's open) and the latest close of each held ETF."""
import csv, glob, json, os, sys

START = "2026-01-01"  # SET THIS to the day you start the paper book: only journal rows from this date count
bars_dir, out = sys.argv[1], sys.argv[2]
prev = sys.argv[3] if len(sys.argv) > 3 else ""

rows = {}
if prev and os.path.exists(prev):
    for r in (lambda _d: _d.get("rows", []) if isinstance(_d, dict) else _d)(json.load(open(prev))):
        rows[(r["date"], r["symbol"])] = r
for path in sorted(glob.glob(os.path.join(bars_dir, "*.csv"))):
    sym = os.path.basename(path)[:-4].upper()
    for r in csv.DictReader(open(path)):
        d = r["date"][:10]
        if d < START:
            continue
        rows[(d, sym)] = {"date": d, "symbol": sym, **{k: round(float(r[k]), 4) for k in ("open", "high", "low", "close")}}
data = [rows[k] for k in sorted(rows)]
json.dump(data, open(out, "w"))
dates = sorted({r["date"] for r in data})
print(len(data), "rows,", len({r["symbol"] for r in data}), "symbols,", dates[0] if dates else "-", "to", dates[-1] if dates else "-")
