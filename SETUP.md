# Quick Setup Guide

## 🚀 Getting Started in 3 Steps

### Step 1: Install Python
Make sure you have Python 3.8+ installed on your computer.
- Download from: https://www.python.org/downloads/
- During installation, check "Add Python to PATH"

### Step 2: Install Dependencies
Open a terminal/command prompt in this folder and run:

**Windows:**
```
pip install -r requirements.txt
```

**Mac/Linux:**
```
pip3 install -r requirements.txt
```

### Step 3: Start the Application

**Windows:**
- Double-click `start.bat`

**Mac/Linux:**
```bash
./start.sh
```

Or run directly:
```bash
python app.py
```

## 📱 Access the Application

Once started, open your web browser and go to:
```
http://localhost:5000
```

## 🔐 Login

### Admin Account (Full Access)
- **Username:** admin
- **Password:** admin123

### Collector Account (View & Complete Pickups)
- **Username:** collector
- **Password:** collector123

## ✅ What's Already Done

✓ Database created with SQLite
✓ All 221 customers imported from your Excel file
✓ Admin and Collector accounts created
✓ All templates and routes configured

## 📋 Quick Feature Overview

### As Admin, you can:
- View dashboard with statistics
- Add, edit, delete customers
- Search and filter customers
- View all pickups by date
- Manage user accounts
- See completion status

### As Collector, you can:
- View today's scheduled pickups
- See customer details and addresses
- Mark pickups as completed
- Add notes about each pickup
- See completion history

## 🔧 Common Tasks

### Import New Data
To re-import or update customer data:
```bash
python import_data.py path/to/your_excel_file.xlsx
```

### Create New Users
1. Login as admin
2. Go to Users menu
3. Click "Add User"
4. Fill in details and select role

### Backup Database
Simply copy the file:
```
waste_collection.db
```

## 🆘 Troubleshooting

**Port Already in Use?**
Edit `app.py` and change the port number:
```python
app.run(debug=True, host='0.0.0.0', port=5001)
```

**Module Not Found Error?**
Make sure you installed dependencies:
```bash
pip install -r requirements.txt
```

**Database Error?**
Delete the database and reimport:
```bash
rm waste_collection.db
python import_data.py path/to/excel_file.xlsx
```

## 📞 Support

For detailed documentation, see the `README.md` file.

## 🔒 Security Note

⚠️ **IMPORTANT**: Change the default passwords before using in production!

1. Login as admin
2. Go to Users
3. Create new admin user with secure password
4. Delete the default admin account

---

**Enjoy using your Waste Collection Management System!** 🎉
