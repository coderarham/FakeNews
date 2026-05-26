"""
Quick test script for Agent Swarm
Run: python test_agent_swarm.py
"""

from fact_swarm import run_swarm
import json

print("[*] Testing Agent Swarm...\n")

# Test article
article = """
Breaking News: NASA announces discovery of water on Mars. 
Scientists confirm liquid water found beneath Martian surface. 
This could indicate potential for life on the red planet.
"""

print("[ARTICLE] Article to verify:")
print(article)
print("\n" + "="*60)
print("[LAUNCH] Launching 20 agents... (this will take 20-40 seconds)")
print("="*60 + "\n")

# Run swarm
result = run_swarm(article)

# Display results
print("[VERDICT]", result['verdict']['verdict'])
print("[CONFIDENCE]", f"{result['verdict']['confidence']*100:.1f}%")
print("[CREDIBLE SOURCES]", result['verdict']['credible_sources_found'])
print("[UNRELIABLE SOURCES]", result['verdict']['unreliable_sources_found'])
print("[TIME TAKEN]", f"{result['elapsed_seconds']}s")
print("\n[REASONING]")
print(result['verdict']['reasoning'])

print("\n[KEYWORDS EXTRACTED]")
print(", ".join(result['keywords']))

print("\n[AGENT EVIDENCE]")
found_count = 0
for agent in result['agent_results']:
    if agent['found']:
        found_count += 1
        marker = "[CREDIBLE]" if agent['credible'] else "[UNRELIABLE]"
        print(f"\n{marker} {agent['domain'].upper()} ({agent['site']})")
        for ev in agent['evidence']:
            print(f"   - {ev['title'][:80]}")
            print(f"     Jaccard: {ev['jaccard']}")

print(f"\n[SUMMARY] {found_count}/20 agents found evidence")
print("\n[SUCCESS] Agent Swarm test complete!")
