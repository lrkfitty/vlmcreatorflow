import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from execution.auth import auth_mgr

def test_auth_system():
    print("Testing Auth Manager SQL...")
    
    # 1. Admin Init Check
    admin_token, msg = auth_mgr.login("admin", "admin")
    if admin_token:
        print("✅ Admin Login Success")
        admin_creds = auth_mgr.get_credits("admin")
        print(f"✅ Admin Credits: {admin_creds} (Expected 1000)")
    else:
        print(f"❌ Admin Login Failed: {msg}")
        return

    # 2. Allowlist Check (Enforcement)
    # Mock Environment to force check
    os.environ["ENFORCE_ALLOWLIST"] = "True"
    print("\nTesting Allowlist Enforcement...")
    
    # Try invalid user
    success, msg = auth_mgr.create_user("hackerman@bad.com", "pass")
    if not success and "Allowlist" in msg:
        print("✅ Blocked invalid email correctly.")
    else:
        print(f"❌ Failed to block invalid email. Msg: {msg}")

    # Add to Allowlist
    print("\nAdding student@school.edu to Allowlist...")
    auth_mgr.add_to_allowlist("student@school.edu", "Test Student")
    
    # Try valid user
    success, msg = auth_mgr.create_user("student@school.edu", "pass")
    if success:
        print("✅ Created allowlisted user successfully.")
    else:
        print(f"❌ Failed to create allowlisted user: {msg}")
        
    # 3. Credit Deduction
    print("\nTesting Credit Deduction...")
    if auth_mgr.deduct_credits("student@school.edu", 5):
        new_creds = auth_mgr.get_credits("student@school.edu")
        if new_creds == 195:
             print("✅ Credits deducted correctly (200 -> 195)")
        else:
             print(f"❌ Credit math wrong: {new_creds}")
    else:
        print("❌ Failed to deduct credits")

    print("\n🎉 Auth System Verification Complete.")

if __name__ == "__main__":
    test_auth_system()
