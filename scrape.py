# scrape.py
import requests
from bs4 import BeautifulSoup
import os
import re

os.makedirs("data", exist_ok=True)

URL = "https://www.mayoclinic.org/symptoms/abdominal-pain/basics/causes/sym-20050728"

def clean_text(s: str) -> str:
    s = re.sub(r"\s+", " ", s)
    return s.strip()

def main():
    resp = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"})
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "lxml")

    # Remove non-content tags
    for t in soup(["script", "style", "noscript", "header", "footer", "nav", "aside"]):
        t.decompose()

    main = soup.select_one("main, article, .content, .content-body") or soup

    # Keep headings/paragraphs/lists — causes are often in lists
    parts = []
    for el in main.find_all(["h1", "h2", "h3", "p", "li"]):
        txt = el.get_text(" ", strip=True)
        txt = clean_text(txt)
        if txt and len(txt) > 2:
            parts.append(txt)

    text = "\n".join(parts)

    out_path = "data/abdominal_clean.txt"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(text)

    print("✅ Saved cleaned causes text ->", out_path)

if __name__ == "__main__":
    main()
