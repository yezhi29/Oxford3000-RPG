import csv
import json
import sys
from pathlib import Path
from datetime import date, timedelta

BASE_DIR = Path(__file__).resolve().parents[1]

VOCAB_FILE = BASE_DIR / "vocabulary" / "oxford5000_extra.csv"
REVIEW_FILE = BASE_DIR / "story" / "review_queue.jsonl"
MISSION_LOG = BASE_DIR / "story" / "practice_logs.jsonl"
TODAY_MISSION_FILE = BASE_DIR / "story" / "today_mission.json"

ROLES = ["Ada", "Claire", "Jill", "Sherry", "Rose", "Grace", "Rebecca", "Ashley"]

ROLE_CN = {
    "Ada": "艾达",
    "Claire": "克莱尔",
    "Jill": "吉尔",
    "Sherry": "雪莉",
    "Rose": "萝丝",
    "Grace": "格蕾丝",
    "Rebecca": "瑞贝卡",
    "Ashley": "阿什利",
}

ROLE_TASKS = {
    "Ada": "商务谈判 / 危机判断",
    "Claire": "情绪支持 / 人际安抚",
    "Jill": "行动执行 / 安全控制",
    "Sherry": "逻辑分析 / 线索复盘",
    "Rose": "心理记忆 / 深层概念",
    "Grace": "高级表达 / 正式写作",
    "Rebecca": "科学医学 / 生化机制",
    "Ashley": "生活口语 / 情绪反应",
}

FIELDNAMES = [
    "word", "level", "status", "mastery", "last_seen", "scene", "source",
    "meaning_cn", "example", "collocations", "scene_text"
]


def read_vocab():
    if not VOCAB_FILE.exists():
        print(f"找不到词库文件：{VOCAB_FILE}")
        sys.exit(1)
    with open(VOCAB_FILE, "r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_vocab(rows):
    VOCAB_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(VOCAB_FILE, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def read_jsonl(path):
    if not path.exists():
        return []
    items = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                items.append(json.loads(line))
    return items


def append_jsonl(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")


def write_jsonl(path, items):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for item in items:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")


def normalize():
    rows = read_vocab()
    fixed = []
    for i, row in enumerate(rows):
        scene = row.get("scene", "").strip()
        if scene not in ROLES:
            scene = ROLES[i % len(ROLES)]
        fixed.append({
            "word": row.get("word", "").strip(),
            "level": row.get("level", "").strip(),
            "status": row.get("status", "new").strip() or "new",
            "mastery": row.get("mastery", "0").strip() or "0",
            "last_seen": row.get("last_seen", "").strip(),
            "scene": scene,
            "source": row.get("source", "Oxford5000").strip() or "Oxford5000",
            "meaning_cn": row.get("meaning_cn", "").strip(),
            "example": row.get("example", "").strip(),
            "collocations": row.get("collocations", "").strip(),
            "scene_text": row.get("scene_text", "").strip(),
        })
    write_vocab(fixed)
    print("词库检查完成。")
    print(f"词库文件：{VOCAB_FILE}")
    print(f"总词条：{len(fixed)}")


def build_today_mission_file(mission_id, selected, today):
    cards = []
    for i, row in enumerate(selected):
        role = row.get("scene") or ROLES[i % len(ROLES)]
        if role not in ROLES:
            role = ROLES[i % len(ROLES)]
        cards.append({
            "role": role,
            "role_cn": ROLE_CN[role],
            "role_task": ROLE_TASKS[role],
            "word": row["word"],
            "level": row.get("level", ""),
            "status": row.get("status", "learning"),
            "mastery": int(row.get("mastery", "1") or 1),
            "source": row.get("source", "Oxford5000"),
            "meaning_cn": row.get("meaning_cn", ""),
            "example": row.get("example", ""),
            "collocations": row.get("collocations", ""),
            "scene_text": row.get("scene_text", "")
        })

    data = {
        "date": today,
        "mission_id": mission_id,
        "title": "今日 8 人角色词汇任务",
        "task": "请用至少 5 个今日词汇写一段英文剧情。先不用追求完美，重点是把词用出来。",
        "cards": cards
    }

    TODAY_MISSION_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(TODAY_MISSION_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def start_new_mission():
    rows = read_vocab()
    today = str(date.today())
    new_rows = [row for row in rows if row.get("status") == "new"]

    if len(new_rows) < 8:
        print("新词不足 8 个。请先复习，或者导入更多词。")
        return

    selected = new_rows[:8]
    mission_id = f"mission_{date.today().strftime('%Y%m%d')}_{len(read_jsonl(MISSION_LOG)) + 1:03d}"
    selected_words = []

    for i, selected_row in enumerate(selected):
        role = ROLES[i]
        word = selected_row["word"]
        selected_words.append(word)
        for row in rows:
            if row["word"] == word:
                row["scene"] = role
                row["status"] = "learning"
                row["mastery"] = "1"
                row["last_seen"] = today

    write_vocab(rows)

    selected_after_update = []
    word_set = set(selected_words)
    for row in rows:
        if row["word"] in word_set:
            selected_after_update.append(row)
    selected_after_update.sort(key=lambda r: selected_words.index(r["word"]))

    for i, row in enumerate(selected_after_update):
        role = ROLES[i]
        append_jsonl(REVIEW_FILE, {
            "word": row["word"],
            "level": row.get("level", ""),
            "scene": role,
            "stage": 1,
            "next_review": str(date.today() + timedelta(days=1)),
            "wrong_count": 0
        })

    append_jsonl(MISSION_LOG, {
        "date": today,
        "mission_id": mission_id,
        "type": "new_mission",
        "words": selected_words,
        "done": False
    })

    build_today_mission_file(mission_id, selected_after_update, today)

    print("\n==============================")
    print("今日新任务")
    print("==============================")
    print(f"任务编号：{mission_id}\n")
    for i, row in enumerate(selected_after_update):
        role = ROLES[i]
        print(f"{ROLE_CN[role]} {role}: {row['word']} / {row.get('level', '')}")

    print("\n网页数据已生成：story/today_mission.json")
    print("\n复制下面这段给 ChatGPT：")
    print("--------------------------------")
    print("请根据下面 8 个词，生成 8 张角色词汇卡片，并设计一个剧情任务。")
    print("要求：一个角色一个词，不要编号，不要重复；每张卡包含英文词、中文核心意思、例句、搭配、角色场景。\n")
    for i, row in enumerate(selected_after_update):
        role = ROLES[i]
        print(f"{ROLE_CN[role]} {role}: {row['word']} / {row.get('level', '')}")
    print("--------------------------------")


def review_today():
    rows = read_vocab()
    queue = read_jsonl(REVIEW_FILE)
    today = str(date.today())
    due_items = [item for item in queue if item.get("next_review", "") <= today]

    if not due_items:
        print("今天没有到期复习。")
        print("你可以运行：python tools/vocab_trainer.py new")
        return

    vocab_map = {row["word"]: row for row in rows}
    print("\n==============================")
    print("今日复习")
    print("==============================\n")

    for item in due_items:
        word = item["word"]
        row = vocab_map.get(word)
        if not row:
            continue
        role = item.get("scene", row.get("scene", ""))
        stage = int(item.get("stage", 1))

        print(f"{ROLE_CN.get(role, role)} {role}: {word} / {row.get('level', '')}")
        if row.get("meaning_cn"):
            print(f"中文：{row.get('meaning_cn')}")
        if stage == 1:
            print("复习形式：回忆中文意思 + 自己造句")
            print(f"请回忆这个词的意思：{word}")
        elif stage == 2:
            first = word[0]
            blanks = "_" * (len(word) - 1)
            print("复习形式：首字母填空")
            print(f"{first}{blanks}")
        elif stage == 3:
            print("复习形式：英文造句")
            print(f"请用 {word} 写一个英文句子。")
        elif stage == 4:
            print("复习形式：角色台词")
            print(f"请扮演 {ROLE_CN.get(role, role)}，用 {word} 说一句剧情台词。")
        else:
            print("复习形式：最终输出")
            print(f"请用 {word} 写一个和项目、危机或生化剧情有关的句子。")
        print("--------------------------------")

    print("\n复习完成后：")
    print("会了就运行：python tools/vocab_trainer.py pass")
    print("不会就运行：python tools/vocab_trainer.py fail")


def pass_review():
    rows = read_vocab()
    queue = read_jsonl(REVIEW_FILE)
    today = date.today()
    today_str = str(today)
    new_queue = []

    for item in queue:
        if item.get("next_review", "") <= today_str:
            word = item["word"]
            old_stage = int(item.get("stage", 1))
            new_stage = old_stage + 1
            delay = {2: 2, 3: 4, 4: 7, 5: 14}.get(new_stage, 30)

            for row in rows:
                if row["word"] == word:
                    old_mastery = int(row.get("mastery", "0") or "0")
                    new_mastery = min(old_mastery + 1, 5)
                    row["mastery"] = str(new_mastery)
                    row["last_seen"] = today_str
                    row["status"] = "mastered" if new_mastery >= 5 else "review"

            if new_stage <= 5:
                item["stage"] = new_stage
                item["next_review"] = str(today + timedelta(days=delay))
                new_queue.append(item)
        else:
            new_queue.append(item)

    write_vocab(rows)
    write_jsonl(REVIEW_FILE, new_queue)
    print("已通过今日复习。掌握度 +1，下一次复习时间已更新。")


def fail_review():
    rows = read_vocab()
    queue = read_jsonl(REVIEW_FILE)
    today = date.today()
    today_str = str(today)

    for item in queue:
        if item.get("next_review", "") <= today_str:
            word = item["word"]
            item["stage"] = 1
            item["next_review"] = str(today + timedelta(days=1))
            item["wrong_count"] = int(item.get("wrong_count", 0)) + 1
            for row in rows:
                if row["word"] == word:
                    old_mastery = int(row.get("mastery", "0") or "0")
                    row["mastery"] = str(max(old_mastery - 1, 0))
                    row["status"] = "review"
                    row["last_seen"] = today_str

    write_vocab(rows)
    write_jsonl(REVIEW_FILE, queue)
    print("已记录为复习失败。掌握度 -1，明天继续复习。")


def show_status():
    rows = read_vocab()
    total = len(rows)
    new_count = len([r for r in rows if r.get("status") == "new"])
    learning_count = len([r for r in rows if r.get("status") == "learning"])
    review_count = len([r for r in rows if r.get("status") == "review"])
    mastered_count = len([r for r in rows if r.get("status") == "mastered"])
    enriched_count = len([r for r in rows if r.get("meaning_cn") and r.get("example")])

    print("\n==============================")
    print("学习状态")
    print("==============================")
    print(f"词库文件：{VOCAB_FILE}")
    print(f"总词数：{total}")
    print(f"未学习：{new_count}")
    print(f"学习中：{learning_count}")
    print(f"待复习：{review_count}")
    print(f"已掌握：{mastered_count}")
    print(f"已补充卡片内容：{enriched_count}")


def help_text():
    print("""
用法：

检查词库：
python tools/vocab_trainer.py init

开始新任务：
python tools/vocab_trainer.py new

今日复习：
python tools/vocab_trainer.py review

复习通过：
python tools/vocab_trainer.py pass

复习失败：
python tools/vocab_trainer.py fail

查看状态：
python tools/vocab_trainer.py status
""")


def main():
    if len(sys.argv) < 2:
        help_text()
        return

    cmd = sys.argv[1]
    if cmd == "init":
        normalize()
    elif cmd == "new":
        start_new_mission()
    elif cmd == "review":
        review_today()
    elif cmd == "pass":
        pass_review()
    elif cmd == "fail":
        fail_review()
    elif cmd == "status":
        show_status()
    else:
        help_text()


if __name__ == "__main__":
    main()
