# one_click_vocab_web_setup.py
# 放到 Oxford3000-RPG 项目根目录后运行：python one_click_vocab_web_setup.py
# 它会自动备份词库、写入网页和训练脚本、生成今天的 8 张卡片数据。

from pathlib import Path
from datetime import datetime
import shutil, subprocess, sys

ROOT = Path(__file__).resolve().parent
VOCAB = ROOT / "vocabulary" / "oxford5000_extra.csv"
TOOLS = ROOT / "tools"
STORY = ROOT / "story"
BACKUP = ROOT / "backup"

TRAINER = r'''
import csv, json, sys
from pathlib import Path
from datetime import date, timedelta

BASE = Path(__file__).resolve().parents[1]
VOCAB = BASE / "vocabulary" / "oxford5000_extra.csv"
STORY = BASE / "story"
REVIEW = STORY / "review_queue.jsonl"
LOG = STORY / "practice_logs.jsonl"
TODAY = STORY / "today_mission.json"
ROLES = ["Ada", "Claire", "Jill", "Sherry", "Rose", "Grace", "Rebecca", "Ashley"]
CN = {"Ada":"艾达","Claire":"克莱尔","Jill":"吉尔","Sherry":"雪莉","Rose":"萝丝","Grace":"格蕾丝","Rebecca":"瑞贝卡","Ashley":"阿什利"}
ROLE_TASK = {"Ada":"商务谈判 / 危机判断","Claire":"情绪支持 / 人际安抚","Jill":"行动执行 / 安全控制","Sherry":"逻辑分析 / 线索复盘","Rose":"心理记忆 / 深层概念","Grace":"高级表达 / 正式写作","Rebecca":"科学医学 / 生化机制","Ashley":"生活口语 / 情绪反应"}
FIELDS = ["word","level","status","mastery","last_seen","scene","source"]

def read_vocab():
    if not VOCAB.exists():
        print("找不到词库：", VOCAB); sys.exit(1)
    with open(VOCAB, "r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))

def write_vocab(rows):
    with open(VOCAB, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader(); w.writerows(rows)

def read_jsonl(path):
    if not path.exists(): return []
    out=[]
    with open(path,"r",encoding="utf-8") as f:
        for line in f:
            line=line.strip()
            if line: out.append(json.loads(line))
    return out

def append_jsonl(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path,"a",encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False)+"\n")

def write_jsonl(path, items):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path,"w",encoding="utf-8") as f:
        for item in items: f.write(json.dumps(item, ensure_ascii=False)+"\n")

def init_vocab():
    rows = read_vocab(); fixed=[]
    for r in rows:
        fixed.append({
            "word": (r.get("word") or "").strip(),
            "level": (r.get("level") or "").strip(),
            "status": (r.get("status") or "new").strip(),
            "mastery": (r.get("mastery") or "0").strip(),
            "last_seen": (r.get("last_seen") or "").strip(),
            "scene": (r.get("scene") or "").strip(),
            "source": (r.get("source") or "Oxford5000").strip(),
        })
    write_vocab(fixed)
    print("词库检查完成：", len(fixed), "个词")

def status():
    rows=read_vocab()
    def count(s): return sum(1 for r in rows if r.get("status")==s)
    print("\n=== 学习状态 ===")
    print("总词数：", len(rows))
    print("未学习：", count("new"))
    print("学习中：", count("learning"))
    print("待复习：", count("review"))
    print("已掌握：", count("mastered"))

def new():
    rows=read_vocab(); today=str(date.today())
    candidates=[r for r in rows if r.get("status")=="new"]
    if len(candidates)<8:
        print("新词不足 8 个。先复习或导入更多词。"); return
    selected=candidates[:8]
    mission_id=f"mission_{date.today().strftime('%Y%m%d')}_{len(read_jsonl(LOG))+1:03d}"
    words=[]; cards=[]
    for i, s in enumerate(selected):
        role=ROLES[i]; word=s["word"]; words.append(word)
        for r in rows:
            if r["word"]==word:
                r["scene"]=role; r["status"]="learning"; r["mastery"]="1"; r["last_seen"]=today
        append_jsonl(REVIEW,{"word":word,"level":s.get("level",""),"scene":role,"stage":1,"next_review":str(date.today()+timedelta(days=1)),"wrong_count":0})
        cards.append({"role":role,"role_cn":CN[role],"role_task":ROLE_TASK[role],"word":word,"level":s.get("level",""),"status":"learning","mastery":1,"source":s.get("source","Oxford5000"),"meaning_cn":"待补充","example":"","collocations":""})
    write_vocab(rows)
    append_jsonl(LOG,{"date":today,"mission_id":mission_id,"type":"new_mission","words":words,"done":False})
    TODAY.parent.mkdir(parents=True, exist_ok=True)
    TODAY.write_text(json.dumps({"date":today,"mission_id":mission_id,"title":"今日 8 人角色词汇任务","task":"请用至少 5 个今日词汇写一段英文剧情。","cards":cards}, ensure_ascii=False, indent=2), encoding="utf-8")
    print("\n=== 今日新任务 ===")
    print("任务编号：", mission_id)
    for c in cards: print(f"{c['role_cn']} {c['role']}: {c['word']} / {c['level']}")
    print("\n网页数据已生成：story/today_mission.json")
    print("\n复制给 ChatGPT：")
    print("请根据下面 8 个词，生成 8 张角色词汇卡片，并设计一个剧情任务。")
    for c in cards: print(f"{c['role_cn']} {c['role']}: {c['word']} / {c['level']}")

def review():
    rows=read_vocab(); q=read_jsonl(REVIEW); today=str(date.today())
    due=[x for x in q if x.get("next_review","")<=today]
    if not due:
        print("今天没有到期复习。可以运行：python tools/vocab_trainer.py new"); return
    m={r["word"]:r for r in rows}
    print("\n=== 今日复习 ===")
    for item in due:
        word=item["word"]; role=item.get("scene",""); stage=int(item.get("stage",1))
        print(f"\n{CN.get(role,role)} {role}: {word} / {m.get(word,{}).get('level','')}")
        if stage==1: print("回忆中文意思 + 自己造句")
        elif stage==2: print("首字母填空：", word[0]+"_"*(len(word)-1))
        elif stage==3: print("英文造句：请用这个词写一句")
        elif stage==4: print("角色台词：用这个词说一句剧情台词")
        else: print("最终输出：用这个词写项目/危机/生化剧情句")
    print("\n会了运行：python tools/vocab_trainer.py pass")
    print("不会运行：python tools/vocab_trainer.py fail")

def pass_review():
    rows=read_vocab(); q=read_jsonl(REVIEW); today=date.today(); kept=[]
    for item in q:
        if item.get("next_review","")<=str(today):
            word=item["word"]; new_stage=int(item.get("stage",1))+1
            delay={2:2,3:4,4:7,5:14}.get(new_stage,30)
            for r in rows:
                if r["word"]==word:
                    mastery=min(int(r.get("mastery") or 0)+1,5); r["mastery"]=str(mastery); r["last_seen"]=str(today); r["status"]="mastered" if mastery>=5 else "review"
            if new_stage<=5:
                item["stage"]=new_stage; item["next_review"]=str(today+timedelta(days=delay)); kept.append(item)
        else: kept.append(item)
    write_vocab(rows); write_jsonl(REVIEW, kept)
    print("已通过复习，下一次复习时间已更新。")

def fail_review():
    rows=read_vocab(); q=read_jsonl(REVIEW); today=date.today()
    for item in q:
        if item.get("next_review","")<=str(today):
            item["stage"]=1; item["next_review"]=str(today+timedelta(days=1)); item["wrong_count"]=int(item.get("wrong_count",0))+1
            for r in rows:
                if r["word"]==item["word"]:
                    r["mastery"]=str(max(int(r.get("mastery") or 0)-1,0)); r["status"]="review"; r["last_seen"]=str(today)
    write_vocab(rows); write_jsonl(REVIEW,q)
    print("已记录为不会，明天继续复习。")

def help():
    print("""
用法：
python tools/vocab_trainer.py init
python tools/vocab_trainer.py status
python tools/vocab_trainer.py new
python tools/vocab_trainer.py review
python tools/vocab_trainer.py pass
python tools/vocab_trainer.py fail
""")

if __name__ == "__main__":
    cmd=sys.argv[1] if len(sys.argv)>1 else "help"
    {"init":init_vocab,"status":status,"new":new,"review":review,"pass":pass_review,"fail":fail_review}.get(cmd,help)()
'''

INDEX = r'''
<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8"><title>Oxford RPG Vocabulary Cards</title>
<style>
body{margin:0;font-family:"Microsoft YaHei",Arial,sans-serif;background:#0b0d12;color:#f2f2f2}header{padding:24px 32px;background:linear-gradient(90deg,#151824,#251018);border-bottom:1px solid #3a1f2a}h1{margin:0;font-size:28px;color:#f4d7b5}.subtitle{margin-top:8px;color:#b9a89a}.container{padding:28px 32px}.mission-box{background:#121722;border:1px solid #2e374a;border-radius:14px;padding:20px;margin-bottom:28px}.mission-title{font-size:22px;color:#f4d7b5;margin-bottom:8px}.mission-meta{color:#9ca9bd;font-size:14px;margin-bottom:12px}.task{color:#d8d8d8;line-height:1.7}.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:18px}.card{background:linear-gradient(180deg,#171b26,#0e1118);border:1px solid #374151;border-radius:18px;padding:20px;min-height:255px;position:relative;overflow:hidden;box-shadow:0 8px 24px rgba(0,0,0,.35)}.role{font-size:14px;color:#c9a46b;margin-bottom:12px}.role-task{color:#9ca9bd;font-size:13px;margin-bottom:12px}.word{font-size:34px;font-weight:bold;color:#f1e6d0;margin-bottom:10px}.level{display:inline-block;padding:4px 9px;border-radius:999px;background:#263144;color:#9fc4ff;font-size:12px;margin-bottom:18px}.info{margin-top:12px;color:#cfd6e4;line-height:1.65;font-size:14px}.label{color:#8fa3c4}.mastery{margin-top:14px;height:8px;background:#252c3a;border-radius:999px;overflow:hidden}.error{background:#2a1111;border:1px solid #7a2c2c;color:#ffd1d1;padding:18px;border-radius:12px;line-height:1.7}textarea{width:100%;min-height:130px;background:#0e1118;color:#f2f2f2;border:1px solid #374151;border-radius:12px;padding:14px;font-size:15px;box-sizing:border-box;margin-top:16px;line-height:1.6}code{background:#151a25;padding:2px 6px;border-radius:6px;color:#ffd7a8}
</style></head><body><header><h1>Oxford 5000 RPG 词汇卡片</h1><div class="subtitle">8 个角色 · 每日任务 · 防重复复习系统</div></header><div class="container"><div id="app">正在读取今日任务……</div></div>
<script>
const colors={Ada:'#8b1e2d',Claire:'#b45309',Jill:'#1d4ed8',Sherry:'#ca8a04',Rose:'#7e22ce',Grace:'#b7791f',Rebecca:'#047857',Ashley:'#be185d'};
async function load(){const app=document.getElementById('app');try{const res=await fetch('story/today_mission.json');if(!res.ok)throw new Error();const data=await res.json();app.innerHTML=`<div class="mission-box"><div class="mission-title">${data.title}</div><div class="mission-meta">日期：${data.date} ｜ 任务编号：${data.mission_id}</div><div class="task">${data.task}</div><textarea placeholder="在这里写你的英文输出：用至少 5 个今日词汇写一段剧情。"></textarea></div><div class="cards">${data.cards.map(card).join('')}</div>`}catch(e){app.innerHTML=`<div class="error"><b>还没有今日任务。</b><br><br>先在终端运行：<br><code>python tools/vocab_trainer.py new</code><br><br>然后刷新网页。</div>`}}
function card(c){const color=colors[c.role]||'#8b1e2d',w=Math.min(Number(c.mastery||1)*20,100);return `<div class="card"><div style="position:absolute;top:0;left:0;height:4px;width:100%;background:${color}"></div><div class="role">${c.role_cn} ${c.role}</div><div class="role-task">${c.role_task||''}</div><div class="word">${c.word}</div><div class="level">${c.level||'B2/C1'}</div><div class="info"><div><span class="label">状态：</span>${c.status}</div><div><span class="label">来源：</span>${c.source}</div><div><span class="label">掌握度：</span>${c.mastery} / 5</div><div><span class="label">中文：</span>${c.meaning_cn||'待补充'}</div></div><div class="mastery"><div style="height:100%;width:${w}%;background:${color}"></div></div></div>`}
load();
</script></body></html>
'''

def main():
    print("=== Oxford RPG 网页词汇卡一键安装 ===")
    if not (ROOT/"vocabulary").exists() or not (ROOT/"tools").exists():
        print("请把本文件放在项目根目录，也就是能看到 vocabulary 和 tools 文件夹的位置。")
        sys.exit(1)
    if not VOCAB.exists():
        print("找不到词库：", VOCAB)
        sys.exit(1)
    BACKUP.mkdir(exist_ok=True); STORY.mkdir(exist_ok=True); TOOLS.mkdir(exist_ok=True)
    backup_file=BACKUP/f"oxford5000_extra_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    shutil.copy2(VOCAB, backup_file)
    print("已备份词库：", backup_file)
    (TOOLS/"vocab_trainer.py").write_text(TRAINER.strip()+"\n", encoding="utf-8")
    (ROOT/"index.html").write_text(INDEX.strip()+"\n", encoding="utf-8")
    (STORY/"review_queue.jsonl").touch(exist_ok=True)
    (STORY/"practice_logs.jsonl").touch(exist_ok=True)
    print("已写入 tools/vocab_trainer.py 和 index.html")
    py=sys.executable
    for cmd in ([py,"tools/vocab_trainer.py","init"],[py,"tools/vocab_trainer.py","status"],[py,"tools/vocab_trainer.py","new"]):
        print("\n运行：", " ".join(cmd))
        subprocess.run(cmd, cwd=ROOT, check=True)
    print("\n完成。现在运行：python -m http.server 8000")
    print("然后打开：http://localhost:8000")

if __name__ == "__main__":
    main()
