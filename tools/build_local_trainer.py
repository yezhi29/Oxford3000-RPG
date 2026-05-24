from pathlib import Path

BASE = Path(__file__).resolve().parents[1]

APP = BASE / "app.py"
INDEX = BASE / "index.html"
STORY = BASE / "story"
VOCAB = BASE / "vocabulary"

STORY.mkdir(exist_ok=True)
VOCAB.mkdir(exist_ok=True)

app_code = r'''
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
'''

index_code = r'''
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Oxford3000 Chunk RPG Trainer</title>

<style>
body{
    background:#0f1016;
    color:white;
    font-family:Arial, sans-serif;
    padding:30px;
}

.title{
    font-size:42px;
    color:#ff4d6d;
    margin-bottom:8px;
}

.subtitle{
    color:#aaa;
    margin-bottom:25px;
}

.panel{
    background:#1d1d25;
    border:1px solid #444;
    border-radius:16px;
    padding:22px;
    margin-top:18px;
}

.character{
    color:#ff4d6d;
    font-size:28px;
    font-weight:bold;
}

.support{
    color:#00d4ff;
    font-size:22px;
    font-weight:bold;
}

.chunk{
    color:#00ff99;
    font-weight:bold;
}

.warning{
    color:#ffcc00;
    font-weight:bold;
}

.danger{
    color:#ff6666;
    font-weight:bold;
}

button{
    margin-top:12px;
    margin-right:10px;
    padding:14px 25px;
    background:#ff4d6d;
    border:none;
    border-radius:10px;
    color:white;
    font-size:17px;
    cursor:pointer;
}

button:hover{
    background:#ff6b81;
}

textarea{
    width:100%;
    height:140px;
    margin-top:20px;
    background:#15151c;
    color:white;
    border:1px solid #666;
    border-radius:12px;
    padding:15px;
    font-size:18px;
}

.message{
    background:#15151c;
    border:1px solid #444;
    border-radius:12px;
    padding:18px;
    margin-top:18px;
}

.you{
    color:#00d4ff;
    font-weight:bold;
}

.ai{
    color:#ff4d6d;
    font-weight:bold;
}

.small{
    color:#aaa;
    font-size:14px;
}

.grid{
    display:grid;
    grid-template-columns: 1fr 1fr;
    gap:18px;
}

@media(max-width:900px){
    .grid{
        grid-template-columns:1fr;
    }
}
</style>
</head>

<body>

<div class="title">Oxford3000 Chunk RPG Trainer</div>
<div class="subtitle">不是记笔记。现在开始：场景任务 → 角色压力 → chunk 输出 → 自动记录 → 自动更新 mastery。</div>

<button onclick="loadMission()">New Mission</button>

<div class="grid">
    <div class="panel">
        <div class="character" id="characters">No mission loaded</div>
        <p><b>Scenario:</b> <span id="scenario">-</span></p>
        <p><b>Pressure:</b> <span id="pressure">-</span></p>
        <p><b>Mission:</b> <span id="mission">Click New Mission.</span></p>
    </div>

    <div class="panel">
        <div class="support">Target Chunks</div>
        <ul id="targets">
            <li>No targets yet.</li>
        </ul>
    </div>
</div>

<div class="panel">
    <div class="support">Scene Dialogue</div>
    <div id="dialogue">
        Click New Mission to start.
    </div>
</div>

<textarea id="playerInput" placeholder="Use the target chunks to respond. Do not write freely. Solve the scene."></textarea>

<button onclick="submitResponse()">Send Response & Save</button>

<div id="result"></div>

<script>
let currentMission = null;

async function loadMission(){
    const res = await fetch("/api/mission");
    currentMission = await res.json();

    if(currentMission.error){
        alert(currentMission.error);
        return;
    }

    document.getElementById("characters").innerText =
        currentMission.main_character + " + " + currentMission.support_character;

    document.getElementById("scenario").innerText =
        currentMission.scenario_name;

    document.getElementById("pressure").innerText =
        currentMission.pressure_level;

    document.getElementById("mission").innerText =
        currentMission.mission;

    document.getElementById("targets").innerHTML =
        currentMission.targets.map(t => `
            <li>
                <span class="chunk">${t.chunk}</span>
                <span class="small"> — ${t.meaning || "no meaning yet"} | mastery: ${t.mastery}</span>
            </li>
        `).join("");

    document.getElementById("dialogue").innerHTML =
        currentMission.opening.map(item => `
            <p><b class="ai">${item.speaker}:</b> ${item.line}</p>
        `).join("");

    document.getElementById("result").innerHTML = "";
    document.getElementById("playerInput").value = "";
}

async function submitResponse(){
    if(!currentMission){
        alert("Load a mission first.");
        return;
    }

    const response = document.getElementById("playerInput").value.trim();

    if(!response){
        alert("Write your response first.");
        return;
    }

    const res = await fetch("/api/submit", {
        method:"POST",
        headers:{
            "Content-Type":"application/json"
        },
        body: JSON.stringify({
            response,
            targets: currentMission.targets,
            scenario: {
                id: currentMission.scenario_id,
                name: currentMission.scenario_name,
                main_character: currentMission.main_character,
                support_character: currentMission.support_character,
                pressure_level: currentMission.pressure_level,
                mission: currentMission.mission
            }
        })
    });

    const data = await res.json();

    document.getElementById("result").innerHTML += `
        <div class="message">
            <div class="you">You</div>
            <p>${response}</p>

            <div class="ai">${currentMission.main_character}</div>
            <p>
                Controlled output score:
                <span class="chunk">${data.score}%</span>
            </p>

            <p><b class="chunk">Used chunks:</b> ${data.used.length ? data.used.join(", ") : "None"}</p>
            <p><b class="warning">Missing chunks:</b> ${data.missing.length ? data.missing.join(", ") : "None"}</p>

            <p class="small">
                Saved to story/practice_logs.jsonl. Mastery updated in vocabulary/chunks.csv.
            </p>
        </div>
    `;

    document.getElementById("playerInput").value = "";
}

loadMission();
</script>

</body>
</html>
'''

APP.write_text(app_code, encoding="utf-8")
INDEX.write_text(index_code, encoding="utf-8")

print("Local trainer created.")
print("Created/updated: app.py")
print("Created/updated: index.html")
print("Next:")
print("python app.py")
print("Open: http://127.0.0.1:8000")