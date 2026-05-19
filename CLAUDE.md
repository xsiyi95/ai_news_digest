# AI News Digest

## Project Goal
A daily AI news digest agent that fetches headlines from reputable sources, scrapes article content, and generates a summary using the Claude API.

## Stack
- **Python 3.11** (Anaconda)
- **Anthropic Claude API** (`claude-haiku-4-5-20251001`) — used in `main.py` for summarization and digest generation
- **Ollama** (`phi3`) — alternate implementation in `main_ollama.py`, runs locally with no API cost
- **feedparser** — reads RSS feeds from news sources
- **requests + BeautifulSoup** — scrapes full article text from each link
- **memory.md** — tracks previously covered stories so the agent avoids repeating them

## How It Works
1. `fetch_headlines()` — pulls top 5 entries from each RSS feed and scrapes article body text
2. `generate_digest()` — sends headlines + memory context to Ollama to produce a 5–7 bullet summary
3. Digest is saved to `digests/YYYY-MM-DD.txt`
4. `memory.md` is updated with today's digest for future context

## News Sources (RSS Feeds)
- Ars Technica Technology Lab
- MIT Technology Review
- Hacker News (AI-filtered)

## Skills
See `skills.md` for implemented and planned agent capabilities.

## Key Decisions
- `main.py` uses the Anthropic Claude API (`claude-haiku-4-5-20251001`) — primary production version with email delivery
- `main_ollama.py` kept as a free local alternative using `phi3` via Ollama, no API key needed
- Article scraping capped at 500 chars per article to keep model input manageable
- `memory.md` gives the agent context of past digests to avoid repetition

## API Cost Estimates
- Model: `claude-haiku-4-5-20251001`
- ~16 API calls per run (15 article summaries + 1 final digest)
- ~$0.02–$0.03 per run
- $5 Anthropic credits ≈ 150–250 runs ≈ 5–8 months of daily runs

## Next Session TODO
- **Set up GitHub Actions for daily scheduling** — user wants to automate `main.py` to run every day via GitHub Actions (free, cloud-based, runs even when Mac is off). Workflow file to create: `.github/workflows/daily_digest.yml` with a `cron: '0 8 * * *'` schedule. Secrets needed in GitHub repo settings: `ANTHROPIC_API_KEY`, `GMAIL_USER`, `GMAIL_APP_PASSWORD`, `DIGEST_RECIPIENT`.
- **Optional:** Set up MCP connectors to deliver digest to Slack, Notion, or email instead of just saving to a txt file

## Pending Code Improvements
- **Parallelize article summarization** — `fetch_headlines()` calls Claude sequentially for 15 articles. Use `asyncio` or `concurrent.futures` to run them in parallel and cut runtime by ~5-10x.
- **Deduplicate `main.py` and `main_ollama.py`** — `load_memory`, `update_memory`, `scrape_article`, `fetch_headlines` are identical in both files. Extract to a shared `utils.py` module.
- **Move hardcoded values to config** — feed URLs, timeouts, model names, `max_tokens` are all hardcoded. Move to a `config.yaml` or env vars.
- **Add retry logic** — no retries anywhere. Add exponential backoff for scraping, Claude API calls, and email sending.
- **Prune `memory.md`** — file grows unbounded. Add rotation to keep only the last N days to avoid increasing Claude's context window costs.
- **Add caching** — scraped article content is re-fetched on every run. Cache with a short TTL to avoid redundant scraping.
