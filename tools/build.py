"""Build the catalog page: merge data/parts/**/*.json into site/template.html -> <out>/index.html (+ open data JSON).
Usage: python tools/build.py --out _site"""
import argparse
import glob
import json
import os
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ap = argparse.ArgumentParser()
ap.add_argument("--out", default="_site")
out = os.path.join(ROOT, ap.parse_args().out)
parts = []
for f in sorted(glob.glob(os.path.join(ROOT, "data", "parts", "*", "*.json"))):
    with open(f, encoding="utf8") as fh:
        p = json.load(fh)
    if not p.get("withdrawn"):
        parts.append(p)
parts.sort(key=lambda p: (p["year"], p["system"], p["id"]))
with open(os.path.join(ROOT, "site", "template.html"), encoding="utf8") as fh:
    html = fh.read()
with open(os.path.join(ROOT, "site", "vendor", "land-rings.json"), encoding="utf8") as fh:
    land = fh.read()
payload = json.dumps(parts, ensure_ascii=False).replace("</", "<\\/")
page = html.replace("/*DATA*/", payload).replace("/*LAND*/", land)
os.makedirs(out, exist_ok=True)
with open(os.path.join(out, "index.html"), "w", encoding="utf8") as fh:
    fh.write(page)
with open(os.path.join(out, "human-catalog.json"), "w", encoding="utf8") as fh:
    json.dump(parts, fh, ensure_ascii=False, indent=1)
shutil.copytree(os.path.join(ROOT, "site", "fonts"), os.path.join(out, "fonts"), dirs_exist_ok=True)
for name in ("people.json", "figure-qids.json", "people-stats.json"):
    src = os.path.join(ROOT, "data", "people", name)
    if os.path.exists(src):
        shutil.copy(src, os.path.join(out, name))
outside = sum(p["region"] != "Europe" for p in parts) / max(len(parts), 1)
print(f"built {len(parts)} parts, {outside:.0%} outside Europe, page {len(page) // 1024} KB -> {out}")
