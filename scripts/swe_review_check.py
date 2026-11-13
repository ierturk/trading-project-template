#!/usr/bin/env python3
"""SWE review line check : stop new entries and review the
system if the SWE book falls $3,000 or more below its peak (8 x $1,500 book;
).

Same curve as the Trading Desk's "SIM equity curve" card: for each daily close since
the first SWE entry, closed P&L (exit - entry) x qty of SWE trades exited by then plus
open P&L (close - entry) x qty of SWE trades held at that close, across both accounts
(paper-account rows in the journal since the reset). Peak starts at $0.

Usage:
  python3 swe_review_check.py <sim_journal.json> <swe_bars.json> [review_line]

Prints one line. It starts with "REVIEW:" when the drop from the peak reaches the line.
"""
import json
import sys

REVIEW_LINE = 3000.0  # $ below the SWE book peak; 8 x $1,500 on $12,000; worst backtest drawdown about $3.0k
START = "2026-01-01"  # SET THIS to the day you start the paper book: only journal rows from this date count


def usd(v):
    return ("+" if v > 0 else "-" if v < 0 else "") + "${:,.0f}".format(abs(v))


def curve(journal, bars):
    trades = [t for t in journal
              if t.get("strategy") in ("SWE", "SWD") and t.get("entry") is not None
              and t.get("status") in ("Open", "Closed") and t.get("date", "") >= START]
    dates = sorted({b["date"] for b in bars})
    close = {(b["date"], b["symbol"]): float(b["close"]) for b in bars}
    last_close = {}
    peak = 0.0
    rows = []
    for d in dates:
        if not any(t["date"] <= d for t in trades):
            continue
        for t in trades:
            c = close.get((d, t["symbol"]))
            if c is not None:
                last_close[t["symbol"]] = c
        realized = opn = 0.0
        for t in trades:
            q, e = float(t["qty"]), float(t["entry"])
            exit_date = (t.get("exit_date") or dates[-1]) if t["status"] == "Closed" else None
            if exit_date and exit_date <= d:
                realized += (float(t["exit"]) - e) * q
            elif t["date"] <= d and t["symbol"] in last_close:
                opn += (last_close[t["symbol"]] - e) * q
        total = realized + opn
        peak = max(peak, total)
        rows.append({"date": d, "realized": realized, "open": opn, "total": total,
                     "peak": peak, "drawdown": total - peak})
    return rows


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    line = float(sys.argv[3]) if len(sys.argv) > 3 else REVIEW_LINE
    with open(sys.argv[1]) as f:
        journal = (lambda _d: _d.get("rows", []) if isinstance(_d, dict) else _d)(json.load(f))
    with open(sys.argv[2]) as f:
        bars = (lambda _d: _d.get("rows", []) if isinstance(_d, dict) else _d)(json.load(f))
    rows = curve(journal, bars)
    if not rows:
        print("Review line: no SWE trades with daily bars yet (line -${:,.0f} from the peak).".format(line))
        return
    r = rows[-1]
    worst = min(x["drawdown"] for x in rows)
    msg = ("SWE book {} on {} (closed {}, open {}), peak {}, {} from the peak; review line -${:,.0f} "
           "(${:,.0f} to go; worst so far {}).").format(
        usd(r["total"]), r["date"], usd(r["realized"]), usd(r["open"]), usd(r["peak"]),
        usd(r["drawdown"]), line, max(0.0, line + r["drawdown"]), usd(worst))
    if r["drawdown"] <= -line:
        print("REVIEW: the SWE book is ${:,.0f} below its peak, at or past the -${:,.0f} line: "
              "stop new entries and review the system. ".format(-r["drawdown"], line) + msg)
    else:
        print("Review line OK: " + msg)


if __name__ == "__main__":
    main()
