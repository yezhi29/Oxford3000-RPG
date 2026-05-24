
import csv
import json
import random
from datetime import datetime
from pathlib import Path
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

BASE = Path(__file__).resolve().parent
VOCAB = BASE / "vocabulary"
STORY = BASE / "story"

CHUNKS_PATH = VOCAB / "chunks.csv"
SCENARIOS_PATH = STORY / "scenarios.csv"
LOG_PATH = STORY / "practice_logs.jsonl"


def read_csv(path):
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_chunks(rows):
    fieldnames = ["word", "chunk", "meaning", "scene", "status", "mastery"]
    with CHUNKS_PATH.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def normalize(text):
    return text.lower().strip()


def choose_mission():
    scenarios = read_csv(SCENARIOS_PATH)
    chunks = read_csv(CHUNKS_PATH)

    if not scenarios:
        return {
            "error": "No scenarios found. Please check story/scenarios.csv"
        }

    scenario = random.choice(scenarios)

    raw_targets = [
        item.strip()
        for item in scenario.get("target_chunks", "").split(";")
        if item.strip()
    ]

    chunk_map = {row.get("chunk", ""): row for row in chunks}

    targets = []
    for chunk in raw_targets:
        row = chunk_map.get(chunk)
        if row:
            targets.append({
                "chunk": chunk,
                "word": row.get("word", ""),
                "meaning": row.get("meaning", ""),
                "mastery": int(row.get("mastery", "0") or 0),
                "status": row.get("status", "new")
            })
        else:
            targets.append({
                "chunk": chunk,
                "word": "",
                "meaning": "",
                "mastery": 0,
                "status": "new"
            })

    return {
        "scenario_id": scenario.get("scenario_id", ""),
        "scenario_name": scenario.get("scenario_name", ""),
        "main_character": scenario.get("main_character", ""),
        "support_character": scenario.get("support_character", ""),
        "scene_type": scenario.get("scene_type", ""),
        "pressure_level": scenario.get("pressure_level", ""),
        "mission": scenario.get("mission", ""),
        "targets": targets,
        "opening": build_opening(scenario)
    }


def build_opening(s):
    scene_type = s.get("scene_type", "")
    main = s.get("main_character", "Ada Wong")
    support = s.get("support_character", "Claire Redfield")

    if scene_type == "supplier_crisis":
        return [
            {"speaker": main, "line": "The supplier postponed the shipment again. If we fail to meet the deadline, the client may lose confidence."},
            {"speaker": support, "line": "I can follow up with the supplier, but we may also need to find an alternative supplier."}
        ]

    if scene_type == "quality_check":
        return [
            {"speaker": main, "line": "The alternative material may not match the project specifications."},
            {"speaker": support, "line": "If this becomes a technical issue, we need to explain the risk clearly."}
        ]

    if scene_type == "client_escalation":
        return [
            {"speaker": main, "line": "The client is dissatisfied and they are asking for compensation."},
            {"speaker": support, "line": "We need a recovery plan that can restore client confidence."}
        ]

    if scene_type == "negotiation":
        return [
            {"speaker": main, "line": "The negotiation is under pressure. The client may reject our first proposal."},
            {"speaker": support, "line": "We need to reach a compromise without causing further delay."}
        ]

    return [
        {"speaker": main, "line": s.get("mission", "We have a new issue. What is your action plan?")},
        {"speaker": support, "line": "Use the target chunks and give us a clear response."}
    ]


def update_mastery(used_chunks, missing_chunks):
    rows = read_csv(CHUNKS_PATH)
    used_set = set(used_chunks)
    missing_set = set(missing_chunks)

    for row in rows:
        chunk = row.get("chunk", "")
        mastery = int(row.get("mastery", "0") or 0)

        if chunk in used_set:
            mastery += 10
        elif chunk in missing_set:
            mastery -= 4

        mastery = max(0, min(100, mastery))
        row["mastery"] = str(mastery)

        if mastery >= 80:
            row["status"] = "strong"
        elif mastery >= 40:
            row["status"] = "review"
        else:
            row["status"] = "weak"

    write_chunks(rows)


def save_log(data):
    LOG_PATH.parent.mkdir(exist_ok=True)

    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False) + "\n")


class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/api/mission":
            self.send_json(choose_mission())
            return

        return super().do_GET()

    def do_POST(self):
        if self.path == "/api/submit":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length).decode("utf-8")
            data = json.loads(body)

            response = data.get("response", "")
            targets = data.get("targets", [])
            target_chunks = [t["chunk"] for t in targets]

            lower_response = normalize(response)

            used = [
                chunk for chunk in target_chunks
                if normalize(chunk) in lower_response
            ]

            missing = [
                chunk for chunk in target_chunks
                if chunk not in used
            ]

            score = round((len(used) / len(target_chunks)) * 100) if target_chunks else 0

            update_mastery(used, missing)

            log = {
                "time": datetime.now().isoformat(timespec="seconds"),
                "scenario": data.get("scenario", {}),
                "targets": target_chunks,
                "response": response,
                "used": used,
                "missing": missing,
                "score": score
            }

            save_log(log)

            self.send_json({
                "score": score,
                "used": used,
                "missing": missing,
                "saved": True,
                "message": "Practice saved. Mastery updated."
            })
            return

        self.send_error(404)

    def send_json(self, data):
        content = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)


if __name__ == "__main__":
    print("Oxford3000 Chunk RPG Trainer is running.")
    print("Open this URL:")
    print("http://127.0.0.1:8000")
    server = ThreadingHTTPServer(("127.0.0.1", 8000), Handler)
    server.serve_forever()
