# Usage Guide for Document Q&A Skill

This guide provides instructions and tips for effectively using the Document Q&A skill.

## 1. Providing Documents

You can provide documents in two ways:

*   **Individual File:** Specify the direct path to a `.pdf`, `.docx`, or `.txt` file.
    Example: `/path/to/your/document.pdf`

*   **Folder:** Specify the path to a folder containing multiple `.pdf`, `.docx`, or `.txt` files. The skill will process all supported documents within that folder.
    Example: `/path/to/your/document_folder/`

## 2. Asking Questions

Once the document(s) have been processed, you can ask questions. Remember these guidelines for best results:

*   **Context-Specific:** Your questions should be directly related to the content within the provided documents.
*   **Clear and Concise:** Formulate your questions clearly. Avoid ambiguity.
*   **Focus on Facts:** This skill is designed for factual retrieval from the documents, not for general knowledge or external analysis.
*   **Examples:**
    *   "What is the main topic of the document?"
    *   "Summarize the section on 'Introduction'."
    *   "Who are the authors mentioned in the report?"
    *   "What are the key findings of the study?"

## 3. Important Notes

*   **Dependencies:** Ensure that the necessary Python libraries (`PyPDF2`, `python-docx`) are installed in your environment for PDF and DOCX extraction to work correctly. You might need to run `pip install PyPDF2 python-docx`.
*   **Long Documents:** For very long documents, the skill will attempt to chunk the text to fit within the model's context window. If you ask a question that requires information from disparate parts of an extremely long document, it might not always capture everything.
*   **Error Handling:** The skill will report errors if it cannot find a specified file or folder, or if there are issues during text extraction from a particular file.
