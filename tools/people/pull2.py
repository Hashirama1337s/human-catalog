"""People layer v2 (review fixes): Wikidata via QLever, one row per person, date precision + calendar model, no living
people, era-scaled notability. Output: people-raw2.json
Notability (sitelinks = number of Wikipedia/Wikimedia language editions): born before 1500 >= 15; 1500-1799 >= 25; later >= 40.
Living-person rule: included only if a death date is recorded, or born in or before 1925 (shown as 'death date unknown')."""
import json
import urllib.parse
import urllib.request

EP = "https://qlever.dev/api/wikidata"
Q = """PREFIX wdt: <http://www.wikidata.org/prop/direct/>
PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX p: <http://www.wikidata.org/prop/>
PREFIX psv: <http://www.wikidata.org/prop/statement/value/>
PREFIX wikibase: <http://wikiba.se/ontology#>
PREFIX schema: <http://schema.org/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?p (MAX(?l) AS ?links) (SAMPLE(?nm) AS ?name) (SAMPLE(?ds) AS ?desc)
       (SAMPLE(?b) AS ?born) (SAMPLE(?bp) AS ?bprec) (SAMPLE(?bc) AS ?bcal)
       (SAMPLE(?d) AS ?died) (SAMPLE(?dp) AS ?dprec) (SAMPLE(?dc) AS ?dcal) (SAMPLE(?g) AS ?sex) WHERE {
  ?p wdt:P31 wd:Q5 . ?p wikibase:sitelinks ?l . FILTER(?l >= 15)
  ?p wdt:P569 ?b . ?p p:P569/psv:P569 ?bv . ?bv wikibase:timeValue ?b ; wikibase:timePrecision ?bp ; wikibase:timeCalendarModel ?bc .
  OPTIONAL { ?p wdt:P570 ?d . ?p p:P570/psv:P570 ?dv . ?dv wikibase:timeValue ?d ; wikibase:timePrecision ?dp ; wikibase:timeCalendarModel ?dc . }
  OPTIONAL { ?p wdt:P21 ?g . }
  FILTER( (YEAR(?b) < 1500 && ?l >= 15) || (YEAR(?b) < 1800 && ?l >= 25) || ?l >= 40 )
  FILTER( BOUND(?d) || YEAR(?b) <= 1925 )
  ?p rdfs:label ?nm . FILTER(LANG(?nm) = "en")
  OPTIONAL { ?p schema:description ?ds . FILTER(LANG(?ds) = "en") }
} GROUP BY ?p"""
url = EP + "?" + urllib.parse.urlencode({"query": Q})
req = urllib.request.Request(url, headers={"Accept": "application/sparql-results+json", "User-Agent": "human-catalog-build/2.2"})
with urllib.request.urlopen(req, timeout=900) as r:
    rows = json.load(r)["results"]["bindings"]
out = [{k: v["value"] for k, v in row.items()} for row in rows]
json.dump(out, open("people-raw2.json", "w", encoding="utf8"), ensure_ascii=False)
print("rows", len(out))
