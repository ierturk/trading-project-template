# Trading project template

A starter pack for a Claude project that watches a small set of US ETFs for you, keeps paper-trading books, and reports every day. **It never places orders.** You trade by hand; Claude checks, computes and reports.

It is a copy of a working setup with all personal details removed. Everything you must fill in is written as `{{PLACEHOLDER}}` (list in [PLACEHOLDERS.md](PLACEHOLDERS.md)).

Not financial advice. The strategies here are research ideas tested on past data. Paper trade first and decide for yourself.

## What you get

| Folder | What it is |
|---|---|
| `project/` | Generic project instructions to paste into your Claude project, plus the working rules |
| `prompts/` | The two scheduled tasks: **Close Loop** (after the US close) and **Open Check** (before the open), shared blocks, weekly digest |
| `skills/` | Three skills: `swe-check` (on-demand signal check), `swe-fill-log` (log a fill you did by hand), `weekly-digest` |
| `strategies/` | Rules for the stock books (SWE ETF breakout, TREND-HOLD) and the two optional option-spread paper books |
| `desk/` | Spec for a blank "Trading Desk" dashboard artifact and its datasets |
| `scripts/` | Small Python helpers (signals, bar cache, month-end check, review line). Standard library only |

## The setup in one picture

1. **Close Loop** runs weekdays after the US close. It reads your broker account (read only), fetches daily bars, computes signals for the next open and the monthly TREND-HOLD list, marks any open spreads, refreshes the Desk, and writes a result file.
2. **Open Check** runs weekdays before the open. It reads the Close Loop result and gets live quotes only for what is due, so on most days it is one line: "nothing due today".
3. You place any order **by hand** in your broker app, then send Claude a fill line. The `swe-fill-log` skill records it in the Desk journal and checks it against the rules.
4. The Desk dashboard shows signals, books against their review lines, the journal and the rules.

## Set it up (about an hour)

1. **Create the project.** In Claude, create a new project. Add your own GitHub repo (fork or copy this one) as a project source if you want the files versioned.
2. **Put the files in the project folder.** Copy `prompts/`, `strategies/`, `scripts/` and `desk/` into the project's shared files, keeping the folder names. The prompts expect these paths, so edit them in `prompts/common.md` if you rename anything:
   - `/mnt/project-files/scheduled-tasks/` (the prompts, `desk_changed.py`, `state/`)
   - `/mnt/project-files/research/swe-ibkr/scripts/` (the helper scripts in `scripts/`, except `desk_changed.py`, which goes in `scheduled-tasks/` next to the prompts; rename the prompt files there as `close-loop.md`, `open-check.md`, `common.md`, `close-loop-spreads.md`, `close-loop-routine-rows.md`, `weekly-digest.md`; the `state/` folder is created by the tasks, see `state/README.md`)
   - `/mnt/project-files/research/` (the strategy rule files)
3. **Paste the project instructions.** Copy `project/project-instructions.md` into the project's instructions and fill the placeholders.
4. **Connect your broker for reading.** The prompts were written for the Interactive Brokers (IBKR) connector (price history, quotes, account read, option data). Another broker works if its connector offers the same reads; then edit the tool names in `prompts/common.md`. Put the connector on a **paper** account first. Never grant or use order tools for these tasks.
5. **Install the skills.** Ask Claude to save each file under `skills/` as a skill (the project has a "propose skills" flow), after filling the placeholders.
6. **Build the Desk** from `desk/desk-spec.md` (ask Claude to create it as a dashboard artifact), then put its link in `prompts/common.md` as `{{DESK_URL}}`.
7. **Seed the bar cache.** Run the Close Loop once by hand; with an empty cache it fetches 260 bars per ETF (see `prompts/common.md`). Do this on a weekday after the close.
8. **Create the two scheduled tasks** from `prompts/close-loop.md` and `prompts/open-check.md`:
   - Close Loop: 18:17 New York time, Monday to Friday.
   - Open Check: 08:43 New York time, Monday to Friday.
   - Output: push notification only. A smaller model is enough for both.
   - Test each by running it manually before relying on the schedule.
9. **Check the first morning.** If the Open Check says "CLOSE LOOP MISSING" or "OLD", the evening task did not run; it never uses old numbers.

## Rules that are built in (keep them)

- **Report only.** No task, skill or script places, changes or cancels an order or an order instruction, on paper or live. You enter every order by hand.
- **No orders without your explicit words** naming the exact order. "Looks safe" is not approval.
- **Check every backtest report against the settings used** (costs, slippage, balance, position size, date range, symbols). Add costs by hand if the tool ignored them.
- **Never fill numbers from memory.** If a data call fails, the report says so on the first line.
- **One connector environment at a time.** The connector serves paper or live, not both. Keep it on paper for the daily tasks and say so if it shows live.
- Paper first. Run the stock book on paper for several weeks with no rule breaks before any live step, and size a live trial small.

## Books included

- **SWE** (stock): 20-ETF breakout, 8 positions of $1,500, GTC stop 2 x ATR14, exit on a close below the 20-day low. See `strategies/swe.md`.
- **TREND-HOLD** (stock): five ETFs, held only while the ETF and SPY close the month above their 200-day averages, checked monthly. See `strategies/trend-hold.md`.
- **SWE-SPREAD / SWE-PUTCS** (options, optional): monthly call debit spreads and put credit spreads on SPY, QQQ, GLD. Paper only. Needs options permission at your broker (credit spreads usually need a higher level than debit spreads). See `strategies/spreads.md`.

You can switch any book off by setting its STATUS line to DISABLED in `prompts/close-loop.md`.

## Before you share or reuse

Read [PLACEHOLDERS.md](PLACEHOLDERS.md). The numbers in `strategies/` (profit factors, drawdowns) come from the original author's backtests on data up to 2026 and are examples of what to expect, not promises. Rerun them on your own data and costs.
