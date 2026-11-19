from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from api import ingest, items, query

app = FastAPI(title="DarGlobal & Wasalt AI Assistant")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # dev only; production is same-origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ingest.router)
app.include_router(items.router)
app.include_router(query.router)

DIST = Path(__file__).parent / "dist"
if DIST.exists():
    # Must come last, otherwise it swallows the API routes
    app.mount("/", StaticFiles(directory=DIST, html=True), name="static")
else:
    @app.get("/")
    def root():
        return {"message": "API is running (no frontend build found)"}