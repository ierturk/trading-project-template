#!/usr/bin/env python3
"""Close Loop / Open Check helper . Prints one JSON line.
Usage: python3 -I next_session.py [YYYY-MM-DD New York date; default = today New York]
Keys: ny_date, holiday (full NYSE holiday or weekend), prev_session (last trading day before ny_date), next_session (next trading day after ny_date),
first_of_month_next (next_session is the first trading day of its month), is_monday.
Holiday list is the one in trend_hold_check.py (ends 2027: extend it)."""
import sys, json, datetime as dt, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import trend_hold_check as t
if len(sys.argv) > 1: d = dt.date.fromisoformat(sys.argv[1])
else:
    from zoneinfo import ZoneInfo
    d = dt.datetime.now(ZoneInfo("America/New_York")).date()
n = t.next_td(d)
print(json.dumps(dict(ny_date=d.isoformat(), holiday=not t.trading_day(d), prev_session=t.prev_td(d).isoformat(),
      next_session=n.isoformat(), first_of_month_next=t.prev_td(n).month != n.month, is_monday=d.weekday() == 0)))
