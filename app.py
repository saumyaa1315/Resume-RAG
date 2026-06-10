import streamlit as st

from advanced_search import load_candidates, match_candidates, parse_query
from llama_utils import ask_llama3


def build_summary_prompt(query: str, candidates: list[dict]) -> str:
    candidate_lines = []
    for index, candidate in enumerate(candidates[:3], start=1):
        candidate_lines.append(
            f"{index}. {candidate.get('name') or 'N/A'}, "
            f"{candidate.get('experience')} years, "
            f"skills: {', '.join(candidate.get('skills', []))}"
        )

    return f"""
You are an AI recruiter assistant.

User query:
{query}

Top candidates:
{chr(10).join(candidate_lines)}

Give a short recommendation. Mention the best fit and why.
Do not invent information.
"""


st.set_page_config(page_title="Resume RAG Copilot", layout="wide")

st.title("Resume RAG Copilot")

query = st.text_input(
    "Search resumes",
    placeholder="Example: Best React developer with 4-6 years experience",
)

use_llama = st.checkbox("Use Llama 3 explanation", value=False)
top_k = st.slider("Number of results", min_value=1, max_value=10, value=5)

if st.button("Search", type="primary") and query.strip():
    candidates = load_candidates()
    required_skills, experience_range, highest_only = parse_query(query)
    results = match_candidates(candidates, required_skills, experience_range, highest_only)
    results = results[:top_k]

    st.caption(f"Detected skills: {', '.join(required_skills) if required_skills else 'None'}")
    st.caption(f"Experience filter: {experience_range if experience_range else 'None'}")

    if not results:
        st.warning("No matching candidates found.")
    else:
        for rank, candidate in enumerate(results, start=1):
            with st.container(border=True):
                st.subheader(f"{rank}. {candidate.get('name') or 'N/A'}")
                col1, col2, col3 = st.columns(3)
                col1.metric("Experience", f"{candidate.get('experience', 0)} years")
                col2.metric("Match Score", candidate.get("match_score", 0))
                col3.write(f"Resume: `{candidate.get('resume')}`")
                st.write("Skills:")
                st.write(", ".join(candidate.get("skills", [])))

        if use_llama:
            st.divider()
            st.subheader("Llama 3 Recommendation")
            with st.spinner("Asking Llama 3..."):
                st.write(ask_llama3(build_summary_prompt(query, results)))
