
import os
import sys
import subprocess

def process_folder(folder_path):
    all_extracted_text = []
    supported_extensions_internal = {
        ".docx": "extract_docx.py",
        ".txt": "extract_txt.py",
        ".xlsx": "extract_excel.py"
    }

    # Construct absolute path to the external PDF reader skill's script
    current_script_dir = os.path.dirname(os.path.abspath(__file__))
    # Go up from 'document-qa/scripts' to 'document-qa', then up to 'skills'
    skills_dir = os.path.abspath(os.path.join(current_script_dir, os.pardir, os.pardir)) # Corrected: go up two levels
    pdf_reader_skill_dir = os.path.join(skills_dir, "iyeque-pdf-reader-1.1.0")
    pdf_reader_script_path = os.path.join(pdf_reader_skill_dir, "reader.py")

    # Debugging prints
    # print(f"DEBUG: current_script_dir = {current_script_dir}", file=sys.stderr)
    # print(f"DEBUG: skills_dir = {skills_dir}", file=sys.stderr)
    # print(f"DEBUG: pdf_reader_skill_dir = {pdf_reader_skill_dir}", file=sys.stderr)
    # print(f"DEBUG: pdf_reader_script_path = {pdf_reader_script_path}", file=sys.stderr)

    if not os.path.isdir(folder_path):
        return f"Error: Folder not found at {folder_path}"

    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):
            extension = os.path.splitext(filename)[1].lower()

            if extension == ".pdf":
                if not os.path.exists(pdf_reader_script_path):
                    all_extracted_text.append(f"--- Error processing {filename} ---\n")
                    all_extracted_text.append(f"Error: PDF reader script not found at {pdf_reader_script_path}\n")
                    continue
                try:
                    result = subprocess.run([sys.executable, pdf_reader_script_path, "extract", file_path], capture_output=True, text=True, check=True)
                    all_extracted_text.append(f"--- Content from {filename} ---\n")
                    all_extracted_text.append(result.stdout)
                    all_extracted_text.append("\n")
                except subprocess.CalledProcessError as e:
                    all_extracted_text.append(f"--- Error processing {filename} ---\n")
                    all_extracted_text.append(f"Error: {e.stderr}\n")
                except Exception as e:
                    all_extracted_text.append(f"--- Error processing {filename} ---\n")
                    all_extracted_text.append(f"Error: {e}\n")
            elif extension in supported_extensions_internal:
                script_name = supported_extensions_internal[extension]
                script_path = os.path.join(current_script_dir, script_name)
                
                try:
                    result = subprocess.run([sys.executable, script_path, file_path], capture_output=True, text=True, check=True)
                    all_extracted_text.append(f"--- Content from {filename} ---\n")
                    all_extracted_text.append(result.stdout)
                    all_extracted_text.append("\n")
                except subprocess.CalledProcessError as e:
                    all_extracted_text.append(f"--- Error processing {filename} ---\n")
                    all_extracted_text.append(f"Error: {e.stderr}\n")
                except Exception as e:
                    all_extracted_text.append(f"--- Error processing {filename} ---\n")
                    all_extracted_text.append(f"Error: {e}\n")
            # else: unsupported file type, implicitly skipped

    return "\n".join(all_extracted_text)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        target_path = sys.argv[1]
        current_script_dir = os.path.dirname(os.path.abspath(__file__))
        skills_dir = os.path.abspath(os.path.join(current_script_dir, os.pardir, os.pardir)) # Corrected: go up two levels
        pdf_reader_skill_dir = os.path.join(skills_dir, "iyeque-pdf-reader-1.1.0")
        pdf_reader_script_path_main = os.path.join(pdf_reader_skill_dir, "reader.py")

        # Debugging prints
        # print(f"DEBUG (main): current_script_dir = {current_script_dir}", file=sys.stderr)
        # print(f"DEBUG (main): skills_dir = {skills_dir}", file=sys.stderr)
        # print(f"DEBUG (main): pdf_reader_skill_dir = {pdf_reader_skill_dir}", file=sys.stderr)
        # print(f"DEBUG (main): pdf_reader_script_path_main = {pdf_reader_script_path_main}", file=sys.stderr)

        if os.path.isdir(target_path):
            extracted_content = process_folder(target_path)
            print(extracted_content)
        elif os.path.isfile(target_path):
            extension = os.path.splitext(target_path)[1].lower()
            if extension == ".pdf":
                if not os.path.exists(pdf_reader_script_path_main):
                    print(f"Error: PDF reader script not found at {pdf_reader_script_path_main}", file=sys.stderr)
                    sys.exit(1)
                try:
                    result = subprocess.run([sys.executable, pdf_reader_script_path_main, "extract", target_path], capture_output=True, text=True, check=True)
                    print(result.stdout)
                except subprocess.CalledProcessError as e:
                    print(f"Error processing {target_path}: {e.stderr}", file=sys.stderr)
                except Exception as e:
                    print(f"Error processing {target_path}: {e}", file=sys.stderr)
            else:
                script_name = None
                if extension == ".docx":
                    script_name = "extract_docx.py"
                elif extension == ".txt":
                    script_name = "extract_txt.py"
                elif extension == ".xlsx":
                    script_name = "extract_excel.py"
                
                if script_name:
                    script_path = os.path.join(current_script_dir, script_name)
                    try:
                        result = subprocess.run([sys.executable, script_path, target_path], capture_output=True, text=True, check=True)
                        print(result.stdout)
                    except subprocess.CalledProcessError as e:
                        print(f"Error processing {target_path}: {e.stderr}", file=sys.stderr)
                    except Exception as e:
                        print(f"Error processing {target_path}: {e}", file=sys.stderr)
                else:
                    print(f"Error: Unsupported file type: {extension}", file=sys.stderr)
        else:
            print(f"Error: Path is neither a file nor a directory: {target_path}", file=sys.stderr)
    else:
        print("Usage: python process_folder.py <path_to_file_or_folder>")
