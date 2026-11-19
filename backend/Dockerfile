FROM python:3.11-slim

# Hugging Face Spaces runs containers as UID 1000
RUN useradd -m -u 1000 user && mkdir -p /app && chown user:user /app
WORKDIR /app

# CPU-only torch first (avoids the huge CUDA build), then the rest
COPY requirements.txt .
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu \
 && pip install --no-cache-dir -r requirements.txt

ENV HOME=/home/user \
    HF_HOME=/home/user/.cache/huggingface \
    PYTHONUNBUFFERED=1
USER user

# Bake the embedding model into the image so the first request is not slow
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')"

# App code + dist/ (built frontend) + pre-seeded items.db
COPY --chown=user:user . .

EXPOSE 7860
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]