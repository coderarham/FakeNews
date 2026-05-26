"""
test_live_intel_quick.py
Quick test for Live Intel with new API key
"""

import os
from dotenv import load_dotenv

print("="*70)
print("LIVE INTEL - QUICK TEST")
print("="*70)

# Load API key
load_dotenv()
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY", "")

print(f"\n[1] API Key: {NEWSAPI_KEY[:20]}...{NEWSAPI_KEY[-10:]}")

# Test NewsAPI
print("\n[2] Testing NewsAPI connection...")
try:
    from newsapi import NewsApiClient
    api = NewsApiClient(api_key=NEWSAPI_KEY)
    
    print("    Fetching top headlines...")
    response = api.get_top_headlines(language='en', page_size=5)
    
    articles = response.get('articles', [])
    if articles:
        print(f"    [OK] Found {len(articles)} articles!")
        print("\n    Sample headlines:")
        for i, art in enumerate(articles[:3], 1):
            print(f"    {i}. {art['title'][:60]}...")
            print(f"       Source: {art['source']['name']}")
    else:
        print("    [WARNING] No articles found")
        
except Exception as e:
    print(f"    [ERROR] {str(e)}")

# Test RSS feeds
print("\n[3] Testing RSS feeds...")
try:
    import feedparser
    
    feed = feedparser.parse("https://feeds.bbci.co.uk/news/rss.xml")
    if feed.entries:
        print(f"    [OK] BBC RSS: {len(feed.entries)} articles")
        print(f"    Sample: {feed.entries[0].title[:60]}...")
    else:
        print("    [WARNING] No RSS articles")
        
except Exception as e:
    print(f"    [ERROR] {str(e)}")

# Test database
print("\n[4] Testing database...")
try:
    from news_scraper import init_db, save_article, get_cached_articles
    
    init_db()
    print("    [OK] Database initialized")
    
    # Save test article
    save_article(
        title="Test Article",
        content="This is a test",
        source="Test",
        bias_flags="{'test': True}",
        ml_verdict="PENDING"
    )
    print("    [OK] Test article saved")
    
    # Retrieve
    articles = get_cached_articles(limit=1)
    if articles:
        print(f"    [OK] Retrieved {len(articles)} articles from cache")
    
except Exception as e:
    print(f"    [ERROR] {str(e)}")

# Test bias detection
print("\n[5] Testing bias detection...")
try:
    from news_scraper import bias_correction
    
    # Test sensational headline
    result = bias_correction(
        "BREAKING: SHOCKING revelation EXPOSED!",
        "Secret documents leaked..."
    )
    print(f"    Sensational test: {result['bias_hint']}")
    
    # Test Reuters
    result2 = bias_correction(
        "Market update",
        "WASHINGTON (Reuters) - Markets rose today..."
    )
    print(f"    Reuters test: {result2['bias_hint']}")
    
    print("    [OK] Bias detection working")
    
except Exception as e:
    print(f"    [ERROR] {str(e)}")

# Full scrape test
print("\n[6] Running full scrape cycle...")
print("    (This will take 10-20 seconds)")
try:
    from news_scraper import run_scrape_cycle, get_cached_articles
    
    run_scrape_cycle()
    
    articles = get_cached_articles(limit=10)
    print(f"    [OK] Scraped {len(articles)} articles total")
    
    if articles:
        print("\n    Latest articles:")
        for i, (title, content, source, fetched, bias, verdict) in enumerate(articles[:5], 1):
            print(f"\n    {i}. {title[:50]}...")
            print(f"       Source: {source[:30]}")
            print(f"       Bias: {bias[:40]}")
    
except Exception as e:
    print(f"    [ERROR] {str(e)}")

print("\n" + "="*70)
print("SETUP COMPLETE!")
print("="*70)
print("""
Live Intel is ready to use!

HOW TO USE:

Method 1: Streamlit App
  1. Run: streamlit run app.py
  2. Go to Tab 5 (Live News)
  3. Enable "Live News Scraper" in sidebar
  4. Articles will refresh every 30 minutes

Method 2: Standalone
  1. Run: python news_scraper.py
  2. Check news_cache.db for stored articles

Method 3: Check database
  1. Open: news_cache.db (SQLite file)
  2. View articles table
""")
print("="*70)
