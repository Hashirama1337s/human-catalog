"""people-raw2.json -> ../../people/people.json  rows [qid, name, desc, born, bprec, died|null, dprec|null, links]
- Wikidata RDF timeValue is proleptic Gregorian with astronomical years (0000 = 1 BCE).
- Dates whose calendar model is Julian and precision is day/month are converted back to the Julian calendar (so Newton is
  born 25 December 1642, as history books print it). Year-or-coarser precision is left as the stored year.
- Historical year = astronomical year - 1 for astronomical years <= 0.
Also prints the bias numbers disclosed on the page."""
import json
import os
import re
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
JULIAN = "http://www.wikidata.org/entity/Q1985786"
RX = re.compile(r"^(-?)(\d+)-(\d\d)-(\d\d)")


def gregorian_to_jdn(y, m, d):
    a = (14 - m) // 12
    y2, m2 = y + 4800 - a, m + 12 * a - 3
    return d + (153 * m2 + 2) // 5 + 365 * y2 + y2 // 4 - y2 // 100 + y2 // 400 - 32045


def jdn_to_julian(j):
    c = j + 32082
    d = (4 * c + 3) // 1461
    e = c - 1461 * d // 4
    m = (5 * e + 2) // 153
    return d - 4800 + m // 10, m + 3 - 12 * (m // 10)


def year_of(value, prec, cal):
    m = RX.match(value or "")
    if not m:
        return None
    y = int(m.group(2)) * (-1 if m.group(1) else 1)
    mo, dd = int(m.group(3)), int(m.group(4))
    if cal == JULIAN and prec >= 10:
        y, _ = jdn_to_julian(gregorian_to_jdn(y, mo, dd))
    return y - 1 if y <= 0 else y


raw = json.load(open(os.path.join(HERE, "people-raw2.json"), encoding="utf8"))
rows, drop = [], Counter()
sex = Counter()
for r in raw:
    name = (r.get("name") or "").strip()
    bp = int(r.get("bprec", 9))
    b = year_of(r.get("born"), bp, r.get("bcal"))
    d = year_of(r.get("died"), int(r.get("dprec", 9)), r.get("dcal")) if r.get("died") else None
    if b is None or not name or re.fullmatch(r"Q\d+", name):
        drop["no date or name"] += 1
        continue
    dp_ = int(r.get("dprec", 9)) if r.get("died") else 11
    coarse = bp < 9 or dp_ < 9  # decade/century/millennium: Wikidata stores the period start, so spans are not exact
    slack = 0 if not coarse else (100 if min(bp, dp_) == 7 else 10 if min(bp, dp_) == 8 else 1000)
    if d is not None and (d < b - slack or d - b > 125 + slack):
        drop["impossible lifespan"] += 1
        continue
    if d is None and b > 1925:
        drop["possibly living"] += 1
        continue
    rows.append([r["p"].rsplit("/", 1)[1], name, (r.get("desc") or "").strip()[:90], b, bp, d,
                 int(r["dprec"]) if r.get("dprec") else None, int(r["links"])])
    sex[{"http://www.wikidata.org/entity/Q6581072": "female", "http://www.wikidata.org/entity/Q6581097": "male"}.get(r.get("sex"), "other/unknown")] += 1
# --- merge pass 2 (no literal birth: death or floruit) and pass 3 (possibly legendary, with birth) ---
seen = {r[0] for r in rows}
for f, legendary in (("people-raw3.json", None), ("people-raw4.json", True)):
    if not os.path.exists(os.path.join(HERE, f)):
        continue
    for r in json.load(open(os.path.join(HERE, f), encoding="utf8")):
        q = r["p"].rsplit("/", 1)[1]
        if q in seen:
            continue
        name = (r.get("name") or "").strip()
        if not name or re.fullmatch(r"Q\d+", name):
            continue
        leg = legendary or r.get("type", "").endswith("Q21070568")
        b = year_of(r.get("born"), 9, "") if r.get("born") else None
        d = year_of(r.get("died"), 9, "") if r.get("died") else None
        fl = year_of(r.get("floruit"), 9, "") if r.get("floruit") else None
        if b is None and d is None and fl is None:
            continue
        if b is None and d is None and fl is not None and fl > 1925:
            continue
        if b is not None and d is None and b > 1925:
            continue
        flag = ("legend" if leg else "") + (("|fl:%d" % fl) if (b is None and fl is not None) else "")
        rows.append([q, name, (r.get("desc") or "").strip()[:90], b, 9 if b is not None else None, d, 9 if d is not None else None, int(r["links"]), flag.strip("|")])
        seen.add(q)
rows = [r + [""] if len(r) == 8 else r for r in rows]
rows.sort(key=lambda x: (-x[7], x[3] if x[3] is not None else (x[5] or 0)))
os.makedirs(os.path.join(ROOT, "people"), exist_ok=True)
json.dump(rows, open(os.path.join(ROOT, "people", "people.json"), "w", encoding="utf8"), ensure_ascii=False, separators=(",", ":"))
n = len(rows)
era = Counter("before 500" if (r[3] if r[3] is not None else (r[5] or 0)) < 500 else "500-1499" if (r[3] or r[5] or 0) < 1500 else "1500-1799" if (r[3] or r[5] or 0) < 1800 else "1800-1899" if (r[3] or r[5] or 0) < 1900 else "1900+" for r in rows)
stats = {"people": n, "dropped": dict(drop), "female_share": round(sex["female"] / n, 3), "by_birth_era": dict(era),
         "death_unknown": sum(1 for r in rows if r[5] is None), "coarse_birth_precision": sum(1 for r in rows if r[4] is not None and r[4] < 9), "legendary": sum(1 for r in rows if "legend" in r[8]), "dated_by_death_or_floruit_only": sum(1 for r in rows if r[3] is None),
         "bytes": os.path.getsize(os.path.join(ROOT, "people", "people.json"))}
json.dump(stats, open(os.path.join(ROOT, "people", "people-stats.json"), "w"), indent=1)
print(json.dumps(stats, indent=1))
for nm in ("Homer", "Laozi", "Isaac Newton", "Socrates", "Julius Caesar", "Ibn Battuta", "Nzinga of Ndongo and Matamba", "Gregor Mendel", "Sundiata Keita", "Kimpa Vita", "Hypatia"):
    print([x for x in rows if x[1] == nm][:1] or ("MISSING " + nm))
