# People list

Built from Wikidata (CC0) with the queries in `tools/people/` (pull2, pull3, pull4, then compact2 and linkfig).

Rows: `[wikidata id, name, description, born, born precision, died, died precision, language editions, flags]`.
Precision follows Wikidata (11 day, 10 month, 9 year, 8 decade, 7 century). Julian-calendar dates are converted back to
the Julian calendar, so dates match the history books.

Included: people covered in at least 15 Wikipedia language editions if born before 1500, 25 if born 1500-1799, 40 if
later; no living people (only people with a recorded death, or born in or before 1925); plus everyone named in a catalog
part. Flags: `legend` = Wikidata files the person as possibly legendary; `fl:<year>` = known only by when they were active.

These rows come straight from Wikidata and were not refereed like catalog parts. See `people-stats.json` for the known
bias (share of women, spread by era).
