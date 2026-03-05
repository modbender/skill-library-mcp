---
name: paper-engineering
description: Automated academic writing assistant based on a three-layer architecture: Framework Layer, Summary Layer, and Body Layer. Organizes all files in a structured project directory.
version: 1.0.0
author: OpenClaw Community
permissions: Filesystem read/write, network access (for literature search)
---

# Paper Engineering Assistant

## 1. Skill Description
This skill automates a structured academic writing workflow based on a three-layer architecture: **Framework Layer**, **Summary Layer**, and **Body Layer**. It maintains data consistency across all layers through automatic synchronization mechanisms. The skill operates within a user-designated project directory (default: `./PaperProject/`).

## 2. When to Use
Use this skill when the user needs systematic assistance with academic writing, especially for long-form documents like theses or dissertations.
- User says: "Start working on my thesis."
- User says: "Read and structure all literature in the `references` folder."
- User says: "Generate a preliminary framework based on my research proposal."
- User says: "I've modified Section 2.1, please sync the framework and summaries."
- User says: "Find and download recent literature about 'performance management'."

## 3. Core Concepts & Workflow
This skill strictly follows the three-layer architecture:

### **A. Core Three-Layer Structure**
1.  **Framework Layer (`structs.json`)**: The blueprint/map of the entire paper. A JSON array describing the hierarchical structure of chapters, sections, and paragraphs with IDs, titles, abstracts, keywords, and key points.
2.  **Summary Layer (`summaries.json`)**: The content database. Provides detailed summaries for each framework node and records related node IDs for content traceability.
3.  **Body Layer (`./document_body/` directory)**: The actual written content. A directory and Markdown file collection that exactly mirrors the framework layer structure, with each file corresponding to a writing unit.

### **B. Workflow Stages**
**Stage 1: Literature Review & Processing**
1.  **Initialization**: Create necessary subdirectories in the project directory (e.g., `./document_body/`, `./processed_references/`).
2.  **Process References**:
    - Iterate through each reference in the `references` directory.
    - Create a dedicated folder for each reference (named after the reference) and initialize an `information.md` file with metadata (title, author, abstract, keywords, download link).
    - If the reference file (e.g., PDF) is available, parse it using the same three-layer architecture, generating corresponding `structs.json`, `summaries.json`, and body files stored within that reference's folder. This creates a "knowledge base" for each reference.
    - If the original text cannot be downloaded, only save the `information.md`.
3.  **Read Other Materials**: Review non-reference materials like research proposals, institutional guidelines, etc., to understand requirements and existing foundations.

**Stage 2: Document Writing**
1.  **Generate Framework Layer**: Create the initial `structs.json` based on the research topic, proposal, and processed references. If an exemplary reference paper exists, its structure can be emulated.
2.  **Generate Summary Layer**: Write detailed summaries for each framework node, forming `summaries.json`.
3.  **Write Body Layer**: Based on the framework structure and summary content, write detailed content for each part in the `./document_body/` directory, following the format `Chapter_X/Section_X.X_Title.md`. If a section becomes too long, split it into multiple files (e.g., `Section_X.X_Title_trunc_1.md`).

**Stage 3: Assembly & Synchronization**
1.  **Assemble Final Document**: Run a concatenation script that reads all Markdown files in `./document_body/` and merges them in the order defined by the framework layer into a complete `thesis_final.md` file. This is a programmatic process, not reliant on AI.
2.  **Critical: Synchronization Mechanism**:
    - **Top-down Modification**: When the user or AI modifies the **Framework Layer (`structs.json`)** or **Summary Layer (`summaries.json`)**, the corresponding **Body Layer** files must be rewritten or updated.
    - **Bottom-up Modification**: When the user or AI modifies a **Body Layer** file, extract its core information to update the corresponding **Summary Layer** entry and **Framework Layer** abstract.
    - This synchronization is crucial for maintaining logical consistency and preventing fragmentation, and must be executed after each modification.

## 4. How to Use (Operating Steps)
When the user triggers the skill, I will work according to the following logic:

1.  **Confirm Working Directory**: I will first establish the project root directory. If not specified, I will use the default `./PaperProject/` in the current working directory. All generated files will be placed within this directory or its subdirectories.
2.  **Execute the Requested Task**:
    - **If the request is "start" or "process references"**:
        a. Check the directory structure and list all items in the `references` folder.
        b. Execute the "Literature Review & Processing" workflow for each item.
        c. Generate a `literature_review_report.md` summarizing key findings and interconnections.
    - **If the request is "generate framework"**:
        a. Comprehensively analyze the research proposal, core insights from processed references, and institutional guidelines.
        b. Generate or update `structs.json` (Framework Layer) in the project root.
    - **If the request is "write body"**:
        a. Read `structs.json` and `summaries.json`.
        b. Create corresponding folders and files in the `./document_body/` directory and begin writing content. Existing files in this directory may be overwritten.
        c. While writing each section, query `summaries.json` and the associated reference knowledge bases.
    - **If the request is "sync modification"**:
        a. The user indicates which file was modified (e.g., `./document_body/Chapter_3/3.1_Current_Analysis.md`).
        b. I first read the modified file content, extract a new abstract and key points.
        c. Update the `section_summary` for the corresponding `section_id` in `summaries.json`.
        d. Update the `abstract` and `key_points` for the corresponding `section_id` in `structs.json`.
    - **If the request is "find literature"**:
        a. Perform a network search based on the user-provided keywords.
        b. Attempt to download PDFs to the `references` directory.
        c. Create a folder and `information.md` for each, regardless of download success. If downloaded successfully, proceed with structured parsing.
3.  **Output & Confirmation**: After each operation, I will clearly state which files were generated, their paths, and briefly describe their content.

## 5. Edge Cases
- **Directory Doesn't Exist**: If the project directory doesn't exist, I will ask the user if they want to create it.
- **References Folder Empty**: If the `references` folder is empty, I will notify the user and ask if they want to proceed directly to framework design or start a network search for literature.
- **Research Proposal Missing**: If no research proposal is found, I will generate a very basic initial framework based on the paper title and general academic structure, noting that it will require significant revision.
- **Sync Conflict**: If major, irreconcilable discrepancies are detected between the Framework, Summary, and Body layers for the same section, I will list the conflicts and **pause automatic synchronization**, requesting manual user judgment and instruction.