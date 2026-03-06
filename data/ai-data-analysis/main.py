#!/usr/bin/env python3
# Data Analysis Service - Main Script

import os
import sys
import pandas as pd
from pathlib import Path
from datetime import datetime

SCRIPT_DIR = Path(__file__).parent.resolve()
OUTPUT_DIR = SCRIPT_DIR / "output"

def analyze_csv(file_path, analysis_type="summary"):
    """分析CSV文件"""
    try:
        df = pd.read_csv(file_path)
        output = f"# Data Analysis Report: {file_path.name}\n\n"
        output += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        output += f"## Data Overview\n\n"
        output += f"- Rows: {len(df)}\n"
        output += f"- Columns: {len(df.columns)}\n"
        output += f"- Columns: {', '.join(df.columns.tolist())}\n\n"
        output += f"## Summary Statistics\n\n"
        output += df.describe().to_markdown() + "\n\n"

        output_file = OUTPUT_DIR / f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        output_file.write_text(output, encoding='utf-8')

        return str(output_file)
    except Exception as e:
        return f"Error: {str(e)}"

def clean_data(file_path, output_format="csv"):
    """清洗数据"""
    try:
        df = pd.read_csv(file_path)

        # Remove duplicates
        df_clean = df.drop_duplicates()

        # Fill missing values
        df_clean = df_clean.fillna(method='ffill').fillna(method='bfill')

        output_file = OUTPUT_DIR / f"cleaned_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{output_format}"
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        if output_format == "csv":
            df_clean.to_csv(output_file, index=False)
        elif output_format == "json":
            df_clean.to_json(output_file, orient='records', indent=2)

        return str(output_file)
    except Exception as e:
        return f"Error: {str(e)}"

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 main.py <action> <file> [options]")
        print("\nActions:")
        print("  analyze  <file> [analysis_type] - Analyze CSV file")
        print("  clean    <file> [format]        - Clean data")
        print("\nExamples:")
        print("  python3 main.py analyze data.csv")
        print("  python3 main.py clean data.csv json")
        sys.exit(1)

    action = sys.argv[1]
    file_path = sys.argv[2]

    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}")
        sys.exit(1)

    if action == "analyze":
        analysis_type = sys.argv[3] if len(sys.argv) > 3 else "summary"
        result = analyze_csv(file_path, analysis_type)
        print(f"Analysis saved to: {result}")
    elif action == "clean":
        output_format = sys.argv[3] if len(sys.argv) > 3 else "csv"
        result = clean_data(file_path, output_format)
        print(f"Cleaned data saved to: {result}")
    else:
        print(f"Unknown action: {action}")
        sys.exit(1)

if __name__ == "__main__":
    main()
