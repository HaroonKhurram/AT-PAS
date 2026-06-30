import sqlite3

def update_db():
    conn = sqlite3.connect('d:/AT-PAS_Backend/instance/school.db')
    cursor = conn.cursor()
    
    try:
        print("Attempting to add admin_comment column...")
        cursor.execute("ALTER TABLE leave_request ADD COLUMN admin_comment VARCHAR(255)")
        print("admin_comment column added.")
    except sqlite3.OperationalError as e:
        print(f"Skipping admin_comment: {e}")

    try:
        print("Attempting to add attachment column...")
        cursor.execute("ALTER TABLE leave_request ADD COLUMN attachment VARCHAR(255)")
        print("attachment column added.")
    except sqlite3.OperationalError as e:
        print(f"Skipping attachment: {e}")
        
    conn.commit()
    conn.close()
    print("Database update attempt finished.")

if __name__ == "__main__":
    update_db()
