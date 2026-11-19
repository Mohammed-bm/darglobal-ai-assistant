FROM python:3.11-slim

# Non-root user (also works on hosts that require it)
RUN useradd -m -u 1000 user && mkdir -p /app && chown user:user /app
WORKDIR /app

# No PyTorch: fastembed runs the model with ONNX, so the image stays small
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

ENV HOME=/home/user \
    FASTEMBED_CACHE=/home/user/.cache/fastembed \
    PYTHONUNBUFFERED=1
USER user

# Bake the embedding model into the image so the first request is not slow
RUN python -c "from fastembed import TextEmbedding; TextEmbedding(model_name='sentence-transformers/all-MiniLM-L6-v2', cache_dir='/home/user/.cache/fastembed')"

# App code + dist/ (built frontend) + pre-seeded items.db
COPY --chown=user:user . .

# Render sets PORT; fall back to 10000 when it is not set
EXPOSE 10000
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-10000}"]