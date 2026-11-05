# Contributing to the Human Catalog

Thank you. This catalog is only as good as its sources, so every change goes through the same steps:
**robot checks → a reviewer opens your source → merge → you are credited in [ERRATA.md](ERRATA.md) / [CHANGELOG.md](CHANGELOG.md).**

## The easy way
- [Report an error](../../issues/new?template=report-error.yml) or [suggest a part](../../issues/new?template=suggest-part.yml). A source link is required.

## The pull-request way
Each part is one file: `data/parts/<SYSTEM>/<part-number>.json`. Copy an existing file, edit it, and run
`python tools/check.py --all` and `python tools/build.py --out _site` before opening the pull request. New parts leave
`id` as `"NEW"`; the maintainer assigns the permanent number when merging.

## The six rules we learned the hard way
Before the First Edition shipped, referees re-checked all 669 parts and corrected 173 of them. The errors were almost
never dates. They were these:

1. **Open a source and link it.** Wikipedia, Britannica, a museum, a journal. "I remember" is not a source. The source
   must support the date *and* the place.
2. **"Earliest known", never "first ever".** Missing evidence is not proof that nobody did it earlier. Write "oldest
   known", "first recorded", "oldest surviving".
3. **If specialists argue, mark it `debated`.** New finds re-date things.
4. **Places from the source, not from memory.**
5. **Interchange means independent.** List a parallel only if specialists agree there was no contact. Ideas that spread
   by trade or conquest are not interchange.
6. **Plain words, short, your own.** Title ≤ 60 characters, summary ≤ 40 words, why ≤ 25 words. Do not paste sentences
   from the source.

Wording: plagues, famines and collapses are shown as sober Notices. "Superseded" is used for tools and methods, never for
peoples, faiths or cultures.

## Dating
Negative years are BCE and there is no year 0 (1 BCE = `-1`). Deep time: `year = 1950 - years_before_present`.
See [SCHEMA.md](SCHEMA.md) for every field.
