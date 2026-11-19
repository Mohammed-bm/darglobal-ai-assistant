import re, requests
from bs4 import BeautifulSoup

URLS = [
    "https://darglobal.co.uk/",
    "https://darglobal.co.uk/about",
    "https://darglobal.co.uk/projects",
    "https://darglobal.co.uk/lp/trump-international-qatar",
]
H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36",
     "Accept-Language": "en-US,en;q=0.9"}

for u in URLS:
    r = requests.get(u, headers=H, timeout=20)
    soup = BeautifulSoup(r.text, "html.parser")
    has_next = bool(soup.find("script", id="__NEXT_DATA__"))
    for t in soup(["script", "style", "noscript", "svg"]):
        t.decompose()
    text = re.sub(r"\s+", " ", soup.get_text(" ", strip=True))
    print(f"\n{u}\n status={r.status_code} html={len(r.text)} words={len(text.split())} next_data={has_next}")
    print(" sample:", text[:300])