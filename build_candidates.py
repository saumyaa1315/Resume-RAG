import glob
import json
from pathlib import Path

from pypdf import PdfReader

from candidate_utils import extract_candidate_info


def extract_text_from_pdf(pdf_path: str) -> str:
    try:
        reader = PdfReader(pdf_path)
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n\n".join(pages).strip()
    except Exception as exc:
        print(f"Error reading {pdf_path}: {exc}")
        return ""


def build_candidates_database(
    resume_dir: str = "resumes",
    output_file: str = "candidates.json",
) -> None:
    pdf_files = sorted(glob.glob(str(Path(resume_dir) / "*.pdf")))

    if not pdf_files:
        print(f"No PDF files found in {resume_dir}/")
        return

    candidates = []
    for pdf_path in pdf_files:
        resume_filename = Path(pdf_path).name
        text = extract_text_from_pdf(pdf_path)

        if not text:
            print(f"Warning: Could not extract text from {resume_filename}")
            continue

        info = extract_candidate_info(text)
        candidates.append(
            {
                "resume": resume_filename,
                "name": info.get("name"),
                "experience": info.get("experience", 0),
                "skills": info.get("skills", []),
            }
        )

    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(candidates, file, indent=2, ensure_ascii=False)

    print(f"Candidates extracted successfully: {len(candidates)}")
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    build_candidates_database()
