"""
Custom Agent Swarm Test
Apna article yahan paste karo aur test karo
"""

from fact_swarm import run_swarm

# ============================================
# YAHAN APNA ARTICLE PASTE KARO:
# ============================================
article = """
Donald Trump announces new policy on immigration.
President says border wall construction will resume.
Critics call it controversial and divisive.
"""
# ============================================

print("\n" + "="*60)
print("AGENT SWARM TEST")
print("="*60)
print("\nArticle:", article[:100] + "...")
print("\nLaunching 20 agents...\n")

result = run_swarm(article)

print("\n" + "="*60)
print("RESULTS")
print("="*60)
print(f"\nVerdict: {result['verdict']['verdict']}")
print(f"Confidence: {result['verdict']['confidence']*100:.0f}%")
print(f"Credible Sources: {result['verdict']['credible_sources_found']}")
print(f"Time: {result['elapsed_seconds']}s")
print(f"\nReasoning: {result['verdict']['reasoning']}")
print(f"\nKeywords: {', '.join(result['keywords'][:8])}")

# Show evidence
print("\n" + "="*60)
print("EVIDENCE FOUND")
print("="*60)
found = 0
for agent in result['agent_results']:
    if agent['found']:
        found += 1
        print(f"\n[{agent['domain'].upper()}] {agent['site']}")
        for ev in agent['evidence'][:2]:
            print(f"  - {ev['title'][:70]}")

print(f"\n\nTotal: {found}/20 agents found evidence")
print("\nDone!\n")
