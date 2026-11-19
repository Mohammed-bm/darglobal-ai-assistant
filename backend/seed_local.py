import re, glob, requests
from bs4 import BeautifulSoup

API_BASE = "http://127.0.0.1:8000"
BASE = "https://darglobal.co.uk"

# file name (without extension) -> page path (used as the citation)
PAGES = {
    "home": "/", "about": "/about", "projects": "/projects", "investor": "/investor",
    "press": "/press", "aida": "/landing-page/aida", "qatar": "/lp/trump-international-qatar",
    "riyadh": "/rayana/trump-mansions", "golf": "/luxury-golf-communities",
    "hospitality": "/hospitality", "aston-martin": "/partners/aston-martin",
    "fendi": "/partners/fendi-casa",
    "press-qatar": "/press/dar-global-opens-sales-trump-villas-simaisma-qatar-unprecedented-interest",
    "press-oman": "/press/darglobal-fendi-casa-announce-azure-oceanfront-villas-oman",
}

def file_to_text(path: str) -> str:
    raw = open(path, encoding="utf-8", errors="ignore").read()
    if path.endswith(".txt"):
        return re.sub(r"\s+", " ", raw).strip()
    soup = BeautifulSoup(raw, "html.parser")
    for t in soup(["script", "style", "noscript", "svg", "nav", "footer"]):
        t.decompose()
    return re.sub(r"\s+", " ", soup.get_text(" ", strip=True))

for name, path in PAGES.items():
    files = glob.glob(f"seed_pages/{name}.*")
    if not files:
        print(f"[SKIP] no file for {name}")
        continue
    text = file_to_text(files[0])
    words = len(text.split())
    print(f"{name}: {words} words")
    if words < 50 or "incapsula" in text.lower():
        print("   too short or a block page, re-save this file")
        continue
    r = requests.post(
        f"{API_BASE}/ingest",
        json={
            "type": "note",
            "raw_text": f"Source: {BASE}{path}\n\n{text}",
            "source": f"{BASE}{path}",
        },
        timeout=180,
    )
    print("  ", r.status_code, r.text[:100])