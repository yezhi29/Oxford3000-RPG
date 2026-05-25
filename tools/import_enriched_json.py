import csv
import json
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
VOCAB_FILE = BASE_DIR / "vocabulary" / "oxford5000_extra.csv"

FIELDNAMES = [
    "word", "level", "status", "mastery", "last_seen", "scene", "source",
    "meaning_cn", "example", "collocations", "scene_text"
]


def read_vocab():
    with open(VOCAB_FILE, "r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_vocab(rows):
    with open(VOCAB_FILE, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def main():
    if len(sys.argv) < 2:
        print("用法：python tools/import_enriched_json.py batches/batch_001_enriched.json")
        return

    path = Path(sys.argv[1])
    if not path.exists():
        print(f"找不到文件：{path}")
        return

    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict) and "items" in data:
        data = data["items"]

    if not isinstance(data, list):
        print("JSON 必须是数组，或包含 items 数组。")
        return

    rows = read_vocab()
    by_word = {r["word"]: r for r in rows}

    updated = 0
    for item in data:
        word = item.get("word")
        if not word or word not in by_word:
            continue
        row = by_word[word]
        for key in ["meaning_cn", "example", "collocations", "scene_text"]:
            if item.get(key):
                row[key] = item[key]
        updated += 1

    write_vocab(rows)
    print(f"已导入 {updated} 条增强卡片内容。")


if __name__ == "__main__":
    main()
