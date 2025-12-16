# Complete Usage Guide

## Table of Contents
1. [First Time Login](#first-time-login)
2. [Admin Features](#admin-features)
3. [Collector Features](#collector-features)
4. [Daily Workflows](#daily-workflows)

---

## First Time Login

### Starting the Application
1. Run `start.bat` (Windows) or `./start.sh` (Mac/Linux)
2. Open browser to http://localhost:5000
3. You'll see the login page

### Login Credentials
Use the default credentials provided in SETUP.md

---

## Admin Features

### 1. Dashboard Overview

When you login as admin, you'll see:
- **Total Customers**: Count of all customers in system
- **Active Customers**: Customers with active subscriptions
- **Today's Pickups**: Number of pickups scheduled for today
- **Completed Today**: How many have been marked as done

**Quick Actions:**
- Add New Customer
- View All Customers
- View Today's Pickups
- Add New User

### 2. Customer Management

#### Viewing Customers
- Navigate to "Customers" from the menu
- See list of all customers with key information
- Use pagination to browse (20 customers per page)

**Columns Shown:**
- Customer number
- Name
- Address
- Phone
- Ward
- Bin size and quantity
- Schedule (M, T, W, Th, F, S)
- Status (Active/Inactive)

#### Searching Customers
- Use the search bar at the top
- Search by: name, address, or phone number
- Results update automatically

#### Adding a New Customer

1. Click "Add Customer" button
2. Fill in the form with customer details:

**Basic Information:**
- Customer Number (optional)
- Customer Name (required)
- Address
- Phone Number
- Type (e.g., Commercial, Residential)
- Ward

**Service Details:**
- Bin Size (e.g., 240L, 660L)
- Bin Quantity (number of bins)
- Frequency
- Pickup Time
- Pickup Days (check the days when pickup is needed)

**Payment Information:**
- Sales Representative
- Payment Type
- Amount Paid
- Month Acquired

**Subscription:**
- Start Date
- End Date
- Status (Active/Inactive)

3. Click "Save Customer"

#### Editing a Customer

1. Find the customer in the list
2. Click the pencil (✏️) icon
3. Update any information needed
4. Click "Update Customer"

**Note:** All pickup schedules will automatically update for collectors

#### Deleting a Customer

1. Find the customer in the list
2. Click the trash (🗑️) icon
3. Confirm deletion
4. Customer and all their pickup records are removed

### 3. Pickup Management

#### Viewing All Pickups

1. Navigate to "Pickups" from menu
2. See all pickups for selected date
3. Default shows today's date

**Information Shown:**
- Completion status (badge)
- Customer name and details
- Who completed it
- When it was completed
- Any notes added

**Status Indicators:**
- 🟢 Green row = Completed
- 🟡 Yellow row = Pending

#### Filtering by Date

1. Use the date picker at the top
2. Click "Filter"
3. View pickups for any date

**Use Cases:**
- Review yesterday's completion rate
- Plan for upcoming days
- Check historical data

### 4. User Management

#### Viewing Users

Navigate to "Users" to see:
- All system users
- Their roles (Admin/Collector)
- Full names

#### Adding a New User

1. Click "Add User"
2. Fill in:
   - Username (must be unique)
   - Full Name
   - Password (minimum 6 characters)
   - Role:
     - **Admin**: Full access to everything
     - **Collector**: Can only view and complete pickups

3. Click "Create User"

**Important:** Give collectors secure passwords and change them regularly

#### Deleting Users

1. Find the user in the list
2. Click "Delete"
3. Confirm deletion

**Note:** You cannot delete your own account

---

## Collector Features

### Daily Pickup View

When you login as collector:

1. You immediately see today's pickups
2. Pickups are shown as cards
3. Each card contains all info needed for the pickup

### Understanding Pickup Cards

Each card shows:

**Header:**
- Customer name
- Status badge (Done/Pending)

**Body:**
- 📍 Address (for navigation)
- 📞 Phone number (to call if needed)
- 🕐 Pickup time
- 🗑️ Bin information (quantity and size)

**Footer:**
- Button to mark as complete

**If Already Completed:**
- Shows who completed it
- When it was completed
- Any notes that were added
- Button to mark as incomplete (if mistake)

### Completing a Pickup

1. Navigate to the customer location
2. Complete the pickup
3. Click "Mark as Completed" on the card
4. Add any notes (optional):
   - Issues encountered
   - Special observations
   - Customer requests
5. Click "Complete Pickup"

**The card will:**
- Turn green
- Show completion details
- Move to bottom of list

### Adding Notes

Good examples of notes:
- "Gate was locked, left bins outside"
- "Customer requested extra pickup next week"
- "Bins were overfilled"
- "Dog in yard - careful on next visit"
- "Customer away, pickup rescheduled"

### Undoing a Completion

If you marked wrong pickup by mistake:

1. Find the completed pickup (green card)
2. Click "Mark as Incomplete"
3. Confirm the action
4. Card returns to pending status

---

## Daily Workflows

### Admin Morning Routine

1. **Login and check dashboard**
   - Review stats
   - Note any issues from previous day

2. **Check today's pickups**
   - Go to Pickups menu
   - Review the list
   - Ensure all active customers are included

3. **Handle customer changes**
   - Update any subscription statuses
   - Add new customers if signed up
   - Modify schedules as needed

4. **Monitor progress throughout day**
   - Check completion rate
   - Follow up on any delays

### Collector Daily Workflow

1. **Login in the morning**
   - See all today's pickups
   - Note total number

2. **Plan your route**
   - Review addresses
   - Group by area if possible
   - Note any special times

3. **During pickups**
   - Check each customer off as you complete
   - Add notes for any issues
   - Call customers if needed (phone shown on card)

4. **End of day**
   - Verify all pickups completed
   - Report any missed pickups to admin

### Admin End of Day Review

1. **Check completion rate**
   - Go to Pickups
   - Filter for today
   - Review completed vs pending

2. **Follow up on incomplete pickups**
   - Contact collectors for reasons
   - Reschedule if necessary

3. **Review collector notes**
   - Address any customer issues
   - Plan follow-ups

4. **Prepare for next day**
   - Check tomorrow's schedule
   - Ensure all customers are current

---

## Tips & Best Practices

### For Admins

**Customer Data:**
- Keep phone numbers updated
- Verify addresses are accurate
- Note special instructions in address field
- Review inactive customers monthly

**Scheduling:**
- Review pickup days match customer contracts
- Update when customers change frequency
- Coordinate with collectors on route efficiency

**User Management:**
- Create separate accounts for each collector
- This helps track who completed what
- Regular password updates

### For Collectors

**Using the App:**
- Check in the morning for total count
- Mark completed immediately (don't wait)
- Always add notes for issues
- If customer not home, note it

**Communication:**
- Call customers if gate locked
- Report persistent issues to admin
- Suggest route improvements

**Efficiency:**
- Sort mentally by area
- Group nearby addresses
- Note best times for each customer

---

## Frequently Asked Questions

**Q: What if I don't see a customer on my pickup list?**
A: Check with admin - customer may be marked inactive or wrong day selected

**Q: Can I see previous days' pickups?**
A: Collectors can only see today. Ask admin to check past dates

**Q: What if customer has extra bins?**
A: Add a note about it, admin can update record

**Q: How do I change my password?**
A: Contact admin to reset it (feature can be added)

**Q: App not loading?**
A: Check if server is running, verify URL is correct

**Q: Can I access this from my phone?**
A: Yes! The interface is mobile-friendly, just use the browser

---

## Technical Notes

### Data Updates
- Changes by admin are immediately visible to collectors
- Pickup records are created automatically
- No manual sync needed

### Browser Requirements
- Modern browser (Chrome, Firefox, Safari, Edge)
- JavaScript must be enabled
- Internet connection not required (runs locally)

### Backup Recommendations
- Daily backup of waste_collection.db file
- Keep copy of latest Excel import
- Store backups in safe location

---

## Getting Help

1. Check this guide first
2. Review README.md for technical details
3. Check SETUP.md for installation issues
4. Contact system administrator

---

**Last Updated:** December 2024
