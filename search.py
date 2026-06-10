import os
from collections import defaultdict

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings


def load_vector_store(persist_dir: str = "vector_db", collection_name: str = "langchain") -> Chroma:
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    return Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory=persist_dir,
    )


def group_scores_by_resume(results: list[tuple]) -> list[tuple[str, float, int]]:
    scores_by_resume: dict[str, list[float]] = defaultdict(list)

    for document, score in results:
        metadata = getattr(document, "metadata", {}) or {}
        source = metadata.get("resume_name") or metadata.get("source") or "unknown"
        resume_name = os.path.basename(source)
        scores_by_resume[resume_name].append(score)

    grouped = []
    for resume_name, scores in scores_by_resume.items():
        average_score = sum(scores) / len(scores)
        grouped.append((resume_name, average_score, len(scores)))

    grouped.sort(key=lambda item: item[1])
    return grouped


def semantic_search(query: str, k: int = 20) -> list[tuple[str, float, int]]:
    db = load_vector_store()
    results = db.similarity_search_with_score(query, k=k)
    return group_scores_by_resume(results)


def print_ranked_resumes(grouped_scores: list[tuple[str, float, int]]) -> None:
    print("\nTOP MATCHING CANDIDATES\n")
    print(f"{'Rank':<4} {'Resume Name':<36} {'Distance':>12}")
    print("-" * 56)
    for rank, (resume_name, avg_score, _) in enumerate(grouped_scores, start=1):
        print(f"{rank:<4} {resume_name:<36} {avg_score:12.4f}")


if __name__ == "__main__":
    query = input("Enter semantic search query: ").strip()
    if query:
        print_ranked_resumes(semantic_search(query))
