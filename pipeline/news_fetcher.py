import os
import requests
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

GNEWS_API_KEY = os.getenv("GNEWS_API_KEY")

if not GNEWS_API_KEY or GNEWS_API_KEY == "your_gnews_key_here":
    print("⚠️ GNEWS_API_KEY not set! News fetching will not work.")
else:
    print("✅ GNews API Key loaded!")

def fetch_latest_news(query: str = "health", max_results: int = 10) -> list:
    """Fetch latest news articles from GNews API"""
    try:
        if not GNEWS_API_KEY or GNEWS_API_KEY == "your_gnews_key_here":
            print("❌ Cannot fetch news: API key not configured")
            return []
        
        # Simple single-word queries work best with GNews
        url = "https://gnews.io/api/v4/top-headlines"
        params = {
            "category": "general",
            "lang": "en",
            "max": max_results,
            "apikey": GNEWS_API_KEY
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
        if "errors" in data:
            print(f"❌ GNews Error: {data['errors']}")
            return []
        
        articles = []
        for article in data.get("articles", []):
            articles.append({
                "title": article.get("title", ""),
                "description": article.get("description", ""),
                "content": article.get("content", ""),
                "source": article.get("source", {}).get("name", "Unknown"),
                "url": article.get("url", ""),
                "published": article.get("publishedAt", ""),
                "fetched_at": datetime.now().isoformat()
            })
        
        print(f"📰 Fetched {len(articles)} articles")
        return articles

    except Exception as e:
        print(f"❌ News fetch error: {e}")
        return []

def fetch_news_by_topic(topic: str = "science", max_results: int = 10) -> list:
    """Fetch news by specific topic"""
    try:
        if not GNEWS_API_KEY or GNEWS_API_KEY == "your_gnews_key_here":
            return []
        
        url = "https://gnews.io/api/v4/top-headlines"
        params = {
            "category": topic,  # general, world, nation, business, technology, entertainment, sports, science, health
            "lang": "en",
            "max": max_results,
            "apikey": GNEWS_API_KEY
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
        articles = []
        for article in data.get("articles", []):
            articles.append({
                "title": article.get("title", ""),
                "description": article.get("description", ""),
                "content": article.get("content", ""),
                "source": article.get("source", {}).get("name", "Unknown"),
                "url": article.get("url", ""),
                "published": article.get("publishedAt", ""),
                "fetched_at": datetime.now().isoformat()
            })
        
        print(f"📰 Fetched {len(articles)} {topic} articles")
        return articles

    except Exception as e:
        print(f"❌ News fetch error: {e}")
        return []

def save_articles_to_folder(articles: list, folder: str = "data/articles"):
    """Save articles as text files for Pathway to ingest"""
    os.makedirs(folder, exist_ok=True)
    
    saved_count = 0
    for i, article in enumerate(articles):
        filename = f"{folder}/article_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{i}.txt"
        content = f"""TITLE: {article['title']}
SOURCE: {article['source']}
DATE: {article['published']}
URL: {article['url']}

{article['description']}

{article['content']}
"""
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        saved_count += 1
    
    print(f"💾 Saved {saved_count} articles to {folder}")
    return saved_count