from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import mysql.connector
from mysql.connector import Error
import hashlib
from datetime import datetime
import re
import random
import string

# Import admin, customer, and deliveryman blueprints
from admin import admin_bp
from customer import customer_bp
from deliveryman import deliveryman_bp

app = Flask(__name__)
app.secret_key = 'our_secret_key_here'  # Change this to a secure secret key

# Register blueprints
app.register_blueprint(admin_bp)
app.register_blueprint(customer_bp)
app.register_blueprint(deliveryman_bp)

# Database configuration
DB_CONFIG = {
    'host': '127.0.0.1',
    'database': 'drugweb',
    'user': 'root',
    'password': ''  # Add your MySQL password here
}

def get_db_connection():
    """Create and return a database connection"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        # Test if database exists, if not create it
        cursor = connection.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS drugweb")
        cursor.execute("USE drugweb")
        cursor.close()
        
        # Reconnect to the database
        DB_CONFIG['database'] = 'drugweb'
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        print("Please ensure MySQL server is running and accessible")
        return None

def generate_customer_id():
    """Generate next customer ID in format CM001, CM002, etc."""
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute("SELECT Customer_ID FROM customer ORDER BY Customer_ID DESC LIMIT 1")
        result = cursor.fetchone()
        
        if result:
            last_id = result[0]
            number = int(last_id[2:]) + 1
            new_id = f"CM{number:03d}"
        else:
            new_id = "CM001"
        
        cursor.close()
        connection.close()
        return new_id
    return "CM001"

@app.route('/')
def index():
    return render_template('index.html')

# --- MAINTENANCE ROUTES (Restored) ---

@app.route('/update_medicine_db')
def update_medicine_db():
    """Add Category column to medicine table"""
    connection = get_db_connection()
    if not connection:
        return "❌ Database connection failed."
    
    try:
        cursor = connection.cursor()
        cursor.execute("ALTER TABLE medicine ADD COLUMN Category VARCHAR(50)")
        connection.commit()
        
        cursor.execute("UPDATE medicine SET Category = 'Pain Relief' WHERE Name LIKE '%Paracetamol%' OR Name LIKE '%Aspirin%'")
        cursor.execute("UPDATE medicine SET Category = 'Antibiotic' WHERE Name LIKE '%Amoxicillin%' OR Name LIKE '%Penicillin%'")
        cursor.execute("UPDATE medicine SET Category = 'General' WHERE Category IS NULL")
        connection.commit()
        
        cursor.close()
        connection.close()
        return "✅ Category column added to medicine table and sample data updated!"
    except Exception as e:
        return f"Database update result: {str(e)}<br><small>Note: If error mentions 'Duplicate column name', the column already exists and this is normal.</small>"

@app.route('/update_db')
def update_db():
    """Add Status column to customer_request table"""
    connection = get_db_connection()
    if not connection:
        return "❌ Database connection failed."
    
    try:
        cursor = connection.cursor()
        cursor.execute("ALTER TABLE customer_request ADD COLUMN Status VARCHAR(20) DEFAULT 'Pending'")
        connection.commit()
        cursor.close()
        connection.close()
        return "✅ Status column added to customer_request table successfully!"
    except Exception as e:
        return f"Database update result: {str(e)}<br><small>Note: If error mentions 'Duplicate column name', the column already exists and this is normal.</small>"

@app.route('/fix_db')
def fix_db():
    """Fix database by adding missing columns"""
    connection = get_db_connection()
    if not connection:
        return "❌ Database connection failed."
    
    try:
        cursor = connection.cursor()
        
        cursor.execute("""
            ALTER TABLE customer_request 
            ADD COLUMN Request_ID INT AUTO_INCREMENT PRIMARY KEY FIRST
        """)
        
        cursor.execute("""
            ALTER TABLE customer_request 
            ADD COLUMN IF NOT EXISTS Status VARCHAR(20) DEFAULT 'Pending'
        """)
        
        connection.commit()
        cursor.close()
        connection.close()
        return "✅ Database structure fixed! Request_ID and Status columns added."
    except Exception as e:
        return f"Database fix result: {str(e)} (This might be normal if columns already exist)"

# --- MAIN SETUP ROUTE (Updated with new design) ---

@app.route('/setup_db')
def setup_db():
    """Setup database tables and create test customer"""
    connection = get_db_connection()
    if not connection:
        return "❌ Database connection failed. Please start MySQL server."
    
    try:
        cursor = connection.cursor()
        
        # Create user table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user (
                ID VARCHAR(10) PRIMARY KEY,
                F_name VARCHAR(50) NOT NULL,
                L_name VARCHAR(50) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password VARCHAR(100) NOT NULL,
                address TEXT,
                phone VARCHAR(20)
            )
        """)
        
        # Create customer table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customer (
                Customer_ID VARCHAR(10) PRIMARY KEY,
                points INT DEFAULT 0,
                FOREIGN KEY (Customer_ID) REFERENCES user(ID)
            )
        """)
        
        # Create admin table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admin (
                Admin_ID VARCHAR(10) PRIMARY KEY,
                FOREIGN KEY (Admin_ID) REFERENCES user(ID)
            )
        """)
        
        # Create delivery man table (Updated to match deliveryman.py expectations)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS deliveryman (
                DeliveryMan_ID VARCHAR(10) PRIMARY KEY,
                Name VARCHAR(100),
                Phone VARCHAR(20),
                Email VARCHAR(100),
                Area VARCHAR(100),
                FOREIGN KEY (DeliveryMan_ID) REFERENCES user(ID)
            )
        """)
        
        # Create medicine table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS medicine (
                Med_Code VARCHAR(10) PRIMARY KEY,
                Name VARCHAR(100) NOT NULL,
                Generic_name VARCHAR(100),
                Category VARCHAR(50),
                Price DECIMAL(10,2) NOT NULL,
                Stock INT DEFAULT 0
            )
        """)
        
        # Create customer_review table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customer_review (
                Review_ID INT AUTO_INCREMENT PRIMARY KEY,
                Customer_ID VARCHAR(10),
                review TEXT,
                FOREIGN KEY (Customer_ID) REFERENCES customer(Customer_ID)
            )
        """)
        
        # Create customer_request table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customer_request (
                Request_ID INT AUTO_INCREMENT PRIMARY KEY,
                Customer_ID VARCHAR(10),
                request_med_name VARCHAR(100),
                Expected_date DATE,
                Status VARCHAR(20) DEFAULT 'Pending',
                FOREIGN KEY (Customer_ID) REFERENCES customer(Customer_ID)
            )
        """)
        
        # Create cart table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cart (
                Cart_ID INT AUTO_INCREMENT PRIMARY KEY,
                Customer_ID VARCHAR(10),
                Med_Code VARCHAR(10),
                Med_Name VARCHAR(100),
                Quantity INT DEFAULT 1,
                Price DECIMAL(10,2),
                total_price DECIMAL(10,2),
                Added_Date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (Customer_ID) REFERENCES customer(Customer_ID),
                FOREIGN KEY (Med_Code) REFERENCES medicine(Med_Code)
            )
        """)
        
        # Create notifications table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notifications (
                notification_id INT AUTO_INCREMENT PRIMARY KEY,
                customer_id VARCHAR(10),
                message TEXT NOT NULL,
                type VARCHAR(50) DEFAULT 'general',
                is_read BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customer(Customer_ID)
            )
        """)
        
        # Create points_history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS points_history (
                history_id INT AUTO_INCREMENT PRIMARY KEY,
                customer_id VARCHAR(10),
                points_earned INT NOT NULL,
                transaction_type VARCHAR(20) DEFAULT 'earned',
                payment_id VARCHAR(20),
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customer(Customer_ID)
            )
        """)
        
        # Create payment table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS payment (
                payment_id VARCHAR(20) PRIMARY KEY,
                Customer_ID VARCHAR(10),
                amount DECIMAL(10,2),
                payment_type VARCHAR(50),
                DeliveryMan_ID VARCHAR(10),
                status VARCHAR(50) DEFAULT 'Assigned',
                delivery_date DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (Customer_ID) REFERENCES customer(Customer_ID),
                FOREIGN KEY (DeliveryMan_ID) REFERENCES deliveryman(DeliveryMan_ID)
            )
        """)
        
        # Insert Test Data
        cursor.execute("""
            INSERT IGNORE INTO user (ID, F_name, L_name, email, password, address, phone) 
            VALUES ('CM001', 'John', 'Doe', 'customer@test.com', 'password123', '123 Main St', '555-1234')
        """)
        cursor.execute("""
            INSERT IGNORE INTO customer (Customer_ID, points) 
            VALUES ('CM001', 100)
        """)
        
        cursor.execute("""
            INSERT IGNORE INTO user (ID, F_name, L_name, email, password, address, phone) 
            VALUES ('AD001', 'Admin', 'User', 'admin@test.com', 'admin123', '456 Admin St', '555-5678')
        """)
        cursor.execute("""
            INSERT IGNORE INTO admin (Admin_ID) 
            VALUES ('AD001')
        """)
        
        cursor.execute("""
            INSERT IGNORE INTO user (ID, F_name, L_name, email, password, address, phone) 
            VALUES ('DM001', 'Mike', 'Delivery', 'delivery@test.com', 'delivery123', '789 Delivery St', '555-9999')
        """)
        cursor.execute("""
            INSERT IGNORE INTO deliveryman (DeliveryMan_ID, Name, Phone, Email, Area) 
            VALUES ('DM001', 'Mike Delivery', '555-9999', 'delivery@test.com', 'City Center')
        """)
        
        medicines = [
            ('MED001', 'Paracetamol', 'Acetaminophen', 'Pain Relief', 5.00, 100),
            ('MED002', 'Aspirin', 'Acetylsalicylic Acid', 'Pain Relief', 3.50, 75),
            ('MED003', 'Amoxicillin', 'Amoxicillin', 'Antibiotic', 12.00, 50),
            ('MED004', 'Napa Extra', 'Paracetamol Caffeine', 'Pain Relief', 2.50, 200),
            ('MED005', 'Seclo 20', 'Omeprazole', 'Gastric', 7.00, 150)
        ]
        
        for med in medicines:
            cursor.execute("""
                INSERT IGNORE INTO medicine (Med_Code, Name, Generic_name, Category, Price, Stock) 
                VALUES (%s, %s, %s, %s, %s, %s)
            """, med)
        
        connection.commit()
        cursor.close()
        connection.close()
        
        # --- RETURN THE NEW TEMPLATE ---
        return render_template('setup_success.html')
        
    except Exception as e:
        return f"❌ Error setting up database: {str(e)}"

# --- AUTH ROUTES ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user_type = request.form['user_type']
        
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor(dictionary=True)
            
            # Check user credentials
            cursor.execute("SELECT * FROM user WHERE email = %s AND password = %s", (email, password))
            user = cursor.fetchone()
            
            if user:
                user_id = user['ID']
                
                # Check user type and redirect accordingly
                if user_type == 'admin':
                    cursor.execute("SELECT * FROM admin WHERE Admin_ID = %s", (user_id,))
                    admin = cursor.fetchone()
                    if admin:
                        session['user_id'] = user_id
                        session['user_type'] = 'admin'
                        session['user_name'] = f"{user['F_name']} {user['L_name']}"
                        flash('Admin login successful!', 'success')
                        return redirect(url_for('admin.dashboard'))
                    else:
                        flash('Invalid admin credentials!', 'error')
                
                elif user_type == 'deliveryman':
                    cursor.execute("SELECT * FROM deliveryman WHERE DeliveryMan_ID = %s", (user_id,))
                    deliveryman = cursor.fetchone()
                    if deliveryman:
                        session['user_id'] = user_id
                        session['user_type'] = 'deliveryman'
                        session['user_name'] = f"{user['F_name']} {user['L_name']}"
                        flash('Delivery man login successful!', 'success')
                        return redirect(url_for('deliveryman.dashboard'))
                    else:
                        flash('Invalid delivery man credentials!', 'error')
                
                elif user_type == 'customer':
                    cursor.execute("SELECT * FROM customer WHERE Customer_ID = %s", (user_id,))
                    customer = cursor.fetchone()
                    if customer:
                        session['user_id'] = user_id
                        session['user_type'] = 'customer'
                        session['user_name'] = f"{user['F_name']} {user['L_name']}"
                        flash('Customer login successful!', 'success')
                        return redirect(url_for('customer.dashboard'))
                    else:
                        flash('Invalid customer credentials!', 'error')
            else:
                flash('Invalid email or password!', 'error')
            
            cursor.close()
            connection.close()
        else:
            flash('Database connection failed!', 'error')
    
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        f_name = request.form['f_name']
        l_name = request.form['l_name']
        email = request.form['email']
        password = request.form['password']
        address = request.form['address']
        phone = request.form['phone']
        
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            
            # Check if email already exists
            cursor.execute("SELECT * FROM user WHERE email = %s", (email,))
            existing_user = cursor.fetchone()
            
            if existing_user:
                flash('Email already exists!', 'error')
            else:
                # Generate new customer ID
                customer_id = generate_customer_id()
                
                try:
                    # Insert into user table
                    cursor.execute("""
                        INSERT INTO user (ID, F_name, L_name, email, password, address, phone) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (customer_id, f_name, l_name, email, password, address, phone))
                    
                    # Insert into customer table
                    cursor.execute("INSERT INTO customer (Customer_ID, points) VALUES (%s, 0)", (customer_id,))
                    
                    connection.commit()
                    flash('Account created successfully! Please login.', 'success')
                    return redirect(url_for('login'))
                    
                except Error as e:
                    connection.rollback()
                    flash(f'Error creating account: {e}', 'error')
            
            cursor.close()
            connection.close()
    
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully!', 'success')
    return redirect(url_for('index'))

# --- DEBUG & TESTING ROUTES (Restored) ---

@app.route('/cart_minimal')
def cart_minimal():
    """Minimal cart page for testing"""
    return '''
    <html>
    <head><title>Cart Test</title></head>
    <body>
        <h1>Cart Page Test</h1>
        <p>This is a minimal cart page to test if routing works.</p>
        <a href="/customer/dashboard">Back to Dashboard</a>
    </body>
    </html>
    '''

@app.route('/check_customer_id')
def check_customer_id():
    """Check if current session customer_id exists in customer table"""
    if 'user_id' not in session:
        return "Please login first"
    
    connection = get_db_connection()
    if not connection:
        return "Database connection failed"
    
    try:
        cursor = connection.cursor()
        
        session_customer_id = session['user_id']
        
        # Check if customer exists
        cursor.execute("SELECT * FROM customer WHERE Customer_ID = %s", (session_customer_id,))
        customer = cursor.fetchone()
        
        # Check payment table structure for foreign key constraints
        cursor.execute("SHOW CREATE TABLE payment")
        payment_structure = cursor.fetchone()[1]
        
        # Get all customers
        cursor.execute("SELECT Customer_ID, Name FROM customer LIMIT 5")
        customers = cursor.fetchall()
        
        html = f"""
        <h1>Customer ID Debug</h1>
        <h3>Session Info:</h3>
        <p><strong>Session user_id:</strong> {session_customer_id}</p>
        <p><strong>Customer exists:</strong> {'✅ YES' if customer else '❌ NO'}</p>
        
        <h3>Payment Table Structure:</h3>
        <pre>{payment_structure}</pre>
        """
        return html
        
    except Exception as e:
        return f"<h1>Error</h1><p>{str(e)}</p>"
    finally:
        cursor.close()
        connection.close()

@app.route('/check_payment_table')
def check_payment_table():
    """Check payment table structure and constraints"""
    connection = get_db_connection()
    if not connection:
        return "Database connection failed"
    
    try:
        cursor = connection.cursor()
        cursor.execute("DESCRIBE payment")
        columns = cursor.fetchall()
        
        cursor.execute("SELECT COUNT(*) FROM payment")
        count = cursor.fetchone()[0]
        
        html = "<h1>Payment Table Info</h1>"
        html += f"<p>Total records: {count}</p>"
        html += "<h3>Table Structure:</h3><table border='1'>"
        html += "<tr><th>Field</th><th>Type</th><th>Null</th><th>Key</th><th>Default</th><th>Extra</th></tr>"
        
        for col in columns:
            html += f"<tr><td>{col[0]}</td><td>{col[1]}</td><td>{col[2]}</td><td>{col[3]}</td><td>{col[4]}</td><td>{col[5]}</td></tr>"
        
        html += "</table>"
        return html
    except Exception as e:
        return f"<h1>Error</h1><p>{str(e)}</p>"
    finally:
        cursor.close()
        connection.close()

@app.route('/test_payment')
def test_payment():
    """Test payment page without login requirement"""
    print("DEBUG: Test payment page accessed")
    
    cart_items = [
        {'name': 'Test Medicine A', 'quantity': 2, 'unit_price': 15.50, 'total': 31.00},
        {'name': 'Test Medicine B', 'quantity': 1, 'unit_price': 25.75, 'total': 25.75}
    ]
    total_amount = 56.75
    
    try:
        return render_template('payment_page.html', cart_items=cart_items, total_amount=total_amount)
    except Exception as e:
        import traceback
        return f"<h1>Template Error</h1><p>{str(e)}</p><pre>{traceback.format_exc()}</pre>"
@app.route('/force_fix_cart')
def force_fix_cart():
    connection = get_db_connection()
    if not connection: return "❌ DB Connection Failed"
    try:
        cursor = connection.cursor()
        # 1. Drop the bad table completely
        cursor.execute("DROP TABLE IF EXISTS cart")
        
        # 2. Recreate it with the missing 'total_price' column
        cursor.execute("""
            CREATE TABLE cart (
                Cart_ID INT AUTO_INCREMENT PRIMARY KEY,
                Customer_ID VARCHAR(10),
                Med_Code VARCHAR(10),
                Med_Name VARCHAR(100),
                Quantity INT DEFAULT 1,
                Price DECIMAL(10,2),
                total_price DECIMAL(10,2),
                Added_Date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (Customer_ID) REFERENCES customer(Customer_ID),
                FOREIGN KEY (Med_Code) REFERENCES medicine(Med_Code)
            )
        """)
        connection.commit()
        cursor.close()
        connection.close()
        return "<h1>✅ FIX APPLIED!</h1><p>The cart table has been reset. You can now go back to the dashboard.</p>"
    except Exception as e:
        return f"<h1>Error:</h1> {str(e)}"

if __name__ == '__main__':
    app.run(debug=True)
    
