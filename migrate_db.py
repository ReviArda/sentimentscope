import sqlite3
import os

db_path = os.path.join('instance', 'sentiment.db')

def migrate():
    if not os.path.exists(db_path):
        print("Database not found.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        cursor.execute("ALTER TABLE analyses ADD COLUMN correction VARCHAR(20)")
        print("Successfully added 'correction' column.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("Column 'correction' already exists.")
        else:
            print(f"Error: {e}")
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    migrate()
