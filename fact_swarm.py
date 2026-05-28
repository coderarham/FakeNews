"""
fact_swarm.py
20-agent parallel Fact Verification Swarm using concurrent.futures (Strands-compatible).
Each agent scrapes one domain; a Gemini 2.5 Flash coordinator produces the final verdict.
"""

import re
import os
import time
import logging
import requests
import feedparser
from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()  # Load .env file

log = logging.getLogger(__name__)

GEMINI_KEY = os.getenv("GOOGLE_GENAI_KEY", "YOUR_GEMINI_KEY")

# ── Domain Registry ────────────────────────────────────────────────────────
CREDIBLE_DOMAINS = {
    "bbc":          ("https://feeds.bbci.co.uk/news/rss.xml",       "bbc.co.uk"),
    "reuters":      ("https://feeds.reuters.com/reuters/topNews",    "reuters.com"),
    "nytimes":      ("https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml", "nytimes.com"),
    "guardian":     ("https://www.theguardian.com/world/rss",        "theguardian.com"),
    "washpost":     ("https://feeds.washingtonpost.com/rss/world",   "washingtonpost.com"),
    "ap":           ("https://rsshub.app/apnews/topics/apf-topnews", "apnews.com"),
    "npr":          ("https://feeds.npr.org/1001/rss.xml",           "npr.org"),
    "aljazeera":    ("https://www.aljazeera.com/xml/rss/all.xml",    "aljazeera.com"),
    "economist":    ("https://www.economist.com/rss/the_world_this_week_rss.xml", "economist.com"),
    "ft":           ("https://www.ft.com/rss/home",                  "ft.com"),
    "abc":          ("https://feeds.abcnews.com/abcnews/topstories", "abcnews.go.com"),
    "cbs":          ("https://www.cbsnews.com/latest/rss/main",      "cbsnews.com"),
    "cnn":          ("http://rss.cnn.com/rss/edition.rss",           "cnn.com"),
    "nbc":          ("https://feeds.nbcnews.com/nbcnews/public/news","nbcnews.com"),
    "skynews":      ("https://feeds.skynews.com/feeds/rss/world.xml","news.sky.com"),
    "dw":           ("https://rss.dw.com/rdf/rss-en-all",            "dw.com"),
}

UNRELIABLE_DOMAINS = {
    "babylonbee":   (None, "babylonbee.com"),
    "theonion":     ("https://www.theonion.com/rss",                 "theonion.com"),
    "zerohedge":    (None, "zerohedge.com"),
    "infowars":     (None, "infowars.com"),
}

ALL_DOMAINS = {**CREDIBLE_DOMAINS, **UNRELIABLE_DOMAINS}
CREDIBLE_KEYS = set(CREDIBLE_DOMAINS.keys())


# ── Keyword Extraction (TF-IDF, top 12) ───────────────────────────────────
def extract_keywords(text: str, n=12) -> list[str]:
    vec = TfidfVectorizer(stop_words="english", max_features=500,
                          token_pattern=r"(?u)\b[a-zA-Z]{4,}\b")
    try:
        X = vec.fit_transform([text])
        names = vec.get_feature_names_out()
        scores = X.toarray()[0]
        top_idx = scores.argsort()[-n:][::-1]
        return [names[i] for i in top_idx if scores[i] > 0]
    except Exception:
        return text.split()[:n]


# ── Jaccard Similarity ─────────────────────────────────────────────────────
def jaccard(a: set, b: set) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


# ── Single Domain Agent ────────────────────────────────────────────────────
def _agent_search(domain_key: str, keywords: list[str]) -> dict:
    """
    Priority 1: DuckDuckGo site-scoped search
    Priority 2: RSS feed
    Priority 3: Homepage scrape
    Returns evidence dict.
    """
    rss_url, site = ALL_DOMAINS[domain_key]
    is_credible = domain_key in CREDIBLE_KEYS
    kw_set = set(k.lower() for k in keywords)
    evidence = []

    # Priority 1 – DuckDuckGo site search
    try:
        from duckduckgo_search import DDGS
        query = " ".join(keywords[:5]) + f" site:{site}"
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=5):
                title = r.get("title", "")
                body  = r.get("body", "")
                combined = (title + " " + body).lower()
                doc_kws = set(combined.split()) & kw_set
                j = jaccard(kw_set, doc_kws)
                if j >= 0.08:
                    evidence.append({"title": title, "snippet": body[:200],
                                     "jaccard": round(j, 3), "source": site})
    except ImportError:
        log.warning(f"duckduckgo_search not installed, skipping DDG search for {domain_key}")
    except Exception as e:
        log.debug(f"DDG search failed for {domain_key}: {e}")

    # Priority 2 – RSS
    if not evidence and rss_url:
        try:
            feed = feedparser.parse(rss_url)
            for entry in feed.entries[:15]:
                text = (entry.get("title", "") + " " + entry.get("summary", "")).lower()
                doc_kws = set(text.split()) & kw_set
                j = jaccard(kw_set, doc_kws)
                if j >= 0.08:
                    evidence.append({"title": entry.get("title", ""),
                                     "snippet": entry.get("summary", "")[:200],
                                     "jaccard": round(j, 3), "source": site})
        except Exception as e:
            log.debug(f"RSS feed failed for {domain_key}: {e}")

    # Priority 3 – Homepage scrape
    if not evidence:
        try:
            r = requests.get(f"https://{site}", timeout=6,
                             headers={"User-Agent": "TruthLens/1.0"})
            soup = BeautifulSoup(r.text, "lxml")
            headlines = [a.get_text() for a in soup.find_all("a") if len(a.get_text()) > 20]
            for h in headlines[:30]:
                doc_kws = set(h.lower().split()) & kw_set
                j = jaccard(kw_set, doc_kws)
                if j >= 0.08:
                    evidence.append({"title": h, "snippet": "",
                                     "jaccard": round(j, 3), "source": site})
        except Exception as e:
            log.debug(f"Homepage scrape failed for {domain_key}: {e}")

    return {
        "domain": domain_key,
        "site": site,
        "credible": is_credible,
        "evidence": evidence[:3],   # top 3 per agent
        "found": len(evidence) > 0,
    }


# ── Coordinator (Gemini 2.5 Flash) ────────────────────────────────────────
def _coordinator_verdict(article_text: str, keywords: list[str],
                          agent_results: list[dict]) -> dict:
    if not GEMINI_KEY or GEMINI_KEY == "YOUR_GEMINI_KEY":
        log.warning("Gemini API key not configured, using fallback verdict")
        return _fallback_verdict(agent_results)

    try:
        genai.configure(api_key=GEMINI_KEY)
        model = genai.GenerativeModel("gemini-1.5-pro")  # Changed to pro version

        evidence_summary = []
        for r in agent_results:
            for ev in r["evidence"]:
                evidence_summary.append(
                    f"[{'CREDIBLE' if r['credible'] else 'UNRELIABLE'}] "
                    f"{r['site']}: \"{ev['title']}\" (Jaccard={ev['jaccard']})"
                )

        prompt = f"""You are a fact-checking coordinator. Analyze the following article and evidence.

ARTICLE KEYWORDS: {', '.join(keywords)}

ARTICLE EXCERPT: {article_text[:500]}

EVIDENCE FOUND BY AGENTS:
{chr(10).join(evidence_summary) if evidence_summary else 'No evidence found.'}

Based on the evidence, provide a JSON response with:
- verdict: one of FAKE / LIKELY_FAKE / INCONCLUSIVE / LIKELY_REAL / REAL
- confidence: float 0.0-1.0
- reasoning: max 150 words
- credible_sources_found: integer
- unreliable_sources_found: integer

Respond ONLY with valid JSON."""

        resp = model.generate_content(prompt)
        text = resp.text.strip()
        # Extract JSON block
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            import json
            return json.loads(match.group())
    except Exception as e:
        log.error(f"Coordinator error: {e}")

    return _fallback_verdict(agent_results)


def _fallback_verdict(agent_results: list[dict]) -> dict:
    """Rule-based fallback when Gemini is unavailable."""
    credible_hits   = sum(1 for r in agent_results if r["credible"] and r["found"])
    unreliable_hits = sum(1 for r in agent_results if not r["credible"] and r["found"])
    total_credible  = len(CREDIBLE_DOMAINS)
    total_unreliable = len(UNRELIABLE_DOMAINS)
    
    # Calculate total evidence strength
    total_evidence = 0
    for r in agent_results:
        if r["found"]:
            for ev in r["evidence"]:
                total_evidence += ev["jaccard"]
    
    # Dynamic confidence based on evidence strength and source count
    if credible_hits >= 5:
        # Strong real: 5+ credible sources
        base_conf = 0.70
        bonus = min(0.25, (credible_hits - 5) * 0.03)  # +3% per extra source
        evidence_bonus = min(0.05, total_evidence * 0.02)
        conf = base_conf + bonus + evidence_bonus
        verdict = "LIKELY_REAL"
    elif credible_hits >= 2:
        # Medium real: 2-4 credible sources
        base_conf = 0.55
        bonus = (credible_hits - 2) * 0.05  # +5% per source
        evidence_bonus = min(0.05, total_evidence * 0.02)
        conf = base_conf + bonus + evidence_bonus
        verdict = "LIKELY_REAL"
    elif unreliable_hits >= 2 and credible_hits == 0:
        # Likely fake: unreliable sources only
        base_conf = 0.60
        bonus = min(0.15, unreliable_hits * 0.05)
        conf = base_conf + bonus
        verdict = "LIKELY_FAKE"
    elif credible_hits == 1:
        # Weak real: only 1 credible source
        conf = 0.50 + min(0.10, total_evidence * 0.05)
        verdict = "LIKELY_REAL"
    else:
        # Inconclusive: no clear evidence
        conf = 0.35 + min(0.10, total_evidence * 0.02)
        verdict = "INCONCLUSIVE"
    
    # Cap confidence at 0.95 (never 100% without Gemini)
    conf = min(0.95, conf)

    return {
        "verdict": verdict,
        "confidence": round(conf, 2),
        "reasoning": f"Rule-based: {credible_hits} credible sources, {unreliable_hits} unreliable sources found. Evidence strength: {total_evidence:.2f}",
        "credible_sources_found": credible_hits,
        "unreliable_sources_found": unreliable_hits,
    }


# ── Public API ─────────────────────────────────────────────────────────────
def run_swarm(article_text: str) -> dict:
    """
    Run all 20 agents in parallel, then coordinate verdict.
    Returns full result dict including per-agent evidence.
    """
    start = time.time()
    keywords = extract_keywords(article_text)
    log.info(f"[Swarm] Keywords: {keywords}")

    agent_results = []
    with ThreadPoolExecutor(max_workers=20) as pool:
        futures = {
            pool.submit(_agent_search, dk, keywords): dk
            for dk in ALL_DOMAINS
        }
        for fut in as_completed(futures, timeout=90):  # 90 second timeout
            try:
                agent_results.append(fut.result(timeout=5))  # 5 sec per agent
            except Exception as e:
                domain = futures.get(fut, 'unknown')
                log.warning(f"Agent {domain} error: {e}")
                # Add empty result for failed agent
                agent_results.append({
                    'domain': domain,
                    'site': ALL_DOMAINS.get(domain, ('', ''))[1] if domain in ALL_DOMAINS else '',
                    'credible': domain in CREDIBLE_KEYS,
                    'evidence': [],
                    'found': False
                })

    verdict = _coordinator_verdict(article_text, keywords, agent_results)
    elapsed = round(time.time() - start, 1)

    return {
        "keywords": keywords,
        "agent_results": agent_results,
        "verdict": verdict,
        "elapsed_seconds": elapsed,
    }
