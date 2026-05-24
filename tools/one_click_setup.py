from pathlib import Path
from datetime import datetime

BASE = Path(__file__).resolve().parents[1]

VOCAB_DIR = BASE / "vocabulary"
STORY_DIR = BASE / "story"
BACKUP_DIR = BASE / "backup"

VOCAB_DIR.mkdir(exist_ok=True)
STORY_DIR.mkdir(exist_ok=True)
BACKUP_DIR.mkdir(exist_ok=True)

chunks_csv = """word,chunk,meaning,scene,status,mastery
approval,get approval,获得批准,project_management,new,0
approval,ask for approval,请求批准,project_management,new,0
approval,need approval from our supervisor,需要主管批准,project_management,new,0
approve,must be approved,必须被批准,project_management,new,0
confirmation,send confirmation to the supplier,给供应商发送确认,supplier_crisis,new,0
confirmation,wait for confirmation,等待确认,supplier_crisis,new,0
supplier,contact the supplier,联系供应商,supplier_crisis,new,0
supplier,follow up with the supplier,跟进供应商,supplier_crisis,new,0
shipment,arrange shipment,安排发货,shipping,new,0
shipment,postpone the shipment,推迟发货,shipping,new,0
shipment,urgent shipment,紧急发货,shipping,new,0
deadline,miss the deadline,错过截止日期,project_delay,new,0
deadline,meet the deadline,赶上截止日期,project_delay,new,0
deadline,before the deadline,截止日期之前,project_delay,new,0
compromise,reach a compromise,达成妥协,negotiation,new,0
compromise,as a compromise,作为妥协方案,negotiation,new,0
alternative,alternative plan,替代方案,project_management,new,0
alternative,find an alternative supplier,寻找替代供应商,supplier_crisis,new,0
negotiation,urgent negotiation,紧急谈判,negotiation,new,0
negotiation,the negotiation may lead to nothing,谈判可能没有结果,negotiation,new,0
responsibility,take responsibility for the delay,为延误承担责任,client_escalation,new,0
responsibility,the responsibility is not on our side,责任不在我们这边,client_escalation,new,0
pressure,deal with pressure,处理压力,team_management,new,0
pressure,under pressure,处于压力之下,team_management,new,0
compensation,offer compensation,提供补偿,client_escalation,new,0
compensation,as compensation,作为补偿,client_escalation,new,0
dissatisfied,be dissatisfied with the explanation,对解释不满意,client_escalation,new,0
recovery plan,create a recovery plan,制定恢复计划,client_escalation,new,0
recovery plan,detailed recovery plan,详细恢复计划,client_escalation,new,0
delay,avoid further delay,避免进一步延误,project_delay,new,0
delay,cause a delay,造成延误,project_delay,new,0
extension,accept a short extension,接受短期延期,negotiation,new,0
guarantee,guarantee there will be no further delay,保证不会再延误,negotiation,new,0
price,price increase,涨价,cost_control,new,0
cost,increase the cost,增加成本,cost_control,new,0
risk,reduce the risk,降低风险,risk_management,new,0
risk,high risk,高风险,risk_management,new,0
client,restore client confidence,恢复客户信心,client_escalation,new,0
confidence,lose confidence,失去信心,team_management,new,0
confidence,restore confidence,恢复信心,team_management,new,0
quality,quality control,质量控制,quality_check,new,0
inspection,run another inspection,再做一次检查,quality_check,new,0
specification,verify the material specifications,确认材料规格,quality_check,new,0
issue,technical issue,技术问题,quality_check,new,0
"""

scenarios_csv = """scenario_id,scenario_name,main_character,support_character,scene_type,pressure_level,target_chunks,mission
S001,Supplier Delay,Ada Wong,Claire Redfield,supplier_crisis,medium,"postpone the shipment;follow up with the supplier;send confirmation to the supplier;find an alternative supplier;meet the deadline","The supplier delayed the shipment. Explain the risk and propose an alternative plan."
S002,Client Escalation,Ada Wong,Jill Valentine,client_escalation,high,"create a recovery plan;offer compensation;take responsibility for the delay;avoid further delay;restore client confidence","The client is dissatisfied and asks for compensation. Prepare a recovery plan."
S003,Urgent Shipment,Jill Valentine,Claire Redfield,shipping_crisis,high,"arrange shipment;urgent shipment;meet the deadline;guarantee there will be no further delay","The client will only accept the order if urgent shipment is arranged today."
S004,Management Approval,Ada Wong,Rose Winters,internal_approval,medium,"get approval;ask for approval;need approval from our supervisor;must be approved","The team needs management approval before accepting higher delivery costs."
S005,Technical Verification,Rebecca Chambers,Grace Ashcroft,quality_check,medium,"verify the material specifications;run another inspection;technical issue;quality control","The alternative material may not match the project specifications. Explain the risk."
S006,Negotiation Failure,Ada Wong,Grace Ashcroft,negotiation,high,"urgent negotiation;reach a compromise;the negotiation may lead to nothing;deal with pressure","The client rejects the first proposal. Try to reach a compromise."
S007,Factory Problem,Rebecca Chambers,Jill Valentine,factory_issue,high,"cause a delay;quality control;technical issue;avoid further delay","A factory problem may delay production. Report the issue and propose action."
S008,Team Pressure,Rose Winters,Claire Redfield,team_management,low,"under pressure;deal with pressure;restore confidence;lose confidence","The team is losing confidence. Explain how to keep communication stable."
S009,Price Increase,Ada Wong,Claire Redfield,cost_control,medium,"price increase;increase the cost;get approval;reach a compromise","The supplier asks for a 10 percent price increase. Decide whether to accept it."
S010,Deadline Crisis,Jill Valentine,Ada Wong,project_delay,high,"miss the deadline;meet the deadline;before the deadline;avoid further delay","The deadline is close. Make an action plan to protect the project."
"""

index_html = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Oxford3000 Chunk RPG</title>

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
    margin-bottom:30px;
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

button{
    margin-top:15px;
    margin-right:10px;
    padding:14px 26px;
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

<div class="title">Oxford3000 Chunk RPG</div>
<div class="subtitle">角色 + 世界观 + 场景任务 + Oxford3000 chunks 输出训练</div>

<div class="panel">
    <div class="character" id="mainCharacter">Loading character...</div>
    <p><b>Scenario:</b> <span id="scenarioName">Loading...</span></p>
    <p><b>Pressure Level:</b> <span id="pressureLevel">Loading...</span></p>
    <p><b>Mission:</b> <span id="missionText">Loading...</span></p>
</div>

<div class="panel">
    <div class="support">Today's Target Chunks</div>
    <ul id="chunkList">
        <li>Loading chunks...</li>
    </ul>
</div>

<div class="panel">
    <div class="character" id="speakerName">Ada Wong</div>
    <p id="openingLine">
        Loading scene...
    </p>
</div>

<textarea id="playerInput" placeholder="Use today's target chunks to answer the character..."></textarea>

<button onclick="sendResponse()">Send Response</button>
<button onclick="newMission()">New Mission</button>

<div id="chatLog"></div>

<script>
let currentScenario = null;
let targetChunks = [];

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

async function loadScenarios(){
    const response = await fetch("story/scenarios.csv");
    const text = await response.text();
    const lines = text.trim().split("\n").slice(1);

    return lines.map(line => {
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
}

async function newMission(){
    const scenarios = await loadScenarios();
    currentScenario = scenarios[Math.floor(Math.random() * scenarios.length)];
    targetChunks = currentScenario.chunks;

    document.getElementById("mainCharacter").innerText =
        currentScenario.main + " + " + currentScenario.support;

    document.getElementById("scenarioName").innerText = currentScenario.name;
    document.getElementById("pressureLevel").innerText = currentScenario.pressure;
    document.getElementById("missionText").innerText = currentScenario.mission;

    document.getElementById("chunkList").innerHTML =
        targetChunks.map(chunk => `<li><span class="chunk">${chunk}</span></li>`).join("");

    document.getElementById("speakerName").innerText = currentScenario.main;

    document.getElementById("openingLine").innerHTML =
        generateOpeningLine(currentScenario);

    document.getElementById("chatLog").innerHTML = "";
}

function generateOpeningLine(s){
    if(s.type === "supplier_crisis"){
        return `The supplier postponed the shipment again. We need to meet the deadline. What is your action plan?`;
    }

    if(s.type === "client_escalation"){
        return `The client is dissatisfied. They want compensation and a recovery plan. How do you respond?`;
    }

    if(s.type === "shipping_crisis"){
        return `The client will only accept urgent shipment. We must guarantee there will be no further delay. What should we do?`;
    }

    if(s.type === "internal_approval"){
        return `Management wants a clear reason before they approve the extra cost. How do you ask for approval?`;
    }

    if(s.type === "quality_check"){
        return `Rebecca found a possible technical issue. We need to verify the material specifications. How do you explain the risk?`;
    }

    if(s.type === "negotiation"){
        return `The negotiation is under pressure. We need to reach a compromise. What is your proposal?`;
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

    const used = targetChunks.filter(chunk =>
        lower.includes(chunk.toLowerCase())
    );

    const missing = targetChunks.filter(chunk =>
        !lower.includes(chunk.toLowerCase())
    );

    const score = Math.round((used.length / targetChunks.length) * 100);

    document.getElementById("chatLog").innerHTML += `
        <div class="message">
            <div class="you">You</div>
            <p>${response}</p>

            <div class="ada">${currentScenario.main}</div>
            <p>
                Good. Your chunk usage score is <span class="chunk">${score}%</span>.
                ${score >= 80 ? "This is strong controlled output." : "You need to include more target chunks."}
            </p>

            <p><b class="chunk">Used chunks:</b> ${used.length ? used.join(", ") : "None"}</p>
            <p><b class="warning">Missing chunks:</b> ${missing.length ? missing.join(", ") : "None"}</p>

            <p class="small">
                Training rule: do not write freely. Use the target chunks under pressure until they become automatic.
            </p>
        </div>
    `;

    document.getElementById("playerInput").value = "";
}

newMission();
</script>

</body>
</html>
"""

(VOCAB_DIR / "chunks.csv").write_text(chunks_csv, encoding="utf-8")
(STORY_DIR / "scenarios.csv").write_text(scenarios_csv, encoding="utf-8")

index_path = BASE / "index.html"
if index_path.exists():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = BACKUP_DIR / f"index_backup_{timestamp}.html"
    backup_path.write_text(index_path.read_text(encoding="utf-8"), encoding="utf-8")

index_path.write_text(index_html, encoding="utf-8")

print("One-click setup completed.")
print("Created: vocabulary/chunks.csv")
print("Created: story/scenarios.csv")
print("Updated: index.html")
print("Old index.html was backed up in backup/ if it existed.")