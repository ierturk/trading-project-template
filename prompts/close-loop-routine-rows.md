Side file of close-loop.md. Read it ONLY when the tag in `state/routine_version.txt` differs from ROUTINE VERSION (step 4c).

Write the Desk dataset `routine` (the Guide & Rules table). Read the current rows with Artifact action "read" (url = the Desk, path = the asset id from the dataset's source.url `/_blob/<id>`). If that read fails, write the standard rows below from scratch. Keys per row: order, when, what, kind, detail. Standard rows:
1. "Weekdays 18:17 New York" / "Close Loop report (Mondays also the weekly digest)" / "Scheduled task, push only" / what it reads and writes (account read-only, bars, signals for the next open, TREND-HOLD list, spread marks, Desk refresh; which books are ON; sizes and review lines; report pushed to your phone).
2. "Weekdays 08:43 New York" / "Open Check" / "Scheduled task, push only" / reads the Close Loop result, says first if it failed or is missing, gets live quotes only for what is due at the open (SWE signals, TREND-HOLD order days, first-trading-day spread entries, CLOSE lines). No orders.
3. "On request" / skills (swe-check, swe-fill-log, weekly-digest) / "Skill" / what each does and that none places orders.
Describe only books whose STATUS is ENABLED. When done write the ROUTINE VERSION value into `state/routine_version.txt` and upload `routine` by the DESK method.
