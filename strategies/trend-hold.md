# TREND-HOLD: monthly trend-filter stock book (paper first)

STATUS: report only. No task, skill or script places an order; you enter every order by hand and send the fill line.

## What it is
A second paper stock book next to SWE. No options. It changes no SWE rule.

## Rule
- ETFs: SPY, QQQ, GLD, XLE, IWM.
- Check day: the last trading day of each month, after the close.
- IN for the next month if the ETF closed above its 200-day average of closes AND SPY closed above SPY's 200-day average. Otherwise OUT.
- Changes at the open of the first trading day of the new month: buy what turned IN, sell what turned OUT. Nothing in between. No stop, no target, no adding. The month-end check is the only exit.
- Bars: the same unadjusted IBKR daily bars the SWE step caches.
- Set `FIRST_CHECK` in `scripts/trend_hold_check.py` to your first month-end check.

## Size and money
- $2,000 per ETF, $10,000 total, fixed. Shares = nearest whole number for $2,000 at the month-end close (at least 1); one fewer if the book's cash does not cover it.
- No rebalancing while held; a position sold and bought later starts at $2,000 again.
- Own cash: 10,000 + closed TREND-HOLD P&L - cost of open rows. Never uses SWE cash or the spread reserve. Cash only.
- Orders: market-on-open, day only, entered by hand.

## Review line
-$2,500 from the book's peak, counted from the first fill. At or past it the report prints "TREND-HOLD REVIEW": no new buys, review together; open positions still follow the month-end rule.

## Same ETF in two books
SWE can hold the same ETF at the same time. The account then shows one combined position; the journal tells them apart (strategy "SWE" vs "TREND-HOLD"). SWE held symbols come from the journal, and account quantity must equal SWE qty + TREND-HOLD qty.

## Logging
Journal row per position, strategy "TREND-HOLD": symbol, date, qty, entry, open_px, status, exit, exit_date, exit_open_px. Fill lines go through `swe-fill-log`.

## What to expect (original 21-year test, $10,000, costs included; rerun on your own data)
About $1,000 a year on average (10%); 6% to 10% across reasonable settings. Worst drawdown about $1,800 (18%), up to about $2,500 with other settings. Losing years 2 of 21; flat years are common. About 91 closed trades in 21 years, 55% wins. It moves with the SWE book (monthly correlation about 0.67). XLE is the least tested ETF of the list.

## What the paper test is for
Process: every month-end check logged, every change entered on the first session, no rule breaks, fills against the official open. It is not a profit test (about 4 to 5 changes a year).
