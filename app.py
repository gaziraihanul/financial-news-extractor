import json
import os
import feedparser
from openai import OpenAI
from fastapi import FastAPI
from dotenv import load_dotenv

# Load API key from .env file instead of hardcoding it
load_dotenv()

app = FastAPI()


FEEDS = {
    "marketwatch": "https://feeds.content.dowjones.io/public/rss/mw_realtimeheadlines",
    "reuters": "https://feeds.reuters.com/reuters/businessNews",
    "yahoo": "https://finance.yahoo.com/news/rssindex",
}


client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

def clean_nulls(data: dict) -> dict:
    """
    The LLM sometimes returns the string "null" instead of real null.
    This converts any "null" strings to Python None.
    """
    for key, value in data.items():
        if value == "null" or value == "":
            data[key] = None
    return data


def extract_article(entry) -> dict:
    """
    Takes one RSS feed entry, sends it to the LLM,
    and returns structured data as a Python dictionary.
    """
    article_text = entry.title + ". " + entry.get("summary", "")

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "user",
                "content": f"""Extract information from this financial news article.
Return ONLY a JSON object with these exact fields, nothing else:
{{
  "company_name": "full company name or null if not about a specific company",
  "ticker_symbol": "stock ticker or null if unknown",
  "exchange_extension": ":NASDAQ or :NYSE or :TSX or null if unknown",
  "headline": "one sentence summary of the news",
  "source_url": "{entry.get('link', '')}"
}}

Article: {article_text}"""
            }
        ]
    )

    raw_response = response.choices[0].message.content
    data = json.loads(raw_response)
    data = clean_nulls(data)  # Fix any "null" strings
    return data


@app.get("/")
def root():
    """Health check — confirms the server is running."""
    return {"status": "running"}


@app.get("/extract")
def extract_news(feed_name: str = "marketwatch"):
    """
    Fetches the latest articles from the selected RSS feed,
    Use ?feed=marketwatch or ?feed=reuters or ?feed=yahoo
    extracts structured financial data from each,
    and returns them as JSON.
    """

    if feed_name not in FEEDS:
        return {"error": f"Invalid feed. Choose from: {list(FEEDS.keys())}"}

    feed_url = FEEDS[feed_name]
    parsed_feed = feedparser.parse(feed_url)

    results = []
    for entry in parsed_feed.entries[:5]:
        try:
            data = extract_article(entry)
            results.append(data)
        except Exception as e:
            print(f"Skipping '{entry.title[:50]}' — error: {e}")
            continue

    return {"count": len(results), "articles": results}