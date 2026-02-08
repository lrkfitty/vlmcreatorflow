import sqlite3
import os

db_path = "users.db"
if not os.path.exists(db_path):
    print(f"Database {db_path} not found.")
else:
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    try:
        c.execute("SELECT username, role, credits FROM users")
        rows = c.fetchall()
        print(f"{'USERNAME':<20} | {'ROLE':<10} | {'CREDITS'}")
        print("-" * 45)
        for r in rows:
            print(f"{r[0]:<20} | {r[1]:<10} | {r[2]}")
    except Exception as e:
        print(f"Error reading DB: {e}")
    finally:
        conn.close()
