# DarGlobal & Wasalt AI Assistant

A retrieval-augmented (RAG) chatbot that answers questions about DarGlobal and Wasalt using content collected from their public websites. Every answer comes with the source passages it was built from and a similarity score.

**Live demo:** `<YOUR-RENDER-URL>`

The demo runs on a free hosting tier that sleeps when idle, so the first load after a quiet period can take a minute or two.

## What it does

- Answers questions about DarGlobal projects, partners and news, and about Wasalt's platform.
- Shows the retrieved sources (page, passage, match percentage) for each answer.
- Says it doesn't know when the answer isn't in the saved content.
- Lets you add more notes or URLs to the knowledge base from the UI.

## Tech stack

| Layer | Choice |
|---|---|
| Backend | FastAPI, SQLite |
| Embeddings | `all-MiniLM-L6-v2` run locally through fastembed (ONNX, CPU only, no PyTorch) |
| LLM | Free models on OpenRouter, with fallback (see below) |
| Frontend | React (hooks), Vite, Tailwind CSS |
| Packaging and hosting | Docker, deployed on Render (free web service) |

## How it works

1. **Ingest** (`POST /ingest`): text from a note or a fetched URL is cleaned, split into overlapping chunks (200 words, 40 overlap) and embedded locally. Chunks and embeddings are stored in SQLite.
2. **Retrieve** (`POST /query`): the question is embedded and compared by cosine similarity against all stored chunks. The top 5 chunks are selected.
3. **Generate**: the question and the 5 chunks go to an OpenRouter free model with an instruction to answer only from the context. The answer and its sources are returned.

The LLM call tries the configured model first, then `baidu/ernie-5.5-flash-preview:free`, then `openrouter/free`, with a second pass after a short pause when free models are rate-limited.

## Data collection

- **Wasalt:** ingested directly by URL through the same `/ingest` endpoint.
- **DarGlobal:** the site's bot protection blocks scripted requests, so the pages were opened in a normal browser, saved as text, and ingested through the same cleaning, chunking and embedding pipeline. All content is from publicly available pages.

The pre-seeded database (`backend/items.db`) ships with the project, so the deployed bot works immediately. It contains 11 DarGlobal pages (home, about, projects, investor, press, AIDA, Trump Mansions, partner pages and two press releases) and the Wasalt English homepage.

## Run locally

Requires Python 3.11 or newer and Node 18 or newer.

```bash
# Backend
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Create `backend/.env`:

```
OPENROUTER_API_KEY=your_key_here
# optional: OPENROUTER_MODEL=baidu/ernie-5.5-flash-preview:free
```

```bash
uvicorn main:app --reload        # http://localhost:8000
```

```bash
# Frontend (development, with API proxy)
cd frontend
npm install
npm run dev                      # http://localhost:5173
```

### Single-server build

FastAPI serves the built UI, so one process handles everything:

```bash
cd frontend
npm run build
cp -r dist ../backend/dist       # Windows: Copy-Item -Recurse dist ..\backend\dist
cd ../backend
uvicorn main:app                 # http://localhost:8000
```

## Docker

```bash
cd backend
docker build -t darglobal-bot .
docker run -p 10000:10000 -e OPENROUTER_API_KEY=your_key_here darglobal-bot
```

Then open `http://localhost:10000`. The image uses ONNX instead of PyTorch to keep memory low, downloads the embedding model at build time so the first request is fast, runs as a non-root user, and listens on the `PORT` environment variable (default 10000).

## Deploy on Render

1. Push the repository to GitHub.
2. In Render choose **New → Web Service** and select the repository.
3. Set **Language** to Docker, **Root Directory** to `backend`, and **Instance Type** to Free.
4. Add the environment variable `OPENROUTER_API_KEY`.
5. Deploy. Render builds the Dockerfile and serves the app at its `onrender.com` URL.

## API

| Method | Path | Body | Purpose |
|---|---|---|---|
| POST | `/ingest` | `{"type": "note", "raw_text": "...", "source": "optional URL"}` or `{"type": "url", "source": "https://..."}` | Add content |
| GET | `/items` | none | List saved items |
| POST | `/query` | `{"question": "...", "top_k": 5}` | Ask a question |

`/query` returns `{"answer": "...", "sources": [{"snippet", "source", "type", "score"}]}`.

## Re-seeding the database

`backend/seed.py` wipes the database and ingests the Wasalt page. `backend/seed_local.py` then adds DarGlobal pages from text files saved in `backend/seed_pages/` (not committed). Running `seed.py` deletes everything, so only use it when you mean to rebuild the database from scratch. If you change the embedding model, re-seed, because embeddings from different models cannot be compared.

## Project structure

```
backend/
  main.py            app setup, routers, static UI
  db.py              SQLite connection and schema
  utils.py           cleaning, chunking, URL fetching, embeddings, LLM client
  api/               ingest, items, query routes
  items.db           pre-seeded knowledge base
  dist/              built frontend
  Dockerfile
frontend/
  src/               React app (components, api helper)
```

## Design decisions and limits

- **Free models:** OpenRouter's free tier is rate-limited, and `openrouter/free` picks a different model each time, so answer style can vary. If every model is busy the UI shows a retry message.
- **Small local embedding model:** `all-MiniLM-L6-v2` has no API key or cost and fits the free host's 512 MB of memory. It is English-only. A multilingual model would handle Arabic questions better but needs more memory than the free tier offers.
- **Simple vector search:** all chunks are scored in Python with cosine similarity. That is fine for thousands of chunks; a larger corpus would need a vector index such as pgvector.
- **Single user, no auth:** anyone with the URL can add content. Content added after deployment may be lost when the service restarts, because the disk is not persistent. The pre-seeded data is part of the image.
- **Free hosting:** the service sleeps after about 15 minutes without traffic, and the first request afterwards is slow.
- **Coverage:** answers are limited to the pages ingested. Questions about pages that were not saved get "I don't know based on the available information".
- **Source cleanup:** page navigation text repeated on every DarGlobal page is stripped from displayed snippets, but remains in the stored chunks.