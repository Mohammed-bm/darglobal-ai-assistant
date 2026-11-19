import os
import re
import time
from typing import List, Optional

import numpy as np
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from fastembed import TextEmbedding

load_dotenv()

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"  # 384-dim, small, English


# ---------------------------------------------------------------------------
# Text helpers
# ---------------------------------------------------------------------------
def clean_text(text: str) -> str:
    """Basic text cleaning before chunking / embedding."""
    return re.sub(r"\s+", " ", text.strip())


def chunk_text(text: str, chunk_size: int = 200, overlap: int = 40) -> List[str]:
    """Split text into overlapping word chunks."""
    if overlap >= chunk_size:  # guard against an infinite loop
        overlap = chunk_size // 4

    words = text.split()
    chunks: List[str] = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunks.append(" ".join(words[start:end]))
        if end >= len(words):
            break
        start = end - overlap
    return chunks


BLOCK_MARKERS = (
    "incapsula incident",
    "request unsuccessful",
    "access denied",
    "attention required",
    "enable javascript and cookies",
)


def fetch_and_clean_url(url: str) -> str:
    """Fetch a page and return its visible text, or "" if blocked/empty."""
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
        ),
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
        # <header> is kept on purpose: some sites put the <h1> and intro text there

        text = re.sub(r"\s+", " ", soup.get_text(separator=" ", strip=True)).strip()

        # Bot-protection pages often return HTTP 200 with a tiny block page
        if len(text.split()) < 50 or any(m in text.lower() for m in BLOCK_MARKERS):
            print(f"[fetch] blocked or empty page: {url}")
            return ""
        return text

    except Exception as e:
        print("URL extraction error:", repr(e))
        return ""


# ---------------------------------------------------------------------------
# LLM (OpenRouter, free models with fallback)
# ---------------------------------------------------------------------------
class LLMService:
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY", "").strip()
        self.model = os.getenv(
            "OPENROUTER_MODEL", "baidu/ernie-5.5-flash-preview:free"
        ).strip()
        self.referer = os.getenv("APP_URL", "http://localhost:8000")

    def _build_prompt(self, question: str, context: Optional[str]) -> str:
        if not context:
            return question
        return f"""You are a helpful AI assistant for DarGlobal and Wasalt real estate.
Answer the question using ONLY the provided context.
If the answer is not in the context, say you don't know based on the available information.

Context:
{context}

Question:
{question}"""

    def generate_answer(self, question: str, context: Optional[str] = None) -> str:
        if not self.api_key:
            return "Missing OPENROUTER_API_KEY. Set it in backend/.env or as an environment variable."

        prompt = self._build_prompt(question, context)

        # Preferred model first, then fallbacks. openrouter/free picks any available free model.
        models_to_try = list(dict.fromkeys([
            self.model,
            "baidu/ernie-5.5-flash-preview:free",
            "openrouter/free",
        ]))

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": self.referer,
            "X-Title": "DarGlobal Wasalt AI Assistant",
        }

        last_error = None
        for attempt in range(2):  # two passes, with a short back-off between them
            for m in models_to_try:
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
                        timeout=45,
                    )
                    print(f"[{m}] Status: {res.status_code} | Body: {res.text.strip()[:200]}")

                    if "application/json" not in res.headers.get("content-type", ""):
                        last_error = f"{m}: non-JSON response (HTTP {res.status_code})"
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

            if attempt == 0:
                time.sleep(2)

        print("All OpenRouter models failed. Last error:", last_error)
        return (
            "The free AI models are busy right now. "
            "Please try again in a few seconds."
        )


llm_service = LLMService()


# ---------------------------------------------------------------------------
# Embeddings (local, ONNX via fastembed: no PyTorch, low memory)
# ---------------------------------------------------------------------------
class EmbeddingService:
    def __init__(self, model_name: str = EMBEDDING_MODEL):
        self.model = TextEmbedding(
            model_name=model_name,
            cache_dir=os.getenv("FASTEMBED_CACHE") or None,
        )

    @staticmethod
    def _normalize(vec) -> List[float]:
        v = np.asarray(vec, dtype=np.float32)
        norm = float(np.linalg.norm(v)) or 1.0
        return (v / norm).tolist()

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Embed many texts (ingestion)."""
        return [self._normalize(v) for v in self.model.embed(texts)]

    def embed_query(self, text: str) -> List[float]:
        """Embed one query (search)."""
        return self._normalize(next(iter(self.model.embed([text]))))


# Loaded once at import time so requests are fast
embedding_service = EmbeddingService()