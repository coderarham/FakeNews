# 🕸️ AGENT SWARM & 📰 LIVE INTEL - Simple Explanation

---

## 🕸️ AGENT SWARM (fact_swarm.py)

### Kya Hai Ye?
**20 parallel agents** jo internet pe fact-checking karte hain!

### Kaise Kaam Karta Hai?

```
User Article → Extract Keywords → 20 Agents Search → Coordinator → Final Verdict
```

### Step-by-Step:

#### 1️⃣ **Keyword Extraction**
```python
Article: "NASA confirms aliens living among us!"
Keywords: ["NASA", "confirms", "aliens", "living", "among"]
```
- TF-IDF se top 12 keywords nikalta hai
- Important words identify karta hai

#### 2️⃣ **20 Agents Deploy**
```
16 CREDIBLE Agents:
- BBC, Reuters, NYTimes, Guardian, Washington Post
- AP, NPR, Al Jazeera, Economist, Financial Times
- ABC, CBS, CNN, NBC, Sky News, DW

4 UNRELIABLE Agents:
- Babylon Bee (satire)
- The Onion (satire)
- ZeroHedge (conspiracy)
- InfoWars (conspiracy)
```

#### 3️⃣ **Each Agent Searches**
```
Agent "BBC":
  1. DuckDuckGo search: "NASA aliens site:bbc.co.uk"
  2. If not found → Check BBC RSS feed
  3. If not found → Scrape BBC homepage
  
  Found articles:
  - "NASA denies alien claims" (Jaccard: 0.65)
  - "Conspiracy theories debunked" (Jaccard: 0.42)
```

**Jaccard Similarity:**
```
Article keywords: {NASA, aliens, confirms}
BBC article words: {NASA, denies, alien, claims}

Jaccard = (matching words) / (total unique words)
        = 2 / 5 = 0.40 (40% match)
```

#### 4️⃣ **Coordinator (Gemini AI)**
```
Evidence collected:
- 0 credible sources found article
- 2 credible sources DENY the claim
- 1 unreliable source (InfoWars) supports it

Gemini analyzes:
"No credible sources confirm this. Multiple credible 
sources deny it. Only unreliable sources support."

Verdict: FAKE (Confidence: 85%)
```

### Example Output:
```json
{
  "keywords": ["NASA", "aliens", "confirms"],
  "agent_results": [
    {
      "domain": "bbc",
      "credible": true,
      "found": true,
      "evidence": [
        {
          "title": "NASA denies alien claims",
          "jaccard": 0.65,
          "source": "bbc.co.uk"
        }
      ]
    },
    ...
  ],
  "verdict": {
    "verdict": "FAKE",
    "confidence": 0.85,
    "reasoning": "No credible sources confirm...",
    "credible_sources_found": 0,
    "unreliable_sources_found": 1
  },
  "elapsed_seconds": 25
}
```

### Kab Use Kare?
- Jab article ka fact verify karna ho
- Jab multiple sources check karne ho
- Jab detailed evidence chahiye

---

## 📰 LIVE INTEL (news_scraper.py)

### Kya Hai Ye?
**Real-time news scraper** jo live news collect karta hai aur bias detect karta hai!

### Kaise Kaam Karta Hai?

```
Every 30 minutes:
  → Scrape NewsAPI
  → Scrape RSS Feeds (BBC, NYTimes, Guardian, etc.)
  → Apply 3-Layer Bias Correction
  → Store in SQLite Database
  → Delete articles older than 72 hours
```

### Step-by-Step:

#### 1️⃣ **News Sources**
```
NewsAPI:
- Top 50 headlines from 100+ sources
- Real-time breaking news

RSS Feeds:
- BBC News
- New York Times
- The Guardian
- NPR
- Al Jazeera
```

#### 2️⃣ **3-Layer Bias Correction Engine**

**Layer 1: Reuters Dateline Detection**
```
Article starts with: "WASHINGTON (Reuters) - ..."
Flag: reuters_dateline = True
Hint: LIKELY_REAL (Reuters is credible)
```

**Layer 2: Sensationalism Detection**
```
Title: "BREAKING: SHOCKING revelation EXPOSED!"
Keywords found: BREAKING, SHOCKING, EXPOSED
Flag: sensational_headline = True
Hint: LIKELY_FAKE (too sensational)
```

**Layer 3: All-Caps Ratio**
```
Title: "GOVERNMENT HIDING TRUTH ABOUT ALIENS"
Caps words: 5 out of 6 = 83%
Flag: high_caps = True
Hint: LIKELY_FAKE (tabloid style)
```

#### 3️⃣ **Database Storage**
```sql
CREATE TABLE articles (
  id          INTEGER PRIMARY KEY,
  url_hash    TEXT UNIQUE,
  title       TEXT,
  content     TEXT,
  source      TEXT,
  fetched_at  TEXT,
  bias_flags  TEXT,
  ml_verdict  TEXT
)
```

#### 4️⃣ **Auto-Cleanup**
```
Every scrape cycle:
- Delete articles older than 72 hours
- Keep only fresh news
- Prevent database bloat
```

### Example Flow:

```
[30 min timer triggers]

1. Scrape NewsAPI:
   - Found 50 articles
   - Article 1: "Fed maintains interest rates"
     Bias check: No flags → NEUTRAL
     Save to DB

   - Article 2: "SHOCKING: Government EXPOSED!"
     Bias check: Sensational + High caps → LIKELY_FAKE
     Save to DB

2. Scrape RSS Feeds:
   - BBC: 10 articles
   - NYTimes: 10 articles
   - Guardian: 10 articles
   
3. Purge old articles:
   - Deleted 23 articles older than 72h

4. Database now has:
   - 150 fresh articles
   - Each with bias flags
   - Ready for analysis

[Wait 30 minutes, repeat]
```

### Kab Use Kare?
- Tab 5 (Live News) mein
- Real-time news monitoring
- Bias detection in live feeds
- Trending news analysis

---

## 🔄 How They Work Together:

### Scenario: User checks breaking news

```
1. LIVE INTEL scrapes:
   "BREAKING: Aliens confirmed by NASA!"
   Bias flags: sensational_headline=True
   Stored in database

2. User opens Tab 5 (Live News):
   Sees article with bias warning

3. User clicks "Verify with Agent Swarm":
   → Launches 20 agents
   → Searches credible sources
   → Finds NO confirmation
   → Verdict: FAKE

4. User now knows:
   - Article is sensational (Live Intel)
   - No credible sources confirm (Agent Swarm)
   - Conclusion: FAKE NEWS
```

---

## 📊 Comparison:

| Feature | Agent Swarm | Live Intel |
|---------|-------------|------------|
| **Purpose** | Fact verification | News collection |
| **Speed** | 20-40 seconds | Continuous (30 min) |
| **Sources** | 20 domains | NewsAPI + 5 RSS |
| **Output** | Verdict + Evidence | Cached articles |
| **Use Case** | Verify specific claim | Monitor live news |
| **Tab** | Tab 6 | Tab 5 |

---

## 🎯 Key Concepts:

### 1. Parallel Processing
```
Traditional: Agent 1 → Agent 2 → Agent 3 (60 seconds)
Swarm:       Agent 1 ↘
             Agent 2 → Coordinator (20 seconds)
             Agent 3 ↗
```

### 2. Jaccard Similarity
```
How similar are two texts?

Article: {NASA, aliens, confirmed}
Source:  {NASA, denies, alien}

Match: {NASA, alien/aliens} = 2 words
Total: {NASA, aliens, confirmed, denies, alien} = 5 words

Jaccard = 2/5 = 0.40 (40% similar)
```

### 3. Bias Correction
```
Raw article → Check patterns → Flag biases → Hint verdict

Example:
"BREAKING: SHOCKING news!" 
→ Sensational keywords detected
→ Flag: sensational_headline=True
→ Hint: LIKELY_FAKE
```

### 4. SQLite Caching
```
Why cache?
- Avoid re-scraping same articles
- Fast retrieval (no API calls)
- 72-hour retention (fresh news only)
- Offline access
```

---

## 🚀 Real-World Example:

### Article: "Elon Musk buys Twitter for $44 billion"

**Live Intel:**
```
1. Scrapes from NewsAPI
2. Bias check:
   - No sensational keywords
   - Professional writing
   - Multiple credible sources
3. Flags: NEUTRAL
4. Stores in DB
```

**Agent Swarm:**
```
1. Keywords: [Elon, Musk, Twitter, billion, buys]
2. 20 agents search:
   - BBC: Found 3 articles (Jaccard: 0.75)
   - Reuters: Found 5 articles (Jaccard: 0.82)
   - NYTimes: Found 4 articles (Jaccard: 0.68)
   - InfoWars: Found 0 articles
3. Coordinator:
   - 12 credible sources confirm
   - 0 unreliable sources
4. Verdict: REAL (Confidence: 95%)
```

---

## 💡 Summary:

### Agent Swarm = Detective Team
```
20 detectives search internet
Find evidence from multiple sources
Coordinator makes final decision
```

### Live Intel = News Monitor
```
Constantly watches news feeds
Flags suspicious articles
Stores for later analysis
```

### Together = Powerful System
```
Live Intel: "Here's breaking news"
Agent Swarm: "Let me verify that"
User: "Now I know the truth!"
```

---

## 🎓 Technical Terms Simplified:

| Term | Simple Meaning |
|------|----------------|
| **Agent** | A program that searches one website |
| **Swarm** | Many agents working together |
| **Parallel** | All at the same time (not one-by-one) |
| **Jaccard** | How similar two texts are (0-1) |
| **TF-IDF** | Find important words in text |
| **RSS Feed** | Website's news updates in XML format |
| **SQLite** | Small database file (like Excel) |
| **Bias** | Unfair preference or prejudice |
| **Coordinator** | AI that makes final decision |
| **Scraper** | Program that collects data from websites |

---

**Ab samajh aaya? 😊**

Agent Swarm = Fact checker (20 agents)
Live Intel = News collector (continuous monitoring)
