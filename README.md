# AI News Digest

A daily AI news digest agent that scrapes tech RSS feeds, summarizes articles using Claude, and emails you a curated digest each day.

## How it works

1. Fetches headlines from Ars Technica, MIT Technology Review, and Hacker News (AI-filtered)
2. Scrapes and summarizes each article using Claude Haiku
3. Generates a 5–7 bullet digest, avoiding repetition of previously covered stories
4. Saves the digest locally and emails it to you

## Setup

**1. Install dependencies**
```bash
pip install -r requirements.txt
```

**2. Configure environment variables**

Copy `.env.example` to `.env` and fill in your values:
```bash
cp .env.example .env
```

| Variable | Description |
|---|---|
| `ANTHROPIC_API_KEY` | Your Anthropic API key |
| `GMAIL_USER` | Your Gmail address |
| `GMAIL_APP_PASSWORD` | Gmail [App Password](https://myaccount.google.com/apppasswords) (not your regular password) |
| `DIGEST_RECIPIENT` | Email to send digest to (defaults to `GMAIL_USER`) |

**3. Run**
```bash
python main.py
```

## Output

- Digest is saved to `digests/YYYY-MM-DD.txt`
- A running memory log (`memory.md`) tracks past stories to avoid repetition across runs
