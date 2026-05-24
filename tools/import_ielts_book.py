from pathlib import Path
import zipfile
import re
import csv
from html.parser import HTMLParser

BASE = Path(__file__).resolve().parents[1]

EPUB_PATH = BASE / "source_books" / "ielts_100_sentences.epub"
OUT_DIR = BASE / "book_missions"
VOCAB_DIR = BASE / "vocabulary"

OUT_DIR.mkdir(exist_ok=True)
VOCAB_DIR.mkdir(exist_ok=True)

BOOK_CHUNKS_PATH = VOCAB_DIR / "book_chunks.csv"


class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []

    def handle_data(self, data):
        text = data.strip()
        if text:
            self.parts.append(text)

    def get_text(self):
        return "\n".join(self.parts)


def clean_text(text):
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def html_to_text(raw):
    parser = TextExtractor()
    parser.feed(raw)
    return clean_text(parser.get_text())


def guess_theme(text):
    lower = text.lower()

    if any(w in lower for w in ["environment", "pollution", "climate", "waste"]):
        return "environmental_crisis"
    if any(w in lower for w in ["technology", "computer", "internet", "data"]):
        return "technology_risk"
    if any(w in lower for w in ["education", "student", "school", "university"]):
        return "education_policy"
    if any(w in lower for w in ["health", "medical", "disease", "patient"]):
        return "health_risk"
    if any(w in lower for w in ["government", "law", "policy", "society"]):
        return "public_policy"
    if any(w in lower for w in ["business", "company", "economic", "market"]):
        return "corporate_crisis"

    return "general_issue"


def make_training_mission(idx, title, text):
    theme = guess_theme(text)

    mission = f"""# IELTS Sentence Mission {idx:03d}

## Source

Book:
100个句子记完7000个雅思单词

Source Unit:
{title}

## Theme

{theme}

## Learning Goal

Turn the source sentence vocabulary into usable chunks through a Biohazard-style crisis mission.

## Important Note

Do not memorize isolated words.
Use chunks in a realistic situation.

## Source Digest

This unit should be processed into:
- key vocabulary
- useful chunks
- sentence frames
- character mission
- final speaking/writing task

## Biohazard Corporate Scenario

Auria Dynamics is facing a new crisis related to:

{theme}

Ada Wong needs a clear decision.
Rebecca Chambers needs technical clarity.
Grace Ashcroft needs evidence and logic.
Rose Winters needs client trust to be protected.

## Your Mission

Explain the situation in English and propose an action plan.

## Training Structure

1. Understand the source sentence.
2. Extract 5 to 8 useful chunks.
3. Use the chunks in a role-play crisis.
4. Receive correction.
5. Save strong chunks into `vocabulary/book_chunks.csv`.

## Raw Extract Preview

{text[:900]}
"""

    return mission


def extract_epub_texts():
    if not EPUB_PATH.exists():
        raise FileNotFoundError(f"EPUB not found: {EPUB_PATH}")

    items = []

    with zipfile.ZipFile(EPUB_PATH, "r") as z:
        html_files = [
            name for name in z.namelist()
            if name.lower().endswith((".xhtml", ".html", ".htm"))
            and "Text/" in name
        ]

        html_files.sort()

        for name in html_files:
            raw = z.read(name).decode("utf-8", errors="ignore")
            text = html_to_text(raw)

            if len(text) < 100:
                continue

            # Skip cover / copyright / table-of-contents-like files when possible
            if "版权" in text[:300] or "目录" in text[:300]:
                continue

            items.append((name, text))

    return items


def main():
    items = extract_epub_texts()

    print(f"Extracted text units: {len(items)}")

    useful_items = []
    for name, text in items:
        if len(text) > 300:
            useful_items.append((name, text))

    print(f"Useful units: {len(useful_items)}")

    for idx, (name, text) in enumerate(useful_items[:100], start=1):
        md = make_training_mission(idx, name, text)
        out_path = OUT_DIR / f"sentence_{idx:03d}.md"
        out_path.write_text(md, encoding="utf-8")

    if not BOOK_CHUNKS_PATH.exists():
        with BOOK_CHUNKS_PATH.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["source_id", "word", "chunk", "meaning", "theme", "status", "mastery"])

    print("Created:")
    print("book_missions/sentence_001.md ...")
    print("vocabulary/book_chunks.csv")
    print()
    print("Next step:")
    print("Open one sentence mission, send it to ChatGPT, and convert it into chunks + role-play mission.")


if __name__ == "__main__":
    main()