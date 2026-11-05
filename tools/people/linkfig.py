"""Link every person named in a catalog part ("figures") to a Wikidata id, and add missing ones to people.json.
1) exact name match against people.json;  2) unmatched -> Wikidata search API (wbsearchentities, en), keep the first
   result that is a human (P31 Q5 / Q21070568) per a batched SPARQL check, with its dates;  3) write figure-qids.json.
Polite: one search call per name, 0.2 s apart."""
import glob
import json
import os
import re
import time
import urllib.parse
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
UA = {"User-Agent": "human-catalog-build/2.2 (open history catalog)"}


def get_json(url, tries=8):
    for k in range(tries):
        try:
            return json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60))
        except urllib.error.HTTPError as e:
            if e.code not in (429, 503) or k == tries - 1:
                raise
            time.sleep(120)
people = json.load(open(os.path.join(ROOT, "people", "people.json"), encoding="utf8"))
by_name = {}
for r in people:
    by_name.setdefault(r[1].lower(), r[0])
figs = set()
for f in glob.glob(os.path.join(ROOT, "data", "*.json")):
    for p in json.load(open(f, encoding="utf8")):
        for x in p.get("figures") or []:
            if x and not re.search(r"\b(and|team|crew|people|computers|programmers|talkers|unknown)\b", x, re.I):
                figs.add(x.strip())
link, unmatched = {}, []
for x in sorted(figs):
    q = by_name.get(x.lower())
    (link.__setitem__(x, q) if q else unmatched.append(x))
print("figures", len(figs), "matched exactly", len(link), "to search", len(unmatched))
CACHE = os.path.join(HERE, "search-cache.json")
cand = json.load(open(CACHE, encoding="utf8")) if os.path.exists(CACHE) else {}
errs = 0
for x in [u for u in unmatched if not cand.get(u)]:
    url = "https://www.wikidata.org/w/api.php?" + urllib.parse.urlencode({"action": "wbsearchentities", "search": x, "language": "en", "type": "item", "limit": 3, "format": "json"})
    try:
        res = get_json(url)
        cand[x] = [s["id"] for s in res.get("search", [])]
    except Exception as e:
        errs += 1
        if errs <= 3:
            print("search error", x, str(e)[:120])
        time.sleep(2)
        continue
    time.sleep(4)
    json.dump(cand, open(CACHE, "w", encoding="utf8"), ensure_ascii=False)
json.dump(cand, open(CACHE, "w", encoding="utf8"), ensure_ascii=False)
ids = sorted({q for v in cand.values() for q in v})
info = {}
HUMAN = {"Q5", "Q21070568"}


def tv(claims, prop):
    for c in claims.get(prop, []):
        dv = c.get("mainsnak", {}).get("datavalue", {})
        if dv.get("type") == "time":
            return dv["value"]["time"].lstrip("+")
    return None


for i in range(0, len(ids), 50):
    url = "https://www.wikidata.org/w/api.php?" + urllib.parse.urlencode({"action": "wbgetentities", "ids": "|".join(ids[i:i + 50]),
          "props": "claims|labels|descriptions|sitelinks", "languages": "en", "format": "json"})
    ents = get_json(url).get("entities", {})
    for q, e in ents.items():
        cl = e.get("claims", {})
        kinds = {c.get("mainsnak", {}).get("datavalue", {}).get("value", {}).get("id") for c in cl.get("P31", [])}
        k = next((x for x in kinds if x in HUMAN), None)
        if not k:
            continue
        info[q] = {"kind": "/" + k, "name": e.get("labels", {}).get("en", {}).get("value", ""),
                   "desc": e.get("descriptions", {}).get("en", {}).get("value", ""),
                   "born": tv(cl, "P569"), "died": tv(cl, "P570"), "fl": tv(cl, "P1317"), "links": len(e.get("sitelinks", {}))}
    time.sleep(5)


def yr(v):
    m = re.match(r"^(-?)(\d+)", v or "")
    if not m:
        return None
    y = int(m.group(2)) * (-1 if m.group(1) else 1)
    return y - 1 if y <= 0 else y


have = {r[0] for r in people}
added, nohit = 0, []
for x in unmatched:
    q = next((c for c in cand.get(x, []) if c in info), None)
    if not q:
        nohit.append(x)
        continue
    link[x] = q
    if q in have:
        continue
    r = info[q]
    b, d, fl = yr(r.get("born")), yr(r.get("died")), yr(r.get("fl"))
    if b is None and d is None and fl is None:
        continue
    if d is None and ((b or fl or 0) > 1925):
        continue  # possibly living: not added
    flag = ("legend" if r.get("kind", "").endswith("Q21070568") else "") + (("|fl:%d" % fl) if b is None and fl is not None else "")
    people.append([q, r.get("name", x), (r.get("desc") or "")[:90], b, 9 if b is not None else None, d, 9 if d is not None else None, int(r.get("links", 0)), flag.strip("|")])
    have.add(q)
    added += 1
json.dump(people, open(os.path.join(ROOT, "people", "people.json"), "w", encoding="utf8"), ensure_ascii=False, separators=(",", ":"))
json.dump(link, open(os.path.join(ROOT, "people", "figure-qids.json"), "w", encoding="utf8"), ensure_ascii=False, indent=0)
print("linked", len(link), "of", len(figs), "| added to people", added, "| no human found", len(nohit), nohit[:25])
for nm in ("Nzinga", "Sundiata", "Kimpa"):
    print(nm, [(k, v) for k, v in link.items() if nm.lower() in k.lower()])
