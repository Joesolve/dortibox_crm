from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date, timedelta
import pandas as pd
import os
import secrets
from functools import wraps
from io import BytesIO

app = Flask(__name__)

# Security: Use environment variable for secret key, generate random if not set
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///waste_collection.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Session security settings
app.config['SESSION_COOKIE_SECURE'] = os.environ.get('FLASK_ENV') == 'production'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=8)

db = SQLAlchemy(app)
csrf = CSRFProtect(app)

# Make datetime and abs available in templates
@app.context_processor
def inject_now():
    return {
        'now': datetime.now,
        'abs': abs  # Add abs function
    }

# ==================== DATABASE MODELS ====================

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    full_name = db.Column(db.String(100))

    assigned_wards = db.relationship('CollectorWard', backref='user', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_ward_names(self):
        return [cw.ward for cw in self.assigned_wards]


class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_number = db.Column(db.Integer)
    customer_name = db.Column(db.String(200), nullable=False)
    address = db.Column(db.String(300))
    phone_number = db.Column(db.String(50))
    type = db.Column(db.String(100))
    ward = db.Column(db.String(100))
    bin_size = db.Column(db.String(50))  # Now stores multiple sizes like "300L, 50L"
    bin_qty = db.Column(db.Integer)
    frequency = db.Column(db.String(50))
    time = db.Column(db.String(50))
    
    monday = db.Column(db.Integer, default=0)
    tuesday = db.Column(db.Integer, default=0)
    wednesday = db.Column(db.Integer, default=0)
    thursday = db.Column(db.Integer, default=0)
    friday = db.Column(db.Integer, default=0)
    saturday = db.Column(db.Integer, default=0)
    
    sales_rep = db.Column(db.String(100))
    payment_type = db.Column(db.String(100))
    subscription_start = db.Column(db.Date)
    subscription_end = db.Column(db.Date)
    active = db.Column(db.String(10))
    target_month_start = db.Column(db.Date)
    target_month_end = db.Column(db.Date)
    month_acquired = db.Column(db.String(50))
    amount_paid = db.Column(db.Float)
    
    pickups = db.relationship('Pickup', backref='customer', lazy=True, cascade='all, delete-orphan')
    
    def subscription_status(self):
        """Return subscription status"""
        if not self.subscription_end:
            return 'no_date'
        
        today = date.today()
        days_until_end = (self.subscription_end - today).days
        
        if days_until_end < 0:
            return 'expired'
        elif days_until_end <= 7:
            return 'expiring_week'
        elif days_until_end <= 30:
            return 'expiring_month'
        else:
            return 'active'
    
    def days_until_expiry(self):
        """Return days until expiry"""
        if not self.subscription_end:
            return None
        return (self.subscription_end - date.today()).days


class CollectorWard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    ward = db.Column(db.String(100), nullable=False)

    __table_args__ = (db.UniqueConstraint('user_id', 'ward', name='uq_user_ward'),)


class Pickup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    pickup_date = db.Column(db.Date, nullable=False)
    completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime)
    completed_by = db.Column(db.String(100))
    notes = db.Column(db.Text)


# ==================== AUTHENTICATION ====================

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        user = User.query.get(session['user_id'])
        if user.role != 'admin':
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function


# ==================== ROUTES ====================

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            flash(f'Welcome back, {user.full_name or user.username}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'danger')
    
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

def validate_password(password):
    """Validate password meets security requirements. Returns (is_valid, error_message)."""
    if len(password) < 8:
        return False, 'Password must be at least 8 characters.'
    if not any(c.isalpha() for c in password):
        return False, 'Password must contain at least one letter.'
    if not any(c.isdigit() for c in password):
        return False, 'Password must contain at least one number.'
    return True, None


@app.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        user = User.query.get(session['user_id'])

        if not user.check_password(current_password):
            flash('Current password is incorrect.', 'danger')
        elif new_password != confirm_password:
            flash('New passwords do not match.', 'danger')
        else:
            is_valid, error_msg = validate_password(new_password)
            if not is_valid:
                flash(error_msg, 'danger')
            else:
                user.set_password(new_password)
                db.session.commit()
                flash('Password changed successfully!', 'success')
                return redirect(url_for('dashboard'))

    return render_template('change_password.html')

@app.route('/dashboard')
@login_required
def dashboard():
    user = User.query.get(session['user_id'])
    
    if user.role == 'admin':
        total_customers = Customer.query.count()
        active_customers = Customer.query.filter(
            (Customer.active == 'Yes') | (Customer.active == 'yes')
        ).count()
        
        # Count expiring subscriptions
        today = date.today()
        thirty_days = today + timedelta(days=30)
        expiring_soon = Customer.query.filter(
            Customer.subscription_end.isnot(None),
            Customer.subscription_end <= thirty_days,
            Customer.subscription_end >= today
        ).count()
        
        # Count expired subscriptions
        expired = Customer.query.filter(
            Customer.subscription_end.isnot(None),
            Customer.subscription_end < today
        ).count()
        
        # Today's pickups
        day_name = today.strftime('%A').lower()
        day_column_map = {
            'monday': Customer.monday,
            'tuesday': Customer.tuesday,
            'wednesday': Customer.wednesday,
            'thursday': Customer.thursday,
            'friday': Customer.friday,
            'saturday': Customer.saturday
        }
        
        day_column = day_column_map.get(day_name)
        today_pickups = 0
        completed_pickups = 0
        
        if day_column is not None:
            # Only count active customers with non-expired subscriptions
            today_date = date.today()
            customers_today = Customer.query.filter(
                day_column == 1,
                (Customer.active == 'Yes') | (Customer.active == 'yes'),
                db.or_(
                    Customer.subscription_end.is_(None),  # No end date
                    Customer.subscription_end >= today_date  # Or not expired
                )
            ).all()
            today_pickups = len(customers_today)
            
            completed_pickups = Pickup.query.filter(
                Pickup.pickup_date == today,
                Pickup.completed == True
            ).count()
        
        return render_template('admin_dashboard.html', 
                             total_customers=total_customers,
                             active_customers=active_customers,
                             today_pickups=today_pickups,
                             completed_pickups=completed_pickups,
                             expiring_soon=expiring_soon,
                             expired=expired)
    else:
        today = date.today()
        day_name = today.strftime('%A').lower()

        day_column_map = {
            'monday': Customer.monday,
            'tuesday': Customer.tuesday,
            'wednesday': Customer.wednesday,
            'thursday': Customer.thursday,
            'friday': Customer.friday,
            'saturday': Customer.saturday
        }

        day_column = day_column_map.get(day_name)
        pickups = []

        # Get collector's assigned wards
        collector_wards = user.get_ward_names()

        if day_column is not None:
            # Only show active customers with non-expired subscriptions
            today_date = date.today()
            query = Customer.query.filter(
                day_column == 1,
                (Customer.active == 'Yes') | (Customer.active == 'yes'),
                db.or_(
                    Customer.subscription_end.is_(None),
                    Customer.subscription_end >= today_date
                )
            )

            # Filter by assigned wards - if collector has ward assignments, restrict to those
            if collector_wards:
                query = query.filter(Customer.ward.in_(collector_wards))
            else:
                # No wards assigned means no access
                query = query.filter(db.false())

            customers = query.order_by(Customer.address).all()

            for customer in customers:
                pickup = Pickup.query.filter_by(
                    customer_id=customer.id,
                    pickup_date=today
                ).first()

                if not pickup:
                    pickup = Pickup(
                        customer_id=customer.id,
                        pickup_date=today
                    )
                    db.session.add(pickup)

                pickups.append({
                    'pickup': pickup,
                    'customer': customer
                })

            db.session.commit()

        no_wards = len(collector_wards) == 0
        return render_template('collector_dashboard.html',
                             pickups=pickups,
                             today=today,
                             no_wards=no_wards)


# ==================== ADMIN CUSTOMER ROUTES ====================

@app.route('/admin/customers')
@admin_required
def admin_customers():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    ward_filter = request.args.get('ward', '')
    status_filter = request.args.get('status', '')
    subscription_filter = request.args.get('subscription', '')
    
    query = Customer.query
    
    if search:
        query = query.filter(
            (Customer.customer_name.contains(search)) |
            (Customer.address.contains(search)) |
            (Customer.phone_number.contains(search))
        )
    
    if ward_filter:
        query = query.filter(Customer.ward == ward_filter)
    
    if status_filter == 'active':
        query = query.filter((Customer.active == 'Yes') | (Customer.active == 'yes'))
    elif status_filter == 'inactive':
        query = query.filter(Customer.active == 'No')
    
    # Subscription filter
    today = date.today()
    if subscription_filter == 'expired':
        query = query.filter(
            Customer.subscription_end.isnot(None),
            Customer.subscription_end < today
        )
    elif subscription_filter == 'expiring_week':
        week_from_now = today + timedelta(days=7)
        query = query.filter(
            Customer.subscription_end.isnot(None),
            Customer.subscription_end >= today,
            Customer.subscription_end <= week_from_now
        )
    elif subscription_filter == 'expiring_month':
        month_from_now = today + timedelta(days=30)
        query = query.filter(
            Customer.subscription_end.isnot(None),
            Customer.subscription_end >= today,
            Customer.subscription_end <= month_from_now
        )
    elif subscription_filter == 'no_date':
        query = query.filter(Customer.subscription_end.is_(None))
    
    customers = query.order_by(Customer.customer_number).paginate(
        page=page, per_page=20, error_out=False
    )
    
    wards = db.session.query(Customer.ward).filter(Customer.ward.isnot(None)).distinct().order_by(Customer.ward).all()
    wards = [w[0] for w in wards if w[0]]
    
    return render_template('admin_customers.html', 
                         customers=customers, 
                         search=search,
                         ward_filter=ward_filter,
                         status_filter=status_filter,
                         subscription_filter=subscription_filter,
                         wards=wards,
                         today=today)


@app.route('/admin/customers/bulk-delete', methods=['POST'])
@admin_required
def bulk_delete_customers():
    customer_ids = request.form.getlist('customer_ids[]')
    
    if not customer_ids:
        flash('No customers selected.', 'warning')
        return redirect(url_for('admin_customers'))
    
    try:
        customer_ids = [int(id) for id in customer_ids]
        deleted_count = Customer.query.filter(Customer.id.in_(customer_ids)).delete(synchronize_session=False)
        db.session.commit()
        
        # Renumber customers after deletion
        renumber_customers()
        
        flash(f'Successfully deleted {deleted_count} customer(s).', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting customers: {str(e)}', 'danger')
    
    return redirect(url_for('admin_customers'))


@app.route('/admin/customers/bulk-extend', methods=['POST'])
@admin_required
def bulk_extend_subscriptions():
    """Bulk extend subscription end dates"""
    customer_ids = request.form.getlist('customer_ids[]')
    months = request.form.get('extend_months', type=int)
    
    if not customer_ids:
        flash('No customers selected.', 'warning')
        return redirect(url_for('admin_customers'))
    
    if not months or months < 1:
        flash('Please specify number of months to extend.', 'warning')
        return redirect(url_for('admin_customers'))
    
    try:
        customer_ids = [int(id) for id in customer_ids]
        customers = Customer.query.filter(Customer.id.in_(customer_ids)).all()
        
        extended_count = 0
        for customer in customers:
            if customer.subscription_end:
                # Extend from current end date
                customer.subscription_end = customer.subscription_end + timedelta(days=30 * months)
            else:
                # If no end date, set from today
                customer.subscription_end = date.today() + timedelta(days=30 * months)
            
            # Ensure customer is active
            customer.active = 'Yes'
            extended_count += 1
        
        db.session.commit()
        flash(f'Successfully extended subscriptions for {extended_count} customer(s) by {months} month(s).', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error extending subscriptions: {str(e)}', 'danger')
    
    return redirect(url_for('admin_customers'))


def renumber_customers():
    """Renumber all customers sequentially starting from 1"""
    # Order by ID to maintain original order, or use created_at if available
    customers = Customer.query.order_by(Customer.id).all()
    for idx, customer in enumerate(customers, start=1):
        customer.customer_number = idx
    db.session.commit()


@app.route('/admin/customers/export')
@admin_required
def export_customers():
    search = request.args.get('search', '')
    ward_filter = request.args.get('ward', '')
    status_filter = request.args.get('status', '')
    subscription_filter = request.args.get('subscription', '')
    
    query = Customer.query
    
    if search:
        query = query.filter(
            (Customer.customer_name.contains(search)) |
            (Customer.address.contains(search)) |
            (Customer.phone_number.contains(search))
        )
    
    if ward_filter:
        query = query.filter(Customer.ward == ward_filter)
    
    if status_filter == 'active':
        query = query.filter((Customer.active == 'Yes') | (Customer.active == 'yes'))
    elif status_filter == 'inactive':
        query = query.filter(Customer.active == 'No')
    
    # Apply subscription filter
    today = date.today()
    if subscription_filter == 'expired':
        query = query.filter(
            Customer.subscription_end.isnot(None),
            Customer.subscription_end < today
        )
    elif subscription_filter == 'expiring_week':
        week_from_now = today + timedelta(days=7)
        query = query.filter(
            Customer.subscription_end.isnot(None),
            Customer.subscription_end >= today,
            Customer.subscription_end <= week_from_now
        )
    elif subscription_filter == 'expiring_month':
        month_from_now = today + timedelta(days=30)
        query = query.filter(
            Customer.subscription_end.isnot(None),
            Customer.subscription_end >= today,
            Customer.subscription_end <= month_from_now
        )
    elif subscription_filter == 'no_date':
        query = query.filter(Customer.subscription_end.is_(None))
    
    customers = query.order_by(Customer.customer_number).all()
    
    data = []
    for c in customers:
        # Calculate days until expiry
        days_until_expiry = ''
        if c.subscription_end:
            days = (c.subscription_end - today).days
            if days < 0:
                days_until_expiry = f'EXPIRED {abs(days)} days ago'
            else:
                days_until_expiry = f'{days} days remaining'
        
        data.append({
            'Number': c.customer_number,
            'Customer Name': c.customer_name,
            'Address': c.address,
            'Phone Number': c.phone_number,
            'Type': c.type,
            'Ward': c.ward,
            'Bin Size': c.bin_size,
            'Bin Qty': c.bin_qty,
            'Frequency': c.frequency,
            'Time': c.time,
            'Mon': c.monday,
            'Tue': c.tuesday,
            'Wed': c.wednesday,
            'Thurs': c.thursday,
            'Fri': c.friday,
            'Sat': c.saturday,
            'Sales Rep': c.sales_rep,
            'Payment Type': c.payment_type,
            'Subscription Start': c.subscription_start.strftime('%Y-%m-%d') if c.subscription_start else '',
            'Subscription End': c.subscription_end.strftime('%Y-%m-%d') if c.subscription_end else '',
            'Days Until Expiry': days_until_expiry,
            'Active': c.active,
            'Month Acquired': c.month_acquired,
            'Amount Paid SLL': c.amount_paid
        })
    
    df = pd.DataFrame(data)
    
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Customers', index=False)
    
    output.seek(0)
    
    filename = f'customers_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=filename
    )


@app.route('/admin/customers/add', methods=['GET', 'POST'])
@admin_required
def add_customer():
    if request.method == 'POST':
        # Auto-generate customer number
        max_number = db.session.query(db.func.max(Customer.customer_number)).scalar()
        next_number = (max_number or 0) + 1
        
        customer = Customer(
            customer_number=next_number,  # Auto-generated
            customer_name=request.form.get('customer_name'),
            address=request.form.get('address'),
            phone_number=request.form.get('phone_number'),
            type=request.form.get('type'),
            ward=request.form.get('ward'),
            bin_size=request.form.get('bin_size'),  # Now can store multiple sizes
            bin_qty=request.form.get('bin_qty', type=int),
            frequency=request.form.get('frequency'),
            time=request.form.get('time'),
            monday=1 if request.form.get('monday') else 0,
            tuesday=1 if request.form.get('tuesday') else 0,
            wednesday=1 if request.form.get('wednesday') else 0,
            thursday=1 if request.form.get('thursday') else 0,
            friday=1 if request.form.get('friday') else 0,
            saturday=1 if request.form.get('saturday') else 0,
            sales_rep=request.form.get('sales_rep'),
            payment_type=request.form.get('payment_type'),
            active=request.form.get('active', 'Yes'),
            month_acquired=request.form.get('month_acquired'),
            amount_paid=request.form.get('amount_paid', type=float)
        )
        
        if request.form.get('subscription_start'):
            customer.subscription_start = datetime.strptime(
                request.form.get('subscription_start'), '%Y-%m-%d'
            ).date()
        if request.form.get('subscription_end'):
            customer.subscription_end = datetime.strptime(
                request.form.get('subscription_end'), '%Y-%m-%d'
            ).date()
        
        db.session.add(customer)
        db.session.commit()
        
        flash(f'Customer added successfully! Customer #{next_number}', 'success')
        return redirect(url_for('admin_customers'))
    
    # Get next customer number for display
    max_number = db.session.query(db.func.max(Customer.customer_number)).scalar()
    next_number = (max_number or 0) + 1
    
    return render_template('add_customer.html', next_number=next_number)


@app.route('/admin/customers/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def edit_customer(id):
    customer = Customer.query.get_or_404(id)
    
    if request.method == 'POST':
        # Keep the original customer number - DO NOT change it during edit
        # customer.customer_number stays the same
        customer.customer_name = request.form.get('customer_name')
        customer.address = request.form.get('address')
        customer.phone_number = request.form.get('phone_number')
        customer.type = request.form.get('type')
        customer.ward = request.form.get('ward')
        customer.bin_size = request.form.get('bin_size')  # Can now store multiple sizes
        customer.bin_qty = request.form.get('bin_qty', type=int)
        customer.frequency = request.form.get('frequency')
        customer.time = request.form.get('time')
        customer.monday = 1 if request.form.get('monday') else 0
        customer.tuesday = 1 if request.form.get('tuesday') else 0
        customer.wednesday = 1 if request.form.get('wednesday') else 0
        customer.thursday = 1 if request.form.get('thursday') else 0
        customer.friday = 1 if request.form.get('friday') else 0
        customer.saturday = 1 if request.form.get('saturday') else 0
        customer.sales_rep = request.form.get('sales_rep')
        customer.payment_type = request.form.get('payment_type')
        customer.active = request.form.get('active')
        customer.month_acquired = request.form.get('month_acquired')
        customer.amount_paid = request.form.get('amount_paid', type=float)
        
        if request.form.get('subscription_start'):
            customer.subscription_start = datetime.strptime(
                request.form.get('subscription_start'), '%Y-%m-%d'
            ).date()
        if request.form.get('subscription_end'):
            customer.subscription_end = datetime.strptime(
                request.form.get('subscription_end'), '%Y-%m-%d'
            ).date()
        
        db.session.commit()
        flash('Customer updated successfully!', 'success')
        return redirect(url_for('admin_customers'))
    
    return render_template('edit_customer.html', customer=customer)


@app.route('/admin/customers/delete/<int:id>', methods=['POST'])
@admin_required
def delete_customer(id):
    customer = Customer.query.get_or_404(id)
    db.session.delete(customer)
    db.session.commit()
    
    # Renumber customers after deletion
    renumber_customers()
    
    flash('Customer deleted successfully!', 'success')
    return redirect(url_for('admin_customers'))


@app.route('/admin/customers/renumber', methods=['POST'])
@admin_required
def renumber_all_customers():
    """Manual renumbering route - renumbers all customers sequentially"""
    try:
        renumber_customers()
        flash('All customers have been renumbered successfully!', 'success')
    except Exception as e:
        flash(f'Error renumbering customers: {str(e)}', 'danger')
    return redirect(url_for('admin_customers'))


@app.route('/admin/pickups')
@admin_required
def admin_pickups():
    date_filter = request.args.get('date', date.today().isoformat())
    filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
    
    # Get the day of week for the filter date
    day_name = filter_date.strftime('%A').lower()
    day_column_map = {
        'monday': Customer.monday,
        'tuesday': Customer.tuesday,
        'wednesday': Customer.wednesday,
        'thursday': Customer.thursday,
        'friday': Customer.friday,
        'saturday': Customer.saturday
    }
    
    day_column = day_column_map.get(day_name)
    
    # Get all active customers scheduled for this day with non-expired subscriptions
    if day_column is not None:
        filter_date_obj = filter_date  # filter_date is already a date object
        customers_for_day = Customer.query.filter(
            day_column == 1,
            (Customer.active == 'Yes') | (Customer.active == 'yes'),
            db.or_(
                Customer.subscription_end.is_(None),  # No end date
                Customer.subscription_end >= filter_date_obj  # Or not expired on filter date
            )
        ).all()
        
        # Create pickup records if they don't exist
        for customer in customers_for_day:
            existing_pickup = Pickup.query.filter_by(
                customer_id=customer.id,
                pickup_date=filter_date
            ).first()
            
            if not existing_pickup:
                pickup = Pickup(
                    customer_id=customer.id,
                    pickup_date=filter_date
                )
                db.session.add(pickup)
        
        db.session.commit()
    
    # Now get all pickups for the filter date, but only for customers still scheduled for this day
    if day_column is not None:
        pickups = Pickup.query.filter_by(pickup_date=filter_date).join(Customer).filter(
            day_column == 1,
            (Customer.active == 'Yes') | (Customer.active == 'yes'),
            db.or_(
                Customer.subscription_end.is_(None),
                Customer.subscription_end >= filter_date
            )
        ).order_by(Pickup.completed, Customer.address).all()
    else:
        pickups = []
    
    return render_template('admin_pickups.html', pickups=pickups, filter_date=filter_date)


@app.route('/admin/users')
@admin_required
def admin_users():
    users = User.query.all()
    return render_template('admin_users.html', users=users)


@app.route('/admin/users/add', methods=['GET', 'POST'])
@admin_required
def add_user():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')
        full_name = request.form.get('full_name')

        if User.query.filter_by(username=username).first():
            flash('Username already exists!', 'danger')
        else:
            is_valid, error_msg = validate_password(password)
            if not is_valid:
                flash(error_msg, 'danger')
            else:
                user = User(username=username, role=role, full_name=full_name)
                user.set_password(password)
                db.session.add(user)
                db.session.flush()

                # Assign wards for collectors
                if role == 'collector':
                    selected_wards = request.form.getlist('wards')
                    for ward_name in selected_wards:
                        cw = CollectorWard(user_id=user.id, ward=ward_name)
                        db.session.add(cw)

                db.session.commit()
                flash('User added successfully!', 'success')
                return redirect(url_for('admin_users'))

    wards = db.session.query(Customer.ward).filter(Customer.ward.isnot(None), Customer.ward != '').distinct().order_by(Customer.ward).all()
    wards = [w[0] for w in wards]
    return render_template('add_user.html', wards=wards)


@app.route('/admin/users/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def edit_user(id):
    user = User.query.get_or_404(id)

    if request.method == 'POST':
        user.full_name = request.form.get('full_name')
        new_role = request.form.get('role')
        user.role = new_role

        # Update ward assignments
        CollectorWard.query.filter_by(user_id=user.id).delete()
        if new_role == 'collector':
            selected_wards = request.form.getlist('wards')
            for ward_name in selected_wards:
                cw = CollectorWard(user_id=user.id, ward=ward_name)
                db.session.add(cw)

        db.session.commit()
        flash('User updated successfully!', 'success')
        return redirect(url_for('admin_users'))

    wards = db.session.query(Customer.ward).filter(Customer.ward.isnot(None), Customer.ward != '').distinct().order_by(Customer.ward).all()
    wards = [w[0] for w in wards]
    user_wards = user.get_ward_names()
    return render_template('edit_user.html', user=user, wards=wards, user_wards=user_wards)


@app.route('/admin/users/delete/<int:id>', methods=['POST'])
@admin_required
def delete_user(id):
    if id == session.get('user_id'):
        flash('You cannot delete your own account!', 'danger')
    else:
        user = User.query.get_or_404(id)
        db.session.delete(user)
        db.session.commit()
        flash('User deleted successfully!', 'success')
    return redirect(url_for('admin_users'))


# ==================== COLLECTOR ROUTES ====================

@app.route('/collector/complete/<int:pickup_id>', methods=['POST'])
@login_required
def complete_pickup(pickup_id):
    pickup = Pickup.query.get_or_404(pickup_id)
    user = User.query.get(session['user_id'])

    # Enforce ward access for collectors
    if user.role == 'collector':
        customer = Customer.query.get(pickup.customer_id)
        collector_wards = user.get_ward_names()
        if customer.ward not in collector_wards:
            return jsonify({'success': False, 'message': 'You do not have access to this ward.'}), 403

    data = request.get_json()
    notes = data.get('notes', '')

    pickup.completed = True
    pickup.completed_at = datetime.now()
    pickup.completed_by = user.full_name or user.username
    pickup.notes = notes

    db.session.commit()

    return jsonify({'success': True, 'message': 'Pickup marked as completed!'})


@app.route('/collector/uncomplete/<int:pickup_id>', methods=['POST'])
@login_required
def uncomplete_pickup(pickup_id):
    pickup = Pickup.query.get_or_404(pickup_id)
    user = User.query.get(session['user_id'])

    # Enforce ward access for collectors
    if user.role == 'collector':
        customer = Customer.query.get(pickup.customer_id)
        collector_wards = user.get_ward_names()
        if customer.ward not in collector_wards:
            return jsonify({'success': False, 'message': 'You do not have access to this ward.'}), 403

    pickup.completed = False
    pickup.completed_at = None
    pickup.completed_by = None
    pickup.notes = None

    db.session.commit()

    return jsonify({'success': True, 'message': 'Pickup marked as incomplete!'})


# ==================== SETTINGS ROUTES ====================

def allowed_file(filename):
    """Check if file has allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'xlsx', 'xls'}


def is_day_scheduled(value):
    """Check if a day column value indicates the day is scheduled.
    Handles: 1, 1.0, 'X', 'x', '1', True, and similar values."""
    if pd.isna(value):
        return False
    if isinstance(value, (int, float)):
        return value == 1 or value == 1.0
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        val = value.strip().upper()
        return val in ('X', '1', 'YES', 'Y', 'TRUE')
    return False


@app.route('/admin/settings', methods=['GET'])
@admin_required
def settings():
    """Settings page with file upload"""
    customer_count = Customer.query.count()
    return render_template('settings.html', customer_count=customer_count)


@app.route('/admin/settings/upload', methods=['POST'])
@admin_required
def upload_excel():
    """Handle Excel file upload and update database"""
    if 'excel_file' not in request.files:
        flash('No file selected', 'danger')
        return redirect(url_for('settings'))

    file = request.files['excel_file']

    if file.filename == '':
        flash('No file selected', 'danger')
        return redirect(url_for('settings'))

    if not allowed_file(file.filename):
        flash('Invalid file type. Please upload an Excel file (.xlsx or .xls)', 'danger')
        return redirect(url_for('settings'))

    try:
        df = pd.read_excel(file, sheet_name='Service Log', header=1)
        df.columns = df.columns.str.strip()
        df = df[df['Number'].notna()]

        import_mode = request.form.get('import_mode', 'update')

        if import_mode == 'replace':
            deleted_count = Customer.query.delete()
            db.session.commit()
            flash(f'Deleted {deleted_count} existing customers', 'info')

        imported = 0
        updated = 0
        errors = 0

        for _, row in df.iterrows():
            try:
                customer_number = int(row['Number']) if pd.notna(row.get('Number')) else None
                if customer_number is None:
                    continue

                customer_data = {
                    'customer_number': customer_number,
                    'customer_name': str(row.get('Customer Name', '')).strip() if pd.notna(row.get('Customer Name')) else '',
                    'address': str(row.get('Address', '')).strip() if pd.notna(row.get('Address')) else '',
                    'phone_number': str(row.get('Phone Number', '')).strip() if pd.notna(row.get('Phone Number')) else '',
                    'type': str(row.get('Type', 'Commercial')).strip() if pd.notna(row.get('Type')) else 'Commercial',
                    'bin_size': str(row.get('Bin Size', '')).strip() if pd.notna(row.get('Bin Size')) else '',
                    'bin_qty': int(row.get('Bin Qty', 1)) if pd.notna(row.get('Bin Qty')) else 1,
                    'ward': str(row.get('Ward', '')).strip() if pd.notna(row.get('Ward')) else '',
                    'frequency': str(row.get('Frequency', '')).strip() if pd.notna(row.get('Frequency')) else '',
                    'time': str(row.get('Time', '')).strip() if pd.notna(row.get('Time')) else '',
                    'sales_rep': str(row.get('Sales Rep', '')).strip() if pd.notna(row.get('Sales Rep')) else '',
                    'payment_type': str(row.get('Payment Type', '')).strip() if pd.notna(row.get('Payment Type')) else '',
                    'month_acquired': str(row.get('Month Acquired', '')).strip() if pd.notna(row.get('Month Acquired')) else '',
                    'active': 'Yes' if str(row.get('Active in Target Month?', '')).upper() == 'YES' else 'No',
                    'monday': 1 if is_day_scheduled(row.get('Mon')) else 0,
                    'tuesday': 1 if is_day_scheduled(row.get('Tue')) else 0,
                    'wednesday': 1 if is_day_scheduled(row.get('Wed')) else 0,
                    'thursday': 1 if is_day_scheduled(row.get('Thurs')) else 0,
                    'friday': 1 if is_day_scheduled(row.get('Fri')) else 0,
                    'saturday': 1 if is_day_scheduled(row.get('Sat')) else 0,
                }

                # Handle amount paid
                amount = row.get('Amount Paid')
                if pd.notna(amount):
                    try:
                        customer_data['amount_paid'] = float(amount)
                    except (ValueError, TypeError):
                        customer_data['amount_paid'] = None

                # Handle subscription dates
                for date_field, col_name in [('subscription_start', 'Subscription Start'), ('subscription_end', 'Subscription End')]:
                    date_val = row.get(col_name)
                    if pd.notna(date_val):
                        if isinstance(date_val, str):
                            try:
                                customer_data[date_field] = datetime.strptime(date_val, '%Y-%m-%d').date()
                            except ValueError:
                                try:
                                    customer_data[date_field] = datetime.strptime(date_val, '%d/%m/%Y').date()
                                except ValueError:
                                    customer_data[date_field] = None
                        else:
                            customer_data[date_field] = date_val.date() if hasattr(date_val, 'date') else date_val
                    else:
                        customer_data[date_field] = None

                existing = Customer.query.filter_by(customer_number=customer_number).first()

                if existing:
                    for key, value in customer_data.items():
                        setattr(existing, key, value)
                    updated += 1
                else:
                    new_customer = Customer(**customer_data)
                    db.session.add(new_customer)
                    imported += 1

            except Exception as e:
                errors += 1
                print(f"Error processing row: {e}")
                continue

        db.session.commit()

        msg_parts = []
        if imported > 0:
            msg_parts.append(f'{imported} new customers imported')
        if updated > 0:
            msg_parts.append(f'{updated} customers updated')
        if errors > 0:
            msg_parts.append(f'{errors} rows had errors')

        flash(f"Import complete: {', '.join(msg_parts)}", 'success')

    except ValueError as e:
        if 'Service Log' in str(e):
            flash('Could not find "Service Log" sheet in the Excel file.', 'danger')
        else:
            flash(f'Error reading Excel file: {str(e)}', 'danger')
    except Exception as e:
        flash(f'Error processing file: {str(e)}', 'danger')

    return redirect(url_for('settings'))


@app.route('/admin/settings/preview', methods=['POST'])
@admin_required
def preview_excel():
    """Preview Excel file contents before importing"""
    if 'excel_file' not in request.files:
        return jsonify({'error': 'No file selected'}), 400

    file = request.files['excel_file']

    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type'}), 400

    try:
        xl_file = pd.ExcelFile(file)

        if 'Service Log' not in xl_file.sheet_names:
            return jsonify({
                'error': f'Sheet "Service Log" not found. Available sheets: {", ".join(xl_file.sheet_names)}'
            }), 400

        df = pd.read_excel(xl_file, sheet_name='Service Log', header=1)
        df.columns = df.columns.str.strip()
        df = df[df['Number'].notna()]

        total_rows = len(df)
        active_count = len(df[df['Active in Target Month?'].str.upper() == 'YES']) if 'Active in Target Month?' in df.columns else 0

        sample_cols = ['Number', 'Customer Name', 'Address', 'Active in Target Month?']
        available_cols = [col for col in sample_cols if col in df.columns]
        sample_data = df[available_cols].head(5).to_dict('records')

        return jsonify({
            'success': True,
            'total_customers': total_rows,
            'active_customers': active_count,
            'inactive_customers': total_rows - active_count,
            'columns_found': list(df.columns),
            'sample_data': sample_data,
            'current_db_count': Customer.query.count()
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/admin/settings/backup', methods=['POST'])
@admin_required
def backup_database():
    """Create a backup of current customer data as Excel file"""
    try:
        customers = Customer.query.all()

        data = []
        for c in customers:
            data.append({
                'Number': c.customer_number,
                'Customer Name': c.customer_name,
                'Address': c.address,
                'Phone Number': c.phone_number,
                'Type': c.type,
                'Bin Size': c.bin_size,
                'Bin Qty': c.bin_qty,
                'Ward': c.ward,
                'Frequency': c.frequency,
                'Time': c.time,
                'Sales Rep': c.sales_rep,
                'Payment Type': c.payment_type,
                'Month Acquired': c.month_acquired,
                'Active in Target Month?': c.active if c.active else 'No',
                'Mon': 'X' if c.monday else '',
                'Tue': 'X' if c.tuesday else '',
                'Wed': 'X' if c.wednesday else '',
                'Thurs': 'X' if c.thursday else '',
                'Fri': 'X' if c.friday else '',
                'Sat': 'X' if c.saturday else '',
                'Subscription Start': c.subscription_start,
                'Subscription End': c.subscription_end,
                'Amount Paid': c.amount_paid
            })

        df = pd.DataFrame(data)

        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Service Log', index=False)
        output.seek(0)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'customer_backup_{timestamp}.xlsx'

        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        flash(f'Error creating backup: {str(e)}', 'danger')
        return redirect(url_for('settings'))


# ==================== INITIALIZATION ====================

def init_database():
    with app.app_context():
        db.create_all()

        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin', role='admin', full_name='Administrator')
            admin.set_password('admin123')
            db.session.add(admin)

        if not User.query.filter_by(username='collector').first():
            collector = User(username='collector', role='collector', full_name='Collector User')
            collector.set_password('collector123')
            db.session.add(collector)

        db.session.commit()


# Always ensure all tables exist (handles new models added to a running system)
with app.app_context():
    db.create_all()


if __name__ == '__main__':
    init_database()
    # Use environment variable to control debug mode (default: False for security)
    debug_mode = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    host = os.environ.get('FLASK_HOST', '127.0.0.1')  # Default to localhost for security
    port = int(os.environ.get('FLASK_PORT', 5000))
    app.run(debug=debug_mode, host=host, port=port)