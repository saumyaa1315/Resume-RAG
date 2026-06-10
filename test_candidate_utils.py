import glob
import os

from pypdf import PdfReader

from candidate_utils import extract_candidate_info


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from a PDF file."""
    try:
        reader = PdfReader(pdf_path)
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n\n".join(pages).strip()
    except Exception as e:
        print(f"  Error reading {pdf_path}: {e}")
        return ""


def main() -> None:
    resume_dir = "resumes"
    pdf_pattern = os.path.join(resume_dir, "*.pdf")
    pdf_paths = sorted(glob.glob(pdf_pattern))

    if not pdf_paths:
        print(f"No PDF files found in '{resume_dir}' directory.")
        return

    print(f"\n{'='*80}")
    print(f"CANDIDATE INFORMATION EXTRACTION TEST")
    print(f"{'='*80}\n")
    print(f"Found {len(pdf_paths)} resume(s).\n")

    for idx, pdf_path in enumerate(pdf_paths, start=1):
        resume_name = os.path.basename(pdf_path)
        print(f"{'-'*80}")
        print(f"Resume #{idx}: {resume_name}")
        print(f"{'-'*80}")

        # Extract text from PDF
        text = extract_text_from_pdf(pdf_path)
        if not text:
            print("  (No text extracted)")
            continue

        # Extract candidate information
        candidate_info = extract_candidate_info(text)

        # Print results
        print(f"Name:        {candidate_info['name'] or 'N/A'}")
        print(f"Experience:  {candidate_info['experience']} years")
        print(f"Skills:      {', '.join(candidate_info['skills']) if candidate_info['skills'] else 'None'}")
        print()

    print(f"{'='*80}")
    print(f"Test completed successfully!")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    main()
