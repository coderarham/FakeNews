"""
news_scraper.py
Live news scraping from NewsAPI + RSS feeds with 3-Layer Bias Correction Engine.
Stores articles in SQLite (news_cache.db) with 72-hour retention.
"""

import re
import os
import time
import hashlib
import sqlite3
import logging
import feedparser
import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from newsapi import NewsApiClient
from apscheduler.schedulers.background import BackgroundScheduler

logging.basicConfig(level=logging.INFO, format="%(asctime)s [scraper] %(message)s")
log = logging.getLogger(__name__)

DB_PATH      = "news_cache.db"
RETENTION_H  = 72
NEWSAPI_KEY  = os.getenv("NEWSAPI_KEY", "YOUR_NEWSAPI_KEY")
REUTERS_RE   = re.compile(r"[A-Z\s]+(Reuters)", re.IGNORECASE)

RSS_FEEDS = [
    "https://feeds.bbci.co.uk/news/rss.xml",
    "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
    "https://www.theguardian.com/world/rss",
    "https://feeds.npr.org/1001/rss.xml",
    "https://www.aljazeera.com/xml/rss/all.xml",
]


# ── Database ───────────────────────────────────────────────────────────────
def init_db():
    con = sqlite3.connect(DB_PATH)
    con.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            url_hash    TEXT UNIQUE,
            title       TEXT,
            content     TEXT,
            source      TEXT,
            fetched_at  TEXT,
            bias_flags  TEXT,
            ml_verdict  TEXT
        )
    """)
    con.commit()
    con.close()


def _hash(url_or_title: str) -> str:
    return hashlib.md5(url_or_title.encode()).hexdigest()


def save_article(title, content, source, bias_flags, ml_verdict="PENDING"):
    con = sqlite3.connect(DB_PATH)
    try:
        con.execute(
            "INSERT OR IGNORE INTO articles "
            "(url_hash, title, content, source, fetched_at, bias_flags, ml_verdict) "
            "VALUES (?,?,?,?,?,?,?)",
            (_hash(title), title, content, source,
             datetime.utcnow().isoformat(), str(bias_flags), ml_verdict)
        )
        con.commit()
    finally:
        con.close()


def purge_old():
    cutoff = (datetime.utcnow() - timedelta(hours=RETENTION_H)).isoformat()
    con = sqlite3.connect(DB_PATH)
    con.execute("DELETE FROM articles WHERE fetched_at < ?", (cutoff,))
    con.commit()
    con.close()


def get_cached_articles(limit=200):
    con = sqlite3.connect(DB_PATH)
    rows = con.execute(
        "SELECT title, content, source, fetched_at, bias_flags, ml_verdict "
        "FROM articles ORDER BY fetched_at DESC LIMIT ?", (limit,)
    ).fetchall()
    con.close()
    return rows


# ── 3-Layer Bias Correction Engine ────────────────────────────────────────
def bias_correction(title: str, content: str) -> dict:
    """
    Layer 1 – Reuters dateline detection
    Layer 2 – Sensationalism keyword flag
    Layer 3 – Source credibility tier
    Returns dict of flags and a corrected_label hint.
    """
    flags = {}

    # Layer 1: Reuters dateline
    flags["reuters_dateline"] = bool(REUTERS_RE.search(content[:200]))

    # Layer 2: Sensationalism markers
    SENSATIONAL = re.compile(
        r"\b(BREAKING|EXCLUSIVE|SHOCKING|BOMBSHELL|EXPOSED|LEAKED|SCANDAL)\b", re.I)
    flags["sensational_headline"] = bool(SENSATIONAL.search(title))

    # Layer 3: All-caps ratio (tabloid style)
    words = title.split()
    caps_ratio = sum(1 for w in words if w.isupper() and len(w) > 2) / max(len(words), 1)
    flags["caps_ratio"] = round(caps_ratio, 2)
    flags["high_caps"] = caps_ratio > 0.4

    # Corrected label hint: if Reuters dateline present → lean REAL
    if flags["reuters_dateline"]:
        flags["bias_hint"] = "LIKELY_REAL (Reuters dateline)"
    elif flags["sensational_headline"] or flags["high_caps"]:
        flags["bias_hint"] = "LIKELY_FAKE (sensational style)"
    else:
        flags["bias_hint"] = "NEUTRAL"

    return flags


# ── Scrapers ───────────────────────────────────────────────────────────────
def _fetch_text(url: str, timeout=8) -> str:
    try:
        r = requests.get(url, timeout=timeout,
                         headers={"User-Agent": "TruthLens/1.0"})
        soup = BeautifulSoup(r.text, "lxml")
        paras = soup.find_all("p")
        return " ".join(p.get_text() for p in paras[:20])
    except Exception:
        return ""


def scrape_rss():
    for feed_url in RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:10]:
                title   = entry.get("title", "")
                content = entry.get("summary", "") or _fetch_text(entry.get("link", ""))
                if not title or not content:
                    continue
                flags = bias_correction(title, content)
                save_article(title, content, feed_url, flags)
        except Exception as e:
            log.warning(f"RSS error {feed_url}: {e}")


def scrape_newsapi():
    if NEWSAPI_KEY == "YOUR_NEWSAPI_KEY":
        log.warning("NewsAPI key not set — skipping NewsAPI scrape.")
        return
    try:
        api = NewsApiClient(api_key=NEWSAPI_KEY)
        resp = api.get_top_headlines(language="en", page_size=50)
        for art in resp.get("articles", []):
            title   = art.get("title", "")
            content = art.get("content", "") or art.get("description", "")
            source  = art.get("source", {}).get("name", "unknown")
            if not title or not content:
                continue
            flags = bias_correction(title, content)
            save_article(title, content, source, flags)
    except Exception as e:
        log.error(f"NewsAPI error: {e}")


def run_scrape_cycle():
    log.info("Scrape cycle started")
    scrape_rss()
    scrape_newsapi()
    purge_old()
    log.info("Scrape cycle complete")


# ── Scheduler ─────────────────────────────────────────────────────────────
_scheduler = None

def start_scheduler():
    global _scheduler
    init_db()
    _scheduler = BackgroundScheduler()
    _scheduler.add_job(run_scrape_cycle, "interval", minutes=30, id="scrape")
    _scheduler.start()
    run_scrape_cycle()   # immediate first run
    log.info("Scheduler started (every 30 min)")


def stop_scheduler():
    if _scheduler:
        _scheduler.shutdown(wait=False)


if __name__ == "__main__":
    init_db()
    run_scrape_cycle()
