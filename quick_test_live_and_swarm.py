"""
quick_test_live_and_swarm.py
Quick test for Live Intel + Agent Swarm
"""

print("="*70)
print("TESTING LIVE INTEL + AGENT SWARM")
print("="*70)

# ═══════════════════════════════════════════════════════════════════
# TEST 1: LIVE INTEL
# ═══════════════════════════════════════════════════════════════════
print("\n[TEST 1] LIVE INTEL - News Scraper")
print("="*70)

try:
    from news_scraper import init_db, run_scrape_cycle, get_cached_articles
    
    print("\n1. Initializing database...")
    init_db()
    print("   [OK] Database ready")
    
    print("\n2. Running scrape cycle...")
    print("   (This will take 10-20 seconds)")
    run_scrape_cycle()
    print("   [OK] Scrape complete")
    
    print("\n3. Checking cached articles...")
    articles = get_cached_articles(limit=5)
    
    if articles:
        print(f"   [OK] Found {len(articles)} articles in cache")
        print("\n   Sample articles:")
        for i, (title, content, source, fetched, bias, verdict) in enumerate(articles[:3], 1):
            print(f"\n   Article {i}:")
            print(f"   Title: {title[:60]}...")
            print(f"   Source: {source}")
            print(f"   Bias: {bias}")
            print(f"   Verdict: {verdict}")
    else:
        print("   [WARNING] No articles found")
        print("   This is normal if NewsAPI key is not set")
    
    print("\n[OK] LIVE INTEL WORKING!")

except Exception as e:
    print(f"\n[ERROR] Live Intel failed: {str(e)[:100]}")

# ═══════════════════════════════════════════════════════════════════
# TEST 2: AGENT SWARM
# ═══════════════════════════════════════════════════════════════════
print("\n\n[TEST 2] AGENT SWARM - Fact Verification")
print("="*70)

test_article = """
BREAKING NEWS: NASA Scientists Confirm Aliens Living Among Us!

Secret government documents leaked by anonymous whistleblower reveal 
shocking truth about extraterrestrial beings. Mainstream media covering 
it up! Share before this gets deleted!
"""

try:
    from fact_swarm import run_swarm
    
    print("\n1. Test Article:")
    print(f"   {test_article[:100].strip()}...")
    
    print("\n2. Launching 20-agent swarm...")
    print("   (This will take 20-40 seconds)")
    
    result = run_swarm(test_article)
    
    print(f"\n3. Results:")
    print(f"   Keywords: {', '.join(result['keywords'][:5])}")
    print(f"   Execution Time: {result['elapsed_seconds']}s")
    
    verdict = result['verdict']
    print(f"\n   Verdict: {verdict['verdict']}")
    print(f"   Confidence: {verdict['confidence']*100:.1f}%")
    print(f"   Credible Sources Found: {verdict['credible_sources_found']}")
    print(f"   Unreliable Sources Found: {verdict.get('unreliable_sources_found', 0)}")
    print(f"\n   Reasoning:")
    print(f"   {verdict['reasoning'][:150]}...")
    
    # Show some agent results
    print(f"\n   Agent Evidence (sample):")
    for agent in result['agent_results'][:3]:
        if agent['found']:
            status = "CREDIBLE" if agent['credible'] else "UNRELIABLE"
            print(f"   [{status}] {agent['site']}: Found {len(agent['evidence'])} matches")
    
    print("\n[OK] AGENT SWARM WORKING!")

except Exception as e:
    print(f"\n[ERROR] Agent Swarm failed: {str(e)[:100]}")
    print("\n   Common issues:")
    print("   - No internet connection")
    print("   - GOOGLE_GENAI_KEY not set in .env")
    print("   - DuckDuckGo search blocked")

# ═══════════════════════════════════════════════════════════════════
# SUMMARY
# ═══════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("SUMMARY")
print("="*70)
print("""
LIVE INTEL:
- Scrapes news every 30 minutes
- Detects bias in headlines
- Stores in SQLite database
- Use: Tab 5 in Streamlit app

AGENT SWARM:
- 20 parallel agents search internet
- Verifies facts across multiple sources
- Gemini AI coordinator decides verdict
- Use: Tab 6 in Streamlit app

HOW TO USE:
1. Start Streamlit: streamlit run app.py
2. Go to Tab 5 for Live News
3. Go to Tab 6 for Agent Swarm
4. Paste article and click "Launch Swarm"
""")
print("="*70)
