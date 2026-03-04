---
name: tpt-generate-cover
version: 0.1.0
description: Generate a TPT cover using the AI Studio DinoCover tool and save it locally with the book title as filename.
tags: [tpt, cover, gemini, browser, automation]
---

# TPT Generate Cover (AI Studio DinoCover Tool)

## Purpose
Automatically generate a Teachers Pay Teachers (TPT) cover using the custom AI Studio application "DinoCover Gen" and save the generated image to the local output folder.

This skill uses browser profile `geminibuild`, which must already have a persisted Google login session.

---

## Tool URL
https://aistudio.google.com/apps/drive/1dsPpIhA2HzaacwO16jxddnerC-B64MuC?showPreview=true&showAssistant=true&fullscreenApplet=true

---

## Preconditions

- Browser profile `geminibuild` exists.
- Google account is already logged in.
- Input folders exist:
  - Reference covers:
    E:\AI\openclaw-tpt\input\cover\
  - Story TXT files:
    E:\AI\openclaw-tpt\input\TXT\
- Output folder exists:
  E:\AI\openclaw-tpt\output\COVER\

This skill must not attempt Google account login or MFA handling.

---

## Inputs

- Latest TXT file inside:
  E:\AI\openclaw-tpt\input\TXT\
  
TXT structure assumed:
- First line = TITLE
- Remaining content = STORY CONTEXT

- Reference images:
  All PNG files inside:
  E:\AI\openclaw-tpt\input\cover\

---

## Outputs

- Generated PNG image
- Saved to:
  E:\AI\openclaw-tpt\output\COVER\
- Filename:
  <TITLE>.png

---

## Procedure

1. Launch browser using profile `geminibuild`.
2. Open the DinoCover tool URL.
3. Wait until UI fully loads.

4. Upload all reference images from:
   E:\AI\openclaw-tpt\input\cover\

5. Read latest TXT file from:
   E:\AI\openclaw-tpt\input\TXT\
   - Extract TITLE (first line)
   - Extract STORY CONTEXT (remaining content)

6. Fill the TITLE field in the tool.
7. Fill STORY CONTEXT field.

8. Click "Generate Cover".

9. Wait for generated image preview to appear.

10. Download generated image.

11. Save image to:
    E:\AI\openclaw-tpt\output\COVER\
    Filename:
    <TITLE>.png

---

## Success Criteria

- Generated image is visible.
- Image downloaded successfully.
- File saved under correct filename.
- File exists in output folder.

---

## Stop / Hand-off Conditions (Human Required)

- Google login page appears.
- MFA / verification prompt appears.
- Captcha appears.
- Generate button fails repeatedly.
- No preview appears after reasonable wait.

---

## Safety Boundaries

- Do not change Google account settings.
- Do not modify Drive files.
- Do not delete reference images.
- Only upload, generate, download.

---

# 中文说明（人工校验用）

目标：  
用 geminibuild profile 打开 DinoCover 工具，上传参考封面，读取 TXT 标题与故事，生成封面，并保存到 output/COVER。

停止条件：  
出现登录验证、人机验证、异常页面，必须停止。

文件命名规则：  
标题.png