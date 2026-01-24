import os
import json
import hashlib
import time
import jwt
import uuid
from dotenv import load_dotenv

load_dotenv()

class AuthManager:
    def __init__(self, db_path="users.json", secret_key=None):
        self.db_path = db_path
        # Use a consistent secret key, fallback to random if not set (invalidates tokens on restart if random)
        self.secret_key = secret_key or os.getenv("JWT_SECRET_KEY") or "super-secret-dev-key-change-me"
        self.users = {}
        self.load_users()

    def load_users(self):
        """Loads users from JSON file."""
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, "r") as f:
                    self.users = json.load(f)
            except json.JSONDecodeError:
                self.users = {}
        else:
            self.users = {}
            # Initialize with Env Admin if empty
            self._init_default_admin()

    def _init_default_admin(self):
        """Creates default admin if no users exist."""
        env_user = os.getenv("APP_ADMIN_USER", "admin")
        env_pass = os.getenv("APP_PASSWORD", "admin")
        
        # Check if ANY user exists (to prevent overwrite if DB is populated)
        # But specifically check for this admin user
        if env_user not in self.users:
            print(f"Auth: Initializing default admin user: {env_user}")
            self.create_user(env_user, env_pass, role="admin")

    def save_users(self):
        """Saves users to JSON file."""
        with open(self.db_path, "w") as f:
            json.dump(self.users, f, indent=4)

    def _hash_password(self, password, salt=None):
        """Simple SHA256 hash with salt."""
        if not salt:
            salt = uuid.uuid4().hex
        
        # Hash = SHA256(salt + password)
        hash_obj = hashlib.sha256((salt + password).encode())
        return hash_obj.hexdigest(), salt

    def create_user(self, username, password, role="viewer"):
        """Register a new user."""
        # Case-insensitive check
        username_lower = username.lower()
        existing_users = {u.lower(): u for u in self.users.keys()}
        
        if username_lower in existing_users:
            return False, "User already exists"
            
        pass_hash, salt = self._hash_password(password)
        
        # Store with original casing provided
        self.users[username] = {
            "username": username,
            "hash": pass_hash,
            "salt": salt,
            "role": role,
            "created_at": time.time()
        }
        self.save_users()
        return True, "User created"

    def login(self, username, password):
        """Verify credentials and return token."""
        # Case-insensitive lookup
        username_lower = username.lower()
        existing_users = {u.lower(): u for u in self.users.keys()}
        
        real_username = existing_users.get(username_lower)
        if not real_username:
            return None, "User not found"
            
        user = self.users.get(real_username)
            
        stored_hash = user.get("hash")
        salt = user.get("salt")
        
        # Verify
        check_hash, _ = self._hash_password(password, salt)
        
        if check_hash == stored_hash:
            # Create JWT
            payload = {
                "username": real_username,
                "role": user.get("role"),
                "exp": time.time() + (7 * 24 * 60 * 60) # 7 Day Expiry
            }
            token = jwt.encode(payload, self.secret_key, algorithm="HS256")
            return token, "Success"
        else:
            return None, "Invalid Password"

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
