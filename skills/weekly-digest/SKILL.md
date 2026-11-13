---
name: "weekly-digest"
description: "Use when {{OWNER_NAME}} asks for the weekly digest, weekly summary, \"how are the accounts\", balances, cash, the SWE and TREND-HOLD books vs their review lines, the spread books, or upcoming events. Broker read only."
---

# Weekly digest (read only)

## Hard rules
1. NEVER place, change, cancel, confirm or create an order or order instruction. Check and report only.
2. Data = the IBKR connector, Python on its bars, or official web calendars.
3. Never switch the connector environment: it serves paper ({{PAPER_ACCOUNT}}) or live ({{LIVE_ACCOUNT}}); report the one it is on and say which is not read.
4. If a call fails say so in the first line; never fill numbers from memory. Do not re-offer declined ideas or tuning proposals.

## Steps
Follow `prompts/weekly-digest.md` (copy kept in the project folder at `/mnt/project-files/scheduled-tasks/weekly-digest.md`):
1. Balances: `get_account_summary`, `get_account_balances`, `get_account_positions`; account id, equity, cash, positions. In the live account flag (info only) any holding other than your idle-cash parking ETF; in paper the ETFs are the SWE and TREND-HOLD books by design.
2. Change since last week from `state/live_hist.json` (same account only); update that file with today's row.
3. SWE book: open positions x 8 slots, entry, last close, open P&L, closed P&L since the start date, review line via `swe_review_check.py` (a "REVIEW" line goes first), paper goal check (every signal logged, no rule breaks), slippage line (fills with `open_px`; "SLIPPAGE REVIEW due" at 10 fills).
4. Spread books (if enabled): open and closed, closed P&L, marks, distance to their lines, spreads with 7 days or fewer to expiry, goal check; PUTCS gate (closed spreads out of 6 and days left to the gate date; process check only).
5. COMBINED WORST CASE line (info only, not a stop).
6. TREND-HOLD book via `trend_hold_check.py`: positions open of 5, P&L, distance to -$2,500, month-end status, next check date, goal check.
7. Events: every Monday check the next 14 days against official pages (FOMC federalreserve.gov, jobs and CPI bls.gov, NYSE holiday notices); on the first Monday of the month the full 8-week sweep. Update the Desk `events` dataset only if asked.
8. Output: decisions first (REVIEW lines, rule breaks, anything needing a call), then accounts, books, events. One closing line.

Not financial advice.
