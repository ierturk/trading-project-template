"""Merge freshly fetched IBKR daily bars into the SWE bar cache .
Usage: python3 -I swe_bars_cache.py <cache_dir> <new_dir> <drop_from_YYYY-MM-DD> [--tol 0.005]
cache_dir : state/swe_bars_cache/<SYM>.csv   (header date,open,high,low,close, oldest first) = full history
new_dir   : <scratchpad>/swe_new/<SYM>.csv   (same format) = the bars just fetched (about 12 recent, or 260 for a seed/refetch)
drop_from : bars dated on/after this day are dropped (today's partial bar; common.md DAILY BARS rule)
Per symbol: no cache = seed; 150+ fetched bars with a cache = full replace; otherwise the overlap must match the cache
(close within tol, relative) and have at least 3 common dates, else the symbol is listed under REFETCH and the cache is untouched.
Sanity per row (3% slack): high >= max(open, close), low <= min(open, close), close > 0; bad rows are skipped and counted.
Prints one line per symbol, the symbols below 200 bars ("n of 200 bars"), and a final line "REFETCH: A,B" or "REFETCH: none".
The signals/bars scripts then read cache_dir directly as their bars_dir."""
import csv, glob, os, sys

args = [a for a in sys.argv[1:] if not a.startswith("--")]
tol = 0.005
if "--tol" in sys.argv:
    tol = float(sys.argv[sys.argv.index("--tol") + 1]); args = [a for a in args if a != str(tol) and a != sys.argv[sys.argv.index("--tol") + 1]]
cache_dir, new_dir, drop_from = args[0], args[1], args[2]
os.makedirs(cache_dir, exist_ok=True)

def load(path):
    rows, bad = {}, 0
    for r in csv.DictReader(open(path)):
        d = r["date"][:10]
        try:
            o, h, l, c = (float(r[k]) for k in ("open", "high", "low", "close"))
        except (KeyError, ValueError):
            bad += 1; continue
        if d >= drop_from:
            continue
        if not (c > 0 and h >= max(o, c) * 0.97 and l <= min(o, c) * 1.03):  # 3% slack: IBKR data has quirks (a close a few cents under the low)
            bad += 1; continue
        rows[d] = (o, h, l, c)
    return rows, bad

def save(path, rows):
    with open(path, "w", newline="") as f:
        w = csv.writer(f); w.writerow(["date", "open", "high", "low", "close"])
        for d in sorted(rows):
            w.writerow([d, *[round(x, 4) for x in rows[d]]])

refetch, short = [], []
for p in sorted(glob.glob(os.path.join(new_dir, "*.csv"))):
    sym = os.path.basename(p)[:-4].upper()
    new, bad = load(p)
    cp = os.path.join(cache_dir, sym + ".csv")
    if not new:
        refetch.append(sym); print(f"{sym}: REFETCH (no usable new bars, {bad} bad rows)"); continue
    if not os.path.exists(cp):
        save(cp, new); status = f"seeded {len(new)} bars"
    else:
        old, _ = load(cp)
        common = sorted(set(old) & set(new))
        worst = max((abs(new[d][3] / old[d][3] - 1) for d in common), default=1)
        if len(new) >= 150:
            save(cp, new); status = f"full replace {len(new)} bars"
        elif len(common) < 3 or worst > tol:
            refetch.append(sym); print(f"{sym}: REFETCH (common dates {len(common)}, worst close diff {worst:.2%})"); continue
        else:
            added = len(set(new) - set(old)); old.update(new); save(cp, old); status = f"+{added} new, overlap ok ({len(common)} dates, worst {worst:.2%})"
    total = len(load(cp)[0])
    print(f"{sym}: {status}, {total} bars, last {max(load(cp)[0])}" + (f", {bad} bad rows skipped" if bad else ""))
    if total < 200:
        short.append(f"{sym} {total} of 200 bars")
if short:
    print("NOT ENOUGH HISTORY (no SMA200, no signal yet): " + "; ".join(short))
print("REFETCH: " + (",".join(refetch) if refetch else "none"))
