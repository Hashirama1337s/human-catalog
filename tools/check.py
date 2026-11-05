"""Checks every part file. Errors fail; warnings print.
  python tools/check.py --all                  check every part (overclaim rule = warning)
  python tools/check.py --changed origin/main  overclaim rule is an error on files changed vs that ref
  python tools/check.py --selftest             every file in tools/tests/ must be rejected"""
import argparse
import glob
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SYSTEMS = {"MIG", "TEC", "FOD", "SCI", "MED", "WRT", "ART", "IDE", "GOV", "ECO", "WAR", "TRN", "RCL"}
REGIONS = {"Africa", "West Asia", "South Asia", "East Asia", "Southeast Asia", "Central Asia", "Europe",
           "North America", "Central & South America", "Oceania", "Global"}
REQUIRED = ["id", "year", "dateLabel", "title", "system", "place", "region", "summary", "why", "confidence", "source"]
ALLOWED = set(REQUIRED) | {"yearEnd", "figures", "interchange", "supersedes", "tags", "route", "audit", "withdrawn", "reason", "kind", "question", "evidence", "wouldSettle", "theories"}
ID_RX = re.compile(r"^HC-([A-Z]{3})-(KA\d+|B\d+|C\d+)-\d{2}$")
OVERCLAIM = re.compile(r"\b(first|oldest|earliest|only|invented|proved)\b", re.I)
QUALIFIED = re.compile(r"\b(earliest|oldest|first)\s+(known|surviving|recorded|documented|dated|attested)\b"
                       r"|\b(known|surviving|recorded|documented)\s+(earliest|oldest|first)\b", re.I)


def date_code(y):
    return ("KA" + str(round((1950 - y) / 1000))) if y < -9050 else ("B" + str(-y)) if y < 0 else ("C" + str(y))


def check_part(p, path, strict_overclaim):
    errs, warns = [], []
    if not isinstance(p, dict):
        return ["not a JSON object"], []
    missing = [k for k in REQUIRED if p.get(k) in (None, "")]
    if missing:
        errs.append(f"missing {missing}")
    extra = set(p) - ALLOWED
    if extra:
        errs.append(f"unknown fields {sorted(extra)}")
    if missing:
        return errs, warns
    pid = p["id"]
    if pid != "NEW":
        m = ID_RX.match(pid)
        if not m:
            errs.append(f"bad id {pid}")
        else:
            if m.group(1) != p["system"]:
                errs.append("id system != system")
            if isinstance(p["year"], int) and m.group(2) != date_code(p["year"]):
                # part numbers are permanent: a later date correction keeps the original number
                warns.append(f"id date code {m.group(2)} differs from year {date_code(p['year'])} (date corrected after numbering)")
        if path and os.path.splitext(os.path.basename(path))[0] != pid:
            errs.append("filename != id")
    if p["system"] not in SYSTEMS:
        errs.append(f"system {p['system']}")
    if p["region"] not in REGIONS:
        errs.append(f"region {p['region']}")
    if p["confidence"] not in ("established", "debated"):
        errs.append("confidence must be established|debated")
    y, ye = p["year"], p.get("yearEnd")
    if not isinstance(y, int) or y == 0:
        errs.append("year must be a non-zero integer")
    if ye is not None and (not isinstance(ye, int) or ye == 0 or (isinstance(y, int) and ye < y)):
        errs.append("yearEnd must be a non-zero integer >= year")
    lab = p["dateLabel"]
    if isinstance(y, int):
        if "BCE" in lab and y > 0:
            errs.append("label says BCE but year > 0")
        if y < 0 and not re.search(r"BCE|ago|BC\b", lab):
            errs.append("year < 0 but label has no BCE / years ago")
    if len(p["title"]) > 60:
        errs.append("title > 60 chars")
    if len(p["summary"].split()) > 40:
        errs.append("summary > 40 words")
    if len(p["why"].split()) > 25:
        errs.append("why > 25 words")
    if len(p.get("figures") or []) > 4:
        errs.append("more than 4 figures")
    src = p["source"]
    if not src.startswith("https://") or "/w/index.php?search" in src or "action=edit" in src or ".m.wikipedia" in src:
        errs.append("source must be an https page (not a search, edit or mobile link)")
    if p["confidence"] == "established":
        text = (p["title"] + " " + p["summary"])
        if OVERCLAIM.search(QUALIFIED.sub("", text)):
            (errs if strict_overclaim else warns).append("bare first/oldest/only/invented on an established part")
    for item in p.get("interchange") or []:
        if re.search(r"\b(spread|brought|introduced from|adopted from)\b", item, re.I):
            warns.append(f"interchange may describe contact, not independence: {item[:60]}")
    return errs, warns


def load(path):
    with open(path, encoding="utf8") as fh:
        return json.load(fh)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--changed")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        bad = 0
        for f in sorted(glob.glob(os.path.join(ROOT, "tools", "tests", "*.json"))):
            try:
                e, _ = check_part(load(f), None, True)
            except Exception as ex:
                e = [str(ex)]
            print(("REJECTED " if e else "MISSED   ") + os.path.basename(f) + (": " + e[0] if e else ""))
            bad += not e
        sys.exit(1 if bad else 0)
    files = sorted(glob.glob(os.path.join(ROOT, "data", "parts", "*", "*.json")))
    touched = set()
    if a.changed:
        diff = subprocess.run(["git", "diff", "--name-only", a.changed, "--", "data/parts"], cwd=ROOT,
                              capture_output=True, text=True).stdout.split()
        touched = {os.path.normpath(os.path.join(ROOT, d)) for d in diff}
    n_err = n_warn = 0
    seen, ids = {}, set()
    europe = 0
    for f in files:
        try:
            p = load(f)
        except json.JSONDecodeError as ex:
            print(f"ERROR {f}: invalid JSON {ex}")
            n_err += 1
            continue
        e, w = check_part(p, f, os.path.normpath(f) in touched)
        key = (str(p.get("title", "")).lower().strip(), p.get("year"))
        if key in seen:
            e.append(f"duplicate of {seen[key]}")
        seen[key] = p.get("id")
        if p.get("id") != "NEW" and p.get("id") in ids:
            e.append("id used twice")
        ids.add(p.get("id"))
        europe += p.get("region") == "Europe"
        rel = os.path.relpath(f, ROOT)
        for x in e:
            print(f"ERROR {rel}: {x}")
        for x in w:
            print(f"warn  {rel}: {x}")
        n_err += len(e)
        n_warn += len(w)
    share = 1 - europe / max(len(files), 1)
    print(f"{len(files)} parts, {share:.0%} outside Europe, {n_err} errors, {n_warn} warnings")
    if share < 0.40:
        print("warn  region balance below 40% outside Europe")
    sys.exit(1 if n_err else 0)


if __name__ == "__main__":
    main()
