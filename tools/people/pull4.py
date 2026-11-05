"""Third pass: 'human who may be fictional' (Q21070568) WITH a literal birth date (e.g. Homer). Output people-raw4.json"""
import json
import urllib.parse
import urllib.request

Q = """PREFIX wdt: <http://www.wikidata.org/prop/direct/>
PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX wikibase: <http://wikiba.se/ontology#>
PREFIX schema: <http://schema.org/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?p (MAX(?l) AS ?links) (SAMPLE(?nm) AS ?name) (SAMPLE(?ds) AS ?desc) (SAMPLE(?b) AS ?born) (SAMPLE(?d) AS ?died) WHERE {
  ?p wdt:P31 wd:Q21070568 . ?p wikibase:sitelinks ?l . FILTER(?l >= 15)
  ?p wdt:P569 ?b . FILTER(isLiteral(?b))
  OPTIONAL { ?p wdt:P570 ?d . FILTER(isLiteral(?d)) }
  ?p rdfs:label ?nm . FILTER(LANG(?nm) = "en")
  OPTIONAL { ?p schema:description ?ds . FILTER(LANG(?ds) = "en") }
} GROUP BY ?p"""
url = "https://qlever.dev/api/wikidata?" + urllib.parse.urlencode({"query": Q})
req = urllib.request.Request(url, headers={"Accept": "application/sparql-results+json", "User-Agent": "human-catalog-build/2.2"})
with urllib.request.urlopen(req, timeout=600) as r:
    rows = json.load(r)["results"]["bindings"]
out = [{k: v["value"] for k, v in row.items()} for row in rows]
json.dump(out, open("people-raw4.json", "w", encoding="utf8"), ensure_ascii=False)
print("rows", len(out), [(r["name"], r["born"][:6]) for r in out if r["name"] in ("Homer", "Laozi", "Sun Tzu", "Pythagoras")][:5])
