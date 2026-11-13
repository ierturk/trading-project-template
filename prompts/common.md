# Shared blocks for the Close Loop and the Open Check

Each task prompt points here; read this file at the start of the run and treat it as part of the prompt. Where the task prompt is more specific, the task prompt wins.

## SCOPE
Broker data = the IBKR connector (replace the tool names below if you use another broker). No futures. Alpaca (or another broker's paper account) appears only if you run the put-credit-spread book; tasks never read it, its book is the journal rows.

## NO ORDERS
Never place, change, cancel, confirm or create an order or order instruction, paper or live. {{OWNER_NAME}} trades by hand. Check and report only.

## IBKR CONNECTOR
Tools used: `get_account_summary`, `get_account_positions`, `get_account_balances` (read only), `get_price_history`, `get_price_snapshot`, `get_option_parameters`, `get_option_data`, `search_contracts`. The connector serves ONE environment at a time: paper ({{PAPER_ACCOUNT}}) or live ({{LIVE_ACCOUNT}}). Account id: use the id the call returns; if none, use `state/ibkr_account.json` ({"id","label"}) and say so. Never switch environments. If a call fails, say so in the first line, leave the affected rows and datasets untouched and go on.

## DAILY BARS
`get_price_history`, security_type STK, step ONE_DAY, outside_rth false.
- IBKR limits: 10 requests per second, 30 per minute, 1000 bars per call. A full run is about 22 calls (2 account reads + 20 history calls), so send history calls in batches of at most 6 in parallel per turn, retry rejected ETFs once after `sleep 30`, never exceed 30 calls a minute.
- Cache: `state/swe_bars_cache/<SYM>.csv` (header `date,open,high,low,close`, oldest first, date = bar open time UTC [:10]) holds each ETF's history. Cache has 30+ bars -> `step_count` 12; otherwise (no file, under 30 bars, or listed under REFETCH) -> `step_count` 260. Never fetch fewer than 5 bars (the overlap check needs 3 common dates).
- Save what you fetched as `<scratchpad>/swe_new/<SYM>.csv` with ONE python call (never echo raw bars), then run `python3 -I /mnt/project-files/research/swe-ibkr/scripts/swe_bars_cache.py /mnt/project-files/scheduled-tasks/state/swe_bars_cache <scratchpad>/swe_new <DROP_FROM>`. DROP_FROM = today's New York date, or tomorrow's if the run starts after 22:00 UTC (the signal day is the last completed session). The Close Loop starts after 22:00 UTC, so DROP_FROM = ny_date + 1; the Open Check fetches no bars.
- "REFETCH: A,B" -> fetch those with `step_count` 260 (one batch) and run the script once more; any still listed = report "cache mismatch SYM" and leave it out of the signals. "n of 200 bars" is one short info line (no signal until 200 bars).
- Contract ids live in `state/swe_contracts.json` (symbol -> id); use `search_contracts` only for a missing id and add it to the file.

## LIVE READS (read only)
`get_account_summary` and `get_account_positions`. Show equity, cash, positions per account; flag (info only) any live position other than your idle-cash parking ETF. Nothing from the read goes to the Desk. Two local state files: `state/live_positions.json` (wrapper {"dataset","as_of","rows":[{account,label,symbol,qty,price,value,pnl,checked}]}, replaced each run) and `state/live_hist.json` (rows {date,account,label,equity}; replace the same date+account row, keep other accounts; paper and live never chain).

## DESK
Link: {{DESK_URL}} (see `desk/desk-spec.md`). Tasks only refresh datasets. Method per dataset: write the JSON file; `python3 desk_changed.py check <name> <file>`; upload only when "changed" (Artifact publish with `url` = the Desk, `asset: true`, file_path -> `/_blob/<id>`); `ArtifactData` list collection "datasets" for the doc version; `ArtifactData` update with `if_version`, data `{source:{kind:"file", url:<the /_blob/ url exactly>, name:"<name>.json"}, updated:{at:<now UTC ISO>, by:"Claude scheduled task (<task name>)"}}`; then `desk_changed.py save <name> <file>`. An empty file dataset keeps one row `[{"placeholder": true}]`. Tasks write only: `daily_brief`, `routine` (Close Loop), `events` (Monday digest), `swd_signals`, `swe_bars` (while the SWE step is ENABLED) and `marks`. `sim_journal` is written only by the swe-fill-log skill from fills you report; never create other datasets. If an update fails once, say "Desk NOT refreshed" in the report and the push line.

## SWE STEP
Reads bars, computes signals, writes `swd_signals` and `swe_bars`; never orders. Setup: paper stock book {{PAPER_BALANCE}} account, 8 positions x $1,500, review line -$3,000 from the book's peak counted from {{START_DATE}}. Audit rules: (1) not enough stock-book cash for the full position = skip; (2) every stock fill row in `sim_journal` carries `open_px` (official open of the fill day) so slippage is measurable, review after 10 fills; (3) ETFs not in the original backtest (IBIT, DRAM in the default list) carry the note "untested ETF"; (4) expectation from the original 2006-2026 run of these rules: profit factor about 1.5, about 5% a year on $12,000, a losing year about one in five, drawdown up to about $3,000 (rerun on your own data). The other books (TREND-HOLD, SWE-SPREAD, SWE-PUTCS) are report-only paper books, see `strategies/`.

## END OF RUN PUSH
As the LAST step of every run, load `PushNotification` via ToolSearch (`select:PushNotification`) and call it ONCE with one plain line under 200 characters, no markdown: lead with what needs action (a REVIEW line of any book, a TREND-HOLD LIST or spread entry day, a CLOSE line, a POSITION MISMATCH, a SWE signal, a failed IBKR read, Desk NOT refreshed), else "Close Loop done: nothing needs action" (Open Check: "Open Check done: nothing due today"), then key facts that fit. If the tool is missing or refused, skip it; never loop.

Not financial advice.
