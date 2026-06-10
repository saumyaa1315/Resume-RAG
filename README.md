# Resume RAG Copilot

Resume RAG Copilot searches PDF resumes using semantic search, skill extraction, experience filtering, and optional Llama 3 explanations.

## Tools

- Python
- VS Code
- LangChain
- ChromaDB
- HuggingFace embeddings: `all-MiniLM-L6-v2`
- PyPDF
- Streamlit
- Ollama with Llama 3

## Folder Structure

```text
Resume-RAG-Copilot/
  resumes/
    resume1.pdf
    resume2.pdf
  vector_db/
  app.py
  ingest.py
  build_candidates.py
  advanced_search.py
  search.py
  candidate_utils.py
  llama_utils.py
  candidates.json
  requirements.txt
```

## Setup

```powershell
pip install -r requirements.txt
```

Make sure Ollama and Llama 3 are available:

```powershell
ollama list
ollama run llama3
```

## Run Pipeline

Put PDF resumes inside the `resumes/` folder.

Build vector database:

```powershell
python ingest.py
```

Build structured candidate database:

```powershell
python build_candidates.py
```

Run command line search:

```powershell
python advanced_search.py
```

Run UI:

```powershell
streamlit run app.py
```

## Example Queries

```text
Best React developer with 4-6 years experience
Highest experience candidate
DevOps with cloud experience
Best UI developer
Docker
TypeScript Developer
```
