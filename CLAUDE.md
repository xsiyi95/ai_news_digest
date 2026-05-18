# AI News Digest

## Project Goal
A daily AI news digest agent that fetches headlines from reputable sources, scrapes article content, and generates a summary using a local LLM (Ollama).

## Stack
- **Python 3.11** (Anaconda)
- **Ollama** (local LLM, currently using `phi3` model) — no API key needed
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
- Chose Ollama over Anthropic API to avoid paid API credits
- `phi3` model used as it is lighter than `llama3` and less demanding on the Mac
- Article scraping capped at 500 chars per article to keep model input manageable
- `memory.md` gives the agent context of past digests to avoid repetition

## API Cost Estimates
- Model: `claude-haiku-4-5-20251001`
- ~16 API calls per run (15 article summaries + 1 final digest)
- ~$0.02–$0.03 per run
- $5 Anthropic credits ≈ 150–250 runs ≈ 5–8 months of daily runs

## Next Session TODO
- **Set up GitHub repo** for this project (user has a GitHub account)
- **Decide on scheduling approach:**
  - Option A: Remote scheduled agent (Anthropic's cloud) — needs GitHub repo + Anthropic API credits, script must switch from Ollama back to Anthropic API (`claude-haiku-4-5-20251001`)
  - Option B: Local cron job — runs on Mac with Ollama, free, but Mac must be on
- **Optional:** Set up MCP connectors to deliver digest to Slack, Notion, or email instead of just saving to a txt file
