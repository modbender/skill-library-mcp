
import sys
import os
import subprocess

def run_qa_system(document_path, question):
    # Determine the path to process_folder.py
    script_dir = os.path.dirname(__file__)
    process_folder_script_path = os.path.join(script_dir, "process_folder.py")

    if not os.path.exists(process_folder_script_path):
        print(f"Error: process_folder.py not found at {process_folder_script_path}", file=sys.stderr)
        return

    try:
        # Execute process_folder.py to get all text content
        print(f"Extracting text from: {document_path}")
        result = subprocess.run(
            [sys.executable, process_folder_script_path, document_path],
            capture_output=True,
            text=True,
            check=True
        )
        extracted_content = result.stdout

        # Now, present the extracted content and the question for the LLM to answer
        # Using specific markers to easily identify the context for QA
        print("\n--- DOCUMENT_QA_CONTEXT_START ---")
        print(extracted_content)
        print("--- DOCUMENT_QA_CONTEXT_END ---\n")
        print(f"QUESTION: {question}")

    except subprocess.CalledProcessError as e:
        print(f"Error processing documents: {e.stderr}", file=sys.stderr)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)

if __name__ == "__main__":
    if len(sys.argv) == 3:
        doc_path = sys.argv[1]
        user_question = sys.argv[2]
        run_qa_system(doc_path, user_question)
    else:
        print('Usage: python run_qa.py <path_to_file_or_folder> "<Your question>"', file=sys.stderr)
        sys.exit(1)
