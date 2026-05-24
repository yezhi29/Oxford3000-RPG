from pathlib import Path
from datetime import datetime

BASE = Path(__file__).resolve().parents[1]
BACKUP_DIR = BASE / "backup"
BACKUP_DIR.mkdir(exist_ok=True)

index_path = BASE / "index.html"

if index_path.exists():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = BACKUP_DIR / f"index_before_modes_{timestamp}.html"
    backup_path.write_text(index_path.read_text(encoding="utf-8"), encoding="utf-8")

html = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Oxford3000 / 5000 Chunk RPG</title>

<style>
body{
    background:#101014;
    color:white;
    font-family:Arial, sans-serif;
    padding:30px;
}

.title{
    font-size:42px;
    color:#ff4d6d;
    margin-bottom:10px;
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
    margin-top:20px;
}

.character{
    color:#ff4d6d;
    font-size:26px;
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

button{
    margin-top:10px;
    margin-right:10px;
    padding:13px 22px;
    background:#ff4d6d;
    border:none;
    border-radius:10px;
    color:white;
    font-size:16px;
    cursor:pointer;
}

button:hover{
    background:#ff6b81;
}

textarea{
    width:100%;
    height:130px;
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

.ada{
    color:#ff4d6d;
    font-weight:bold;
}

.small{
    color:#aaa;
    font-size:14px;
}
</style>
</head>

<body>

<div class="title">Oxford3000 / 5000 Chunk RPG</div>
<div class="subtitle">角色 + 世界观 + 场景任务 + Oxford 高频词 / 高级词 / chunks 输出训练</div>

<div class="panel">
    <div class="support">Training Mode</div>
    <button onclick="loadWordMode('vocabulary/oxford3000.csv', 'Oxford3000 Basic Mode')">Oxford3000 Basic</button>
    <button onclick="loadWordMode('vocabulary/oxford5000_extra.csv', 'Oxford5000 Advanced Mode')">Oxford5000 Advanced</button>
    <button onclick="loadChunkMission()">Chunk Mission Mode</button>
</div>

<div class="panel">
    <div class="character" id="modeTitle">Choose a training mode</div>
    <p><b>Scenario:</b> <span id="scenarioName">Not loaded yet</span></p>
    <p><b>Pressure Level:</b> <span id="pressureLevel">-</span></p>
    <p><b>Mission:</b> <span id="missionText">Choose a mode to start training.</span></p>
</div>

<div class="panel">
    <div class="support" id="targetTitle">Today's Targets</div>
    <ul id="targetList">
        <li>No targets loaded yet.</li>
    </ul>
</div>

<div class="panel">
    <div class="character" id="speakerName">Ada Wong</div>
    <p id="openingLine">
        Select a mode above. Then answer using the target words or chunks.
    </p>
</div>

<textarea id="playerInput" placeholder="Use today's targets to answer the character..."></textarea>

<button onclick="sendResponse()">Send Response</button>
<button onclick="refreshCurrentMode()">New Round</button>

<div id="chatLog"></div>

<script>
let currentTargets = [];
let currentMode = "none";
let currentCSVPath = "";
let currentScenario = null;

function parseCSVLine(line){
    const result = [];
    let current = "";
    let insideQuotes = false;

    for(let i = 0; i < line.length; i++){
        const char = line[i];

        if(char === '"'){
            insideQuotes = !insideQuotes;
        } else if(char === "," && !insideQuotes){
            result.push(current);
            current = "";
        } else {
            current += char;
        }
    }

    result.push(current);
    return result;
}

async function loadWordMode(csvPath, modeName){
    currentMode = "word";
    currentCSVPath = csvPath;

    const response = await fetch(csvPath);
    const text = await response.text();
    const lines = text.trim().split("\n").slice(1);

    const words = lines
        .map(line => line.split(",")[0])
        .filter(word => word && word.length > 2);

    currentTargets = words
        .sort(() => Math.random() - 0.5)
        .slice(0, 6);

    document.getElementById("modeTitle").innerText = modeName;
    document.getElementById("scenarioName").innerText = "Controlled Output Drill";
    document.getElementById("pressureLevel").innerText = modeName.includes("5000") ? "high" : "medium";
    document.getElementById("missionText").innerText =
        "Use at least 4 target words in a business crisis response.";

    document.getElementById("targetTitle").innerText = "Today's Target Words";
    document.getElementById("targetList").innerHTML =
        currentTargets.map(w => `<li><span class="chunk">${w}</span></li>`).join("");

    document.getElementById("speakerName").innerText = "Ada Wong";
    document.getElementById("openingLine").innerText =
        "The project situation is unstable. I need a clear response using today's target words. What is your action plan?";

    document.getElementById("chatLog").innerHTML = "";
}

async function loadChunkMission(){
    currentMode = "chunk";

    const response = await fetch("story/scenarios.csv");
    const text = await response.text();
    const lines = text.trim().split("\n").slice(1);

    const scenarios = lines.map(line => {
        const cols = parseCSVLine(line);
        return {
            id: cols[0],
            name: cols[1],
            main: cols[2],
            support: cols[3],
            type: cols[4],
            pressure: cols[5],
            chunks: cols[6].split(";"),
            mission: cols[7]
        };
    });

    currentScenario = scenarios[Math.floor(Math.random() * scenarios.length)];
    currentTargets = currentScenario.chunks;

    document.getElementById("modeTitle").innerText =
        currentScenario.main + " + " + currentScenario.support;

    document.getElementById("scenarioName").innerText = currentScenario.name;
    document.getElementById("pressureLevel").innerText = currentScenario.pressure;
    document.getElementById("missionText").innerText = currentScenario.mission;

    document.getElementById("targetTitle").innerText = "Today's Target Chunks";
    document.getElementById("targetList").innerHTML =
        currentTargets.map(c => `<li><span class="chunk">${c}</span></li>`).join("");

    document.getElementById("speakerName").innerText = currentScenario.main;
    document.getElementById("openingLine").innerText = generateOpeningLine(currentScenario);

    document.getElementById("chatLog").innerHTML = "";
}

function generateOpeningLine(s){
    if(s.type === "supplier_crisis"){
        return "The supplier postponed the shipment again. We need to meet the deadline. What is your action plan?";
    }

    if(s.type === "client_escalation"){
        return "The client is dissatisfied. They want compensation and a recovery plan. How do you respond?";
    }

    if(s.type === "shipping_crisis"){
        return "The client will only accept urgent shipment. We must guarantee there will be no further delay. What should we do?";
    }

    if(s.type === "internal_approval"){
        return "Management wants a clear reason before they approve the extra cost. How do you ask for approval?";
    }

    if(s.type === "quality_check"){
        return "Rebecca found a possible technical issue. We need to verify the material specifications. How do you explain the risk?";
    }

    if(s.type === "negotiation"){
        return "The negotiation is under pressure. We need to reach a compromise. What is your proposal?";
    }

    return s.mission;
}

function sendResponse(){
    const response = document.getElementById("playerInput").value.trim();

    if(!response){
        alert("Write your response first.");
        return;
    }

    const lower = response.toLowerCase();

    const used = currentTargets.filter(target =>
        lower.includes(target.toLowerCase())
    );

    const missing = currentTargets.filter(target =>
        !lower.includes(target.toLowerCase())
    );

    const score = currentTargets.length
        ? Math.round((used.length / currentTargets.length) * 100)
        : 0;

    document.getElementById("chatLog").innerHTML += `
        <div class="message">
            <div class="you">You</div>
            <p>${response}</p>

            <div class="ada">${document.getElementById("speakerName").innerText}</div>
            <p>
                Your controlled output score is <span class="chunk">${score}%</span>.
                ${score >= 80 ? "Strong output. Continue the mission." : "Good attempt, but include more targets."}
            </p>

            <p><b class="chunk">Used:</b> ${used.length ? used.join(", ") : "None"}</p>
            <p><b class="warning">Missing:</b> ${missing.length ? missing.join(", ") : "None"}</p>

            <p class="small">
                Training rule: do not write freely. Use the targets under pressure until they become automatic.
            </p>
        </div>
    `;

    document.getElementById("playerInput").value = "";
}

function refreshCurrentMode(){
    if(currentMode === "word"){
        loadWordMode(currentCSVPath, document.getElementById("modeTitle").innerText);
    } else if(currentMode === "chunk"){
        loadChunkMission();
    } else {
        alert("Choose a training mode first.");
    }
}
</script>

</body>
</html>
"""

index_path.write_text(html, encoding="utf-8")

print("Training modes updated.")
print("Updated: index.html")
print("Backup saved in backup/ if old index.html existed.")