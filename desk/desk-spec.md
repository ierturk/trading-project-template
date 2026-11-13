# Blank Trading Desk: spec

Ask Claude to build this as a dashboard artifact in your own project ("create the Trading Desk from desk/desk-spec.md"), then put its link in `prompts/common.md` as `{{DESK_URL}}`. The scheduled tasks only refresh its datasets; edits to the page itself are done in a conversation.

## Tabs
1. **Today**: Daily brief card (rows from `daily_brief`: account, SWE, spread, PUTCS, Trend-hold, Open check), signals table (`swd_signals`), open positions per book, Books card (slots, risk and review line per book), open spread marks (`marks`), events list (`events`).
2. **Journal**: table of `sim_journal` with filter chips per strategy (SWE, TREND-HOLD, SWE-SPREAD, SWE-PUTCS), equity-by-book chart, closed trades.
3. **Guide & Rules**: the rules text of each book (copy from `strategies/`), the scheduled-task table (`routine`), an "Ask Claude by name" card listing: Close Loop, Open Check, SWE check on demand (skill swe-check), fill log (skill swe-fill-log), weekly digest. Each entry says what to say, what it reads, what it writes; none places orders.

## Datasets (JSON arrays of rows, stored as file blobs under `datasets/<name>`)
| Dataset | Written by | Row keys |
|---|---|---|
| `daily_brief` | Close Loop (and one `open_check` row from the Open Check) | id, as_of, attention, time, kind (Account/SWE), item, note |
| `routine` | Close Loop (when the routine version changes) | order, when, what, kind, detail |
| `events` | Monday digest | date, event, kind, note, confirmed |
| `swd_signals` | Close Loop | symbol, close, sma200, hi50, lo20, atr14, signal, stop, shares, note, as_of |
| `swe_bars` | Close Loop | symbol, date, open, high, low, close (bars since your start date) |
| `marks` | Close Loop | strategy, symbol, expiry, mark, pnl, dte, as_of |
| `sim_journal` | swe-fill-log skill only | id, date, strategy, symbol, qty, entry, stop, status, exit, exit_date, open_px, exit_open_px, pnl, plus expiry, long_strike, short_strike for spreads |
| `swe_bt_summary` | by hand | your backtest summary numbers |

Empty file datasets keep one row `[{"placeholder": true}]`. Never let a task create or write any other dataset.

## Calcs the page needs
Book equity and open P&L per strategy from `sim_journal` plus last bars; review-line distance per book (SWE -$3,000, TREND-HOLD -$2,500, SWE-SPREAD -$2,000 budget, SWE-PUTCS -$1,500); slots used / 8; free cash per book; slippage from `open_px`/`exit_open_px`. SWE calcs must filter strategy "SWE" so other books are excluded.

## Page conventions
- Show "Daily brief", not time-of-day names, so the card stays right when you change schedules.
- Keep JavaScript strings free of apostrophes inside single-quoted strings.
- After you change anything the Desk shows (rows, sizes, review lines, events, signals, journal, guide text), align the Guide & Rules tab too.
