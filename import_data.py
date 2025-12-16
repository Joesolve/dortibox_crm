"""
Import customer data from Excel file into the database
"""
import sys
import os
from datetime import datetime
import pandas as pd
from app import app, db, Customer

def import_customers(excel_file):
    """Import customers from Excel file"""
    with app.app_context():
        # Create all tables
        print("Creating database tables...")
        db.create_all()
        
        # Read Excel file
        print(f"Reading Excel file: {excel_file}")
        df = pd.read_excel(excel_file, sheet_name='Service Log', header=1)
        
        # Clean column names
        df.columns = df.columns.str.strip()
        
        # Drop rows where customer_number is NaN (duplicate rows)
        df = df[df['Number'].notna()]
        
        # Clear existing customers
        print("Clearing existing customer data...")
        Customer.query.delete()
        db.session.commit()
        
        # Import each customer
        print("Importing customers...")
        imported = 0
        for idx, row in df.iterrows():
            try:
                # Parse dates
                sub_start = None
                sub_end = None
                
                if pd.notna(row['Subscription Start']):
                    try:
                        if isinstance(row['Subscription Start'], str):
                            sub_start = datetime.strptime(row['Subscription Start'], '%Y-%m-%d').date()
                        else:
                            sub_start = row['Subscription Start'].date()
                    except:
                        pass
                
                if pd.notna(row['Subscription End']):
                    try:
                        if isinstance(row['Subscription End'], str):
                            sub_end = datetime.strptime(row['Subscription End'], '%Y-%m-%d').date()
                        else:
                            sub_end = row['Subscription End'].date()
                    except:
                        pass
                
                # Create customer object
                customer = Customer(
                    customer_number=int(row['Number']) if pd.notna(row['Number']) else None,
                    customer_name=str(row['Customer Name']) if pd.notna(row['Customer Name']) else '',
                    address=str(row['Address']) if pd.notna(row['Address']) else None,
                    phone_number=str(row['Phone Number']) if pd.notna(row['Phone Number']) else None,
                    type=str(row['Type']) if pd.notna(row['Type']) else None,
                    ward=str(row['Ward']) if pd.notna(row['Ward']) else None,
                    bin_size=str(row['Bin Size']) if pd.notna(row['Bin Size']) else None,
                    bin_qty=int(row['Bin Qty']) if pd.notna(row['Bin Qty']) else None,
                    frequency=str(row['Frequency']) if pd.notna(row['Frequency']) else None,
                    time=str(row['Time']) if pd.notna(row['Time']) else None,
                    monday=1 if pd.notna(row['Mon']) and row['Mon'] == 1 else 0,
                    tuesday=1 if pd.notna(row['Tue']) and row['Tue'] == 1 else 0,
                    wednesday=1 if pd.notna(row['Wed']) and row['Wed'] == 1 else 0,
                    thursday=1 if pd.notna(row['Thurs']) and row['Thurs'] == 1 else 0,
                    friday=1 if pd.notna(row['Fri']) and row['Fri'] == 1 else 0,
                    saturday=1 if pd.notna(row['Sat']) and row['Sat'] == 1 else 0,
                    sales_rep=str(row['Sales Rep']) if pd.notna(row['Sales Rep']) else None,
                    payment_type=str(row['Payment Type']) if pd.notna(row['Payment Type']) else None,
                    subscription_start=sub_start,
                    subscription_end=sub_end,
                    active=str(row['Active in Target Month?']) if pd.notna(row['Active in Target Month?']) else 'No',
                    month_acquired=str(row['MONTH ACQUIRED']) if pd.notna(row['MONTH ACQUIRED']) else None,
                    amount_paid=float(row['Amt Paid SLL']) if pd.notna(row['Amt Paid SLL']) else None
                )
                
                db.session.add(customer)
                imported += 1
                
                if imported % 50 == 0:
                    print(f"Imported {imported} customers...")
                    
            except Exception as e:
                print(f"Error importing row {idx}: {e}")
                continue
        
        # Commit all changes
        db.session.commit()
        print(f"\nSuccessfully imported {imported} customers!")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python import_data.py <path_to_excel_file>")
        sys.exit(1)
    
    excel_file = sys.argv[1]
    
    if not os.path.exists(excel_file):
        print(f"Error: File not found: {excel_file}")
        sys.exit(1)
    
    import_customers(excel_file)
