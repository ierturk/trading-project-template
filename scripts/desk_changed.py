"""Skip Trading Desk writes that change nothing (Close Loop step 4, since 28 Oct 2026).
Usage: python3 desk_changed.py check <name> <file.json>   -> prints "changed" or "same"
       python3 desk_changed.py save  <name> <file.json>   -> run after the dataset update succeeded
Compares the file's rows, ignoring every "as_of" key, with the hash saved after the last successful update
(state/desk-hashes.json next to this script). A missing hash counts as "changed"."""
import hashlib, json, os, sys

mode, name, path = sys.argv[1], sys.argv[2], sys.argv[3]
store = os.path.join(os.path.dirname(os.path.abspath(__file__)), "state", "desk-hashes.json")

def strip(x):
    if isinstance(x, dict):
        return {k: strip(v) for k, v in x.items() if k != "as_of"}
    if isinstance(x, list):
        return [strip(v) for v in x]
    return x

h = hashlib.md5(json.dumps(strip(json.load(open(path))), sort_keys=True).encode()).hexdigest()
saved = json.load(open(store)) if os.path.exists(store) else {}
if mode == "check":
    print("same" if saved.get(name) == h else "changed")
elif mode == "save":
    saved[name] = h
    os.makedirs(os.path.dirname(store), exist_ok=True)
    json.dump(saved, open(store, "w"), indent=0, sort_keys=True)
    print("saved", name)
