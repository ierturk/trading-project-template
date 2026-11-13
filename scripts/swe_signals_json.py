"""Build the Trading Desk "swd_signals" dataset from daily-bar CSVs (date,open,high,low,close; oldest first).
Usage: python3 swe_signals_json.py <bars_dir> <out.json> [HELD,SYMBOLS] [free_slots] [free_cash]
free_cash : cash of the stock book = 12,000 + closed SWE P&L - cost of open SWE positions. An Entry that has a slot but costs more than the cash left is marked "skipped, not enough cash" (rule: not enough cash for the full position = skip). Entries on IBIT and DRAM get the note "untested ETF (not in the backtest)".
Rules : entry = close > SMA200 and > Hi20 (highest close of the 20 sessions before), SPY filter on;
shares = floor(POS_USD/close), POS_USD = 1500 and max 8 positions (paper book); stop = close - 2*ATR14; exit = held and close < Lo20. Key "hi50" is kept for the page."""
import csv, json, math, sys

SYMS = "SPY QQQ IWM DIA SMH SOXX XLK XLF XLE XLV XLI XBI KRE GLD GDX SLV IBIT EWZ EWY DRAM".split()
POS_USD = 1500  # $ per position (8 x $1,500 on a $12,000 paper book)
MAX_POS = 8
bars_dir, out = sys.argv[1], sys.argv[2]
held = set(filter(None, (sys.argv[3] if len(sys.argv) > 3 else "").split(",")))
free = int(sys.argv[4]) if len(sys.argv) > 4 else MAX_POS - len(held)
cash = float(sys.argv[5]) if len(sys.argv) > 5 else None  # stock-book cash; None = no cash check
UNTESTED = {"IBIT", "DRAM"}  # in the live list but not in the backtest (audit 2026)

def load(s):
    rows = {r["date"]: tuple(float(r[k]) for k in ("open", "high", "low", "close"))
            for r in csv.DictReader(open(f"{bars_dir}/{s}.csv"))}
    d = sorted(rows); return d, [rows[x] for x in d]

stats = {}
for s in SYMS:
    d, b = load(s); c = [x[3] for x in b]; n = len(b)
    tr = [max(b[i][1] - b[i][2], abs(b[i][1] - b[i-1][3]), abs(b[i][2] - b[i-1][3])) for i in range(n - 14, n)]
    stats[s] = dict(as_of=d[-1], close=c[-1], sma200=sum(c[-200:]) / 200 if n >= 200 else None,
                    hi=max(c[-21:-1]), lo20=min(x[2] for x in b[-21:-1]), atr14=sum(tr) / 14)
spy = stats["SPY"]; filt = spy["close"] > spy["sma200"]
rows, entries = [], []
for s in SYMS:
    t = stats[s]; r2 = lambda v: None if v is None else round(v, 2)
    row = {"symbol": s, "close": r2(t["close"]), "sma200": r2(t["sma200"]), "hi50": r2(t["hi"]), "lo20": r2(t["lo20"]),
           "atr14": r2(t["atr14"]), "signal": "None", "stop": None, "shares": None, "note": "", "as_of": t["as_of"]}
    pct = (t["close"] / t["hi"] - 1) * 100
    if s in held:
        row["signal"] = "Exit" if t["close"] < t["lo20"] else "Hold"
        row["note"] = f"exit below Lo20 {t['lo20']:.2f}"
    elif t["sma200"] is None:
        row["note"] = f"{pct:+.2f}% vs Hi20" + ("; SMA200 not fetched (no breakout)" if t["close"] <= t["hi"] else "; fewer than 200 bars, no SMA200")
    elif filt and t["close"] > t["sma200"] and t["close"] > t["hi"]:
        row.update(signal="Entry", stop=r2(t["close"] - 2 * t["atr14"]), shares=math.floor(POS_USD / t["close"]),
                   note=f"+{pct:.2f}% above Hi20"); entries.append((pct, row))
    else:
        row["note"] = ("below SMA200; " if t["close"] <= t["sma200"] else "") + f"{pct:+.2f}% vs Hi20"
    rows.append(row)
for i, (_, row) in enumerate(sorted(entries, key=lambda x: -x[0])):
    if row["symbol"] in UNTESTED: row["note"] += "; untested ETF (not in the backtest)"
    if i >= free: row["note"] += "; no slot"; continue
    cost = row["shares"] * row["close"]
    if cash is not None and cost > cash: row["note"] += f"; skipped, not enough cash (needs ${cost:,.0f}, stock book has ${max(cash, 0):,.0f})"
    elif cash is not None: cash -= cost
rows[0]["note"] = f"Filter {'ON' if filt else 'OFF'}: SPY {spy['close']:.2f} {'>' if filt else '<='} 200-day {spy['sma200']:.2f}"
json.dump(rows, open(out, "w"))
print(spy["as_of"], "filter", "ON" if filt else "OFF", "entries", [r["symbol"] for _, r in entries])
