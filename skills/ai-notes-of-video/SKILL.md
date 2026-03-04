---
name: ai-notes-of-video
description: The video AI notes tool is provided by Baidu. Based on the video download address provided by the user, it downloads and parses the video, and finally generates AI notes corresponding to the video (a total of three types of notes can be generated: document notes, outline notes, and image-text notes).
metadata: { "openclaw": { "emoji": "📺", "requires": { "bins": ["python"], "env":["BAIDU_API_KEY"]},"primaryEnv":"BAIDU_API_KEY" } }
---

# AI PPT Generation

This skill allows OpenClaw agents to generate AI notes, Based solely on the video address provided by the user.

## Setup

1.  **API Key:** Ensure the BAIDU_API_KEY environment variable is set with your valid API key.
2.  **Environment:** The API key should be available in the runtime environment.

## API table
|    name    |               path              |            description                |
|------------|---------------------------------|---------------------------------------|
|AINotesTaskCreate|/v2/tools/ai_note/task_create|Create AI notes task based on the video address provided by the user|
|AINotesTaskQuery| /v2/tools/ai_note/query   |Query AI notes task result based on task id|


## Workflow

1. The AINotesTaskCreate API executes the Python script located at `scripts/ai_notes_task_create.py`
2. The AINotesTaskQuery API executes the Python script located at `scripts/ai_notes_task_query.py`
3. The first step ,call the AINotesTaskCreate API to create a task and get the task ID, must give a video address.
4. The second step ,call the AINotesTaskQuery API to query the task result based on the task ID.
5. Repeat the second step until the task status is completed.The task success identifier is status=10002. status=10000 indicates that the task is in progress. All other status codes are failures
6. Each item in the note list is a note content. For each item in the list: the tpl_no field represents the type of stored notes, 1 - manuscript notes, 2 - outline notes, 3 - graphic and text notes. The "detail" field is for note details. In "detail", "status" represents the note status, with 10002 indicating success,with status=10000 indicating progressing and other status codes indicating failure. "content" indicates the note result. The mind map is located at the top of the outline note and is marked by the "Mind" tag

## APIS

### AINotesTaskCreate API 

#### Parameters

- `video_url`: the url of the video (required)

#### Example Usage
```bash
BAIDU_API_KEY=xxx python3 scripts/ai_notes_task_create.py 'https://xxxxx.bj.bcebos.com/1%E5%88%86%E9%92%9F_%E6%9C%89%E5%AD%97%E5%B9%95.mp4'
```

### PPTOutlineGenerate API 

#### Parameters

- `task_id`: task id from AINotesTaskCreate API return（required）


#### Example Usage
```bash
BAIDU_API_KEY=xxx python3 scripts/ai_notes_task_query.py "26943ed4-f5a9-4306-a05b-b087665433a0"
```