# Agent Skills

## Implemented
- **Web Scraper** — fetches full article text from each RSS entry using requests + BeautifulSoup. Capped at 500 chars per article to keep model input manageable.
- **Memory** — reads `memory.md` before each run to avoid repeating past stories. Appends today's digest to `memory.md` after each run.

## Planned
- **Topic Categorizer** — group stories by theme (e.g. LLMs, robotics, policy, research) so the digest is easier to scan
- **Deduplicator** — detect when the same story appears across multiple feeds and merge them into one entry
- **Source Ranker** — weight more reputable sources (e.g. Nature, MIT) higher when selecting top stories
- **Sentiment Analyzer** — flag whether each story is positive, negative, or neutral in tone
