# SWE: ETF breakout stock book (paper first)

STATUS: report only. No task, skill or script places an order; you enter every order by hand and send the fill line.

## Rules
- Universe (20 ETFs): SPY QQQ IWM DIA SMH SOXX XLK XLF XLE XLV XLI XBI KRE GLD GDX SLV IBIT EWZ EWY DRAM. IBIT and DRAM were not in the original backtest ("untested ETF" note on their signals). Edit `SYMS` in `scripts/swe_signals_json.py` to change the list.
- Daily bars, completed sessions only.
- ENTRY: close > 200-day average of closes AND close > highest close of the previous 20 sessions AND SPY close > SPY 200-day average (market filter).
- SIZE: shares = floor($1,500 / signal close). Max 8 open positions. Cash only, no margin. Not enough book cash for the full position = skip. Full book = skip the signal (no swapping of weaker holds).
- ORDER SHAPE (by hand): market-on-open buy at the next open, then a GTC stop at signal close - 2 x ATR14.
- EXIT: held and close < lowest close of the previous 20 sessions, sell at the next open (the stop can fill first).
- REVIEW LINE: -$3,000 from the book's peak (closed P&L plus open positions), counted from your start date. At or past it: no new entries, review together.
- Book money: $12,000 (8 x $1,500). The spread reserve and TREND-HOLD money never count in this book.

## Logging
Journal (`sim_journal`) row per position: symbol, date, qty, entry, stop, open_px (official open of the fill day), status, exit, exit_date, exit_open_px. Review slippage after 10 fills (backtest assumed $0.02 a share).

## Original backtest (rerun on your own data, costs and dates)
2006-2026 on the live rules: profit factor about 1.5, about 5% a year on $12,000, a losing year about one in five, 4 losing years in 21, drawdown up to about $3,000. A short 2022-2026 test showed profit factor 1.65 and drawdown about 13%; prefer the longer run. A shorter list of 18 ETFs gave similar results. Optimization of the 20/20/2 parameters is closed in the original project: do not tune without a new reason.

## Backtest report check
For every backtest: compare the report to the settings used (costs, slippage, balance, position size, date range, symbols). Add commissions by hand if the tool ignored them.

## Before any live step
Run on paper several weeks with every signal logged and no rule breaks. Start live small (the original plan: stock only, up to about half the book, review line scaled down, no margin, options stay paper). Any live step needs your explicit decision.
