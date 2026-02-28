import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os

# Configuration
NEWS_SOURCES = [
    {
        "name": "Reuters - World News",
        "url": "https://www.reuters.com/world/",
        "selector": "h3[data-testid='Heading']"
    },
    {
        "name": "BBC - World News",
        "url": "https://www.bbc.com/news/world",
        "selector": "h2[data-testid='card-headline']"
    }
]

OUTPUT_DIR = os.path.expanduser("~/Documents/NewsSummaries")

def fetch_headlines(source):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(source["url"], headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        headlines = []

        # Find elements based on the CSS selector
        elements = soup.select(source["selector"])

        for el in elements[:10]: # Get top 10
            text = el.get_text().strip()
            link = el.get('href')
            if link and not link.startswith('http'):
                # Handle relative URLs
                base_url = "/".join(source["url"].split("/")[:3])
                link = base_url + link

            if text:
                headlines.append({"text": text, "link": link})

        return headlines
    except Exception as e:
        print(f"Error fetching from {source['name']}: {e}")
        return []

def save_summary(all_news):
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    today = datetime.now().strftime("%Y-%m-%d")
    filename = f"News_Summary_{today}.md"
    filepath = os.path.join(OUTPUT_DIR, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"# Daily News Summary - {today}\n\n")

        for source_name, headlines in all_news.items():
            f.write(f"## {source_name}\n")
            if not headlines:
                f.write("Failed to fetch headlines for this source.\n\n")
                continue

            for i, item in enumerate(headlines, 1):
                if item['link']:
                    f.write(f"{i}. [{item['text']}]({item['link']})\n")
                else:
                    f.write(f"{i}. {item['text']}\n")
            f.write("\n")

    return filepath

if __name__ == "__main__":
    print("Fetching latest news...")
    all_news = {}

    for source in NEWS_SOURCES:
        print(f"Scraping {source['name']}...")
        headlines = fetch_headlines(source)
        all_news[source["name"]] = headlines

    summary_file = save_summary(all_news)
    print(f"Summary saved to: {summary_file}")
