# Logic Flow v0.2.0-phase1 (Stage-Gated)

## 1) High-Level

```text
Input (txt/json/staged)
   -> Prepare (storyboard/assets/staged artifacts)
   -> Confirm Gate
   -> Storyboard Images
   -> Confirm Gate
   -> Render Shots
   -> Concat Final Video
   -> Confirm Gate
   -> Delivery Ready
```

## 2) Detailed Flow

```text
┌────────────────────────────────────────────────────────────────┐
│ Command: run_story.py run --project-dir ... --stage render    │
└────────────────────────────────────────────────────────────────┘
                     │
                     v
          [Load existing checkpoints]
                     │
                     ├─ if any checkpoint exists && confirmed=false
                     │      -> STOP
                     │      -> return pending_confirmation_stage + next_action
                     │
                     v
┌─────────────────────────── Stage 1: outline ───────────────────────────┐
│ call prepare_storyboard.py                                              │
│ outputs: storyboard.draft / assets / parse-report / staged-artifacts    │
│ write checkpoint-outline (confirmed=false)                              │
└──────────────────────────────────────────────────────────────────────────┘
                     │
                     v
                 STOP (wait confirm outline)
                     │
                     v
┌──────────────────────── Stage 2: episode_plan ──────────────────────────┐
│ validate episode-plan artifact exists                                   │
│ write checkpoint-episode_plan (confirmed=false)                         │
└──────────────────────────────────────────────────────────────────────────┘
                     │
                     v
              STOP (wait confirm episode_plan)
                     │
                     v
┌────────────────────────── Stage 3: storyboard ──────────────────────────┐
│ validate storyboard draft exists                                        │
│ write checkpoint-storyboard (confirmed=false)                           │
└──────────────────────────────────────────────────────────────────────────┘
                     │
                     v
               STOP (wait confirm storyboard)
                     │
                     v
┌─────────────────────── Stage 4: storyboard_images ──────────────────────┐
│ call seedream_image.py storyboard ...                                   │
│ write checkpoint-storyboard_images (confirmed=false)                    │
└──────────────────────────────────────────────────────────────────────────┘
                     │
                     v
            STOP (wait confirm storyboard_images)
                     │
                     v
┌──────────────────────────── Stage 5: render ────────────────────────────┐
│ call orchestrate_story.py run ...                                       │
│ parse mixed stdout via parse_last_json()                                │
│ optional: concat_videos.py -> final-video.mp4                           │
│ write checkpoint-render (confirmed=false)                               │
└──────────────────────────────────────────────────────────────────────────┘
                     │
                     v
                 STOP (wait confirm render)
```

## 3) Confirm Flow

```text
run_story.py confirm --stage <stage>
  -> write checkpoint-<stage>.json { confirmed: true, timestamp, notes }
  -> run run_story.py run again to continue next stage
```

## 4) Status Flow

```text
run_story.py status --project-dir <dir>
  -> aggregate checkpoint-outline ... checkpoint-render
  -> output each stage confirmed/timestamp/notes
```

## 5) Failure & Recovery

- Any stage failure does not delete artifacts.
- Re-run with same `project_dir`.
- Workflow resumes from first unconfirmed stage.
