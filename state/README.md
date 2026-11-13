# state/ (create in your project at /mnt/project-files/scheduled-tasks/state/)

Files the tasks create and keep; start empty:
- `swe_bars_cache/<SYM>.csv`: daily bars (date,open,high,low,close), built by the first Close Loop run
- `swe_contracts.json`: {"SPY": <contract id>, ...}; tasks add missing ids with `search_contracts`
- `ibkr_account.json`: {"id": "{{PAPER_ACCOUNT}}", "label": "paper"} fallback when the connector shows no id
- `live_positions.json`, `live_hist.json`, `close_loop_result.json`, `routine_version.txt`, `desk-hashes.json`: written by the tasks
