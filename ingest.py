import glob
import os

from langchain_community.document_loaders import PyPDFLoader
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter


def load_resume_paths(resume_dir: str) -> list[str]:
    pdf_pattern = os.path.join(resume_dir, "*.pdf")
    return sorted(glob.glob(pdf_pattern))


def load_and_split_resume(path: str, splitter: RecursiveCharacterTextSplitter) -> list:
    loader = PyPDFLoader(path)
    documents = loader.load()
    for document in documents:
        document.metadata["resume_name"] = os.path.basename(path)
    return splitter.split_documents(documents)


def build_vector_db(resume_dir: str = "resumes", persist_dir: str = "vector_db") -> None:
    resume_paths = load_resume_paths(resume_dir)
    if not resume_paths:
        print(f"No PDF resumes found in '{resume_dir}'.")
        return

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
    )

    all_chunks = []
    for resume_path in resume_paths:
        chunks = load_and_split_resume(resume_path, text_splitter)
        all_chunks.extend(chunks)

    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    Chroma.from_documents(
        documents=all_chunks,
        embedding=embeddings,
        persist_directory=persist_dir,
    )

    print(f"Number of resumes loaded: {len(resume_paths)}")
    print(f"Number of chunks created: {len(all_chunks)}")
    print(f"ChromaDB persisted successfully in '{persist_dir}'.")


if __name__ == "__main__":
    build_vector_db()
