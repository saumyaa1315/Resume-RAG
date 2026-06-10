"""Test advanced_search.py with example queries."""

from advanced_search import load_candidates, parse_query, match_candidates


candidates = load_candidates()

test_queries = [
    "React",
    "React with 4-6 years experience",
    "Candidates with minimum 3 years experience",
    "Highest Experience Candidate",
    "Docker",
    "TypeScript Developer",
    "React and Redux",
    "DevOps with cloud experience",
    "Best UI developer",
]

print("=" * 100)
print("TESTING ADVANCED SEARCH")
print("=" * 100)

for query in test_queries:
    print(f"\n[Query] {query}")
    print("-" * 100)

    required_skills, experience_range, highest_only = parse_query(query)
    print(f"Skills detected: {required_skills}")
    print(f"Experience range: {experience_range}")
    print(f"Highest only: {highest_only}")

    matched = match_candidates(candidates, required_skills, experience_range, highest_only)
    print(f"Matched candidates: {len(matched)}")

    for idx, candidate in enumerate(matched, 1):
        print(
            f"  {idx}. {candidate.get('name') or 'N/A'} - "
            f"{candidate.get('experience', 0)} years - "
            f"{candidate.get('resume')} - score {candidate.get('match_score', 0)}"
        )

    print()
