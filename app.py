from flask import Flask, render_template, request, redirect, url_for, send_from_directory, session, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for session management

app.config['UPLOAD_FOLDER'] = 'reports/'

if not os.path.exists('reports'):
    os.makedirs('reports')

def init_db():
    conn = sqlite3.connect('adminlogin.db')
    cursor = conn.cursor()
    
    # Create 'patients' table if not exists
    cursor.execute('''CREATE TABLE IF NOT EXISTS patients (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT, age INTEGER, gender TEXT, phone TEXT,
                        email TEXT, address TEXT, medical_history TEXT, report TEXT)''')

    # Create 'admins' table if not exists
    cursor.execute('''CREATE TABLE IF NOT EXISTS admins (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT NOT NULL UNIQUE,
                        email TEXT NOT NULL UNIQUE,
                        phone TEXT NOT NULL UNIQUE,
                        password TEXT NOT NULL)''')

    conn.commit()
    conn.close()

# Call the function to initialize the database
init_db()

# Routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        conn = sqlite3.connect('adminlogin.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM admins WHERE username=? AND password=?", (username, password))
        admin = cursor.fetchone()
        conn.close()

        if admin:
            session['admin_logged_in'] = True  # Store session
            session['admin_username'] = username
            return redirect(url_for('admin_dashboard'))
        else:
            flash("Invalid username or password", "error")
            return redirect(url_for('admin_login'))

    return render_template('admin_login.html')

@app.route('/admin_dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        flash("Please log in first", "error")
        return redirect(url_for('admin_login'))
    return render_template('admin_dashboard.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        phone = request.form.get('phone')
        password = request.form.get('password')

        try:
            conn = sqlite3.connect('adminlogin.db')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO admins (username, email, phone, password) VALUES (?, ?, ?, ?)",
                           (username, email, phone, password))
            conn.commit()
            conn.close()

            flash("Signup successful! Please log in.", "success")
            return redirect(url_for('admin_login'))

        except sqlite3.IntegrityError:
            flash("Email or phone number already exists", "error")
            return redirect(url_for('signup'))

    return render_template('signup.html')

@app.route('/add_patient', methods=['GET', 'POST'])
def add_patient():
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        gender = request.form['gender']
        phone = request.form['phone']
        email = request.form['email']
        address = request.form['address']
        medical_history = request.form['medical_history']
        
        # Handling File Upload
        report = request.files['report']
        report_filename = ''
        if report:
            report_filename = os.path.join(app.config['UPLOAD_FOLDER'], report.filename)
            report.save(report_filename)
        
        # Insert into Database
        conn = sqlite3.connect('addpatient.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO patients (name, age, gender, phone, email, address, medical_history, report) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                       (name, age, gender, phone, email, address, medical_history, report_filename))
        conn.commit()
        conn.close()
        
        flash("Patient added successfully!", "success")
        return redirect(url_for('admin_dashboard'))
    return render_template('add_patient.html')

@app.route('/view_reports')
def view_reports():
    conn = sqlite3.connect('addpatient.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM patients")
    patients = cursor.fetchall()
    conn.close()
    return render_template('view_reports.html', patients=patients)

@app.route('/reports/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    flash("Logged out successfully", "success")
    return redirect(url_for('admin_login'))

if __name__ == '__main__':
    app.run(debug=True)
