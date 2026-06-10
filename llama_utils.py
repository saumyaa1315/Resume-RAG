import requests


def ask_llama3(prompt: str, model: str = "llama3") -> str:
    """Ask local Llama 3 through Ollama."""
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
            },
            timeout=90,
        )
        response.raise_for_status()
        return response.json().get("response", "").strip()
    except requests.RequestException as exc:
        return f"Llama 3 explanation unavailable. Please check Ollama is running. Error: {exc}"
