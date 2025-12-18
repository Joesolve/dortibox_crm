"""
Script to inspect the Excel file structure before importing
Run this first to verify the file is correct
"""

import sys
import os
import pandas as pd

def inspect_excel(excel_file):
    """Inspect Excel file structure"""
    try:
        print("="*70)
        print("Excel File Inspector")
        print("="*70)
        print(f"\nFile: {excel_file}")
        
        # Load Excel file
        xl_file = pd.ExcelFile(excel_file)
        
        print(f"\n📊 Sheet Names:")
        for i, sheet in enumerate(xl_file.sheet_names, 1):
            print(f"   {i}. {sheet}")
        
        # Read first sheet
        print(f"\n📋 Analyzing first sheet: {xl_file.sheet_names[0]}")
        
        # Try different header positions
        for header_row in [0, 1]:
            try:
                df = pd.read_excel(excel_file, sheet_name=0, header=header_row)
                df.columns = df.columns.str.strip()
                
                print(f"\n   Header at row {header_row}:")
                print(f"   Shape: {df.shape[0]} rows x {df.shape[1]} columns")
                
                print(f"\n   Columns:")
                for i, col in enumerate(df.columns, 1):
                    print(f"      {i}. {col}")
                
                print(f"\n   First 3 rows of data:")
                print(df.head(3).to_string())
                
                # Check for customer data indicators
                has_customer_name = any('customer' in str(col).lower() for col in df.columns)
                has_number = any('number' in str(col).lower() for col in df.columns)
                has_address = any('address' in str(col).lower() for col in df.columns)
                
                if has_customer_name and (has_number or has_address):
                    print(f"\n   ✓ This looks like customer data!")
                    print(f"     - Customer names: {'Yes' if has_customer_name else 'No'}")
                    print(f"     - Customer numbers: {'Yes' if has_number else 'No'}")
                    print(f"     - Addresses: {'Yes' if has_address else 'No'}")
                    
                    # Count non-empty rows
                    if 'Number' in df.columns:
                        valid_rows = df[df['Number'].notna()].shape[0]
                    elif any('customer' in str(col).lower() for col in df.columns):
                        customer_col = [col for col in df.columns if 'customer' in str(col).lower()][0]
                        valid_rows = df[df[customer_col].notna()].shape[0]
                    else:
                        valid_rows = df.shape[0]
                    
                    print(f"     - Valid customer records: {valid_rows}")
                    
                    break
            except Exception as e:
                print(f"\n   Could not read with header at row {header_row}: {e}")
        
        print("\n" + "="*70)
        print("✓ Inspection complete!")
        print("\nIf the data looks correct, run:")
        print(f"  python reimport_data.py \"{excel_file}\"")
        print("="*70)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python inspect_excel.py <path_to_excel_file>")
        print("\nExample:")
        print("  python inspect_excel.py \"COMMERCIAL MASTER LOG 3.xlsx\"")
        sys.exit(1)
    
    excel_file = sys.argv[1]
    
    if not os.path.exists(excel_file):
        print(f"❌ Error: File not found: {excel_file}")
        sys.exit(1)
    
    inspect_excel(excel_file)