"""
Settings Route for Waste Collection App
Add this code to your app.py file

This provides a settings page where admins can upload an Excel file
to update customer data from the "Service Log" sheet.
"""

# ==================== ADD THESE IMPORTS (if not already present) ====================
# from werkzeug.utils import secure_filename
# import os
# import pandas as pd
# from datetime import datetime

# ==================== ADD THIS CONFIGURATION ====================
# Add near the top of app.py after app = Flask(__name__)
# UPLOAD_FOLDER = 'uploads'
# ALLOWED_EXTENSIONS = {'xlsx', 'xls'}
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ==================== ADD THESE ROUTES TO app.py ====================

def allowed_file(filename):
    """Check if file has allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'xlsx', 'xls'}


@app.route('/admin/settings', methods=['GET'])
@admin_required
def settings():
    """Settings page with file upload"""
    # Get last import info if available
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
        # Read the Excel file directly from the uploaded file
        df = pd.read_excel(file, sheet_name='Service Log', header=1)
        
        # Clean column names
        df.columns = df.columns.str.strip()
        
        # Drop rows where Number is NaN (these are usually empty or header rows)
        df = df[df['Number'].notna()]
        
        # Get import mode
        import_mode = request.form.get('import_mode', 'update')
        
        if import_mode == 'replace':
            # Delete all existing customers
            deleted_count = Customer.query.delete()
            db.session.commit()
            flash(f'Deleted {deleted_count} existing customers', 'info')
        
        # Process each row
        imported = 0
        updated = 0
        errors = 0
        
        for _, row in df.iterrows():
            try:
                customer_number = int(row['Number']) if pd.notna(row.get('Number')) else None
                if customer_number is None:
                    continue
                
                # Extract data from row with proper handling
                # Note: Customer model uses customer_name, type, active (Yes/No string),
                # and monday/tuesday/etc (integer 0/1)
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
                    'monday': 1 if str(row.get('Mon', '')).upper() == 'X' else 0,
                    'tuesday': 1 if str(row.get('Tue', '')).upper() == 'X' else 0,
                    'wednesday': 1 if str(row.get('Wed', '')).upper() == 'X' else 0,
                    'thursday': 1 if str(row.get('Thurs', '')).upper() == 'X' else 0,
                    'friday': 1 if str(row.get('Fri', '')).upper() == 'X' else 0,
                    'saturday': 1 if str(row.get('Sat', '')).upper() == 'X' else 0,
                }

                # Handle amount paid
                amount = row.get('Amount Paid')
                if pd.notna(amount):
                    try:
                        customer_data['amount_paid'] = float(amount)
                    except (ValueError, TypeError):
                        customer_data['amount_paid'] = None

                # Handle subscription start date
                sub_start = row.get('Subscription Start')
                if pd.notna(sub_start):
                    if isinstance(sub_start, str):
                        try:
                            customer_data['subscription_start'] = datetime.strptime(sub_start, '%Y-%m-%d').date()
                        except ValueError:
                            try:
                                customer_data['subscription_start'] = datetime.strptime(sub_start, '%d/%m/%Y').date()
                            except ValueError:
                                customer_data['subscription_start'] = None
                    else:
                        customer_data['subscription_start'] = sub_start.date() if hasattr(sub_start, 'date') else sub_start
                else:
                    customer_data['subscription_start'] = None

                # Handle subscription end date
                sub_end = row.get('Subscription End')
                if pd.notna(sub_end):
                    if isinstance(sub_end, str):
                        try:
                            customer_data['subscription_end'] = datetime.strptime(sub_end, '%Y-%m-%d').date()
                        except ValueError:
                            try:
                                customer_data['subscription_end'] = datetime.strptime(sub_end, '%d/%m/%Y').date()
                            except ValueError:
                                customer_data['subscription_end'] = None
                    else:
                        customer_data['subscription_end'] = sub_end.date() if hasattr(sub_end, 'date') else sub_end
                else:
                    customer_data['subscription_end'] = None
                
                # Check if customer already exists
                existing = Customer.query.filter_by(customer_number=customer_number).first()
                
                if existing:
                    # Update existing customer
                    for key, value in customer_data.items():
                        setattr(existing, key, value)
                    updated += 1
                else:
                    # Create new customer
                    new_customer = Customer(**customer_data)
                    db.session.add(new_customer)
                    imported += 1
                    
            except Exception as e:
                errors += 1
                print(f"Error processing row: {e}")
                continue
        
        db.session.commit()
        
        # Build success message
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
            flash('Could not find "Service Log" sheet in the Excel file. Please ensure the file has a sheet named "Service Log".', 'danger')
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
        # Read Excel file
        xl_file = pd.ExcelFile(file)
        
        # Check if Service Log sheet exists
        if 'Service Log' not in xl_file.sheet_names:
            return jsonify({
                'error': f'Sheet "Service Log" not found. Available sheets: {", ".join(xl_file.sheet_names)}'
            }), 400
        
        # Read the Service Log sheet
        df = pd.read_excel(xl_file, sheet_name='Service Log', header=1)
        df.columns = df.columns.str.strip()
        
        # Drop rows where Number is NaN
        df = df[df['Number'].notna()]
        
        # Get counts
        total_rows = len(df)
        active_count = len(df[df['Active in Target Month?'].str.upper() == 'YES']) if 'Active in Target Month?' in df.columns else 0
        
        # Get sample data (first 5 rows)
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
        
        # Create Excel file in memory
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Service Log', index=False)
        output.seek(0)
        
        # Generate filename with timestamp
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
