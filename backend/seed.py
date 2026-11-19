import sqlite3
import requests

API_BASE = "http://127.0.0.1:8000"
DB_PATH = "items.db"

URLS = [
    "https://wasalt.sa/en",
    # add 3 to 4 more Wasalt pages from its nav
]

QUESTIONS = [
    "What is DarGlobal?",
    "Tell me about Les Vagues",
    "What is Wasalt?",
]


def reset_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("DELETE FROM chunks")
    cur.execute("DELETE FROM items")
    conn.commit()
    conn.close()
    print("Cleared old items and chunks.")


def ingest_urls():
    for url in dict.fromkeys(URLS):  # dedupe, keep order
        try:
            res = requests.post(
                f"{API_BASE}/ingest",  # no trailing slash
                json={"type": "url", "source": url},
                timeout=60,
            )
            status = "OK" if res.status_code == 200 else f"FAILED {res.status_code}"
            print(f"[{status}] {url} -> {res.text[:200]}")
        except Exception as e:
            print(f"[ERROR] {url} -> {e}")


def verify_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    print("\nchunks schema:", [r[1] for r in cur.execute("PRAGMA table_info(chunks)")])
    print("items:", cur.execute("SELECT COUNT(*) FROM items").fetchone()[0])
    print("chunks:", cur.execute("SELECT COUNT(*) FROM chunks").fetchone()[0])
    conn.close()


def test_queries():
    for q in QUESTIONS:
        res = requests.post(f"{API_BASE}/query", json={"question": q}, timeout=90)
        print(f"\nQ: {q}\nHTTP {res.status_code}\n{res.text[:500]}")


if __name__ == "__main__":
    reset_db()
    ingest_urls()
    verify_db()
    test_queries()