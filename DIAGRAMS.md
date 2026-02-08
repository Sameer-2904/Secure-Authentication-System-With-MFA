# 📊 System Diagrams - Secure Authentication System with MFA

This document contains all visual diagrams explaining how the authentication system works.

---

## 1. Complete Authentication Flow Diagram

```mermaid
graph TD
    A[User] -->|Visit Site| B{Choose Action}
    B -->|New User| C[/register]
    B -->|Existing User| D[/login]
    
    C -->|Enter Details| E["POST /api/register<br/>username, email, password"]
    E -->|Validate Input| F{Valid?}
    F -->|No| G["❌ Show Error"]
    G -->|Retry| E
    F -->|Yes| H["Hash Password<br/>bcrypt + salt"]
    H -->|Generate| I["Create MFA Secret<br/>pyotp.random_base32"]
    I -->|Generate| J["Create QR Code<br/>TOTP URI"]
    J -->|Store| K["Save to Database<br/>SQLite"]
    K -->|Display| L["📱 Show QR Code<br/>+ Secret Key"]
    L -->|Setup| M["User Scans with<br/>Authenticator App"]
    M -->|Ready| N[✅ Redirect to Login]
    
    D -->|Enter Credentials| O["POST /api/login<br/>username, password"]
    O -->|Check User| P{User Exists?}
    P -->|No| Q["❌ Invalid Credentials"]
    Q -->|Retry| O
    P -->|Yes| R{Account Locked?}
    R -->|Yes| S["❌ Account Locked<br/>30 min timeout"]
    S -->|Wait| O
    R -->|No| T["Verify Password<br/>bcrypt.check_password_hash"]
    T -->|Match?| U{Password Valid?}
    U -->|No| V["Increment Failed<br/>Attempts Counter"]
    V -->|5+ Attempts?| W{Lock Account?}
    W -->|Yes| X["🔒 Lock Account<br/>+ Timeout"]
    X -->|Show| S
    W -->|No| Y["Show Attempts Left"]
    Y -->|Retry| O
    U -->|Yes| Z["Reset Failed<br/>Attempts to 0"]
    Z -->|Store| AA["Session: username<br/>Session: user_id"]
    AA -->|Redirect| AB[/otp]
    
    AB -->|Enter 6-digit| AC["POST /api/verify-otp<br/>OTP Code"]
    AC -->|Get Secret| AD["Retrieve MFA Secret<br/>from Database"]
    AD -->|Verify| AE["Check TOTP Code<br/>pyotp.TOTP.verify"]
    AE -->|Valid?| AF{OTP Correct?}
    AF -->|No| AG["❌ Invalid OTP"]
    AG -->|Retry| AC
    AF -->|Yes| AH["Generate JWT Token<br/>HS256 + 1hr expiry"]
    AH -->|Store| AI["Save Token to<br/>localStorage"]
    AI -->|Clear Session| AJ["Wipe Session Data"]
    AJ -->|Redirect| AK[/dashboard]
    
    AK -->|Display| AL["🏠 Dashboard"]
    AL -->|Show Profile| AM["GET /api/profile<br/>Authorization: Bearer Token"]
    AM -->|Verify Token| AN{Valid Token?}
    AN -->|No| AO["❌ Redirect to Login"]
    AN -->|Yes| AP["Return User Data<br/>Profile Info"]
    AP -->|Display| AQ["✅ User Profile<br/>Security Status"]
    AQ -->|Action| AR{User Action?}
    AR -->|Logout| AS["POST /api/logout"]
    AS -->|Clear| AT["localStorage.clear"]
    AT -->|Redirect| AU[/login]
    AR -->|Stay| AQ
```

**Description**: This diagram shows the complete user journey from initial visit through registration, login, OTP verification, and dashboard access. It includes all decision points, error handling, and security checks.

---

## 2. System Architecture - Components & Data Flow

```mermaid
graph TB
    Client["🖥️ Client Browser<br/>JavaScript + HTML/CSS"]
    
    Client -->|HTTP Request| Flask["Flask Web Server<br/>Python"]
    
    Flask -->|Route Handler| Reg["📝 Registration<br/>POST /api/register"]
    Flask -->|Route Handler| Log["🔑 Login<br/>POST /api/login"]
    Flask -->|Route Handler| OTP["📱 OTP Verify<br/>POST /api/verify-otp"]
    Flask -->|Route Handler| Prof["👤 Profile<br/>GET /api/profile"]
    
    Reg -->|Security Layer| Bcrypt["🔐 Bcrypt<br/>Password Hashing"]
    Reg -->|Security Layer| Val1["✓ Input Validation<br/>Email, Username"]
    Reg -->|MFA Setup| PyOTP1["📱 PyOTP<br/>Generate Secret"]
    Reg -->|QR Code| QRCode["🎨 PyQRCode<br/>Generate QR"]
    
    Log -->|Security Layer| Rate1["⏱️ Rate Limiter<br/>10/min"]
    Log -->|Security Layer| Bcrypt
    Log -->|Protection| Lock["🔒 Account Lockout<br/>5 attempts"]
    
    OTP -->|Security Layer| Rate2["⏱️ Rate Limiter<br/>10/min"]
    OTP -->|Verification| PyOTP2["📱 PyOTP Verify<br/>TOTP Check"]
    OTP -->|Token Gen| JWT["🔑 JWT<br/>HS256 + 1hr"]
    
    Prof -->|Security Layer| JWTCheck["🔐 JWT Verify<br/>Token Valid?"]
    Prof -->|Protection| Token["🛡️ Auth Required<br/>@token_required"]
    
    Bcrypt --> DB["💾 Database<br/>SQLite"]
    PyOTP1 --> DB
    PyOTP2 --> DB
    Lock --> DB
    JWTCheck --> DB
    
    DB -->|Stored| Users["📊 Users Table<br/>ID, Username, Email<br/>Password Hash, MFA Secret<br/>Failed Attempts, Lock Status"]
    
    JWT -->|Response| Client
    Users -->|Response| Client
```

**Description**: Shows the high-level architecture with all components (Flask, security libraries, database) and how they interact with each other.

---

## 3. Security Layers - Attack Mitigation

```mermaid
graph TB
    subgraph Attack["🚫 Attack Vectors"]
        A1["Brute Force"]
        A2["Password Cracking"]
        A3["Phishing OTP"]
        A4["Session Hijacking"]
        A5["SQL Injection"]
        A6["DDoS Attack"]
    end
    
    subgraph Defense["🛡️ Defense Layers"]
        D1["Rate Limiting<br/>10 req/min login<br/>5 req/hour registration<br/>200 per day global"]
        D2["Bcrypt Hashing<br/>Salted +<br/>256,000+ rounds"]
        D3["TOTP MFA<br/>Time-based<br/>30-second window"]
        D4["JWT Tokens<br/>HS256 Encrypted<br/>1-hour expiry"]
        D5["Input Validation<br/>Sanitization<br/>Parameterized Queries"]
        D6["Account Lockout<br/>5 failed attempts<br/>30-minute timeout"]
    end
    
    subgraph Protected["✅ Protected Resources"]
        P1["User Passwords<br/>Never stored plain"]
        P2["MFA Secrets<br/>Stored in DB"]
        P3["User Sessions<br/>Token-based"]
        P4["API Endpoints<br/>@token_required"]
        P5["User Database<br/>Encrypted credentials"]
    end
    
    A1 --> D1
    A1 --> D6
    A2 --> D2
    A3 --> D3
    A4 --> D4
    A5 --> D5
    A6 --> D1
    
    D1 --> P1
    D2 --> P1
    D3 --> P2
    D4 --> P3
    D5 --> P5
    D6 --> P3
    D4 --> P4
```

**Description**: Maps different attack vectors to their corresponding defense mechanisms. Shows how each security measure protects specific resources.

---

## 4. Detailed Login Sequence - Client, Server & Database Interaction

```mermaid
sequenceDiagram
    participant User as 👤 User
    participant Browser as 🌐 Browser
    participant Server as 🔧 Flask Server
    participant DB as 💾 Database
    participant Auth as 📱 Authenticator App
    
    User->>Browser: 1. Visit /login
    Browser->>Server: GET /login
    Server->>Browser: Return login.html
    
    User->>Browser: 2. Enter username & password
    Browser->>Server: POST /api/login
    Server->>DB: SELECT user by username
    DB-->>Server: User record
    
    alt Password Invalid
        Server->>DB: Increment failed_attempts
        Server->>Browser: ❌ Invalid credentials
    else Password Valid
        Server->>DB: Reset failed_attempts to 0
        Server->>Browser: ✅ Password OK, enter OTP
        Browser->>Server: GET /otp
        Server->>Browser: Return otp.html
        
        User->>Auth: 3. Check Authenticator app
        Auth-->>User: Display 6-digit code (TOTP)
        User->>Browser: Enter OTP code
        Browser->>Server: POST /api/verify-otp
        
        Server->>DB: GET user MFA_SECRET
        DB-->>Server: Secret key
        Server->>Server: Verify TOTP<br/>pyotp.TOTP().verify()
        
        alt OTP Invalid
            Server->>Browser: ❌ Invalid OTP
        else OTP Valid
            Server->>Server: Generate JWT Token<br/>HS256 | username | exp
            Server->>Browser: 🎟️ JWT Token + redirect
            Browser->>Browser: localStorage.setItem<br/>auth_token
            Browser->>Server: GET /dashboard
            Server->>Browser: Return dashboard.html
            
            User->>Browser: 4. Click on profile info
            Browser->>Server: GET /api/profile<br/>+Authorization: Bearer token
            Server->>Server: Verify JWT Token<br/>@token_required decorator
            Server->>DB: SELECT user profile
            DB-->>Server: User profile data
            Server->>Browser: ✅ Return profile JSON
            Browser->>Browser: Display user info
            
            User->>Browser: 5. Click Logout
            Browser->>Server: POST /api/logout
            Server->>Server: Clear session
            Server->>Browser: ✅ Logged out
            Browser->>Browser: localStorage.clear()
            Browser->>Server: GET /
            Server->>Browser: Redirect to login
        end
    end
```

**Description**: A detailed sequence diagram showing the exact interactions between user, browser, Flask server, database, and authenticator app at each step of the authentication process.

---

## 5. Registration Process - Step by Step

```mermaid
graph LR
    A["📝 User Fills<br/>Registration Form"]
    
    A --> B["Username ✓<br/>3+ chars"]
    A --> C["Email ✓<br/>Valid format"]
    A --> D["Password ✓<br/>8+ chars"]
    
    B --> E{Validate}
    C --> E
    D --> E
    
    E -->|❌ Error| F["Show Error<br/>Message"]
    F --> A
    
    E -->|✅ Valid| G["Hash Password<br/>bcrypt<br/>salt rounds: 12"]
    
    G --> H["Generate<br/>MFA Secret<br/>base32 string"]
    
    H --> I["Create TOTP<br/>Provisioning URI<br/>otpauth://"]
    
    I --> J["Generate QR Code<br/>from URI<br/>PyQRCode"]
    
    J --> K["Save User<br/>to Database"]
    
    K --> L["Insert Record<br/>- username<br/>- email<br/>- password_hash<br/>- mfa_secret<br/>- created_at"]
    
    L --> M{Store Success?}
    
    M -->|❌ Fail| N["Show Error<br/>Username/Email<br/>Already Exists"]
    N --> A
    
    M -->|✅ Success| O["Return JSON<br/>- message<br/>- mfa_secret<br/>- qr_code<br/>base64 SVG"]
    
    O --> P["🌐 Browser<br/>Receives Response"]
    
    P --> Q["Hide Form"]
    P --> R["Display QR Code"]
    P --> S["Show Secret Key<br/>Backup"]
    
    R --> T["👤 User Action"]
    
    T --> U["📸 Scan QR<br/>with Authenticator"]
    T --> V["Or Enter<br/>Secret Manually"]
    
    U --> W["✅ Setup Complete"]
    V --> W
    
    W --> X["Redirect to<br/>Login Page"]
```

**Description**: Step-by-step walkthrough of the complete registration process including validation, password hashing, MFA secret generation, QR code creation, and database storage.

---

## 6. Technology Stack & Component Integration

```mermaid
graph TB
    subgraph Frontend["🎨 Frontend Layer"]
        HTML["HTML5<br/>Templates<br/>register.html<br/>login.html<br/>otp.html<br/>dashboard.html"]
        CSS["CSS3<br/>Responsive Design<br/>Mobile-friendly<br/>Gradient Backgrounds"]
        JS["JavaScript<br/>Fetch API<br/>localStorage<br/>Event Handling"]
    end
    
    subgraph Backend["🔧 Backend Layer"]
        Flask["Flask<br/>Web Server<br/>Route Handlers<br/>Request Processing"]
        Auth["Authentication<br/>Bcrypt - Hash<br/>PyOTP - TOTP<br/>PyJWT - Tokens"]
        Security["Security<br/>Flask-Limiter<br/>Input Validation<br/>Rate Limiting"]
    end
    
    subgraph Storage["💾 Data Layer"]
        SQLite["SQLite Database<br/>users.db<br/>User credentials<br/>MFA secrets<br/>Login attempts"]
        QueryEngine["SQL Engine<br/>Parameterized Queries<br/>Transaction Support"]
    end
    
    subgraph Libraries["📦 External Libraries"]
        Bcrypt["🔐 Flask-Bcrypt<br/>Password Hashing<br/>Salted encryption"]
        JWT["🔑 PyJWT<br/>Token Generation<br/>HS256 encryption"]
        TOTP["📱 PyOTP<br/>TOTP Verification<br/>Time-based OTP"]
        QR["🎨 PyQRCode<br/>QR Code Generation<br/>SVG Output"]
        Limiter["⏱️ Flask-Limiter<br/>Rate Limiting<br/>DDoS Protection"]
    end
    
    HTML --> Flask
    CSS --> Flask
    JS --> Flask
    
    Flask --> Auth
    Flask --> Security
    
    Auth --> Bcrypt
    Auth --> JWT
    Auth --> TOTP
    Auth --> QR
    
    Security --> Limiter
    
    Flask --> QueryEngine
    QueryEngine --> SQLite
    
    Auth --> SQLite
    Security --> SQLite
```

**Description**: Shows how all the technology components are layered and integrated together, from frontend to backend to storage.

---

## 7. Security Deep Dive - TOTP & Bcrypt Encryption

```mermaid
graph TB
    subgraph TOTP["📱 TOTP (Time-Based One-Time Password) Process"]
        T1["1. Registration:"]
        T2["Generate Secret Key<br/>32 bytes base32"]
        T3["Display QR Code<br/>otpauth://totp/..."]
        T4["User Scans QR<br/>into Authenticator App"]
        
        T1 --> T2 --> T3 --> T4
        
        T5["2. Login - OTP Generation:"]
        T6["Authenticator App<br/>Starts Timer<br/>0-30 seconds"]
        T7["Uses HMAC-SHA1<br/>+ Current Unix Time<br/>+ Secret Key"]
        T8["Produces 6-Digit<br/>One-Time Code"]
        
        T5 --> T6 --> T7 --> T8
        
        T9["3. Verification:"]
        T10["Server Uses<br/>Same Secret Key<br/>+ Similar Time Window"]
        T11["Generates Expected<br/>TOTP Code"]
        T12["Compares with<br/>User's Entry"]
        T13["✅ Match = Success"]
        
        T9 --> T10 --> T11 --> T12 --> T13
    end
    
    subgraph Hash["🔐 Password Hashing with Bcrypt Process"]
        H1["User Password<br/>e.g., 'Pass@123'"]
        
        H2["Generate Random<br/>Salt<br/>16 bytes"]
        
        H3["Bcrypt Algorithm<br/>12 Rounds<br/>~250ms per hash"]
        
        H4["Combines<br/>Salt + Password<br/>+ Rounds"]
        
        H5["Hash Output<br/>Example:<br/>$2b$12$R9h7cIPz0gi..."]
        
        H6["Store in Database<br/>Never Plain Text!"]
        
        H1 --> H2 --> H3 --> H4 --> H5 --> H6
        
        H7["On Login:"]
        H8["User Enters<br/>Password Again"]
        H9["Extract Salt<br/>from Stored Hash"]
        H10["Re-hash<br/>with Same Salt"]
        H11["Compare Hashes<br/>bcrypt.check()"]
        H12["✅ Match = Valid"]
        
        H7 --> H8 --> H9 --> H10 --> H11 --> H12
    end
```

**Description**: Deep dive into the cryptographic processes - how TOTP generates time-based one-time passwords and how Bcrypt securely hashes passwords with salt.

---

## 📚 How to Use These Diagrams

1. **View in GitHub**: If viewing on GitHub, Mermaid diagrams render automatically
2. **Copy to Other Tools**: Copy the mermaid code blocks into:
   - [Mermaid Live Editor](https://mermaid.live)
   - VSCode with Markdown Preview
   - Confluence / Notion (with Mermaid support)
3. **Export**: Export diagrams as PNG, SVG, or PDF using Mermaid tools

---

## 🔑 Key Takeaways

| Diagram | Key Insight |
|---------|------------|
| Authentication Flow | Complete user journey with all security checks |
| System Architecture | How components interact and communicate |
| Security Layers | Defense mechanisms for different attack vectors |
| Sequence Diagram | Real-time interactions between all system parts |
| Registration Process | Step-by-step data flow during account creation |
| Tech Stack | Technology layers and component dependencies |
| TOTP & Bcrypt | Cryptographic foundations of the system |

---

**Created**: February 8, 2026  
**System**: Secure Authentication System with MFA v1.0.0
