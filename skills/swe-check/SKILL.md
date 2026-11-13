---
name: "swe-check"
description: "Use when {{OWNER_NAME}} asks for the SWE check, signal check, \"any signals\", \"what is open\", slots, the review line, the TREND-HOLD book or its month-end list, or the spread / put spread status on the paper books. Reads broker paper data and option quotes, computes signals, reports only; places no orders."
---

# SWE check (paper account, report only)

## Hard rules
1. NEVER place, change, cancel, confirm or create an order or order instruction, paper or live. {{OWNER_NAME}} trades by hand. Do not call order-instruction tools.
2. Data = the IBKR connector or Python on its daily bars. Forex only to convert currencies, never a trade.
3. The scheduled Close Loop and Open Check already run these checks every weekday; this skill is the manual on-request check and changes nothing about them.
4. Never switch the connector environment. If it is not on paper account {{PAPER_ACCOUNT}}, say "SWE not run: connector is not on the paper account" and stop. Never fill numbers from memory; if a call fails, say so in the first line.
5. Align the Desk only when something it shows changes. This skill itself changes nothing.

## Setup
- Paper account {{PAPER_ACCOUNT}}, SWE stock book $12,000: 8 slots x $1,500, cash, no margin. Review line -$3,000 from the book's peak, counted from {{START_DATE}}. Cash rule: not enough stock-book cash for the full position = skip; stock-book cash = 12,000 + closed P&L of SWE rows in `sim_journal` since the start date - sum of qty x entry of the open SWE rows (the spread reserve never counts).
- Universe (20): SPY QQQ IWM DIA SMH SOXX XLK XLF XLE XLV XLI XBI KRE GLD GDX SLV IBIT EWZ EWY DRAM. An ETF with under 200 cached bars gets no signal and is reported as "n of 200 bars". IBIT and DRAM were not in the backtest: show the note "untested ETF" on their Entry signals.
- Expectation (original 2006-2026 run, rerun on your own data): profit factor about 1.5, about 5% a year on $12,000, a losing year about one in five, drawdown up to about $3,000.
- Other paper books: TREND-HOLD (SPY, QQQ, GLD, XLE, IWM, $2,000 each, own cash $10,000, line -$2,500) and the two optional spread books, which open spreads only on the first trading day of a month.

## Steps
1. `get_account_summary` and `get_account_positions`. Report account id, equity, cash, positions. Held SWE symbols = symbols of the OPEN rows with strategy "SWE" in `sim_journal` (read it from the Desk now), never the account positions. Free slots = 8 minus open SWE rows. Cross-check: account quantity per ETF = open SWE qty + open TREND-HOLD qty; report differences as "POSITION MISMATCH <SYM>". Flag (info only) anything off-rule: more than 8 positions, a position without a working GTC stop (`get_account_orders`), size far from $1,500.
2. Bars: cached in `/mnt/project-files/scheduled-tasks/state/swe_bars_cache/<SYM>.csv`. Fetch with `get_price_history` (STK, ONE_DAY, outside_rth false) in batches of at most 6 parallel calls per turn (limits: 10 per second, 30 per minute), `step_count` 12 for an ETF with 30+ cached bars (never fewer than 5), 260 otherwise; contract ids from `state/swe_contracts.json`; retry rejected calls once after `sleep 30`. Save as `<scratchpad>/swe_new/<SYM>.csv` (date,open,high,low,close; never echo raw bars), then `python3 -I /mnt/project-files/research/swe-ibkr/scripts/swe_bars_cache.py <cache dir> <scratchpad>/swe_new <DROP_FROM>` (DROP_FROM = today's New York date, or tomorrow's after 22:00 UTC). "REFETCH: A,B" = fetch those with 260 once and rerun.
3. Signals: `python3 -I .../swe_signals_json.py <cache dir> <scratchpad>/swd_signals.json <HELD,SYMBOLS> <free slots> <free cash>`. Rules: Entry = close > SMA200 and > highest close of the prior 20 days, and SPY close > SPY SMA200. Shares = floor(1500 / signal close). Stop = signal close - 2 x ATR14. Exit = held and close < 20-day low. Entries beyond free slots are "no slot": list as skipped, no swapping of weaker holds.
4. Review line: read `sim_journal` from the Desk, build `swe_bars.json` with `swe_bars_json.py`, run `swe_review_check.py <sim_journal.json> <swe_bars.json>`. A line starting "REVIEW" = no new entries, review together.
5. Report (short): account line; open positions with entry, last close, open P&L, stop; Entry and Exit signals with shares, stop and the order shape you enter by hand (MKT OPG buy, then GTC stop; exits next open); free slots; review status. End with ONE line: what most needs attention (REVIEW, a signal, a failed read, else "nothing needs action").
5b. Spread books (if enabled): rows with strategy "SWE-SPREAD" / "SWE-PUTCS" from `sim_journal`. New spreads only on a SPREAD ENTRY DAY (first trading day of a month): run step 5d's script and, for each of SPY, QQQ, GLD that is IN at the month-end check and has no open row, suggest the spread by `strategies/spreads.md` using `get_option_parameters`/`get_option_data` (market data only). For open rows: mark, P&L, days to expiry, budget/review lines, "CLOSE <SYM> (7 days to expiry)". Never create an order.
5c. COMBINED WORST CASE (paper, info only): worst loss of everything open: SWE stock = qty x (entry - stop); TREND-HOLD = 10% of qty x last close; call spreads = debit x 100 x qty; put spreads = (short - long - credit) x 100 x qty. Print "COMBINED WORST CASE: $<total> = ..." by ETF. Not a stop; above $8,000 add "above the usual range, review together".
5d. TREND-HOLD: `python3 -I .../trend_hold_check.py <cache dir> <today's New York date, or the next trading day after the close> <sim_journal.json>` after step 2 and print its lines (month-end status, the list on the first trading day, the "SPREAD ENTRY DAY" line, the book line with the distance to the review line).
6. Do not write to the Desk unless asked. `sim_journal` rows come only from your fills (use swe-fill-log).

Not financial advice.
