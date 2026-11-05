# Part record standard

One JSON object per file, `data/parts/<SYSTEM>/<id>.json`.

```json
{
  "id": "HC-WRT-B3300-01",
  "year": -3300,
  "yearEnd": null,
  "dateLabel": "c. 3300 BCE",
  "title": "Writing invented at Uruk (proto-cuneiform)",
  "system": "WRT",
  "place": "Uruk, Iraq",
  "region": "West Asia",
  "figures": [],
  "summary": "1-2 plain sentences, at most 40 words.",
  "why": "Why it matters, at most 25 words.",
  "interchange": [],
  "supersedes": "",
  "tags": ["writing"],
  "route": null,
  "confidence": "established",
  "source": "https://...",
  "audit": {"status": "hold", "edition": "1.0"}
}
```

| Field | Rule |
|---|---|
| `id` | Permanent part number `HC-<SYS>-<date code>-<serial>`; date code `KA<n>` thousands of years ago, `B<n>` BCE, `C<n>` CE. Never reused. New parts: `"NEW"`. |
| `year`, `yearEnd` | Integers, never 0. Negative = BCE. Deep time `1950 - years_before_present`. `yearEnd` for spans, else `null`. |
| `dateLabel` | How a careful book prints the date. |
| `system` | `MIG` Origins & Migration · `TEC` Tools & Technology · `FOD` Food & Farming · `SCI` Science & Mathematics · `MED` Medicine & Health · `WRT` Writing & Records · `ART` Art, Music & Story · `IDE` Belief & Philosophy · `GOV` Power, Law & Government · `ECO` Trade, Money & Work · `WAR` War & Conflict · `TRN` Exploration & Transport · `RCL` Notices (plagues, eruptions, collapses) |
| `region` | Africa · West Asia · South Asia · East Asia · Southeast Asia · Central Asia · Europe · North America · Central & South America · Oceania · Global |
| `figures` | Up to 4 named people. |
| `interchange` | Documented independent parallels only. |
| `tags` | Idea threads (linking, not a claim of independence). |
| `route` | Optional coarse path `[[lat, lon], ...]` for movements of people. |
| `confidence` | `established` or `debated`. |
| `source` | An `https://` page that states the date and claim. |
| `audit` | `hold` / `corrected` (with `notes`) / `new`, and the edition. |

## Open questions ("back-ordered parts")
A part with `"kind": "open"` is a question specialists cannot yet answer. It also carries `question` (one sentence
ending in ?), `evidence` (what we know, ≤ 40 words), `wouldSettle` (what would settle it, ≤ 25 words) and `theories`
(2-4 `{name, idea}` competing explanations specialists actually discuss). Its `confidence` is always `debated`, and its
source must say the question is unresolved. No fringe or pseudo-history theories.
