---
name: "swe-fill-log"
description: "Use when {{OWNER_NAME}} sends a fill line for a paper book: SWE stock or TREND-HOLD stock, SWE-SPREAD call debit spreads, or SWE-PUTCS put credit spreads. Logs it to the Desk sim_journal and checks the rules. Places no orders."
---

# SWE fill log (journal only)

## Hard rules
1. NEVER place, change, cancel or create any order or order instruction. This skill only records fills {{OWNER_NAME}} already did by hand.
2. Write only to the Desk dataset `sim_journal`; never touch other datasets. Spread fills on a second paper account are journal rows only; never read or touch that account.
3. Log only what is stated. Never invent a fill, price, quantity or date. If a field is missing or ambiguous, ask once.
4. After the write say the Desk was aligned (calcs on the page follow from the journal).

## Input
One line per fill: side, symbol, qty, price, optional date/time and stop. Examples:
- Stock: "bought 10 GDX at 88.26 stop 84.11"; "sold 10 GDX at 91.40".
- Spread: "bought 1 SPY Dec18 600/630 call spread at 11.40 debit" / "sold ... at 23.10".
- PUTCS: "sold 1 SPY Jan15 756/718 put spread at 6.80 credit" / "bought back ... at 1.10 debit".
- TREND-HOLD: "trend-hold bought 3 SPY at 756.10". If a stock fill on SPY/QQQ/GLD/XLE/IWM does not say which book (SWE or TREND-HOLD), ask once: the same ETF can be in both.

## Steps
1. Parse each line (default date = today's New York date; ask if unclear).
2. Read `sim_journal` from the Desk (ArtifactData get, collection "datasets", doc "sim_journal" -> data.source.url `/_blob/<id>` -> Artifact read, url = the Desk, path = <id>). Copy the exact keys of an existing row (at least id, date, strategy, symbol, qty, entry, status, exit, exit_date; keep extras such as stop and note). Strategy "SWE" for a SWE stock fill.
3. Rule checks before writing (OK / FLAG; flags do not stop the log, the fill already happened):
   - Slot: open SWE positions after this fill <= 8.
   - Size: qty x price near $1,500 and qty = floor(1500 / signal close); flag above $1,650.
   - Cash: stock-book cash before the buy = 12,000 + closed SWE P&L since the start date - sum of qty x entry of open SWE rows; a buy that costs more = FLAG "not enough cash, the rule was skip".
   - Untested ETF (IBIT, DRAM): FLAG info only.
   - Duplicate symbol open in the SWE book = FLAG (an open TREND-HOLD row on the same ETF is not a duplicate).
   - Signal: a buy must match the latest Entry signal; else FLAG "buy without signal".
   - Stop: a GTC stop at signal close - 2 x ATR14 must exist (read-only `get_account_orders` on paper); missing = FLAG.
   - Exit: a sell should follow a close below the 20-day low or the stop filling; else FLAG "discretionary exit".
3a. Official open (stock fills): find the official open of the fill day in `state/swe_bars_cache/<SYM>.csv`, or ONE `get_price_history` call (STK, ONE_DAY, `step_count` 3). Store it as `open_px` (buy) or `exit_open_px` (sell at the open; a stop fill gets none). If unreadable, leave the key out and say "open not logged". Never guess.
3b. SPREAD fills: strategy "SWE-SPREAD", ONE row per spread: symbol = underlying, entry = net debit per share, qty, plus expiry, long_strike, short_strike. Exit: row Closed, exit = net credit per share, exit_date; pnl = (exit - entry) x 100 x qty minus commission (4 contract-sides at your broker's rate). FLAGS: underlying not SPY/QQQ/GLD; second open spread on one underlying; debit above $20.00 per share; entry not on the first trading day of a month or on an ETF that was OUT at the month-end check (`trend_hold_check.py`); exit more than 7 days before expiry. Spread rows never count toward the stock slots or the stock review line; the book has its own budget line -$2,000.
3c. PUTCS fills: strategy "SWE-PUTCS", one row per spread: symbol, entry = net credit per share, qty, expiry, short_strike, long_strike, account label. Exit: Closed, exit = net debit per share; pnl = (entry - exit) x 100 x qty. FLAGS: as 3b plus credit below 15% of the width, max loss ((width - credit) x 100) above $3,500, long put more than about 4% below the short put, exit more than 7 days before expiry. Own line -$1,500.
3d. TREND-HOLD fills: strategy "TREND-HOLD", one row per position: symbol, date, qty, entry, status, `open_px`; a sell sets Closed with exit, exit_date, `exit_open_px`; pnl = (exit - entry) x qty minus commission. No stop. FLAGS: symbol not in SPY/QQQ/GLD/XLE/IWM; fill not on the first trading day of a month; a buy when the ETF was OUT or a sell when IN (`trend_hold_check.py <cache dir> <fill date>`); size above $2,400; second open row on an ETF; buy above book cash (10,000 + closed P&L - cost of open rows). Own line -$2,500.
4. Write: buy = new row status "Open"; sell/stop = set the matching open row Closed with exit, exit_date; partial sells split the row. Save the full array to `<scratchpad>/sim_journal.json`, then the DESK method (`desk_changed.py check/save`, Artifact publish `asset: true`, `ArtifactData` update with `if_version`). If the update fails once say "Desk NOT refreshed".
5. Reply short: row id, rule checks with any FLAG first, the book now (open count / 8, open P&L), review-line status, and for stock fills the slippage line (fill vs official open in $ and %, "n of 10 fills logged with an open"; at 10 or more say "SLIPPAGE REVIEW due" with the average %).

Not financial advice.
