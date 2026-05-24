import re
import csv
from pathlib import Path

try:
    import fitz  # PyMuPDF
except ImportError:
    print("Missing package: PyMuPDF")
    print("Run this first: pip install pymupdf")
    raise

BASE_DIR = Path(__file__).resolve().parents[1]

PDF_PATH = BASE_DIR / "vocabulary" / "The_Oxford_3000.pdf"
OUT_PATH = BASE_DIR / "vocabulary" / "oxford3000.csv"

def extract_words_from_pdf(pdf_path: Path):
    doc = fitz.open(pdf_path)
    results = []
    seen = set()

    for page in doc:
        text = page.get_text("text")
        lines = [line.strip() for line in text.splitlines() if line.strip()]

        for line in lines:
            # Typical lines may look like:
            # abandon v. B2
            # ability n. A2
            # able adj. A2
            m = re.match(
                r"^([a-zA-Z][a-zA-Z\- ]+?)\s+(?:[a-z]+\.)?\s*(A1|A2|B1|B2)\b",
                line
            )

            if not m:
                continue

            word = m.group(1).strip().lower()
            level = m.group(2).strip()

            if len(word) > 35:
                continue

            if word in {"the oxford", "oxford", "the"}:
                continue

            key = word
            if key not in seen:
                seen.add(key)
                results.append((word, level))

    return results

def main():
    if not PDF_PATH.exists():
        raise FileNotFoundError(f"PDF not found: {PDF_PATH}")

    words = extract_words_from_pdf(PDF_PATH)

    print(f"Extracted {len(words)} entries")

    with OUT_PATH.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["word", "level", "status", "mastery", "last_seen", "scene"])

        for word, level in words:
            writer.writerow([word, level, "new", 0, "", ""])

    print(f"Saved to: {OUT_PATH}")

if __name__ == "__main__":
    main()