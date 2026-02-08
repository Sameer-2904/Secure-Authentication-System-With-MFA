from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from flask_bcrypt import Bcrypt
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import jwt
import datetime
import pyotp
import sqlite3
import os
import io
import base64
import pyqrcode
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-super-secret-key-change-in-production'
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(minutes=30)

bcrypt = Bcrypt(app)
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# Database initialization
DATABASE = 'users.db'

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database with users table"""
    if not os.path.exists(DATABASE):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                mfa_secret TEXT NOT NULL,
                failed_attempts INTEGER DEFAULT 0,
                locked BOOLEAN DEFAULT 0,
                locked_until TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()
        print("Database initialized successfully!")

def token_required(f):
    """Decorator to check if valid JWT token is present"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"message": "Token is missing"}), 401
        
        try:
            token = token.split(" ")[1]  # Remove 'Bearer ' prefix
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = data['user']
        except:
            return jsonify({"message": "Token is invalid"}), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated_function

@app.route('/')
def home():
    """Home page - redirect to login"""
    return render_template('login.html')

@app.route('/register', methods=['GET'])
def register_page():
    """Display registration page"""
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    """Dashboard after successful login"""
    return render_template('dashboard.html')

@app.route('/api/register', methods=['POST'])
@limiter.limit("5 per hour")
def register():
    """Register a new user"""
    try:
        data = request.json
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        # Validation
        if not username or not email or not password:
            return jsonify({"message": "All fields are required"}), 400
        
        if len(password) < 8:
            return jsonify({"message": "Password must be at least 8 characters"}), 400
        
        if len(username) < 3:
            return jsonify({"message": "Username must be at least 3 characters"}), 400
        
        # Check if user already exists
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ? OR email = ?', (username, email))
        
        if cursor.fetchone():
            conn.close()
            return jsonify({"message": "Username or email already exists"}), 400
        
        # Create user
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        mfa_secret = pyotp.random_base32()
        
        cursor.execute('''
            INSERT INTO users (username, email, password_hash, mfa_secret)
            VALUES (?, ?, ?, ?)
        ''', (username, email, hashed_password, mfa_secret))
        
        conn.commit()
        conn.close()
        
        # Generate QR code
        totp = pyotp.TOTP(mfa_secret)
        qr = pyqrcode.create(totp.provisioning_uri(
            name=email,
            issuer_name='Secure Auth System'
        ))
        
        # Convert QR code to base64
        qr_buffer = io.BytesIO()
        qr.svg(qr_buffer, scale=8)
        qr_buffer.seek(0)
        qr_base64 = base64.b64encode(qr_buffer.getvalue()).decode('utf-8')
        
        return jsonify({
            "message": "User registered successfully",
            "mfa_secret": mfa_secret,
            "qr_code": qr_base64
        }), 201
    
    except Exception as e:
        return jsonify({"message": f"Registration error: {str(e)}"}), 500

@app.route('/api/login', methods=['POST'])
@limiter.limit("10 per minute")
def login():
    """Authenticate user with username and password"""
    try:
        data = request.json
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        if not username or not password:
            return jsonify({"message": "Username and password are required"}), 400
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        conn.close()
        
        if not user:
            return jsonify({"message": "Invalid credentials"}), 401
        
        # Check if account is locked
        if user['locked']:
            return jsonify({"message": "Account is locked. Try again later."}), 403
        
        # Verify password
        if not bcrypt.check_password_hash(user['password_hash'], password):
            # Increment failed attempts
            conn = get_db()
            cursor = conn.cursor()
            failed_attempts = user['failed_attempts'] + 1
            
            if failed_attempts >= 5:
                cursor.execute('''
                    UPDATE users 
                    SET failed_attempts = ?, locked = 1, locked_until = datetime('now', '+30 minutes')
                    WHERE id = ?
                ''', (failed_attempts, user['id']))
                conn.commit()
                conn.close()
                return jsonify({"message": "Account locked due to multiple failed attempts"}), 403
            else:
                cursor.execute('''
                    UPDATE users SET failed_attempts = ? WHERE id = ?
                ''', (failed_attempts, user['id']))
                conn.commit()
                conn.close()
                return jsonify({"message": f"Invalid credentials. {5 - failed_attempts} attempts remaining"}), 401
        
        # Reset failed attempts on successful password check
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET failed_attempts = 0 WHERE id = ?', (user['id'],))
        conn.commit()
        conn.close()
        
        # Store user info in session for OTP verification
        session['username'] = username
        session['user_id'] = user['id']
        
        return jsonify({"message": "Password verified. Enter OTP."}), 200
    
    except Exception as e:
        return jsonify({"message": f"Login error: {str(e)}"}), 500

@app.route('/api/verify-otp', methods=['POST'])
@limiter.limit("10 per minute")
def verify_otp():
    """Verify OTP from TOTP app"""
    try:
        data = request.json
        otp = data.get('otp', '').strip()
        
        if not session.get('username'):
            return jsonify({"message": "Please login first"}), 401
        
        if not otp or len(otp) != 6:
            return jsonify({"message": "OTP must be 6 digits"}), 400
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (session['username'],))
        user = cursor.fetchone()
        conn.close()
        
        if not user:
            return jsonify({"message": "User not found"}), 401
        
        # Verify OTP
        totp = pyotp.TOTP(user['mfa_secret'])
        if not totp.verify(otp):
            return jsonify({"message": "Invalid OTP"}), 401
        
        # Generate JWT token
        token = jwt.encode({
            'user': user['username'],
            'user_id': user['id'],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        }, app.config['SECRET_KEY'], algorithm='HS256')
        
        # Clear session after successful login
        session.clear()
        
        return jsonify({
            "message": "Login successful",
            "token": token,
            "username": user['username']
        }), 200
    
    except Exception as e:
        return jsonify({"message": f"OTP verification error: {str(e)}"}), 500

@app.route('/api/profile', methods=['GET'])
@token_required
def profile(current_user):
    """Get user profile (requires valid token)"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT id, username, email, created_at FROM users WHERE username = ?', (current_user,))
        user = cursor.fetchone()
        conn.close()
        
        if not user:
            return jsonify({"message": "User not found"}), 404
        
        return jsonify({
            "username": user['username'],
            "email": user['email'],
            "created_at": user['created_at']
        }), 200
    
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500

@app.route('/api/logout', methods=['POST'])
def logout():
    """Logout user"""
    session.clear()
    return jsonify({"message": "Logged out successfully"}), 200

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='127.0.0.1', port=5000)
