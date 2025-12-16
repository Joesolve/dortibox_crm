# Waste Collection Management System

A comprehensive web-based application for managing waste collection operations, built with Flask and SQLite.

## Features

### Admin Features
- **Dashboard**: Overview of operations with key statistics
- **Customer Management**: Add, edit, delete, and search customers
- **Pickup Tracking**: View all pickups by date with completion status
- **User Management**: Create and manage collector accounts
- **Full CRUD Operations**: Complete control over all operational data

### Collector Features
- **Daily Pickup View**: See all scheduled pickups for today
- **Route Organization**: Pickups organized by address
- **Quick Completion**: One-click pickup completion with optional notes
- **Status Tracking**: Visual distinction between completed and pending pickups
- **Real-time Updates**: Instant feedback on completion status

## System Requirements

- Python 3.8 or higher
- pip (Python package installer)

## Installation & Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Import Your Data

Import your existing customer data from the Excel file:

```bash
python import_data.py /path/to/COMMERCIAL_MASTER_LOG__2_.xlsx
```

This will:
- Create the database
- Import all customer records
- Create default admin and collector accounts

### 3. Run the Application

```bash
python app.py
```

The application will be accessible at: `http://localhost:5000`

## Default Login Credentials

### Admin Account
- **Username**: `admin`
- **Password**: `admin123`
- **Access**: Full system access

### Collector Account
- **Username**: `collector`
- **Password**: `collector123`
- **Access**: View and complete pickups only

**⚠️ IMPORTANT**: Change these default passwords in production!

## Usage Guide

### For Administrators

#### Managing Customers
1. Navigate to "Customers" from the dashboard
2. Use the search bar to find specific customers
3. Click "Add Customer" to create new entries
4. Click the pencil icon to edit existing customers
5. Click the trash icon to delete customers

#### Viewing Pickups
1. Navigate to "Pickups" from the dashboard
2. Use the date filter to view pickups for any date
3. Monitor completion status (Green = Completed, Yellow = Pending)
4. View collector notes and completion times

#### Managing Users
1. Navigate to "Users" from the dashboard
2. Click "Add User" to create new accounts
3. Assign appropriate roles (Admin or Collector)
4. Delete inactive users as needed

### For Collectors

#### Daily Workflow
1. Log in with your collector credentials
2. View all pickups scheduled for today
3. Pickups are displayed as cards with customer information
4. Click "Mark as Completed" when a pickup is done
5. Optionally add notes about the pickup
6. Completed pickups turn green and move to the bottom

#### Pickup Cards Show:
- Customer name and address
- Phone number
- Pickup time
- Number and size of bins
- Current completion status

## Data Structure

### Customer Information
- Basic details (name, address, phone)
- Service details (bin size, quantity, frequency)
- Weekly schedule (which days pickup is needed)
- Subscription dates and active status
- Payment information

### Pickup Records
- Automatic creation based on customer schedules
- Tracks completion status
- Records who completed the pickup and when
- Stores optional notes

## Database

The application uses SQLite for data storage:
- **Location**: `waste_collection.db`
- **Automatic backup**: Consider implementing regular backups
- **Portable**: Can be easily moved between systems

## File Structure

```
waste_collection_app/
├── app.py                  # Main application file
├── import_data.py          # Data import script
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── templates/             # HTML templates
│   ├── base.html
│   ├── login.html
│   ├── admin_dashboard.html
│   ├── collector_dashboard.html
│   ├── admin_customers.html
│   ├── add_customer.html
│   ├── edit_customer.html
│   ├── admin_pickups.html
│   ├── admin_users.html
│   └── add_user.html
└── waste_collection.db    # SQLite database (created after first run)
```

## Key Features Explained

### Automatic Pickup Generation
- The system automatically creates pickup records for collectors
- Based on customer schedules (Monday-Saturday)
- Only shows active customers
- Updates in real-time

### Schedule Management
- Customers can have pickups on any combination of days
- Each day is individually configurable
- Visual indicators (M, T, W, Th, F, S) show the schedule
- Easy to modify via the edit customer form

### Status Tracking
- **Active**: Customer subscription is current
- **Inactive**: Customer subscription has ended
- **Completed**: Pickup has been done
- **Pending**: Pickup is scheduled but not yet completed

## Customization

### Changing Default Credentials
Edit the `init_database()` function in `app.py`:

```python
admin.set_password('your_new_password')
collector.set_password('your_new_password')
```

### Modifying Bin Sizes
Bin sizes are stored as text, allowing flexibility:
- Standard sizes: "Small", "Medium", "Large"
- Specific sizes: "240L", "660L", "1100L"
- Custom descriptions as needed

### Adding Fields
To add new customer fields:
1. Update the `Customer` model in `app.py`
2. Add form fields in `add_customer.html` and `edit_customer.html`
3. Update the form processing in the routes
4. Run migrations if needed

## Troubleshooting

### Database Issues
If you encounter database errors:
```bash
# Delete the database and reimport
rm waste_collection.db
python import_data.py /path/to/excel_file.xlsx
```

### Port Already in Use
If port 5000 is occupied, change it in `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5001)  # Use different port
```

### Missing Pickups
Pickups are generated automatically when collectors view their dashboard.
If pickups are missing:
1. Check that the customer is marked as "Active"
2. Verify the correct day is selected in the customer's schedule
3. Refresh the collector dashboard

## Security Notes

⚠️ **Important Security Considerations**:

1. **Change Default Passwords**: The default credentials are for initial setup only
2. **Secret Key**: Change the `SECRET_KEY` in production:
   ```python
   app.config['SECRET_KEY'] = 'your-secure-random-key'
   ```
3. **HTTPS**: Use HTTPS in production environments
4. **Database Backups**: Implement regular backup procedures
5. **User Management**: Remove unused accounts regularly

## Support & Maintenance

### Regular Maintenance Tasks
- Weekly database backups
- Review and archive old pickup records
- Update customer information as needed
- Add new collectors as staff grows

### Data Export
To export data for analysis:
```python
# Example: Export customers to CSV
import pandas as pd
from app import app, Customer
with app.app_context():
    customers = Customer.query.all()
    # Process and export as needed
```

## Future Enhancements

Potential features for future versions:
- Route optimization for collectors
- SMS/Email notifications
- Mobile app for collectors
- Advanced reporting and analytics
- Integration with accounting systems
- Photo upload for completed pickups
- Customer portal for self-service

## License

This application is provided as-is for business operations management.

## Credits

Built with:
- Flask (Python web framework)
- Bootstrap 5 (Frontend framework)
- SQLAlchemy (Database ORM)
- pandas (Data processing)
