"""Second pass: notable humans WITHOUT a birth date but with a death date (P570) or floruit (P1317).
Same era-scaled notability on the year we have. Output people-raw3.json."""
import json
import urllib.parse
import urllib.request

Q = """PREFIX wdt: <http://www.wikidata.org/prop/direct/>
PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX wikibase: <http://wikiba.se/ontology#>
PREFIX schema: <http://schema.org/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?p (MAX(?l) AS ?links) (SAMPLE(?kind) AS ?type) (SAMPLE(?nm) AS ?name) (SAMPLE(?ds) AS ?desc) (SAMPLE(?d) AS ?died) (SAMPLE(?f) AS ?floruit) (SAMPLE(?g) AS ?sex) WHERE {
  VALUES ?kind { wd:Q5 wd:Q21070568 } ?p wdt:P31 ?kind . ?p wikibase:sitelinks ?l . FILTER(?l >= 15)
  FILTER NOT EXISTS { ?p wdt:P569 ?anyb . FILTER(isLiteral(?anyb)) }
  OPTIONAL { ?p wdt:P570 ?d . FILTER(isLiteral(?d)) }
  OPTIONAL { ?p wdt:P1317 ?f . FILTER(isLiteral(?f)) }
  FILTER(BOUND(?d) || BOUND(?f))
  OPTIONAL { ?p wdt:P21 ?g . }
  ?p rdfs:label ?nm . FILTER(LANG(?nm) = "en")
  OPTIONAL { ?p schema:description ?ds . FILTER(LANG(?ds) = "en") }
} GROUP BY ?p"""
url = "https://qlever.dev/api/wikidata?" + urllib.parse.urlencode({"query": Q})
req = urllib.request.Request(url, headers={"Accept": "application/sparql-results+json", "User-Agent": "human-catalog-build/2.2"})
with urllib.request.urlopen(req, timeout=900) as r:
    rows = json.load(r)["results"]["bindings"]
out = [{k: v["value"] for k, v in row.items()} for row in rows]
json.dump(out, open("people-raw3.json", "w", encoding="utf8"), ensure_ascii=False)
print("rows", len(out))
for nm in ("Nzinga", "Njinga", "Sundiata", "Kimpa", "Homer", "Zoroaster", "Laozi", "Sun Tzu"):
    print(nm, [(r["name"], (r.get("died") or r.get("floruit") or "")[:6], r["links"]) for r in out if nm.lower() in r["name"].lower()][:2])
