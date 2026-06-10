import json
import re
from typing import Optional

from candidate_utils import WHITELISTED_SKILLS
from llama_utils import ask_llama3


ROLE_SKILL_MAP = {
    "ui": {"React", "JavaScript", "TypeScript", "HTML", "CSS"},
    "frontend": {"React", "JavaScript", "TypeScript", "HTML", "CSS"},
    "front end": {"React", "JavaScript", "TypeScript", "HTML", "CSS"},
    "react developer": {"React"},
    "backend": {"Java", "Spring Boot", "Node.js", "SQL", "REST API"},
    "back end": {"Java", "Spring Boot", "Node.js", "SQL", "REST API"},
    "java backend": {"Java", "Spring Boot", "SQL", "REST API"},
    "devops": {"DevOps", "Docker", "Kubernetes", "Jenkins", "AWS", "Azure", "GCP", "CI/CD"},
    "cloud": {"AWS", "Azure", "GCP"},
}


def load_candidates(candidates_file: str = "candidates.json") -> list[dict]:
    try:
        with open(candidates_file, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: {candidates_file} not found. Run python build_candidates.py first.")
        return []
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in {candidates_file}")
        return []


def parse_query(query: str) -> tuple[list[str], Optional[tuple[int, int]], bool]:
    query_lower = query.lower()
    required_skills = set()
    experience_range = None
    highest_only = False

    for skill in WHITELISTED_SKILLS:
        if skill.lower() in query_lower:
            required_skills.add(skill)

    for role_keyword, role_skills in ROLE_SKILL_MAP.items():
        if role_keyword in query_lower:
            required_skills.update(role_skills)

    if "highest" in query_lower or "most experience" in query_lower or "maximum experience" in query_lower:
        highest_only = True

    min_match = re.search(r"(?:minimum|min|at least|minimum of)\s+(\d+)\s+years?", query_lower)
    if min_match:
        experience_range = (int(min_match.group(1)), 1000)

    range_match = re.search(r"(\d+)\s*(?:-|to)\s*(\d+)\s+years?", query_lower)
    if range_match:
        experience_range = (int(range_match.group(1)), int(range_match.group(2)))

    if not experience_range:
        exact_match = re.search(r"\b(\d+)\s+years?\b", query_lower)
        if exact_match:
            years = int(exact_match.group(1))
            experience_range = (years, years)

    return sorted(required_skills), experience_range, highest_only


def calculate_match_score(candidate: dict, required_skills: list[str], experience_range: Optional[tuple[int, int]]) -> int:
    score = 0
    candidate_skills = {skill.lower() for skill in candidate.get("skills", [])}

    for skill in required_skills:
        if skill.lower() in candidate_skills:
            score += 10

    if experience_range:
        min_exp, max_exp = experience_range
        experience = candidate.get("experience", 0)
        if min_exp <= experience <= max_exp:
            score += 20

    score += int(candidate.get("experience", 0))
    return score


def match_candidates(
    candidates: list[dict],
    required_skills: list[str],
    experience_range: Optional[tuple[int, int]],
    highest_only: bool = False,
) -> list[dict]:
    matched = []

    for candidate in candidates:
        candidate_skills = {skill.lower() for skill in candidate.get("skills", [])}

        if required_skills:
            matched_skill_count = sum(1 for skill in required_skills if skill.lower() in candidate_skills)
            if matched_skill_count == 0:
                continue

        if experience_range:
            min_exp, max_exp = experience_range
            experience = candidate.get("experience", 0)
            if not (min_exp <= experience <= max_exp):
                continue

        candidate_copy = dict(candidate)
        candidate_copy["match_score"] = calculate_match_score(candidate, required_skills, experience_range)
        matched.append(candidate_copy)

    matched.sort(key=lambda item: (item.get("match_score", 0), item.get("experience", 0)), reverse=True)

    if highest_only and matched:
        highest_experience = matched[0].get("experience", 0)
        matched = [candidate for candidate in matched if candidate.get("experience", 0) == highest_experience]

    return matched


def build_explanation_prompt(candidate: dict, query: str) -> str:
    return f"""
You are helping a recruiter shortlist resumes.

User query:
{query}

Candidate:
Name: {candidate.get("name") or "N/A"}
Resume: {candidate.get("resume")}
Experience: {candidate.get("experience")} years
Skills: {", ".join(candidate.get("skills", []))}

Explain in 2 short lines why this candidate is a good match.
Do not invent skills or experience.
"""


def explain_candidate_match(candidate: dict, query: str) -> str:
    return ask_llama3(build_explanation_prompt(candidate, query))


def display_results(candidates: list[dict], query: str, explain: bool = False) -> None:
    print("\n" + "=" * 100)
    print(f"Search Query: {query}")
    print("=" * 100)

    if not candidates:
        print("No candidates found matching your criteria.\n")
        return

    print(f"\nFound {len(candidates)} candidate(s):\n")
    print(f"{'Rank':<6} {'Name':<25} {'Resume':<18} {'Experience':<12} {'Score':<8} Skills")
    print("-" * 100)

    for index, candidate in enumerate(candidates, start=1):
        skills = ", ".join(candidate.get("skills", [])[:6])
        print(
            f"{index:<6} "
            f"{(candidate.get('name') or 'N/A')[:24]:<25} "
            f"{candidate.get('resume', ''):<18} "
            f"{str(candidate.get('experience', 0)) + ' years':<12} "
            f"{candidate.get('match_score', 0):<8} "
            f"{skills}"
        )

        if explain:
            print(f"Reason: {explain_candidate_match(candidate, query)}")
            print()


def search_candidates(query: str, explain: bool = False) -> list[dict]:
    candidates = load_candidates()
    required_skills, experience_range, highest_only = parse_query(query)
    matched = match_candidates(candidates, required_skills, experience_range, highest_only)

    if explain:
        for candidate in matched[:3]:
            candidate["explanation"] = explain_candidate_match(candidate, query)

    return matched


def interactive_search() -> None:
    print("\nAdvanced Resume Search")
    print("Examples:")
    print(" - Best React developer with 4-6 years experience")
    print(" - Highest experience candidate")
    print(" - DevOps with cloud experience")
    print(" - Best UI developer")
    print(" - Docker")
    print("\nType quit to exit.\n")

    while True:
        query = input("Enter search query: ").strip()
        if query.lower() in {"quit", "exit", "q"}:
            break
        if not query:
            continue

        required_skills, experience_range, highest_only = parse_query(query)
        candidates = load_candidates()
        matched = match_candidates(candidates, required_skills, experience_range, highest_only)
        display_results(matched, query, explain=False)


if __name__ == "__main__":
    interactive_search()
