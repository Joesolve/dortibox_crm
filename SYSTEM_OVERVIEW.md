# System Overview & Architecture

## System Summary

A web-based waste collection management application built with Python Flask, designed for managing customer data, scheduling pickups, and tracking completion status.

## Technology Stack

- **Backend:** Python 3.8+ with Flask web framework
- **Database:** SQLite (single file, portable)
- **Frontend:** Bootstrap 5 with responsive design
- **Authentication:** Session-based with password hashing
- **Data Import:** Pandas for Excel processing

## Architecture

### Three-Tier Application

```
┌─────────────────────────────────────────┐
│         Presentation Layer              │
│   (HTML Templates + Bootstrap CSS)      │
│   - Login Page                          │
│   - Admin Dashboard                     │
│   - Collector Dashboard                 │
│   - Customer Management Forms           │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│         Application Layer               │
│        (Flask Routes + Logic)           │
│   - Authentication & Authorization      │
│   - CRUD Operations                     │
│   - Pickup Generation                   │
│   - Data Validation                     │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│           Data Layer                    │
│     (SQLite + SQLAlchemy ORM)          │
│   - Users Table                         │
│   - Customers Table                     │
│   - Pickups Table                       │
└─────────────────────────────────────────┘
```

## Database Schema

### Users Table
- **Purpose:** Store admin and collector accounts
- **Fields:** id, username, password_hash, role, full_name
- **Relationships:** None
- **Security:** Passwords hashed with werkzeug

### Customers Table
- **Purpose:** Store customer information and service details
- **Key Fields:**
  - Basic: name, address, phone, ward
  - Service: bin_size, bin_qty, frequency, time
  - Schedule: monday, tuesday, wednesday, thursday, friday, saturday
  - Subscription: start_date, end_date, active status
  - Payment: sales_rep, payment_type, amount_paid
- **Relationships:** One-to-Many with Pickups

### Pickups Table
- **Purpose:** Track daily pickup completions
- **Fields:** id, customer_id, pickup_date, completed, completed_at, completed_by, notes
- **Relationships:** Many-to-One with Customers
- **Auto-Generation:** Created when collector views dashboard

## User Roles & Permissions

### Admin Role
**Full System Access:**
- ✓ View dashboard with statistics
- ✓ Create, read, update, delete customers
- ✓ View all pickups (any date)
- ✓ Create and delete user accounts
- ✓ Access all features

### Collector Role
**Limited Access:**
- ✓ View today's pickups only
- ✓ Mark pickups as complete/incomplete
- ✓ Add notes to pickups
- ✗ Cannot modify customer data
- ✗ Cannot see other dates
- ✗ Cannot manage users

## Data Flow

### Daily Pickup Flow

```
1. System Check
   ↓ (When collector logs in)
   
2. Query Active Customers
   ↓ (Filter by: active status + today's day of week)
   
3. Generate Pickup Records
   ↓ (If not exists for today)
   
4. Display to Collector
   ↓ (Organized by address)
   
5. Collector Marks Complete
   ↓ (Records: who, when, notes)
   
6. Database Updated
   ↓ (Immediately visible to admin)
   
7. Historical Record Created
```

### Customer Management Flow

```
Admin Action (Add/Edit/Delete)
         ↓
   Form Validation
         ↓
   Database Update
         ↓
Schedule Analysis (determine pickup days)
         ↓
   Success Confirmation
         ↓
Collectors See Updated Schedule
```

## Key Features Explained

### Automatic Pickup Generation
- System automatically creates pickup records
- Triggered when collector views their dashboard
- Only creates for today's date
- Based on customer schedule and active status
- No manual intervention needed

### Schedule Management
- Each customer has 6 boolean flags (Mon-Sat)
- 1 = pickup day, 0 = no pickup
- Easy to modify via edit form
- Changes take effect immediately

### Status Tracking
**Customer Status:**
- Active: Shows in pickup lists
- Inactive: Hidden from collectors

**Pickup Status:**
- Pending: Not yet completed
- Completed: Done with timestamp and notes

### Search & Filter
- Customers: Search by name, address, phone
- Pickups: Filter by date
- Pagination: 20 items per page
- Real-time results

## Security Features

### Authentication
- Session-based login
- Password hashing (werkzeug)
- Role-based access control
- Logout functionality

### Authorization
- Decorator-based (@login_required, @admin_required)
- Route protection
- Session validation
- CSRF protection via Flask

### Data Security
- No SQL injection (SQLAlchemy ORM)
- Input validation
- Secure password storage
- Session secrets

## Application Routes

### Public Routes
- `/` - Redirect to dashboard or login
- `/login` - Login page
- `/logout` - Logout and clear session

### Protected Routes (All Users)
- `/dashboard` - Role-based dashboard

### Admin Routes
- `/admin/customers` - List customers
- `/admin/customers/add` - Add customer form
- `/admin/customers/edit/<id>` - Edit customer
- `/admin/customers/delete/<id>` - Delete customer
- `/admin/pickups` - View pickups by date
- `/admin/users` - List users
- `/admin/users/add` - Add user
- `/admin/users/delete/<id>` - Delete user

### Collector Routes
- `/collector/complete/<id>` - Mark pickup complete
- `/collector/uncomplete/<id>` - Undo completion

## Performance Considerations

### Database
- SQLite: Suitable for small-medium operations (1000s of customers)
- Single file: Easy to backup and move
- Indexed: Primary keys and foreign keys
- Efficient queries: Using ORM optimization

### Pagination
- 20 items per page (configurable)
- Reduces page load time
- Better user experience

### Session Management
- Server-side sessions
- Minimal data transfer
- Quick authentication checks

## Scalability Notes

### Current Capacity
- **Customers:** Handles 1000s efficiently
- **Concurrent Users:** 5-10 simultaneous
- **Pickups:** 100s per day
- **Database Size:** Grows slowly (~1MB per 1000 customers)

### Upgrade Path (if needed)
1. **More Users:** Switch to PostgreSQL
2. **Mobile App:** Add REST API
3. **Real-time:** Add WebSocket for live updates
4. **Analytics:** Add reporting module
5. **Cloud:** Deploy to cloud platform

## Backup Strategy

### What to Backup
- `waste_collection.db` (primary database)
- Excel imports (source data)
- Application files (for recovery)

### Recommended Schedule
- **Daily:** Automated db backup
- **Weekly:** Full system backup
- **Monthly:** Archive old data

## Maintenance Tasks

### Daily
- Monitor completion rates
- Check for errors in logs

### Weekly
- Review inactive customers
- Update subscription statuses
- Backup database

### Monthly
- Archive old pickup records
- Review user accounts
- System updates

### Yearly
- Audit data accuracy
- Review and update procedures
- Plan for improvements

## Deployment Options

### Local Network (Recommended for Start)
```
Single computer runs the app
Other devices access via IP:5000
No internet required
Easy to setup
```

### Cloud Deployment (For Growth)
```
Host on: Heroku, DigitalOcean, AWS
Accessible from anywhere
Requires internet
Professional setup
```

### Hybrid Approach
```
Primary: Local network
Backup: Cloud instance
Best of both worlds
Disaster recovery
```

## Integration Possibilities

### Future Integrations
- **Accounting Software:** QuickBooks, Xero
- **Payment Gateways:** Mobile money, cards
- **SMS Service:** Pickup reminders
- **GPS Tracking:** Route optimization
- **Customer Portal:** Self-service access
- **Analytics:** Advanced reporting

## System Requirements

### Server/Host
- **Processor:** Any modern CPU
- **RAM:** 512MB minimum, 1GB recommended
- **Storage:** 100MB + data growth
- **OS:** Windows, Mac, Linux

### Client (User Devices)
- **Browser:** Chrome, Firefox, Safari, Edge
- **JavaScript:** Must be enabled
- **Internet:** Only if server remote
- **Mobile:** Fully responsive design

## Troubleshooting Guide

### Common Issues

**Application won't start**
- Check Python installed
- Verify dependencies installed
- Ensure port 5000 available

**Can't login**
- Verify database exists
- Check username/password
- Look for error messages

**Pickups not showing**
- Check customer active status
- Verify correct day selected
- Check schedule configuration

**Database errors**
- Backup and rebuild
- Check file permissions
- Verify SQLite installation

## Best Practices

### For Smooth Operation
1. Regular backups
2. Update customer data promptly
3. Train users properly
4. Monitor system logs
5. Plan for growth
6. Document changes
7. Test before deploying updates

### Data Quality
- Verify addresses accurate
- Keep phone numbers current
- Update subscriptions timely
- Clean inactive customers
- Review schedules regularly

## Summary

This is a production-ready waste collection management system designed for efficiency, ease of use, and reliability. It provides all necessary features for managing customers, scheduling pickups, and tracking completions while maintaining simplicity and performance.

**Key Strengths:**
- ✅ Easy to install and use
- ✅ Portable database
- ✅ Responsive design
- ✅ Role-based access
- ✅ Automatic scheduling
- ✅ Complete tracking
- ✅ Secure authentication

**Perfect For:**
- Small to medium waste collection businesses
- Companies with 50-1000 customers
- Teams of 1-10 collectors
- Local or regional operations

---

**For more details, see:**
- SETUP.md - Installation
- USAGE_GUIDE.md - How to use
- README.md - Technical details
