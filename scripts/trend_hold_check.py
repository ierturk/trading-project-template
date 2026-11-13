#!/usr/bin/env python3
"""TREND-HOLD month-end check (paper rules). Report only: prints lines, places nothing.

Rule: on the last trading day of a month, an ETF is IN for the next month when its close is above its 200-day
average of closes AND SPY's close is above SPY's 200-day average. Changes are made by hand at the open of the
first trading day of the new month. $2,000 per ETF (nearest whole share at the month-end close), no stop.
The same month-end status of SPY, QQQ, GLD is the entry filter of the two spread books (SWE-SPREAD, SWE-PUTCS).

Usage: python3 -I trend_hold_check.py <bars_cache_dir> <today New York date YYYY-MM-DD> [sim_journal.json] [out.json]
Bars: <SYM>.csv with date,open,high,low,close (oldest first), completed sessions only.
Journal rows used: strategy "TREND-HOLD", keys symbol, qty, entry, date, status Open/Closed, exit, exit_date.
"""
import csv, json, sys, datetime as dt

ETFS = ["SPY", "QQQ", "GLD", "XLE", "IWM"]      #
SPREAD_ETFS = ["SPY", "QQQ", "GLD"]
POS_USD = 2000.0
BOOK_USD = 10000.0
REVIEW_LINE = 2500.0
FIRST_CHECK = "2026-11-30"                      # SET THIS: first month-end check you want counted; orders go in at the open of the next trading day
HOLIDAYS = {"2026-11-26", "2026-12-25", "2027-01-01", "2027-01-18", "2027-02-15", "2027-03-26", "2027-05-31",
            "2027-06-18", "2027-07-05", "2027-09-06", "2027-11-25", "2027-12-24"}   # list ends 2027: extend it

def load(d, s):
    rows = [(r["date"], float(r["close"])) for r in csv.DictReader(open(f"{d}/{s}.csv"))]
    rows.sort(); return rows
def trading_day(x): return x.weekday() < 5 and x.isoformat() not in HOLIDAYS
def next_td(x):
    x += dt.timedelta(1)
    while not trading_day(x): x += dt.timedelta(1)
    return x
def prev_td(x):
    x -= dt.timedelta(1)
    while not trading_day(x): x -= dt.timedelta(1)
    return x
def usd(v): return ("+" if v > 0 else "-" if v < 0 else "") + "${:,.0f}".format(abs(v))

def main():
    if len(sys.argv) < 3: sys.exit(__doc__)
    cache, today = sys.argv[1], dt.date.fromisoformat(sys.argv[2])
    jpath = sys.argv[3] if len(sys.argv) > 3 and sys.argv[3] not in ("", "-") else None
    out = sys.argv[4] if len(sys.argv) > 4 else None
    bars = {s: load(cache, s) for s in ETFS}
    first_session = trading_day(today) and prev_td(today).month != today.month
    last_session = trading_day(today) and next_td(today).month != today.month
    # month-end bar = last cached bar dated before the first day of today's month
    cut = today.replace(day=1).isoformat(); res = {"today": today.isoformat(), "first_session": first_session, "last_session": last_session, "etfs": {}}
    def status(s):
        b = [x for x in bars[s] if x[0] < cut]
        if len(b) < 200: return None
        return dict(date=b[-1][0], close=b[-1][1], sma200=sum(c for _, c in b[-200:]) / 200)
    spy = status("SPY"); expect = prev_td(today.replace(day=1)).isoformat()   # last trading day of the previous month
    stale = spy is None or spy["date"] != expect
    filt = spy is not None and spy["close"] > spy["sma200"]
    journal = []
    if jpath:
        j = json.load(open(jpath)); journal = j.get("rows", []) if isinstance(j, dict) else j
    th = [t for t in journal if t.get("strategy") == "TREND-HOLD" and t.get("entry") is not None and t.get("status") in ("Open", "Closed")]
    held = {t["symbol"]: t for t in th if t["status"] == "Open"}
    parts = []
    for s in ETFS:
        st = status(s)
        if st is None:
            nb = len([x for x in bars[s] if x[0] < cut]); res["etfs"][s] = dict(status="NO DATA", bars_before_month=nb); parts.append(f"{s} no data ({nb} of 200 bars before the month start, joins by itself)"); continue
        inn = filt and st["close"] > st["sma200"]; sh = max(1, int(st["close"] and POS_USD / st["close"] + 0.5))
        act = ("HOLD" if inn else "SELL") if s in held else ("BUY" if inn else "STAY OUT")
        res["etfs"][s] = dict(status="IN" if inn else "OUT", month_end=st["date"], close=round(st["close"], 2), sma200=round(st["sma200"], 2), shares=sh, action=act, held_qty=float(held[s]["qty"]) if s in held else 0)
        parts.append(f"{s} {'IN' if inn else 'OUT'} ({st['close']:.2f} vs avg {st['sma200']:.2f})")
    res["spy_filter"] = "ON" if filt else "OFF"; res["stale"] = stale; res["month_end_expected"] = expect
    started = today.isoformat() > FIRST_CHECK
    print(f"TREND-HOLD status at month end {spy['date'] if spy else '?'}: " + ", ".join(parts) + f"; SPY filter {'ON' if filt else 'OFF'}" + ("" if started else f" (information only: the book starts with the check of {FIRST_CHECK})"))
    if stale: print(f"TREND-HOLD: month-end bar {expect} is not in the cache (last bar before this month: {spy['date'] if spy else 'none'}); do not act on the list until the bars are refreshed")
    if first_session and started and not stale:
        cash = BOOK_USD + sum((float(t["exit"]) - float(t["entry"])) * float(t["qty"]) for t in th if t["status"] == "Closed") - sum(float(t["entry"]) * float(t["qty"]) for t in held.values())
        lines = []
        for s in ETFS:
            e = res["etfs"][s]
            if e.get("action") == "SELL": cash += e["close"] * e["held_qty"]
        for s in ETFS:
            e = res["etfs"][s]
            if e.get("status") == "NO DATA": lines.append(f"{s} NO DATA (under 200 bars before the month end): check by hand, no order from this list"); continue
            if e["action"] == "BUY":
                while e["shares"] > 1 and e["shares"] * e["close"] > cash: e["shares"] -= 1
                if e["shares"] * e["close"] > cash: e["action"] = "SKIP (not enough cash in the book)"; lines.append(f"{s} SKIP, not enough cash"); continue
                cash -= e["shares"] * e["close"]; lines.append(f"BUY {s} {e['shares']} sh at the open (about ${e['shares']*e['close']:,.0f})")
            elif e["action"] == "SELL": lines.append(f"SELL {s} {e['held_qty']:g} sh at the open")
            elif e["action"] == "HOLD": lines.append(f"HOLD {s}")
            else: lines.append(f"STAY OUT {s}")
        print("TREND-HOLD LIST for today's open (market-on-open orders, entered by hand): " + "; ".join(lines))
        print("SPREAD ENTRY DAY: " + ", ".join(f"{s} {res['etfs'][s].get('status')} (month-end close {res['etfs'][s].get('close')})" for s in SPREAD_ETFS) + ". A new spread only for an ETF that is IN and has no open spread in that book.")
    elif first_session and not started:
        print(f"TREND-HOLD: not started yet (first check {FIRST_CHECK}, first orders the next session)")
    if last_session: print("TREND-HOLD: the month-end check runs on tonight's close; the list for the open comes with tomorrow's report")
    # book line and review line
    if th:
        days = sorted({d for s in ETFS for d, _ in bars[s] if d >= min(t["date"] for t in th)}); close = {s: dict(bars[s]) for s in ETFS}; last = {}; peak = 0.0; cur = None
        for d in days:
            tot = 0.0; rl = op = 0.0
            for t in th:
                if t["date"] > d: continue
                q, e = float(t["qty"]), float(t["entry"]); c = close.get(t["symbol"], {}).get(d)
                if c is not None: last[t["symbol"]] = c
                if t["status"] == "Closed" and (t.get("exit_date") or days[-1]) <= d: rl += (float(t["exit"]) - e) * q
                elif t["symbol"] in last: op += (last[t["symbol"]] - e) * q
            tot = rl + op; peak = max(peak, tot); cur = (d, rl, op, tot)
        if cur:
            d, rl, op, tot = cur; dd = tot - peak
            msg = f"TREND-HOLD book {usd(tot)} on {d} (closed {usd(rl)}, open {usd(op)}), peak {usd(peak)}, {usd(dd)} from the peak; review line -${REVIEW_LINE:,.0f} (${max(0.0, REVIEW_LINE + dd):,.0f} to go); open: {', '.join(sorted(held)) or 'none'}"
            print(("TREND-HOLD REVIEW: the book is at or past the line: no new buys, review together. " if dd <= -REVIEW_LINE else "") + msg)
            res["book"] = dict(total=round(tot), from_peak=round(dd), review=dd <= -REVIEW_LINE)
    else:
        print("TREND-HOLD book: no positions logged yet (review line -$2,500 from the peak, counted from the first fill)")
    if out: json.dump(res, open(out, "w"))

if __name__ == "__main__":
    main()
