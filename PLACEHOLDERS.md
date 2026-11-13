# Placeholders to fill in

Search the repo for `{{` to find each one.

| Placeholder | Meaning | Example |
|---|---|---|
| `{{OWNER_NAME}}` | Your name as the reports should say it | Alex |
| `{{TIMEZONE}}` | Your time zone for report timestamps | Europe/London |
| `{{PAPER_ACCOUNT}}` | Broker paper account id the daily tasks expect | DU1234567 |
| `{{LIVE_ACCOUNT}}` | Live account id (read-only checks only), or "none" | U1234567 |
| `{{OPTIONS_PAPER_ACCOUNT}}` | Second paper account for put credit spreads, if you use one | optional |
| `{{DESK_URL}}` | Link of your own Trading Desk artifact | https://claude.ai/artifact/... |
| `{{START_DATE}}` | Day your paper stock book starts (also set `START` in two scripts) | 2026-12-01 |
| `{{PAPER_BALANCE}}` | Paper account balance you set | $30,000 |

Also set in `scripts/`: `START` in `swe_bars_json.py` and `swe_review_check.py`, and `FIRST_CHECK` in `trend_hold_check.py`. The NYSE holiday list in `trend_hold_check.py` ends at 2027: extend it.

Sizes ($1,500 x 8, $2,000 x 5, review lines) are the original author's choices. Change them in the strategy files, the scripts and the Desk together.
