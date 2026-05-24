from pathlib import Path
from datetime import datetime

BASE = Path(__file__).resolve().parents[1]
STORY = BASE / "story"
BACKUP = BASE / "backup"

STORY.mkdir(exist_ok=True)
BACKUP.mkdir(exist_ok=True)

world_bible = """# Biohazard Corporate Crisis Universe

## Core Concept

This is an English learning RPG inspired by biohazard-style crisis storytelling.

The goal is not to copy the original story, but to use a tense survival-corporate universe to train Oxford3000 and Oxford5000 vocabulary through realistic chunks.

## Player Role

You are the Project Crisis Coordinator at Auria Dynamics.

Your job is to handle urgent business, technical, supplier, and client crises in English.

## Company

Auria Dynamics

## Industry

Automotive interior systems, antibacterial materials, safety components, and emergency supply-chain solutions.

## Main Project

Project Phoenix

A high-risk international project to develop antibacterial automotive interior material for a major client.

## Main Conflict

The project is threatened by:

- supplier delays
- material compatibility problems
- client dissatisfaction
- quality control issues
- internal blame
- budget pressure
- urgent shipment problems
- loss of client confidence

## Learning Philosophy

The player does not freely make random sentences.

Every episode provides:

- a scenario
- character pressure
- target chunks
- sentence frames
- a mission
- feedback

The goal is to turn vocabulary into automatic English output.

## Training Rule

One episode should focus on 4 to 6 target chunks.

The same chunk must appear across different scenarios until it becomes automatic.

Example:

get approval

This chunk may appear in:

- supplier price increase
- urgent shipment
- client compensation
- technical change
- management meeting

## Season 01

Season 01: Project Phoenix

The supplier delays a critical material shipment. The client loses confidence. The team must recover the project before termination.
"""

season_01 = """# Season 01: Project Phoenix

## Episode Arc 01 — Supplier Delay

Focus:
- postpone the shipment
- follow up with the supplier
- find an alternative supplier
- meet the deadline
- send confirmation to the supplier

Main Characters:
Ada Wong, Claire Redfield

Training:
Supplier communication and action planning.

---

## Episode Arc 02 — Client Escalation

Focus:
- offer compensation
- create a recovery plan
- restore client confidence
- take responsibility for the delay
- avoid further delay

Main Characters:
Ada Wong, Rose Winters, Jill Valentine

Training:
Client negotiation and trust recovery.

---

## Episode Arc 03 — Technical Contamination

Focus:
- verify the material specifications
- run another inspection
- technical issue
- quality control
- forecast the delivery risk

Main Characters:
Rebecca Chambers, Grace Ashcroft

Training:
Technical explanation and risk reporting.

---

## Episode Arc 04 — Factory Shutdown Risk

Focus:
- cause a delay
- avoid further delay
- urgent shipment
- guarantee the delivery date
- reduce the risk

Main Characters:
Jill Valentine, Rebecca Chambers

Training:
High-pressure action English.

---

## Episode Arc 05 — Internal Blame Game

Focus:
- clarify the responsibility
- the responsibility is not on our side
- understand the business implications
- get approval
- submit a recovery plan

Main Characters:
Grace Ashcroft, Ada Wong

Training:
Responsibility, reporting, and internal communication.

---

## Episode Arc 06 — Final Recovery Negotiation

Focus:
- reach a compromise
- request an extension
- accommodate the client's request
- implement a recovery plan
- restore client confidence

Main Characters:
Ada Wong, Rose Winters, Claire Redfield

Training:
Final negotiation and persuasion.
"""

character_matrix = """# Character Learning Matrix

## Ada Wong

Role:
Senior Project Director

Function:
Forces the player to make strategic business decisions.

Training Focus:
- negotiation
- approval
- risk control
- recovery plan
- responsibility

Personality:
Cold, strategic, direct.

---

## Jill Valentine

Role:
Emergency Operations Manager

Function:
Creates pressure and forces quick action.

Training Focus:
- urgent shipment
- deadline
- guarantee
- delay
- action plan

Personality:
Decisive, tactical, intense.

---

## Claire Redfield

Role:
Supplier Communication Coordinator

Function:
Helps the player communicate with suppliers and team members.

Training Focus:
- follow up with the supplier
- confirmation
- alternative supplier
- shipment status

Personality:
Supportive, practical, warm.

---

## Rebecca Chambers

Role:
Technical Quality Specialist

Function:
Forces technical explanation and quality-related English.

Training Focus:
- verify specifications
- inspection
- technical issue
- quality control
- compatibility risk

Personality:
Careful, intelligent, analytical.

---

## Grace Ashcroft

Role:
Corporate Intelligence Analyst

Function:
Forces reporting, evidence, and responsibility analysis.

Training Focus:
- clarify responsibility
- report the issue
- analyze the cause
- forecast risk

Personality:
Observant, cautious, analytical.

---

## Rose Winters

Role:
Client Trust and Psychological Strategy Consultant

Function:
Trains emotional and persuasive communication.

Training Focus:
- restore confidence
- lose confidence
- deal with pressure
- client relationship

Personality:
Quiet, perceptive, emotionally intelligent.

---

## Sherry Birkin

Role:
Junior Project Assistant

Function:
Helps with simple summaries and daily workplace communication.

Training Focus:
- summarize the meeting
- ask for help
- explain next steps
- confirm tasks

Personality:
Optimistic, sincere, supportive.
"""

# Backup existing files if needed
for filename, content in {
    "world_bible.md": world_bible,
    "season_01_project_phoenix.md": season_01,
    "character_learning_matrix.md": character_matrix,
}.items():
    path = STORY / filename
    if path.exists():
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = BACKUP / f"{filename}_{timestamp}.bak"
        backup_path.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
    path.write_text(content, encoding="utf-8")

print("Universe pack created.")
print("Created/updated:")
print("story/world_bible.md")
print("story/season_01_project_phoenix.md")
print("story/character_learning_matrix.md")