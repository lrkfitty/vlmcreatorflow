import os
import time
import hashlib
import uuid
import sqlite3
import jwt
import datetime
import bcrypt
from dotenv import load_dotenv

load_dotenv()

class AuthManager:
    def __init__(self, db_path="users.db"):
        self.db_path = db_path
        self.secret_key = os.getenv("JWT_SECRET_KEY") or "super-secret-dev-key-change-me"
        self._init_db()
        self._init_default_admin()

    def _get_conn(self):
        return sqlite3.connect(self.db_path, check_same_thread=False)

    def _init_db(self):
        """Ensure DB and Tables exist."""
        conn = self._get_conn()
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                role TEXT DEFAULT 'viewer',
                credits INTEGER DEFAULT 0,
                created_at REAL,
                last_reset_date TEXT
            )
        ''')
        # Allowlist will be used later
        c.execute('''
            CREATE TABLE IF NOT EXISTS allowlist (
                email TEXT PRIMARY KEY,
                name TEXT,
                active INTEGER DEFAULT 1
            )
        ''')
        # Transactions ledger for credits
        c.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                amount INTEGER NOT NULL,
                action TEXT NOT NULL,
                timestamp REAL NOT NULL
            )
        ''')
        conn.commit()
        conn.close()

    def _init_default_admin(self):
        """Creates default admin if not exists (using DB)."""
        env_user = os.getenv("APP_ADMIN_USER", "admin")
        env_pass = os.getenv("APP_PASSWORD", "admin")
        
        conn = self._get_conn()
        c = conn.cursor()
        c.execute("SELECT username FROM users WHERE username=?", (env_user,))
        if not c.fetchone():
            print(f"Auth: Initializing default admin user: {env_user}")
            pass_hash, salt = self._hash_password_bcrypt(env_pass)
            c.execute('''
                INSERT INTO users (username, password_hash, salt, role, credits, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (env_user, pass_hash, salt, "admin", 1000, time.time()))
            conn.commit()
            
            # Log initial grant
            c.execute('''
                INSERT INTO transactions (username, amount, action, timestamp)
                VALUES (?, ?, ?, ?)
            ''', (env_user, 1000, "Initial admin creation", time.time()))
            conn.commit()
            
        conn.close()

    def _hash_password_legacy(self, password, salt=None):
        """Simple SHA256 hash with salt (for backwards compatibility)."""
        if not salt:
            salt = uuid.uuid4().hex
        
        # Hash = SHA256(salt + password)
        hash_obj = hashlib.sha256((salt + password).encode())
        return hash_obj.hexdigest(), salt

    def _hash_password_bcrypt(self, password):
        """Secure bcrypt hasher."""
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode(), ""

    # --- ALLOWLIST LOGIC ---
    def is_email_allowed(self, email):
        """Checks if email is in the allowlist table."""
        # If Allowlist is DISABLED via Env, return True
        if os.getenv("ENFORCE_ALLOWLIST", "True").lower() == "false":
            return True

        conn = self._get_conn()
        c = conn.cursor()
        c.execute("SELECT active FROM allowlist WHERE lower(email)=?", (email.lower(),))
        row = c.fetchone()
        conn.close()
        return True if row and row[0] == 1 else False

    def list_allowlist(self):
        conn = self._get_conn()
        c = conn.cursor()
        c.execute("SELECT email, name, active FROM allowlist")
        rows = c.fetchall()
        conn.close()
        return rows

    def add_to_allowlist(self, email, name=""):
        conn = self._get_conn()
        c = conn.cursor()
        try:
            c.execute("INSERT OR REPLACE INTO allowlist (email, name, active) VALUES (?, ?, 1)", (email.lower(), name))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Allowlist Error: {e}")
            conn.close()
            return False

    # --- TRANSACTIONS LOGIC ---
    def get_transactions(self, username, limit=20):
        """Get recent transactions for a user."""
        conn = self._get_conn()
        c = conn.cursor()
        c.execute("SELECT amount, action, timestamp FROM transactions WHERE username=? ORDER BY timestamp DESC LIMIT ?", (username, limit))
        rows = c.fetchall()
        conn.close()
        
        res = []
        for r in rows:
            res.append({
                "amount": r[0],
                "action": r[1],
                "timestamp": r[2],
                "date": datetime.datetime.fromtimestamp(r[2]).strftime('%Y-%m-%d %H:%M:%S')
            })
        return res

    # --- USER LOGIC ---
    def create_user(self, username, password, role="viewer"):
        """Register a new user."""
        # Allowlist Check
        if not self.is_email_allowed(username):
             return False, "Access Denied: Your email is not found in the School Community Allowlist."

        conn = self._get_conn()
        c = conn.cursor()
        
        # Case-insensitive check
        username_lower = username.lower()
        c.execute("SELECT username FROM users WHERE lower(username)=?", (username_lower,))
        if c.fetchone():
            conn.close()
            return False, "User already exists"
            
        pass_hash, salt = self._hash_password_bcrypt(password)
        
        try:
            c.execute('''
                INSERT INTO users (username, password_hash, salt, role, credits, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (username, pass_hash, salt, role, 200, time.time())) # 200 Initial Credits
            
            c.execute('''
                INSERT INTO transactions (username, amount, action, timestamp)
                VALUES (?, ?, ?, ?)
            ''', (username, 200, "Sign up bonus", time.time()))
            
            conn.commit()
            conn.close()
            return True, "User created"
        except sqlite3.IntegrityError:
             conn.close()
             return False, "User already exists"

    def login(self, username, password):
        """Verify credentials and return token."""
        username_lower = username.lower()
        
        conn = self._get_conn()
        c = conn.cursor()
        c.execute("SELECT username, password_hash, salt, role, credits, last_reset_date FROM users WHERE lower(username)=?", (username_lower,))
        row = c.fetchone()
        
        if not row:
            conn.close()
            return None, "User not found"
            
        real_username, stored_hash, salt, role, credits, last_reset = row
        
        # Verify
        is_valid = False
        if stored_hash.startswith('$2b$'):
            # Bcrypt hash
            if bcrypt.checkpw(password.encode(), stored_hash.encode()):
                is_valid = True
        else:
            # Legacy SHA256 hash
            check_hash, _ = self._hash_password_legacy(password, salt)
            if check_hash == stored_hash:
                is_valid = True
                # Upgrade hash automatically
                new_hash, new_salt = self._hash_password_bcrypt(password)
                c.execute("UPDATE users SET password_hash=?, salt=? WHERE username=?", (new_hash, new_salt, real_username))
                conn.commit()

        if is_valid:
            # --- CREDIT RESET LOGIC (MONTHLY) ---
            now = datetime.datetime.now()
            current_month_str = now.strftime("%Y-%m")
            
            final_credits = credits
            
            if last_reset != current_month_str:
                target_allowance = 200 # Standard Monthly Allowance
                if role != 'admin': 
                    final_credits = target_allowance
                    c.execute("UPDATE users SET credits=?, last_reset_date=? WHERE username=?", (target_allowance, current_month_str, real_username))
                    c.execute('''
                        INSERT INTO transactions (username, amount, action, timestamp)
                        VALUES (?, ?, ?, ?)
                    ''', (real_username, target_allowance, "Monthly reset", time.time()))
                    conn.commit()
            
            conn.close()

            # Create JWT
            payload = {
                "username": real_username,
                "role": role,
                "credits": final_credits,
                "exp": time.time() + (7 * 24 * 60 * 60) # 7 Day Expiry
            }
            token = jwt.encode(payload, self.secret_key, algorithm="HS256")
            return token, "Success"
        else:
            conn.close()
            return None, "Invalid Password"

    def get_credits(self, username):
        """Returns current credit balance."""
        conn = self._get_conn()
        c = conn.cursor()
        c.execute("SELECT credits FROM users WHERE username=?", (username,))
        row = c.fetchone()
        conn.close()
        return row[0] if row else 0

    def deduct_credits(self, username, amount=1, reason="App Usage"):
        """Deducts credits if sufficient balance. Returns True/False."""
        conn = self._get_conn()
        c = conn.cursor()
        
        # Check first
        c.execute("SELECT credits FROM users WHERE username=?", (username,))
        row = c.fetchone()
        if not row:
            conn.close()
            return False
            
        current = row[0]
        if current >= amount:
            c.execute("UPDATE users SET credits=? WHERE username=?", (current - amount, username))
            c.execute('''
                INSERT INTO transactions (username, amount, action, timestamp)
                VALUES (?, ?, ?, ?)
            ''', (username, -amount, reason, time.time()))
            
            conn.commit()
            conn.close()
            return True
            
        conn.close()
        return False
        
    def add_credits(self, username, amount, reason="Admin Grant"):
        """Adds credits to user."""
        conn = self._get_conn()
        c = conn.cursor()
        c.execute("UPDATE users SET credits = credits + ? WHERE username=?", (amount, username))
        c.execute('''
            INSERT INTO transactions (username, amount, action, timestamp)
            VALUES (?, ?, ?, ?)
        ''', (username, amount, reason, time.time()))
        
        conn.commit()
        conn.close()
        return True

    # --- ADMIN FUNCTIONS ---
    def get_all_users(self):
        """Returns list of all users."""
        conn = self._get_conn()
        c = conn.cursor()
        c.execute("SELECT username, role, credits, last_reset_date, created_at FROM users ORDER BY created_at DESC")
        rows = c.fetchall()
        conn.close()
        # Convert to list of dicts
        users = []
        for r in rows:
            users.append({
                "username": r[0],
                "role": r[1],
                "credits": r[2],
                "last_reset": r[3],
                "created_at": datetime.datetime.fromtimestamp(r[4]).strftime('%Y-%m-%d') if r[4] else "N/A"
            })
        return users

    def ban_user(self, username):
        """Deletes user from DB (Ban)."""
        if username == "admin": return False # Safety
        conn = self._get_conn()
        c = conn.cursor()
        c.execute("DELETE FROM users WHERE username=?", (username,))
        conn.commit()
        conn.close()
        return True

    def reset_user_password(self, username, new_password):
        """Admin force reset."""
        pass_hash, salt = self._hash_password_bcrypt(new_password)
        conn = self._get_conn()
        c = conn.cursor()
        c.execute("UPDATE users SET password_hash=?, salt=? WHERE username=?", (pass_hash, salt, username))
        conn.commit()
        conn.close()
        return True

    def toggle_allowlist_enforcement(self, status: bool):
        os.environ["ENFORCE_ALLOWLIST"] = str(status)
        return True

    def verify_token(self, token):
        """Decodes token and returns user info."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            return payload
        except jwt.ExpiredSignatureError:
            return None # Expired
        except jwt.InvalidTokenError:
            return None # Invalid

# Singleton Instance
auth_mgr = AuthManager()
# Enable WAL Mode for Concurrency
try:
    with sqlite3.connect("users.db") as conn:
        conn.execute("PRAGMA journal_mode=WAL;")
except:
    pass
