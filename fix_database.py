# fix_database.py
import sqlite3
import os

db_path = 'instance/reports.db'

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Add phone column to users table
        cursor.execute("ALTER TABLE users ADD COLUMN phone VARCHAR(20)")
        print("✅ Phone column added to users table")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("✅ Phone column already exists")
        else:
            print(f"Error: {e}")
    
    conn.commit()
    conn.close()
    print("✅ Database updated successfully!")
else:
    print("❌ Database not found. Run 'python app.py' first to create it.")