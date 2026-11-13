# Optional option-spread paper books (SWE-SPREAD and SWE-PUTCS)

Optional. Paper only, report only. No task places an order; you enter spreads and exits by hand and send the fill line. Needs option permissions at your broker: debit spreads need a lower level than credit spreads (check your broker's levels; at IBKR credit spreads need a higher level than debit spreads). These books are leverage on the same uptrend rule as TREND-HOLD, not a separate edge: in the original research the stock books made more per dollar of drawdown, and the original author kept live trading to stock only.

## Shared rules
- Underlyings: SPY, QQQ, GLD. One spread per underlying at a time.
- ENTRY DAY: the first trading day of each month. An ETF gets a new spread only if on the last trading day of the previous month it closed above its 200-day average AND SPY closed above SPY's 200-day average (the TREND-HOLD month-end check), and no spread on that ETF is open.
- Expiry: the monthly expiry at least 45 days out (the Thursday if that Friday is a holiday).
- EXIT: 7 calendar days before expiry. Nothing else: no stop exit, no profit target.
- Entry by hand: one combo limit order near the mid.
- Judge the test by process (every entry day looked at and logged, fills near the quotes, no rule breaks), not profit.

## SWE-SPREAD: bull call debit spread
- Buy 1 call at the strike nearest the month-end close, sell 1 call about 5% higher (nearest strike to close x 1.05).
- Size: 1 spread. Skip if net debit (ask of long minus bid of short) is above $2,000, if the two legs' bid/ask widths sum above the larger of $0.50 and 8% of the debit per share, or if data is missing.
- Reserve $5,000. Budget line -$2,000 from the book's peak (a budget for the test, not an alarm): at the line no new spreads, open spreads run to their exit, review together.
- Journal tag "SWE-SPREAD".
- Original model results (2005-2026, one spread per ETF): about 256 spreads, 58% wins, profit factor 1.9, worst drawdown about $10,000 (five times the budget line), 2022 lost on every spread.

## SWE-PUTCS: bull put credit spread
- Sell 1 put at the strike nearest the month-end close, buy 1 put at the strike nearest close x 0.97 (about 3% lower).
- Skip if credit < 15% of the width, max loss ((width - credit) x 100) above $3,500, leg bid/ask widths sum above the larger of $0.50 and 8% of the credit per share, or data missing.
- Own paper account (the original used a $10,000 Alpaca paper account because the IBKR level did not allow credit spreads). Collateral is the full width per spread. Max 3 open. Alert when a spread's mark loss reaches $1,500. Review line -$1,500 from the book's peak (one losing SPY or QQQ spread can cross it; accepted, not a rule break): no new entries, review together.
- Journal tag "SWE-PUTCS". The scheduled tasks never read the second account; the journal rows are the record, quotes come from the IBKR option tools.
- Gate: the test ends at 6 closed spreads or a date you choose. A pass is a PROCESS pass (no rule breaks, fills within about $0.10 per share of the IBKR mid); it never proves the strategy works and never opens a live trial by itself.
- Original model results (2005-2026): about 254 spreads, 72% wins, profit factor 1.7 on model prices, but a stress test with fuller costs came out about break-even (profit factor about 1.1). Treat as a process test.

## Combined exposure
The books lean the same way. In an uptrend SPY, QQQ and GLD can sit in TREND-HOLD and carry a call spread and a put spread at once. The Close Loop prints a COMBINED WORST CASE line (information only; above $8,000 "review together"; re-measure the mark for your own sizes).
