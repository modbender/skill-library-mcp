# Blueprint Recipe Template

## Goal
<one sentence>

## Inputs
- <input 1>
- <input 2>

## Outputs
- <output 1>

## Assumptions
- <assumption>

## Blueprint Recipe (ordered)
1. Event: <BeginPlay / InputAction / CustomEvent>
2. Node: <exact node name> → settings: <important pin values>
3. Branch: <condition>
4. Set Var: <name> (replicated? yes/no)
5. Call: <function/interface>

## Replication Notes
- Runs on: Server / Client / Both
- RPCs: <Server_DoX>, <Client_DoY>
- Replicated Vars: <VarName> (RepNotify? yes/no)
- Bandwidth notes: <what to avoid>

## Assets / Folders
- /Game/Systems/<SystemName>/
- BP_<Thing>
- BPI_<Thing>
- DT_<Thing>

## Test Checklist
- PIE: <expected>
- Dedicated server: <expected>
- With 100 players: <perf notes>