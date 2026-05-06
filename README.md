# Financial News Extractor

A REST API that fetches live financial news from RSS feeds and extracts 
structured data using an LLM.

## What it does
- Pulls articles from financial RSS feeds (MarketWatch, Yahoo Finance)
- Sends each article to an LLM for structured extraction
- Returns clean JSON with company name, ticker, exchange, headline, and source URL

## Tech stack
Python, FastAPI, Groq (LLaMA 3.1), feedparser

## Run locally

1. Clone the repo
2. Create a virtual environment: `python -m venv venv`
3. Activate it: `source venv/bin/activate` (Mac) or `venv\Scripts\activate` (Windows)
4. Install dependencies: `pip install -r requirements.txt`
5. Create a `.env` file with your Groq API key: `GROQ_API_KEY=your-key-here`
6. Run the server: `uvicorn app:app --reload`

## Endpoints

`GET /` — health check

`GET /extract` — fetch and extract articles from default feed (MarketWatch)

`GET /extract?feed_name=yahoo` — fetch from Yahoo Finance

`GET /extract?feed_name=marketwatch` — fetch from MarketWatch

## Example response
{
  "feed": "yahoo",
  "count": 5,
  "articles": [
    {
      "company_name": "Coinbase",
      "ticker_symbol": "COIN",
      "exchange_extension": ":NASDAQ",
      "headline": "Coinbase CEO makes critical move before earnings.",
      "source_url": "https://finance.yahoo.com/..."
    }
  ]
}