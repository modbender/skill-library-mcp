---
name: document-qa
description: "Answers questions based on the content of uploaded documents (PDF, DOCX, TXT), supporting individual files or entire folders."
---

# Document Q&A Skill

This skill allows you to upload documents (PDF, DOCX, TXT) and ask questions about their content.

## How to Use

To use this skill, run the `run_qa.py` script with the path to your document or folder and your question. The skill will extract text from supported files (PDF, DOCX, TXT) and provide it as context for answering your question.

**Command:**
`python ~/.openclaw/workspace/skills/document-qa/scripts/run_qa.py "<path_to_file_or_folder>" "<Your question>"`

**Examples:**
*   To ask about a single PDF file:
    `python ~/.openclaw/workspace/skills/document-qa/scripts/run_qa.py "C:\Users\anandraj\.openclaw\workspace\my_docs\report.pdf" "What are the key findings?"`
*   To ask about documents in a folder:
    `python ~/.openclaw/workspace/skills/document-qa/scripts/run_qa.py "C:\Users\anandraj\.openclaw\workspace\project_docs" "Summarize the project goals."`

The system will extract all relevant text and present it along with your question, allowing me to formulate an answer based on the provided content.

## Supported Document Types

*   PDF (.pdf) **(Requires 'iyeque-pdf-reader-1.1.0' skill installed)**
*   Microsoft Word (.docx)
*   Plain Text (.txt)
*   Microsoft Excel (.xlsx)

**Note:**
*   For PDF support, ensure the `iyeque-pdf-reader-1.1.0` skill is installed in your workspace.
*   For Excel support, you might need to install the `pandas` and `openpyxl` libraries if they are not already installed in your environment:
    `pip install pandas openpyxl`
