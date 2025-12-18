"""
Script to re-import customer data from the correct Excel file
Run this to replace the existing data with correct data
"""

import sys
import os
from datetime import datetime
import pandas as pd
from app import app, db, Customer

def reimport_customers(excel_file):
    """Re-import customers from the correct Excel file"""
    with app.app_context():
        try:
            # Read Excel file
            print(f"Reading Excel file: {excel_file}")
            
            # First, check the sheet names
            xl_file = pd.ExcelFile(excel_file)
            print(f"Available sheets: {xl_file.sheet_names}")
            
            # Try to read the first sheet or 'Service Log' sheet
            if 'Service Log' in xl_file.sheet_names:
                df = pd.read_excel(excel_file, sheet_name='Service Log', header=1)
            else:
                # Try first sheet with different header positions
                df = pd.read_excel(excel_file, sheet_name=0)
                
                # Check if first row looks like headers
                if 'Number' not in df.columns and 'Customer' not in df.columns:
                    # Try with header at row 1
                    df = pd.read_excel(excel_file, sheet_name=0, header=1)
            
            # Clean column names
            df.columns = df.columns.str.strip()
            
            print(f"\nColumns found: {list(df.columns)}")
            print(f"Total rows: {len(df)}")
            
            # Show first few rows
            print("\nFirst 5 rows:")
            print(df.head())
            
            # Map column names (handle variations)
            column_mapping = {
                'Number': 'Number',
                'Customer Name': 'Customer Name',
                'Customer': 'Customer Name',
                'Address': 'Address',
                'Phone Number': 'Phone Number',
                'Phone': 'Phone Number',
                'Type': 'Type',
                'Ward': 'Ward',
                'Bin Size': 'Bin Size',
                'Bin Qty': 'Bin Qty',
                'Frequency': 'Frequency',
                'Time': 'Time',
                'Mon': 'Mon',
                'Monday': 'Mon',
                'Tue': 'Tue',
                'Tuesday': 'Tue',
                'Wed': 'Wed',
                'Wednesday': 'Wed',
                'Thurs': 'Thurs',
                'Thursday': 'Thurs',
                'Fri': 'Fri',
                'Friday': 'Fri',
                'Sat': 'Sat',
                'Saturday': 'Sat',
                'Sales Rep': 'Sales Rep',
                'Payment Type': 'Payment Type',
                'Subscription Start': 'Subscription Start',
                'Subscription End': 'Subscription End',
                'Active in Target Month?': 'Active in Target Month?',
                'Active': 'Active in Target Month?',
                'MONTH ACQUIRED': 'MONTH ACQUIRED',
                'Month Acquired': 'MONTH ACQUIRED',
                'Amt Paid SLL': 'Amt Paid SLL',
                'Amount Paid': 'Amt Paid SLL'
            }
            
            # Rename columns if they match mapping
            for old_col, new_col in column_mapping.items():
                if old_col in df.columns and old_col != new_col:
                    df.rename(columns={old_col: new_col}, inplace=True)
            
            # Drop rows where customer number is NaN (duplicate/blank rows)
            if 'Number' in df.columns:
                df = df[df['Number'].notna()]
            
            print(f"\nRows after cleaning: {len(df)}")
            
            # Confirm before deleting existing data
            print("\n" + "="*60)
            print("⚠️  WARNING: This will DELETE all existing customer data!")
            print("="*60)
            confirm = input("Type 'YES' to continue: ")
            
            if confirm != 'YES':
                print("Import cancelled.")
                return
            
            # Clear existing customers
            print("\nDeleting existing customer data...")
            deleted = Customer.query.delete()
            print(f"Deleted {deleted} existing customers")
            db.session.commit()
            
            # Import each customer
            print("\nImporting new customer data...")
            imported = 0
            errors = 0
            
            for idx, row in df.iterrows():
                try:
                    # Parse dates
                    sub_start = None
                    sub_end = None
                    
                    if 'Subscription Start' in row and pd.notna(row['Subscription Start']):
                        try:
                            if isinstance(row['Subscription Start'], str):
                                sub_start = datetime.strptime(row['Subscription Start'], '%Y-%m-%d').date()
                            else:
                                sub_start = row['Subscription Start'].date()
                        except:
                            pass
                    
                    if 'Subscription End' in row and pd.notna(row['Subscription End']):
                        try:
                            if isinstance(row['Subscription End'], str):
                                sub_end = datetime.strptime(row['Subscription End'], '%Y-%m-%d').date()
                            else:
                                sub_end = row['Subscription End'].date()
                        except:
                            pass
                    
                    # Get customer name
                    customer_name = str(row.get('Customer Name', '')) if pd.notna(row.get('Customer Name')) else ''
                    if not customer_name:
                        print(f"Skipping row {idx} - no customer name")
                        continue
                    
                    # Create customer object
                    customer = Customer(
                        customer_number=int(row['Number']) if 'Number' in row and pd.notna(row['Number']) else None,
                        customer_name=customer_name,
                        address=str(row['Address']) if 'Address' in row and pd.notna(row['Address']) else None,
                        phone_number=str(row['Phone Number']) if 'Phone Number' in row and pd.notna(row['Phone Number']) else None,
                        type=str(row['Type']) if 'Type' in row and pd.notna(row['Type']) else None,
                        ward=str(row['Ward']) if 'Ward' in row and pd.notna(row['Ward']) else None,
                        bin_size=str(row['Bin Size']) if 'Bin Size' in row and pd.notna(row['Bin Size']) else None,
                        bin_qty=int(row['Bin Qty']) if 'Bin Qty' in row and pd.notna(row['Bin Qty']) else None,
                        frequency=str(row['Frequency']) if 'Frequency' in row and pd.notna(row['Frequency']) else None,
                        time=str(row['Time']) if 'Time' in row and pd.notna(row['Time']) else None,
                        monday=1 if 'Mon' in row and pd.notna(row['Mon']) and row['Mon'] == 1 else 0,
                        tuesday=1 if 'Tue' in row and pd.notna(row['Tue']) and row['Tue'] == 1 else 0,
                        wednesday=1 if 'Wed' in row and pd.notna(row['Wed']) and row['Wed'] == 1 else 0,
                        thursday=1 if 'Thurs' in row and pd.notna(row['Thurs']) and row['Thurs'] == 1 else 0,
                        friday=1 if 'Fri' in row and pd.notna(row['Fri']) and row['Fri'] == 1 else 0,
                        saturday=1 if 'Sat' in row and pd.notna(row['Sat']) and row['Sat'] == 1 else 0,
                        sales_rep=str(row['Sales Rep']) if 'Sales Rep' in row and pd.notna(row['Sales Rep']) else None,
                        payment_type=str(row['Payment Type']) if 'Payment Type' in row and pd.notna(row['Payment Type']) else None,
                        subscription_start=sub_start,
                        subscription_end=sub_end,
                        active=str(row['Active in Target Month?']) if 'Active in Target Month?' in row and pd.notna(row['Active in Target Month?']) else 'No',
                        month_acquired=str(row['MONTH ACQUIRED']) if 'MONTH ACQUIRED' in row and pd.notna(row['MONTH ACQUIRED']) else None,
                        amount_paid=float(row['Amt Paid SLL']) if 'Amt Paid SLL' in row and pd.notna(row['Amt Paid SLL']) else None
                    )
                    
                    db.session.add(customer)
                    imported += 1
                    
                    if imported % 50 == 0:
                        print(f"Imported {imported} customers...")
                        db.session.commit()
                        
                except Exception as e:
                    print(f"Error importing row {idx}: {e}")
                    errors += 1
                    continue
            
            # Commit remaining changes
            db.session.commit()
            
            print("\n" + "="*60)
            print(f"✓ Import Complete!")
            print(f"  Successfully imported: {imported} customers")
            if errors > 0:
                print(f"  Errors encountered: {errors} rows")
            print("="*60)
            
        except Exception as e:
            print(f"\n❌ Error during import: {e}")
            import traceback
            traceback.print_exc()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python reimport_data.py <path_to_excel_file>")
        print("\nExample:")
        print("  python reimport_data.py \"COMMERCIAL MASTER LOG 3.xlsx\"")
        sys.exit(1)
    
    excel_file = sys.argv[1]
    
    if not os.path.exists(excel_file):
        print(f"❌ Error: File not found: {excel_file}")
        sys.exit(1)
    
    reimport_customers(excel_file)