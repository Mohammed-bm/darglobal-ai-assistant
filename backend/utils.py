from typing import List, Optional
from bs4 import BeautifulSoup
import re
import math
import requests
import hashlib
import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

load_dotenv()


def clean_text(text: str) -> str:
    """
    Basic text cleaning before chunking / embedding
    """
    text = text.strip()
    text = re.sub(r"\s+", " ", text)
    return text


def chunk_text(
    text: str,
    chunk_size: int = 200,
    overlap: int = 40
) -> List[str]:
    """
    Splits text into overlapping chunks
    """
    words = text.split()
    chunks = []

    start = 0
    while start < len(words):
        end = start + chunk_size
        chunks.append(" ".join(words[start:end]))
        if end >= len(words):
            break
        start = end - overlap

    return chunks


def fetch_and_clean_url(url: str) -> str:
    headers = {
        "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                       "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"),
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": "en-US,en;q=0.9",
    }
    try:
        r = requests.get(url, headers=headers, timeout=20)
        print(f"[fetch] {url} -> {r.status_code}, {len(r.text)} chars")
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        for tag in soup(["script", "style", "noscript", "nav", "footer", "svg"]):
            tag.decompose()
        # Don't drop <header>: some sites put the page's <h1> and intro text in it
        text = soup.get_text(separator=" ", strip=True)
        return re.sub(r"\s+", " ", text).strip()
    except Exception as e:
        print("URL extraction error:", repr(e))
        return ""

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

class LLMService:
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY", "").strip()
        self.model = os.getenv(
            "OPENROUTER_MODEL",
            "baidu/ernie-5.5-flash-preview:free"
        ).strip()

    def generate_answer(self, question: str, context: Optional[str] = None) -> str:
        if not self.api_key:
            return "Missing OPENROUTER_API_KEY in backend/.env"

        if context:
            prompt = f"""You are a helpful AI assistant for DarGlobal and Wasalt real estate.
Answer the question using ONLY the provided context.
If the answer is not in the context, say you don't know based on the available information.

Context:
{context}

Question:
{question}"""
        else:
            prompt = question

        models_to_try = [
            self.model,
            "baidu/ernie-5.5-flash-preview:free",
            "openrouter/free",
        ]

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8000",
            "X-Title": "DarGlobal Wasalt AI Assistant",
        }

        last_error = None
        for m in dict.fromkeys(models_to_try):
            res = None
            try:
                res = requests.post(
                    OPENROUTER_URL,
                    headers=headers,
                    json={
                        "model": m,
                        "messages": [{"role": "user", "content": prompt}],
                        "stream": False,
                    },
                    timeout=30,
                )
                print(f"[{m}] Status: {res.status_code} | Body: {res.text[:250]}")

                if "application/json" not in res.headers.get("content-type", ""):
                    last_error = f"{m}: non-JSON response (HTTP {res.status_code}): {res.text[:200]}"
                    continue

                data = res.json()

                if res.status_code != 200 or "error" in data:
                    last_error = f"{m}: HTTP {res.status_code}: {str(data.get('error', data))[:200]}"
                    continue

                content = (data["choices"][0]["message"].get("content") or "").strip()
                if content:
                    return content
                last_error = f"{m}: empty response content"

            except Exception as e:
                raw = res.text[:150] if res is not None else ""
                last_error = f"{m}: {type(e).__name__}: {e} | Raw: {raw}"
                print(f"Error with {m}: {last_error}")

        return f"OpenRouter API error: {last_error}"

# Singleton instance
llm_service = LLMService()

class EmbeddingService:
    def __init__(self, model_name: str = "paraphrase-multilingual-MiniLM-L12-v2"):
        self.model = SentenceTransformer(model_name)

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        embeddings = self.model.encode(texts, normalize_embeddings=True)
        return embeddings.tolist()

    def embed_query(self, text: str) -> List[float]:
        embedding = self.model.encode(text, normalize_embeddings=True)
        return embedding.tolist()

embedding_service = EmbeddingService()
