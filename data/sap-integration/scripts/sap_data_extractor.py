#!/usr/bin/env python3
"""
SAP Data Extractor - Generic table data extraction with RFC
Built by SAPCONET for enterprise SAP automation
"""

import pyrfc
import pandas as pd
import json
import sys
from typing import Dict, List, Optional, Any
from datetime import datetime

class SAPDataExtractor:
    """Generic SAP data extraction utility using RFC connections"""
    
    def __init__(self, connection_params: Dict[str, str]):
        """Initialize SAP connection"""
        try:
            self.conn = pyrfc.Connection(**connection_params)
            print(f"✅ Connected to SAP system: {connection_params.get('ashost', 'Unknown')}")
        except Exception as e:
            print(f"❌ SAP connection failed: {str(e)}")
            sys.exit(1)
    
    def extract_table_data(self, table_name: str, fields: Optional[List[str]] = None, 
                          where_clause: str = "", max_rows: int = 10000) -> pd.DataFrame:
        """
        Extract data from any SAP table using RFC_READ_TABLE
        
        Args:
            table_name: SAP table name (e.g., 'KNA1', 'VBAK', 'MARA')
            fields: List of fields to extract (None = all fields)
            where_clause: SQL WHERE clause condition
            max_rows: Maximum number of rows to extract
            
        Returns:
            pandas DataFrame with extracted data
        """
        try:
            # Prepare RFC call parameters
            params = {
                'QUERY_TABLE': table_name,
                'DELIMITER': '|',
                'ROWCOUNT': max_rows
            }
            
            # Add field selection if specified
            if fields:
                field_list = [{'FIELDNAME': field} for field in fields]
                params['FIELDS'] = field_list
            
            # Add WHERE clause if specified
            if where_clause:
                # Split long WHERE clauses into 72-character chunks
                where_parts = []
                for i in range(0, len(where_clause), 72):
                    where_parts.append({'TEXT': where_clause[i:i+72]})
                params['OPTIONS'] = where_parts
            
            print(f"🔄 Extracting data from table {table_name}...")
            
            # Execute RFC call
            result = self.conn.call('RFC_READ_TABLE', **params)
            
            # Parse results
            field_names = [field['FIELDNAME'] for field in result['FIELDS']]
            
            # Convert data rows to structured format
            data_rows = []
            for row in result['DATA']:
                row_data = row['WA'].split('|')
                # Ensure we have the right number of columns
                if len(row_data) == len(field_names):
                    data_rows.append(row_data)
                else:
                    print(f"⚠️ Skipping malformed row: {row['WA']}")
            
            # Create DataFrame
            df = pd.DataFrame(data_rows, columns=field_names)
            
            # Clean whitespace
            df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
            
            print(f"✅ Extracted {len(df)} rows from {table_name}")
            return df
            
        except Exception as e:
            print(f"❌ Error extracting from {table_name}: {str(e)}")
            return pd.DataFrame()
    
    def get_table_structure(self, table_name: str) -> pd.DataFrame:
        """Get table field definitions and metadata"""
        try:
            result = self.conn.call('RFC_READ_TABLE',
                                   QUERY_TABLE='DD03L',
                                   DELIMITER='|',
                                   FIELDS=[
                                       {'FIELDNAME': 'FIELDNAME'},
                                       {'FIELDNAME': 'DATATYPE'},
                                       {'FIELDNAME': 'LENG'},
                                       {'FIELDNAME': 'DECIMALS'},
                                       {'FIELDNAME': 'DOMNAME'},
                                       {'FIELDNAME': 'DDTEXT'}
                                   ],
                                   OPTIONS=[{'TEXT': f"TABNAME = '{table_name}' AND AS4LOCAL = 'A'"}])
            
            field_names = [field['FIELDNAME'] for field in result['FIELDS']]
            data_rows = []
            for row in result['DATA']:
                row_data = row['WA'].split('|')
                if len(row_data) == len(field_names):
                    data_rows.append(row_data)
            
            df = pd.DataFrame(data_rows, columns=field_names)
            print(f"✅ Retrieved structure for table {table_name}")
            return df
            
        except Exception as e:
            print(f"❌ Error getting table structure: {str(e)}")
            return pd.DataFrame()
    
    def extract_custom_query(self, query_definition: Dict[str, Any]) -> pd.DataFrame:
        """
        Execute predefined query configurations
        
        Query definition format:
        {
            "name": "Customer Master Data",
            "table": "KNA1", 
            "fields": ["KUNNR", "NAME1", "ORT01", "LAND1"],
            "where": "ERDAT >= '20240101'",
            "joins": [
                {"table": "KNVV", "on": "KUNNR = KUNNR", "fields": ["VKORG", "VTWEG"]}
            ]
        }
        """
        try:
            print(f"🔄 Executing query: {query_definition.get('name', 'Unnamed')}")
            
            # Start with main table
            main_df = self.extract_table_data(
                table_name=query_definition['table'],
                fields=query_definition.get('fields'),
                where_clause=query_definition.get('where', ''),
                max_rows=query_definition.get('max_rows', 10000)
            )
            
            # Handle joins if specified
            if 'joins' in query_definition and not main_df.empty:
                for join_def in query_definition['joins']:
                    join_df = self.extract_table_data(
                        table_name=join_def['table'],
                        fields=join_def.get('fields'),
                        max_rows=query_definition.get('max_rows', 10000)
                    )
                    
                    if not join_df.empty:
                        # Simple join on specified field
                        join_field = join_def['on'].split('=')[0].strip()
                        main_df = pd.merge(main_df, join_df, on=join_field, how='left')
            
            return main_df
            
        except Exception as e:
            print(f"❌ Error executing custom query: {str(e)}")
            return pd.DataFrame()
    
    def export_to_excel(self, data: pd.DataFrame, filename: str, sheet_name: str = 'SAP_Data'):
        """Export DataFrame to Excel with formatting"""
        try:
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                data.to_excel(writer, sheet_name=sheet_name, index=False)
                
                # Add some basic formatting
                worksheet = writer.sheets[sheet_name]
                
                # Auto-adjust column widths
                for idx, col in enumerate(data.columns):
                    max_length = max(len(str(col)), data[col].astype(str).str.len().max())
                    worksheet.column_dimensions[chr(65 + idx)].width = min(max_length + 2, 50)
                
                # Add header formatting
                for cell in worksheet[1]:
                    cell.font = cell.font.copy(bold=True)
                    
            print(f"✅ Data exported to {filename}")
            
        except Exception as e:
            print(f"❌ Error exporting to Excel: {str(e)}")
    
    def close_connection(self):
        """Clean up SAP connection"""
        try:
            self.conn.close()
            print("✅ SAP connection closed")
        except:
            pass

def load_connection_config(config_file: str) -> Dict[str, str]:
    """Load SAP connection parameters from JSON config file"""
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        # Validate required parameters
        required_params = ['ashost', 'sysnr', 'client', 'user', 'passwd']
        for param in required_params:
            if param not in config:
                raise ValueError(f"Missing required parameter: {param}")
        
        return config
        
    except Exception as e:
        print(f"❌ Error loading config: {str(e)}")
        sys.exit(1)

def main():
    """Main execution function with command-line interface"""
    if len(sys.argv) < 2:
        print("Usage: python sap_data_extractor.py <config_file> [table_name] [output_file]")
        print("\nExample:")
        print("  python sap_data_extractor.py sap_config.json KNA1 customer_data.xlsx")
        sys.exit(1)
    
    config_file = sys.argv[1]
    table_name = sys.argv[2] if len(sys.argv) > 2 else None
    output_file = sys.argv[3] if len(sys.argv) > 3 else None
    
    # Load configuration
    config = load_connection_config(config_file)
    
    # Initialize extractor
    extractor = SAPDataExtractor(config)
    
    try:
        if table_name:
            # Extract specific table
            data = extractor.extract_table_data(table_name)
            
            if not data.empty:
                print(f"\n📊 Sample data from {table_name}:")
                print(data.head())
                print(f"\nTotal rows: {len(data)}")
                
                # Export if filename provided
                if output_file:
                    extractor.export_to_excel(data, output_file, table_name)
            else:
                print(f"❌ No data found in table {table_name}")
        else:
            # Interactive mode
            print("\n🔧 SAP Data Extractor - Interactive Mode")
            print("Available commands:")
            print("  table <name> - Extract data from table")
            print("  structure <name> - Show table structure")
            print("  export <filename> - Export last result to Excel")
            print("  quit - Exit")
            
            last_data = pd.DataFrame()
            
            while True:
                command = input("\n> ").strip().split()
                
                if not command:
                    continue
                    
                if command[0] == 'quit':
                    break
                elif command[0] == 'table' and len(command) > 1:
                    last_data = extractor.extract_table_data(command[1])
                    if not last_data.empty:
                        print(last_data.head(10))
                elif command[0] == 'structure' and len(command) > 1:
                    structure = extractor.get_table_structure(command[1])
                    if not structure.empty:
                        print(structure)
                elif command[0] == 'export' and len(command) > 1:
                    if not last_data.empty:
                        extractor.export_to_excel(last_data, command[1])
                    else:
                        print("❌ No data to export")
                else:
                    print("❌ Invalid command")
    
    finally:
        extractor.close_connection()

if __name__ == "__main__":
    main()