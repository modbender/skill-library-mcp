
import pandas as pd
import sys
import os

def extract_text_from_excel(excel_path):
    extracted_data = []
    try:
        xls = pd.ExcelFile(excel_path)
        for sheet_name in xls.sheet_names:
            df = xls.parse(sheet_name)
            extracted_data.append(f"--- Sheet: {sheet_name} ---\n")
            # Convert DataFrame to a string representation, e.g., CSV or tab-separated
            extracted_data.append(df.to_string(index=False))
            extracted_data.append("\n\n")
        return "".join(extracted_data)
    except Exception as e:
        return f"Error extracting text from Excel: {e}"

if __name__ == "__main__":
    if len(sys.argv) > 1:
        excel_file_path = sys.argv[1]
        if os.path.exists(excel_file_path):
            extracted_text = extract_text_from_excel(excel_file_path)
            print(extracted_text)
        else:
            print(f"Error: File not found at {excel_file_path}")
    else:
        print("Usage: python extract_excel.py <path_to_excel_file>")

# NOTE: This script requires the pandas library.
# If running in a new environment, you might need to install it:
# pip install pandas openpyxl
