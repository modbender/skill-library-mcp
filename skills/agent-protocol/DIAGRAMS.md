# Architecture Diagrams

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLAWDBOT SKILLS                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │ Sports   │  │ Research │  │Analytics │  │  Custom  │       │
│  │ Ticker   │  │  Agent   │  │  Agent   │  │  Skill   │       │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘       │
│       │             │              │             │              │
│       └─────────────┴──────────────┴─────────────┘              │
│                          │                                      │
│                          ▼                                      │
│              ┌───────────────────────┐                          │
│              │   publish_event()     │                          │
│              └───────────┬───────────┘                          │
│                          │                                      │
└──────────────────────────┼──────────────────────────────────────┘
                           │
                           ▼
        ┌──────────────────────────────────────┐
        │        AGENT PROTOCOL BUS            │
        │  ~/.clawdbot/events/queue/           │
        │                                      │
        │  ┌──────────┐  ┌──────────┐         │
        │  │ event_1  │  │ event_2  │  ...    │
        │  │  .json   │  │  .json   │         │
        │  └──────────┘  └──────────┘         │
        └───────────────┬──────────────────────┘
                        │
                        ▼
        ┌───────────────────────────────────────┐
        │      WORKFLOW ENGINE                  │
        │  (polls every 30 seconds)             │
        │                                       │
        │  1. Read events from queue            │
        │  2. Match to workflow triggers        │
        │  3. Execute workflow steps            │
        │  4. Mark events processed             │
        └───────────────┬───────────────────────┘
                        │
                        ▼
        ┌───────────────────────────────────────┐
        │         WORKFLOW EXECUTION            │
        │                                       │
        │   Step 1 → Step 2 → Step 3 → Done    │
        │     ↓        ↓        ↓               │
        │   Agent    Agent    Agent             │
        │    Call    Call     Call              │
        └───────────────────────────────────────┘
```

## Event Flow

```
┌─────────────┐
│   SKILL     │
│ (Publisher) │
└──────┬──────┘
       │
       │ publish_event("sports.goal_scored", {...})
       │
       ▼
┌─────────────────────┐
│   EVENT BUS         │
│                     │
│ Write JSON file     │
│ evt_XXX.json        │
│ to queue/           │
└──────┬──────────────┘
       │
       │ (30 seconds later...)
       │
       ▼
┌─────────────────────┐
│ WORKFLOW ENGINE     │
│                     │
│ 1. Read queue       │
│ 2. Match trigger    │
│ 3. Check conditions │
└──────┬──────────────┘
       │
       │ Match found!
       │
       ▼
┌─────────────────────┐
│ EXECUTE WORKFLOW    │
│                     │
│ Step 1: TTS Agent   │
│   announce(...)     │
│                     │
│ Step 2: Notify      │
│   send_telegram(...)│
└──────┬──────────────┘
       │
       │ Success
       │
       ▼
┌─────────────────────┐
│ MARK PROCESSED      │
│                     │
│ Move evt_XXX.json   │
│ queue/ → processed/ │
└─────────────────────┘
```

## Workflow Execution

```
Trigger Event
     │
     ▼
┌─────────────────────────┐
│  Evaluate Conditions    │
│  payload.importance ≥ 7?│
└────────┬────────────────┘
         │
         │ YES
         ▼
┌─────────────────────────┐
│    Step 1               │
│  ┌──────────────────┐   │
│  │ Context:         │   │
│  │ - event          │   │
│  │ - payload        │   │
│  └──────────────────┘   │
│                         │
│  Execute: summary-agent │
└────────┬────────────────┘
         │
         │ Result: {summary: "..."}
         ▼
┌─────────────────────────┐
│    Step 2               │
│  ┌──────────────────┐   │
│  │ Context:         │   │
│  │ - event          │   │
│  │ - payload        │   │
│  │ - previous       │◄──── Result from Step 1
│  └──────────────────┘   │
│                         │
│  Execute: telegram      │
│  Message: {{previous.summary}}
└────────┬────────────────┘
         │
         │ Success
         ▼
┌─────────────────────────┐
│   Mark Processed        │
└─────────────────────────┘
```

## Parallel Execution

```
Trigger Event
     │
     ▼
┌─────────────────────────┐
│  Parallel Steps         │
│                         │
│  ┌──────┐  ┌──────┐    │
│  │Step A│  │Step B│    │
│  └───┬──┘  └───┬──┘    │
└──────┼─────────┼────────┘
       │         │
       ▼         ▼
  ┌────────┐  ┌────────┐
  │Telegram│  │Discord │
  │Notifier│  │Notifier│
  └────┬───┘  └────┬───┘
       │           │
       └─────┬─────┘
             │
             ▼
      All Complete
```

## Conditional Routing

```
Trigger Event
     │
     ▼
┌─────────────────────────┐
│  Check: importance?     │
└────┬──────────────┬─────┘
     │              │
     │ ≥ 9          │ < 9
     ▼              ▼
┌─────────┐   ┌─────────┐
│ Urgent  │   │ Normal  │
│ Handler │   │ Handler │
└─────────┘   └─────────┘
```

## File Structure

```
~/.clawdbot/events/
│
├── queue/                    ← Pending events
│   ├── evt_123.json
│   ├── evt_124.json
│   └── evt_125.json
│
├── processed/                ← Successfully handled
│   ├── evt_100.json
│   ├── evt_101.json
│   └── evt_102.json
│
├── failed/                   ← Failed processing
│   └── evt_103.json
│
├── log/
│   ├── events.log           ← Event bus log
│   ├── audit.log            ← Security audit
│   └── workflows/
│       └── engine.log       ← Workflow execution log
│
└── subscriptions.json       ← Active subscriptions
```

## Integration Example: Sports → TTS

```
┌─────────────────────┐
│  Sports Ticker      │
│  live_monitor.py    │
└──────┬──────────────┘
       │
       │ Goal detected!
       │
       ▼
┌─────────────────────┐
│  publish_event()    │
│                     │
│  Type: sports.goal  │
│  Payload: {         │
│    team: "FCB",     │
│    scorer: "Messi"  │
│  }                  │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Event Queue        │
│  evt_001.json       │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Workflow Engine    │
│                     │
│  Trigger matches:   │
│  "sports.goal"      │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Execute Workflow   │
│                     │
│  Step: TTS Agent    │
│  Input: "Goal for   │
│   {{payload.team}}  │
│   by {{payload.     │
│   scorer}}!"        │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  ElevenLabs Voices  │
│  speak()            │
│                     │
│  🔊 "Goal for FCB   │
│     by Messi!"      │
└─────────────────────┘
```

## Multi-Skill Orchestration

```
         Research Agent
                │
                │ Finds article
                ▼
         publish_event()
         "research.article_found"
                │
                ▼
         Event Bus (Queue)
                │
                ├───────────────┬─────────────┐
                ▼               ▼             ▼
          Workflow 1      Workflow 2    Workflow 3
          Summary         Archive       Notify
                │               │             │
                ▼               ▼             ▼
          Summary Agent   File Manager   Telegram
                │               │             │
                └───────────────┴─────────────┘
                            │
                            ▼
                    All tasks complete!
```

## Error Handling Flow

```
Step Execution
     │
     ▼
┌─────────────────┐
│  Try Execute    │
└────┬────────────┘
     │
     │ Error!
     ▼
┌─────────────────┐
│  Retry?         │
│  attempts < 3?  │
└────┬─────┬──────┘
     │     │
   YES    NO
     │     │
     │     ▼
     │  ┌──────────────┐
     │  │ on_error     │
     │  │ handler      │
     │  └──────┬───────┘
     │         │
     │         ▼
     │  ┌──────────────┐
     │  │ continue?    │
     │  └──────┬───────┘
     │         │
     ▼         ▼
  Retry    Next Step
           or Fail
```

---

**Visual guide to understanding the Agent Protocol architecture** 🦎
