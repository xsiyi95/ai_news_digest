import os
import feedparser
import ollama
import requests
from bs4 import BeautifulSoup
from datetime import date

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
        text = " ".join(p.get_text() for p in paragraphs[:10])
        return text.strip()
    except Exception:
        return ""

def fetch_headlines() -> str:
    items = []
    for url in FEEDS:
        feed = feedparser.parse(url)
        for entry in feed.entries[:5]:
            article_text = scrape_article(entry.link)
            if article_text:
                items.append(f"- {entry.title}\n  {article_text[:500]}")
            else:
                items.append(f"- {entry.title}: {entry.link}")
    return "\n".join(items)

def generate_digest(headlines: str, memory: str) -> str:
    memory_context = (
        f"Here is a log of topics and stories you have already covered in previous digests:\n\n{memory}\n\n"
        if memory.strip() else ""
    )
    response = ollama.chat(
        model="phi3",
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
    return response["message"]["content"]

if __name__ == "__main__":
    print("Fetching headlines...")
    headlines = fetch_headlines()

    print("Loading memory...")
    memory = load_memory()

    print("Generating digest...\n")
    digest = generate_digest(headlines, memory)

    output_dir = "digests"
    os.makedirs(output_dir, exist_ok=True)
    filename = f"{output_dir}/{date.today()}.txt"
    with open(filename, "w") as f:
        f.write(digest)

    update_memory(digest)
    print(f"Saved to {filename}")
