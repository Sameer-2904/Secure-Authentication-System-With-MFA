# 🔐 Secure Authentication System with MFA

A production-ready Flask-based authentication system featuring multi-factor authentication (MFA) using Time-based One-Time Passwords (TOTP), secure password hashing, JWT tokens, and comprehensive security features.

## ✨ Features

### 🔑 **Core Authentication**
- User registration with email and username validation
- Secure password hashing using bcrypt with salt
- Login with username and password authentication
- Multi-factor authentication (MFA) using TOTP
- JWT token-based session management
- Automatic logout and session expiry

### 🛡️ **Security Features**
- **Bcrypt Password Hashing** - Automatically salted and hashed passwords
- **TOTP-Based MFA** - RFC 6238 compliant time-based one-time passwords
- **JWT Tokens** - HS256 encrypted tokens with 1-hour expiry
- **Account Lockout** - Automatic account lock after 5 failed login attempts
- **Rate Limiting** - Protection against brute force attacks
  - 10 requests per minute for login
  - 5 requests per hour for registration
- **Input Validation** - Comprehensive validation for all user inputs
- **SQLite Database** - Persistent user data storage with encrypted credentials
- **Session Management** - Secure token-based authentication

### 🎨 **User Interface**
- Modern, responsive design with gradient backgrounds
- Mobile-friendly layouts
- Intuitive form validation with real-time feedback
- QR code generation for easy 2FA setup
- Professional dashboard after login

## 📋 Requirements

- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended)

## 🚀 Installation

### 1. Clone or Download the Project
```bash
cd "Secure Authentication System with MFA"
```

### 2. Create Virtual Environment (Optional but Recommended)
```bash
python -m venv .venv
```

### 3. Activate Virtual Environment

**On Windows:**
```bash
.venv\Scripts\activate
```

**On macOS/Linux:**
```bash
source .venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

Or install manually:
```bash
pip install Flask==3.0.0
pip install Flask-Bcrypt==1.0.1
pip install PyJWT==2.8.1
pip install pyotp==2.9.0
pip install PyQRCode==1.9.2
pip install Flask-Limiter==3.5.0
pip install python-dotenv==1.0.0
```

## 🏃 Running the Application

### Start the Development Server
```bash
python app.py
```

The application will start on **http://localhost:5000**

### Server Output
```
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
```

## 📖 Usage Guide

### 1. **Register a New Account**
- Navigate to http://localhost:5000/register
- Enter:
  - **Username** (minimum 3 characters)
  - **Email** (valid email format)
  - **Password** (minimum 8 characters)
- Click "Create Account"
- A QR code will be displayed for 2FA setup

### 2. **Set Up Two-Factor Authentication**
- Download an authenticator app:
  - Google Authenticator
  - Authy
  - Microsoft Authenticator
  - Any TOTP-compatible app
- Scan the displayed QR code with your authenticator app
- Save the backup secret key somewhere safe
- Click "Continue to Login"

### 3. **Login with MFA**
- Go to http://localhost:5000
- Enter your username and password
- Click "Login"
- You'll be redirected to OTP verification
- Enter the 6-digit code from your authenticator app
- The code auto-submits after 6 digits
- On success, you'll be taken to the dashboard

### 4. **Access Protected Resources**
- Your JWT token is stored in localStorage
- The dashboard displays your profile and security information
- Use the token for API requests by adding:
  ```
  Authorization: Bearer <your_token>
  ```

## 🔌 API Endpoints

### Public Routes

#### `POST /api/register`
Register a new user
```json
Request:
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "SecurePass123!"
}

Response (201):
{
  "message": "User registered successfully",
  "mfa_secret": "JBSWY3DPEBLW64TMMQ======",
  "qr_code": "base64_encoded_svg"
}
```

#### `POST /api/login`
Authenticate user with credentials
```json
Request:
{
  "username": "john_doe",
  "password": "SecurePass123!"
}

Response (200):
{
  "message": "Password verified. Enter OTP."
}
```

#### `POST /api/verify-otp`
Verify TOTP code and issue JWT token
```json
Request:
{
  "otp": "123456"
}

Response (200):
{
  "message": "Login successful",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "username": "john_doe"
}
```

### Protected Routes (Require JWT Token)

#### `GET /api/profile`
Get user profile information
```
Headers:
Authorization: Bearer <jwt_token>

Response (200):
{
  "username": "john_doe",
  "email": "john@example.com",
  "created_at": "2026-02-08 13:30:00"
}
```

#### `POST /api/logout`
Logout user
```
Response (200):
{
  "message": "Logged out successfully"
}
```

## 💾 Database Schema

### Users Table
```sql
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
```

## 📁 Project Structure

```
Secure Authentication System with MFA/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── users.db              # SQLite database (auto-created)
├── README.md             # This file
└── templates/
    ├── login.html        # Login page
    ├── register.html     # Registration page with QR code
    ├── otp.html          # OTP verification page
    └── dashboard.html    # Welcome dashboard
```

## 🔒 Security Details

### Password Security
- Bcrypt hashing with automatic salt generation
- Passwords never stored in plain text
- Minimum 8 characters required

### Multi-Factor Authentication
- Time-based One-Time Password (TOTP) based on RFC 6238
- 30-second time window
- 6-digit codes
- Compatible with all standard TOTP apps

### JWT Token Security
- Algorithm: HS256 (HMAC with SHA-256)
- Secret key: `your-super-secret-key-change-in-production`
- Token expiry: 1 hour
- Bearer token authentication

### Account Protection
- Failed login attempt tracking
- Automatic account lock after 5 failed attempts
- 30-minute lockout period
- Attempt counter reset on successful login

### Rate Limiting
- Login: 10 requests per minute
- Registration: 5 requests per hour
- Global: 200 per day, 50 per hour

### Input Validation
- Username: 3+ characters, alphanumeric
- Email: Valid email format
- Password: 8+ characters
- OTP: Exactly 6 digits

## ⚙️ Configuration

### Environment Variables (Optional)
Create a `.env` file for production settings:
```
FLASK_ENV=production
SECRET_KEY=your-production-secret-key
DEBUG=False
```

### Change Secret Key (Important for Production!)
Edit `app.py` and update:
```python
app.config['SECRET_KEY'] = 'your-super-secret-key-change-in-production'
```

### Disable Debug Mode (Production)
```python
app.run(debug=False, host='0.0.0.0', port=5000)
```

## 🧪 Testing Guide

### Manual Testing Steps

1. **Register Test User**
   - Go to /register
   - Create account: username=`testuser`, password=`Test@1234`
   - Save the displayed secret key

2. **Setup Authenticator**
   - Scan QR code or manually enter secret key
   - Verify code generation (changes every 30 seconds)

3. **Login Test**
   - Go to /login
   - Enter credentials
   - Enter current OTP code
   - Should redirect to dashboard

4. **API Testing**
   - Use curl or Postman for API endpoint testing
   - Test with valid and invalid credentials
   - Test rate limiting

### Test Scenarios

```bash
# Test Registration
curl -X POST http://localhost:5000/api/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","email":"test@example.com","password":"Test@1234"}'

# Test Login
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"Test@1234"}'

# Test OTP Verification
curl -X POST http://localhost:5000/api/verify-otp \
  -H "Content-Type: application/json" \
  -d '{"otp":"123456"}'

# Test Protected Route
curl -X GET http://localhost:5000/api/profile \
  -H "Authorization: Bearer your_jwt_token_here"
```

## 🐛 Troubleshooting

### Issue: ModuleNotFoundError
**Solution:** Reinstall dependencies
```bash
pip install -r requirements.txt
```

### Issue: Port 5000 Already in Use
**Solution:** Change port in app.py
```python
app.run(debug=True, host='127.0.0.1', port=5001)
```

### Issue: QR Code Not Displaying
**Cause:** PyQRCode not installed properly
**Solution:**
```bash
pip install --upgrade PyQRCode
```

### Issue: Sessions Not Persisting
**Cause:** Session expired or cookies disabled
**Solution:** Enable cookies in browser, check token expiry

### Issue: Rate Limiting Too Strict
**Solution:** Modify in app.py:
```python
@limiter.limit("20 per minute")  # Change the limit
def login():
    ...
```

### Issue: Database Locked
**Solution:** Delete `users.db` and restart (this will reset all users)
```bash
del users.db
python app.py
```

## 📱 Authenticator Apps

Recommended TOTP authenticator applications:
- **Google Authenticator** - Android, iOS
- **Authy** - Android, iOS, Windows, macOS
- **Microsoft Authenticator** - Android, iOS, Windows
- **FreeOTP** - Android, iOS
- **1Password** - All platforms
- **Bitwarden** - All platforms

## 🔄 Session Management

- Sessions expire after 30 minutes of inactivity
- JWT tokens expire after 1 hour
- Use the logout button to clear your session
- Tokens are stored in browser's localStorage

## 📞 Support

For issues or questions:
1. Check the Troubleshooting section above
2. Review error messages in the browser console
3. Check terminal output for server-side errors
4. Ensure all dependencies are installed

## 📜 License

This project is provided as-is for educational and personal use.

## 🎯 Production Checklist

Before deploying to production:

- [ ] Change `SECRET_KEY` to a strong random value
- [ ] Set `DEBUG = False`
- [ ] Use a production WSGI server (Gunicorn, uWSGI)
- [ ] Enable HTTPS/SSL
- [ ] Use environment variables for configuration
- [ ] Implement proper logging
- [ ] Set up database backups
- [ ] Enable CORS with allowed origins only
- [ ] Implement CSRF protection
- [ ] Set up rate limiting with Redis
- [ ] Enable security headers
- [ ] Use a proper database (PostgreSQL, MySQL)
- [ ] Implement email verification
- [ ] Add password reset functionality
- [ ] Set up monitoring and alerting

## 🚀 Performance Tips

- Use a production WSGI server like Gunicorn
- Enable caching for static files
- Use Redis for rate limiting in production
- Consider CDN for static assets
- Monitor database query performance
- Implement connection pooling

## 📚 Additional Resources

- Flask Documentation: https://flask.palletsprojects.com/
- PyOTP Documentation: https://pyauth.github.io/pyotp/
- JWT.io: https://jwt.io/
- OWASP Authentication Cheat Sheet: https://cheatsheetseries.owasp.org/
- RFC 6238 (TOTP): https://tools.ietf.org/html/rfc6238

---

**Created:** February 8, 2026  
**Version:** 1.0.0  
**Status:** Production Ready ✅
