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

PDF_PATH = BASE_DIR / "vocabulary" / "American_Oxford_5000_by_CEFR_level.pdf"
OUT_PATH = BASE_DIR / "vocabulary" / "oxford5000_extra.csv"

VALID_LEVELS = {"B2", "C1"}

def extract_entries(pdf_path: Path):
    print(f"Reading PDF: {pdf_path}")

    doc = fitz.open(pdf_path)
    entries = []
    seen = set()
    current_level = None

    for page in doc:
        text = page.get_text("text")
        lines = [line.strip() for line in text.splitlines() if line.strip()]

        for line in lines:
            if line in VALID_LEVELS:
                current_level = line
                continue

            if "Oxford University Press" in line:
                continue
            if "The Oxford 5000" in line:
                continue
            if "American English" in line:
                continue
            if "©" in line:
                continue

            m = re.match(
                r"^([A-Za-z][A-Za-z\- ]+?)\s+(n\.|v\.|adj\.|adv\.|prep\.|conj\.|det\.|pron\.|modal v\.|exclam\.|n\., v\.|v\., n\.|adj\./adv\.)\s*(B2|C1)?$",
                line
            )

            if not m:
                continue

            word = m.group(1).strip().lower()
            level = m.group(3) or current_level

            if level not in VALID_LEVELS:
                continue

            if len(word) > 40:
                continue

            if word not in seen:
                seen.add(word)
                entries.append((word, level))

    return entries

def main():
    print("Starting Oxford5000 conversion...")

    if not PDF_PATH.exists():
        print("PDF not found!")
        print(f"Expected path: {PDF_PATH}")
        return

    entries = extract_entries(PDF_PATH)

    print(f"Extracted {len(entries)} Oxford5000 entries")

    with OUT_PATH.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["word", "level", "status", "mastery", "last_seen", "scene", "source"])

        for word, level in entries:
            writer.writerow([word, level, "new", 0, "", "", "Oxford5000"])

    print(f"Saved to: {OUT_PATH}")

if __name__ == "__main__":
    main()