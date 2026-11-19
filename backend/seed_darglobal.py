import requests

API_BASE = "http://127.0.0.1:8000"

DARGLOBAL_NOTES = [
    {
        "source": "https://darglobal.co.uk (Company Overview & Metrics)",
        "text": "DarGlobal is a London-listed international luxury real estate developer with a $23 Billion Gross Development Value (GDV), operating across 7 markets (UAE, Saudi Arabia, Qatar, Oman, Spain, UK, US) with 12+ brand partners and 66% revenue growth in HY 2026."
    },
    {
        "source": "https://darglobal.co.uk (Flagship Projects & Newsroom 2026)",
        "text": "Key 2026 developments include AIDA in Muscat, Oman (Trump Golf Villas and FENDI Casa residences), Trump International Simaisma in Qatar, Trump Mansions in Wadi Safar, Riyadh, and a SAR 1 Billion mixed-use development announced in Jeddah."
    },
    {
        "source": "https://darglobal.co.uk (Collaborations, Asset Management & Tokenization)",
        "text": "Brand partners include Aston Martin, Elie Saab, FENDI Casa, Automobili Lamborghini, Marriott, and The Trump Organization. Backed by Dubai-regulated Dar Global Capital Partners (DGCP) and emerging real estate tokenization frameworks."
    }
]

def seed_darglobal():
    for item in DARGLOBAL_NOTES:
        res = requests.post(
            f"{API_BASE}/ingest/",
            json={"type": "note", "raw_text": item["text"], "source": item["source"]},
            timeout=30
        )
        print(f"Status {res.status_code}: {res.json()}")

if __name__ == "__main__":
    seed_darglobal()
