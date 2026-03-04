#!/usr/bin/env python3
"""
Clean dataset for Data Annotation platform.
Handles common cleaning tasks: column renaming, duplicate removal, missing value handling.
"""

import pandas as pd
import sys
import argparse
from pathlib import Path

def clean_dataset(input_path, output_path=None):
    """
    Clean a dataset for upload to Data Annotation platform.
    
    Args:
        input_path: Path to input CSV file
        output_path: Path for cleaned output (optional, defaults to input_cleaned.csv)
    
    Returns:
        Path to cleaned file
    """
    input_path = Path(input_path)
    
    if output_path is None:
        output_path = input_path.parent / f"{input_path.stem}_cleaned.csv"
    else:
        output_path = Path(output_path)
    
    print(f"Loading dataset: {input_path}")
    df = pd.read_csv(input_path)
    
    original_shape = df.shape
    print(f"Original shape: {original_shape}")
    
    # Clean column names - remove spaces, special chars
    df.columns = df.columns.str.strip()
    
    # Remove completely duplicate rows
    df = df.drop_duplicates()
    
    # Handle missing values
    # For numeric columns: fill with median
    numeric_cols = df.select_dtypes(include=['number']).columns
    for col in numeric_cols:
        if df[col].isna().sum() > 0:
            median_val = df[col].median()
            df[col] = df[col].fillna(median_val)
            print(f"  Filled {col} missing values with median: {median_val}")
    
    # For categorical/string columns: fill with mode or 'Unknown'
    categorical_cols = df.select_dtypes(include=['object']).columns
    for col in categorical_cols:
        if df[col].isna().sum() > 0:
            mode_val = df[col].mode()
            if len(mode_val) > 0:
                df[col] = df[col].fillna(mode_val[0])
                print(f"  Filled {col} missing values with mode: {mode_val[0]}")
            else:
                df[col] = df[col].fillna('Unknown')
                print(f"  Filled {col} missing values with 'Unknown'")
    
    # Ensure timestamp column is properly formatted if present
    timestamp_cols = [col for col in df.columns if 'time' in col.lower() or 'date' in col.lower()]
    for col in timestamp_cols:
        try:
            df[col] = pd.to_datetime(df[col])
            print(f"  Converted {col} to datetime")
        except:
            pass
    
    final_shape = df.shape
    print(f"Final shape: {final_shape}")
    print(f"Removed {original_shape[0] - final_shape[0]} duplicate rows")
    
    # Save cleaned dataset
    df.to_csv(output_path, index=False)
    print(f"Saved cleaned dataset to: {output_path}")
    
    # Print column summary for metadata configuration
    print("\n" + "="*60)
    print("COLUMN SUMMARY FOR METADATA CONFIGURATION:")
    print("="*60)
    for col in df.columns:
        dtype = str(df[col].dtype)
        sample = str(df[col].iloc[0]) if len(df) > 0 else "N/A"
        print(f"  {col}: {dtype} (sample: {sample[:50]})")
    
    return output_path

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Clean dataset for Data Annotation platform")
    parser.add_argument("input", help="Input CSV file path")
    parser.add_argument("-o", "--output", help="Output file path (optional)")
    
    args = parser.parse_args()
    clean_dataset(args.input, args.output)
