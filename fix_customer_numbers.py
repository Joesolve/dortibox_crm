"""
Run this script to fix all customer numbers in the database.
This will renumber all customers sequentially starting from 1.

Usage: python fix_customer_numbers.py
"""

from app import app, db, Customer

def fix_customer_numbers():
    """Fix all customer numbers to be sequential starting from 1"""
    with app.app_context():
        # Get all customers ordered by their ID (or you can order by created date if available)
        customers = Customer.query.order_by(Customer.id).all()
        
        print(f"Found {len(customers)} customers to renumber...")
        
        # Renumber them sequentially
        for index, customer in enumerate(customers, start=1):
            old_number = customer.customer_number
            customer.customer_number = index
            print(f"Customer ID {customer.id}: '{customer.customer_name}' - Changed from {old_number} to {index}")
        
        # Commit all changes
        db.session.commit()
        print("\n✓ All customer numbers have been fixed!")
        print(f"✓ {len(customers)} customers now numbered from 1 to {len(customers)}")

if __name__ == '__main__':
    fix_customer_numbers()