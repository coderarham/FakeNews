"""
test_live_intel_setup.py
Simple test to check if Live Intel is working
"""

print("="*70)
print("LIVE INTEL SETUP TEST")
print("="*70)

# Step 1: Check imports
print("\n[STEP 1] Checking dependencies...")
try:
    import feedparser
    print("  [OK] feedparser")
except:
    print("  [X] feedparser - Run: pip install feedparser")

try:
    from bs4 import BeautifulSoup
    print("  [OK] beautifulsoup4")
except:
    print("  [X] beautifulsoup4 - Run: pip install beautifulsoup4")

try:
    import lxml
    print("  [OK] lxml")
except:
    print("  [X] lxml - Run: pip install lxml")

try:
    from newsapi import NewsApiClient
    print("  [OK] newsapi-python")
except:
    print("  [X] newsapi-python - Run: pip install newsapi-python")

try:
    from apscheduler.schedulers.background import BackgroundScheduler
    print("  [OK] apscheduler")
except:
    print("  [X] apscheduler - Run: pip install apscheduler")

# Step 2: Check API key
print("\n[STEP 2] Checking API key...")
import os
from dotenv import load_dotenv
load_dotenv()

NEWSAPI_KEY = os.getenv("NEWSAPI_KEY", "")
if NEWSAPI_KEY and NEWSAPI_KEY != "YOUR_NEWSAPI_KEY":
    print(f"  [OK] NewsAPI key found: {NEWSAPI_KEY[:20]}...")
else:
    print("  [WARNING] NewsAPI key not set")
    print("  Live Intel will work with RSS feeds only")
    print("  To add key: Add NEWSAPI_KEY=your_key to .env file")

# Step 3: Initialize database
print("\n[STEP 3] Initializing database...")
try:
    from news_scraper import init_db
    init_db()
    print("  [OK] Database initialized (news_cache.db)")
except Exception as e:
    print(f"  [X] Database error: {e}")

# Step 4: Test RSS scraping
print("\n[STEP 4] Testing RSS feed scraping...")
print("  Scraping BBC News RSS feed...")
try:
    import feedparser
    feed = feedparser.parse("https://feeds.bbci.co.uk/news/rss.xml")
    if feed.entries:
        print(f"  [OK] Found {len(feed.entries)} articles from BBC")
        print(f"  Sample: {feed.entries[0].title[:60]}...")
    else:
        print("  [WARNING] No articles found")
except Exception as e:
    print(f"  [X] RSS error: {e}")

# Step 5: Test bias detection
print("\n[STEP 5] Testing bias detection...")
try:
    from news_scraper import bias_correction
    
    # Test 1: Normal article
    test1 = bias_correction(
        "Fed maintains interest rates",
        "The Federal Reserve announced today..."
    )
    print(f"  Test 1 (Normal): {test1['bias_hint']}")
    
    # Test 2: Reuters article
    test2 = bias_correction(
        "Market update",
        "WASHINGTON (Reuters) - Stock markets rose today..."
    )
    print(f"  Test 2 (Reuters): {test2['bias_hint']}")
    
    # Test 3: Sensational
    test3 = bias_correction(
        "BREAKING: SHOCKING revelation EXPOSED!",
        "Secret documents leaked..."
    )
    print(f"  Test 3 (Sensational): {test3['bias_hint']}")
    
    print("  [OK] Bias detection working")
except Exception as e:
    print(f"  [X] Bias detection error: {e}")

# Step 6: Test full scrape
print("\n[STEP 6] Testing full scrape cycle...")
print("  (This may take 10-20 seconds)")
try:
    from news_scraper import run_scrape_cycle, get_cached_articles
    
    run_scrape_cycle()
    
    articles = get_cached_articles(limit=5)
    if articles:
        print(f"  [OK] Scraped and cached {len(articles)} articles")
        print("\n  Sample articles:")
        for i, (title, content, source, fetched, bias, verdict) in enumerate(articles[:3], 1):
            print(f"\n  {i}. {title[:50]}...")
            print(f"     Source: {source[:30]}")
            print(f"     Bias: {bias[:50]}")
    else:
        print("  [WARNING] No articles cached")
        print("  This is normal if NewsAPI key is not set")
except Exception as e:
    print(f"  [X] Scrape error: {e}")

# Summary
print("\n" + "="*70)
print("SETUP STATUS")
print("="*70)
print("""
If all steps show [OK], Live Intel is ready!

NEXT STEPS:
1. Start Streamlit app: streamlit run app.py
2. Go to Tab 5 (Live News)
3. Enable "Live News Scraper" checkbox in sidebar
4. Articles will auto-refresh every 30 minutes

OR

Run standalone: python news_scraper.py
""")
print("="*70)
