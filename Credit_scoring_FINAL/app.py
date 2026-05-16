from flask import Flask, render_template, request, jsonify, redirect, session
from functools import wraps
import sqlite3
import pickle
import re
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False

app = Flask(__name__)
app.secret_key = "replace_this_with_a_random_secret"
DATABASE = "credit_history.db"

# Load model
model = pickle.load(open("model.pkl", "rb"))
le_target = pickle.load(open("target.pkl", "rb"))


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function


def calculate_emi(principal, annual_rate, years):
    months = years * 12
    if principal <= 0 or months <= 0:
        return 0.0
    monthly_rate = annual_rate / 1200.0
    if monthly_rate == 0:
        return principal / months
    factor = (1 + monthly_rate) ** months
    return principal * monthly_rate * factor / (factor - 1)


def categorize_cibil_score(cibil_score):
    """Categorize CIBIL score into risk categories."""
    if cibil_score >= 750:
        return "Excellent"
    elif cibil_score >= 650:
        return "Good"
    elif cibil_score >= 550:
        return "Average"
    else:
        return "Poor"


def get_history_date_label(timestamp_str):
    try:
        entry_date = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M").date()
    except ValueError:
        return timestamp_str

    today = datetime.now().date()
    yesterday = today.replace(day=today.day - 1) if today.day > 1 else today - timedelta(days=1)
    if entry_date == today:
        return "Today"
    elif entry_date == yesterday:
        return "Yesterday"
    return entry_date.strftime("%B %d, %Y")


def group_history_by_date(entries):
    grouped = []
    labels = []
    for entry in entries:
        label = get_history_date_label(entry["timestamp"])
        if label not in labels:
            labels.append(label)
            grouped.append({"label": label, "entries": []})
        grouped[-1]["entries"].append(entry)
    return grouped


def approve_loan_decision(cibil_score, emi, monthly_income, loan_type):
    """
    Make loan decision based on CIBIL score and EMI burden.
    Returns: (decision, risk_level, reason)
    """
    emi_to_income_ratio = (emi / monthly_income) * 100 if monthly_income > 0 else 100
    
    # Adjust thresholds based on loan type
    if loan_type == 'education':
        cibil_threshold_high = 700
        cibil_threshold_med = 600
        emi_threshold = 60  # Higher for education
    elif loan_type == 'home':
        cibil_threshold_high = 750
        cibil_threshold_med = 650
        emi_threshold = 50
    elif loan_type == 'vehicle':
        cibil_threshold_high = 750
        cibil_threshold_med = 650
        emi_threshold = 50
    else:  # personal
        cibil_threshold_high = 750
        cibil_threshold_med = 650
        emi_threshold = 50
    
    # Approval logic based on CIBIL + EMI
    if cibil_score >= cibil_threshold_high and emi_to_income_ratio <= emi_threshold:
        return ("Approved", "Low Risk", 
                f"Excellent CIBIL score ({cibil_score}) with manageable EMI ({emi_to_income_ratio:.1f}% of income)")
    elif cibil_threshold_med <= cibil_score < cibil_threshold_high:
        if emi_to_income_ratio <= emi_threshold:
            return ("Conditional Approval", "Medium Risk",
                    f"Good CIBIL score ({cibil_score}) with acceptable EMI burden. Additional verification may be required.")
        else:
            return ("Rejected", "High Risk",
                    f"EMI burden is too high ({emi_to_income_ratio:.1f}% of income). Consider reducing loan amount or extending tenure.")
    elif cibil_score >= 550 and emi_to_income_ratio > emi_threshold:
        return ("Rejected", "High Risk",
                f"EMI burden exceeds safe limits ({emi_to_income_ratio:.1f}% of income).")
    else:
        return ("Rejected", "High Risk",
                f"CIBIL score ({cibil_score}) below acceptable threshold or EMI burden too high ({emi_to_income_ratio:.1f}% of income).")


def create_database():
    with get_db_connection() as conn:
        # Create users table for authentication
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                fullname TEXT NOT NULL,
                phone TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL,
                is_admin INTEGER DEFAULT 0
            )
            """
        )
        
        # Create eligibility submissions table
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS eligibility_submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                loan_type TEXT,
                name TEXT,
                email TEXT,
                phone TEXT,
                occupation TEXT,
                location TEXT,
                age INTEGER,
                income REAL,
                co_applicant_income REAL,
                parent_name TEXT,
                parent_occupation TEXT,
                parent_income REAL,
                parent_cibil INTEGER,
                education_purpose TEXT,
                vehicle_price REAL,
                down_payment REAL,
                vehicle_type TEXT,
                loan REAL,
                interest_rate REAL,
                tenure INTEGER,
                cibil_score INTEGER,
                emi REAL,
                approval_status TEXT,
                risk_level TEXT,
                decision_reason TEXT
            )
            """
        )
        conn.commit()


create_database()

# Validation functions
def validate_email(email):
    """Validate email format"""
    pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
    return re.match(pattern, email) is not None


def validate_phone(phone):
    """Validate phone number (10 digits)"""
    return re.match(r'^\d{10}$', phone) is not None


def validate_password(password):
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one number"
    if not re.search(r'[!@#$%^&*()_+\-=\[\]{};:\'"|,.<>?]', password):
        return False, "Password must contain at least one special character"
    return True, "Password is strong"


def user_exists(username=None, email=None):
    """Check if user already exists"""
    conn = get_db_connection()
    try:
        if username:
            user = conn.execute(
                "SELECT id FROM users WHERE username = ?", (username,)
            ).fetchone()
            if user:
                return True
        if email:
            user = conn.execute(
                "SELECT id FROM users WHERE email = ?", (email,)
            ).fetchone()
            if user:
                return True
        return False
    finally:
        conn.close()

@app.route("/")
def home():
    if not session.get('logged_in'):
        return redirect('/login')
    return render_template("index.html")

@app.route("/about")
@login_required
def about():
    return render_template("about.html")

@app.route("/terms")
def terms():
    return render_template("terms.html")

@app.route("/privacy")
def privacy():
    return render_template("privacy.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get('logged_in'):
        return redirect('/')

    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        
        if not username or not password:
            error = "Please enter both username/email and password."
        else:
            conn = get_db_connection()
            try:
                # Check by username or email
                user = conn.execute(
                    "SELECT id, username, password_hash FROM users WHERE username = ? OR email = ?",
                    (username, username)
                ).fetchone()
                
                if user and check_password_hash(user['password_hash'], password):
                    session['logged_in'] = True
                    session['user_id'] = user['id']
                    session['username'] = user['username']
                    return redirect('/')
                else:
                    error = "Invalid username/email or password."
            except Exception as e:
                error = "An error occurred. Please try again."
            finally:
                conn.close()
    
    return render_template("login.html", error=error)


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if session.get('logged_in'):
        return redirect('/')
    
    error = None
    success = None
    
    if request.method == "POST":
        fullname = request.form.get("fullname", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        confirmPassword = request.form.get("confirmPassword", "").strip()
        
        # Validation
        if not all([fullname, email, phone, username, password, confirmPassword]):
            error = "All fields are required."
        elif len(fullname) < 3:
            error = "Full name must be at least 3 characters."
        elif not validate_email(email):
            error = "Please enter a valid email address."
        elif not validate_phone(phone):
            error = "Phone number must be 10 digits."
        elif len(username) < 4:
            error = "Username must be at least 4 characters."
        elif not re.match(r'^[a-zA-Z0-9_-]+$', username):
            error = "Username can only contain letters, numbers, dash, and underscore."
        elif user_exists(username=username):
            error = "Username already exists. Please choose a different one."
        elif user_exists(email=email):
            error = "Email already registered. Please use a different email or login."
        elif password != confirmPassword:
            error = "Passwords do not match."
        else:
            is_valid, msg = validate_password(password)
            if not is_valid:
                error = msg
        
        # If no error, create the user
        if not error:
            try:
                conn = get_db_connection()
                conn.execute(
                    """
                    INSERT INTO users (username, email, fullname, phone, password_hash, created_at, is_admin)
                    VALUES (?, ?, ?, ?, ?, ?, 0)
                    """,
                    (username, email, fullname, phone, 
                     generate_password_hash(password), datetime.now().strftime("%Y-%m-%d %H:%M"))
                )
                conn.commit()
                conn.close()
                
                success = "Account created successfully! Redirecting to login..."
                return render_template("signup.html", success=success)
            except Exception as e:
                error = f"An error occurred: {str(e)}"
    
    return render_template("signup.html", error=error)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/eligibility", methods=["GET", "POST"])
@login_required
def eligibility():
    loan_type = (request.form.get('loan_type') or request.args.get('type') or 'personal').lower()
    if loan_type not in ['personal', 'home', 'vehicle', 'education']:
        loan_type = 'personal'
    result = False
    approval_status = None
    risk_level = None
    decision_reason = None
    emi = None
    emi_options = []
    loan = None
    interest_rate = {"personal": "10.0", "home": "7.0", "vehicle": "8.0", "education": "6.0"}.get(loan_type, "10.0")
    tenure = "5"
    name = email = phone = occupation = location = ""
    age = income = co_applicant_income = cibil_score = ""
    parent_name = parent_occupation = parent_income = parent_cibil = education_purpose = ""
    vehicle_price = down_payment = vehicle_type = ""
    errors = []
    cibil_category = None
    emi_to_income_ratio = 0

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        occupation = request.form.get("occupation", "").strip()
        location = request.form.get("location", "").strip()
        age = request.form.get("age", "").strip()
        
        if loan_type == 'education':
            parent_name = request.form.get("parent_name", "").strip()
            parent_occupation = request.form.get("parent_occupation", "").strip()
            parent_income = request.form.get("parent_income", "").strip()
            parent_cibil = request.form.get("parent_cibil", "").strip()
            education_purpose = request.form.get("education_purpose", "").strip()
            income = parent_income  # Use parent income for calculations
            cibil_score = parent_cibil
        elif loan_type == 'vehicle':
            vehicle_price = request.form.get("vehicle_price", "").strip()
            down_payment = request.form.get("down_payment", "").strip()
            vehicle_type = request.form.get("vehicle_type", "").strip()
            income = request.form.get("income", "").strip()
            cibil_score = request.form.get("cibil_score", "").strip()
        else:
            income = request.form.get("income", "").strip()
            cibil_score = request.form.get("cibil_score", "").strip()
        
        loan = request.form.get("loan", "").strip()
        interest_rate = request.form.get("interest_rate", interest_rate).strip()
        tenure = request.form.get("tenure", "5").strip()

        # Validation
        if not name:
            errors.append("Full name is required.")
        if not email or "@" not in email or "." not in email:
            errors.append("Enter a valid email address.")
        if not re.match(r"^[0-9+\-\s]{10,16}$", phone):
            errors.append("Enter a valid phone number.")
        if not occupation:
            errors.append("Occupation is required.")
        if not location:
            errors.append("City / State is required.")
        if not age.isdigit() or int(age) <= 0 or int(age) > 120:
            errors.append("Enter a valid age (1-120).")
        
        if loan_type == 'education':
            if not parent_name:
                errors.append("Parent name is required.")
            if not parent_occupation:
                errors.append("Parent occupation is required.")
            if not re.match(r"^\d+(\.\d+)?$", parent_income) or float(parent_income) <= 0:
                errors.append("Enter a valid parent monthly income.")
            if not parent_cibil.isdigit() or int(parent_cibil) < 300 or int(parent_cibil) > 900:
                errors.append("Enter a valid parent CIBIL score (300-900).")
            if not education_purpose:
                errors.append("Select education purpose.")
        elif loan_type == 'vehicle':
            if not re.match(r"^\d+(\.\d+)?$", vehicle_price) or float(vehicle_price) <= 0:
                errors.append("Enter a valid vehicle price.")
            if not re.match(r"^\d+(\.\d+)?$", down_payment) or float(down_payment) < 0:
                errors.append("Enter a valid down payment.")
            if float(down_payment) >= float(vehicle_price):
                errors.append("Down payment must be less than vehicle price.")
            if not vehicle_type:
                errors.append("Select vehicle type.")
            if not re.match(r"^\d+(\.\d+)?$", income) or float(income) <= 0:
                errors.append("Enter a valid monthly income.")
            if not cibil_score.isdigit() or int(cibil_score) < 300 or int(cibil_score) > 900:
                errors.append("Enter a valid CIBIL score (300-900).")
        else:
            if not re.match(r"^\d+(\.\d+)?$", income) or float(income) <= 0:
                errors.append("Enter a valid monthly income.")
            if not cibil_score.isdigit() or int(cibil_score) < 300 or int(cibil_score) > 900:
                errors.append("Enter a valid CIBIL score (300-900).")
        
        if not re.match(r"^\d+(\.\d+)?$", loan) or float(loan) <= 0:
            errors.append("Enter a valid loan amount.")
        if not re.match(r"^\d+(\.\d+)?$", interest_rate) or float(interest_rate) < 0 or float(interest_rate) > 30:
            errors.append("Enter a valid annual interest rate (0-30%).")
        if tenure not in ["1", "3", "5", "10"]:
            errors.append("Select a valid loan tenure (1, 3, 5, or 10 years).")

        if not errors:
            age_val = int(age)
            if loan_type == 'vehicle':
                vehicle_price_val = float(vehicle_price)
                down_payment_val = float(down_payment)
                loan_val = vehicle_price_val - down_payment_val
                income_val = float(income)
                cibil_val = int(cibil_score)
            elif loan_type == 'education':
                income_val = float(parent_income)
                cibil_val = int(parent_cibil)
                loan_val = float(loan)
            else:
                income_val = float(income)
                cibil_val = int(cibil_score)
                loan_val = float(loan)
            
            annual_rate_val = float(interest_rate)
            tenure_val = int(tenure)

            # Calculate EMI
            emi = calculate_emi(loan_val, annual_rate_val, tenure_val)
            emi_to_income_ratio = (emi / income_val) * 100 if income_val > 0 else 100
            cibil_category = categorize_cibil_score(cibil_val)

            # Get approval decision
            approval_status, risk_level, decision_reason = approve_loan_decision(cibil_val, emi, income_val, loan_type)
            
            # Change Conditional to Verification Required
            if approval_status == "Conditional Approval":
                approval_status = "Verification Required"

            # Generate EMI options
            for years in [1, 3, 5, 10]:
                monthly_emi = calculate_emi(loan_val, annual_rate_val, years)
                emi_options.append({
                    "years": years,
                    "months": years * 12,
                    "emi": round(monthly_emi, 2),
                })

            result = True

            # Store in database
            submission_time = datetime.now().strftime("%Y-%m-%d %H:%M")
            with get_db_connection() as conn:
                conn.execute(
                    """
                    INSERT INTO eligibility_submissions (
                        timestamp, loan_type, name, email, phone, occupation, location,
                        age, income, co_applicant_income, parent_name, parent_occupation, parent_income, parent_cibil, education_purpose,
                        vehicle_price, down_payment, vehicle_type, loan, interest_rate, tenure,
                        cibil_score, emi, approval_status, risk_level, decision_reason
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        submission_time, loan_type, name, email, phone, occupation, location,
                        age_val, income_val if 'income_val' in locals() else 0, 0,  # co_applicant_income set to 0
                        parent_name, parent_occupation, float(parent_income) if parent_income else 0, int(parent_cibil) if parent_cibil else 0, education_purpose,
                        float(vehicle_price) if vehicle_price else 0, float(down_payment) if down_payment else 0, vehicle_type,
                        loan_val, annual_rate_val, tenure_val,
                        cibil_val, round(emi, 2), approval_status, risk_level, decision_reason,
                    ),
                )
                conn.commit()

    return render_template("eligibility.html",
                           loan_type=loan_type,
                           result=result,
                           approval_status=approval_status,
                           risk_level=risk_level,
                           decision_reason=decision_reason,
                           cibil_score=cibil_score,
                           cibil_category=cibil_category,
                           loan=loan,
                           emi=emi if emi else 0,
                           emi_to_income_ratio=round(emi_to_income_ratio, 2),
                           emi_options=emi_options,
                           interest_rate=interest_rate,
                           tenure=tenure,
                           errors=errors,
                           name=name,
                           email=email,
                           phone=phone,
                           occupation=occupation,
                           location=location,
                           age=age,
                           income=income,
                           parent_name=parent_name,
                           parent_occupation=parent_occupation,
                           parent_income=parent_income,
                           parent_cibil=parent_cibil,
                           education_purpose=education_purpose,
                           vehicle_price=vehicle_price,
                           down_payment=down_payment,
                           vehicle_type=vehicle_type)

@app.route("/history")
@login_required
def history():
    with get_db_connection() as conn:
        rows = conn.execute(
            "SELECT timestamp, loan_type, name, occupation, location, loan, approval_status, risk_level, emi FROM eligibility_submissions ORDER BY id DESC"
        ).fetchall()

    eligibility_history = [dict(row) for row in rows]
    grouped_history = group_history_by_date(eligibility_history)
    return render_template("history.html",
                           grouped_history=grouped_history)

@app.route("/admin")
@login_required
def admin():
    with get_db_connection() as conn:
        rows = conn.execute(
            "SELECT id, timestamp, loan_type, name, email, phone, approval_status FROM eligibility_submissions WHERE approval_status NOT IN ('Approved', 'Rejected') ORDER BY id DESC"
        ).fetchall()

    pending_verifications = [dict(row) for row in rows]
    return render_template("admin.html", pending_verifications=pending_verifications)

@app.route("/verify/<int:submission_id>", methods=["POST"])
def verify(submission_id):
    action = request.form.get("action")
    print(f"Verifying submission {submission_id} with action {action}")
    print(f"Form data: {request.form}")
    if action in ["Approved", "Rejected"]:
        with get_db_connection() as conn:
            conn.execute(
                "UPDATE eligibility_submissions SET approval_status = ? WHERE id = ?",
                (action, submission_id)
            )
            conn.commit()
            print(f"Updated submission {submission_id} to {action}")
    return redirect("/admin")


@app.route("/generate_report", methods=["POST"])
def generate_report():
    """Generate PDF report for loan eligibility"""
    data = request.json
    
    if not HAS_REPORTLAB:
        return jsonify({"error": "PDF generation not available. Install reportlab: pip install reportlab"}), 400
    
    try:
        from io import BytesIO
        from flask import send_file
        
        # Create PDF
        pdf_buffer = BytesIO()
        doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#0f172a'),
            spaceAfter=30,
            alignment=1
        )
        elements.append(Paragraph("Loan Eligibility Report", title_style))
        elements.append(Spacer(1, 0.3*inch))
        
        # Personal Information
        personal_data = [
            ["Loan Type", data.get("loan_type", "").title()],
            ["Applicant Name", data.get("name", "")],
            ["Email", data.get("email", "")],
            ["Phone", data.get("phone", "")],
            ["Occupation", data.get("occupation", "")],
            ["Location", data.get("location", "")],
            ["Age", data.get("age", "")],
        ]
        
        if data.get("loan_type") == "education":
            personal_data.extend([
                ["Parent Name", data.get("parent_name", "")],
                ["Parent Occupation", data.get("parent_occupation", "")],
                ["Education Purpose", data.get("education_purpose", "").replace("_", " ").title()],
            ])
        
        personal_table = Table(personal_data, colWidths=[2*inch, 4*inch])
        personal_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e0f2fe')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        elements.append(personal_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Loan Details
        loan_data = [
            ["Loan Amount", f"₹{float(data.get('loan', 0)):,.2f}"],
        ]
        if data.get("loan_type") == "education":
            loan_data.append(["Parent Income", f"₹{float(data.get('parent_income', 0)):,.2f}"])
        elif data.get("loan_type") == "vehicle":
            loan_data.extend([
                ["Vehicle Price", f"₹{float(data.get('vehicle_price', 0)):,.2f}"],
                ["Down Payment", f"₹{float(data.get('down_payment', 0)):,.2f}"],
                ["Vehicle Type", data.get("vehicle_type", "").title()],
                ["Applicant Income", f"₹{float(data.get('income', 0)):,.2f}"],
            ])
        else:
            loan_data.append(["Monthly Income", f"₹{float(data.get('income', 0)):,.2f}"])
        loan_data.extend([
            ["Annual Interest Rate", f"{data.get('interest_rate', 0)}%"],
            ["Loan Tenure", f"{data.get('tenure', 0)} years"],
            ["Monthly EMI", f"₹{float(data.get('emi', 0)):,.2f}"],
            ["EMI to Income Ratio", f"{data.get('emi_ratio', 0)}%"],
        ])
        
        loan_table = Table(loan_data, colWidths=[2*inch, 4*inch])
        loan_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#dcfce7')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        elements.append(loan_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Decision
        approval = data.get("approval_status") or "Pending"
        risk = data.get("risk_level") or "Unknown"
        reason = data.get("decision_reason", "")
        
        decision_data = [
            ["CIBIL Score", f"{data.get('cibil_score', '')} ({data.get('cibil_category', '')})"],
            ["Approval Status", approval],
            ["Risk Level", risk],
            ["Decision Reason", reason],
        ]
        
        decision_table = Table(decision_data, colWidths=[2*inch, 4*inch])
        decision_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#fef3c7')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        elements.append(decision_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Footer
        footer_text = "This report has been generated automatically by Smart Lending. Generated on " + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.grey,
            alignment=1
        )
        elements.append(Paragraph(footer_text, footer_style))
        
        doc.build(elements)
        pdf_buffer.seek(0)
        
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f"loan_eligibility_{data.get('name', 'report')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        )
    except Exception as e:
        return jsonify({"error": f"PDF generation failed: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(debug=True)
