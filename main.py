import os
import logging
import smtplib
import feedparser
import anthropic
from datetime import date
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

FEEDS = [
    "https://feeds.arstechnica.com/arstechnica/technology-lab",
    "https://www.technologyreview.com/feed/",
    "https://hnrss.org/frontpage?q=AI",
]

MEMORY_FILE = "memory.md"

def load_memory() -> str:
    if not os.path.exists(MEMORY_FILE):
        return ""
    with open(MEMORY_FILE, "r") as f:
        return f.read()

def update_memory(digest: str):
    memory = load_memory()
    today = str(date.today())
    entry = f"\n### {today}\n{digest}\n"
    with open(MEMORY_FILE, "a") as f:
        f.write(entry)

def scrape_article(url: str) -> str:
    try:
        response = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(response.text, "html.parser")
        paragraphs = soup.find_all("p")
        text = " ".join(p.get_text() for p in paragraphs[:20])
        return text.strip()
    except Exception as e:
        logger.warning("Failed to scrape %s: %s", url, e)
        return ""

def summarize_article(title: str, content: str) -> str:
    client = anthropic.Anthropic()
    try:
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=400,
            messages=[{
                "role": "user",
                "content": (
                    f"Article title: {title}\n\n"
                    f"Article content:\n{content[:5000]}\n\n"
                    "Write a concise summary of this article in 2-3 sentences, capturing the key facts and significance."
                )
            }]
        )
        return response.content[0].text
    except Exception as e:
        logger.warning("Failed to summarize '%s': %s", title, e)
        return ""

def fetch_headlines() -> str:
    items = []
    for url in FEEDS:
        feed = feedparser.parse(url)
        for entry in feed.entries[:5]:
            article_text = scrape_article(entry.link)
            if article_text:
                summary = summarize_article(entry.title, article_text)
                items.append(f"- {entry.title}\n  {summary}")
            else:
                items.append(f"- {entry.title}: {entry.link}")
    return "\n".join(items)

def generate_digest(headlines: str, memory: str) -> str:
    client = anthropic.Anthropic()
    memory_context = (
        f"Here is a log of topics and stories you have already covered in previous digests:\n\n{memory}\n\n"
        if memory.strip() else ""
    )

    try:
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1024,
            messages=[{
                "role": "user",
                "content": (
                    f"{memory_context}"
                    f"Here are today's AI-related headlines:\n\n{headlines}\n\n"
                    "Write a concise daily digest (5–7 bullet points) covering the most important developments. "
                    "If a story was already covered before, mention it briefly as a follow-up rather than repeating it in full."
                )
            }]
        )
        return response.content[0].text
    except Exception as e:
        logger.error("Failed to generate digest: %s", e)
        raise

def send_email(digest: str):
    sender = os.environ["GMAIL_USER"]
    recipient = os.environ.get("DIGEST_RECIPIENT", sender)
    password = os.environ["GMAIL_APP_PASSWORD"]

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"AI News Digest — {date.today()}"
    msg["From"] = sender
    msg["To"] = recipient
    msg.attach(MIMEText(digest, "plain"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender, password)
            server.sendmail(sender, recipient, msg.as_string())
    except Exception as e:
        logger.error("Failed to send email: %s", e)
        raise

if __name__ == "__main__":
    REQUIRED_ENV_VARS = ["ANTHROPIC_API_KEY", "GMAIL_USER", "GMAIL_APP_PASSWORD"]
    missing = [v for v in REQUIRED_ENV_VARS if not os.environ.get(v)]
    if missing:
        logger.error("Missing required environment variables: %s", ", ".join(missing))
        raise SystemExit(1)

    logger.info("Fetching headlines...")
    headlines = fetch_headlines()

    logger.info("Loading memory...")
    memory = load_memory()

    logger.info("Generating digest...")
    digest = generate_digest(headlines, memory)

    output_dir = "digests"
    os.makedirs(output_dir, exist_ok=True)
    filename = f"{output_dir}/{date.today()}.txt"
    with open(filename, "w") as f:
        f.write(digest)

    update_memory(digest)

    logger.info("Sending email...")
    send_email(digest)

    logger.info("Email sent.")
