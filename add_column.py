import sqlite3

def add_column():
    try:
        conn = sqlite3.connect('instance/school.db')
        cursor = conn.cursor()
        cursor.execute("ALTER TABLE leave_request ADD COLUMN rejection_reason VARCHAR(255)")
        conn.commit()
        print("Column 'rejection_reason' added successfully.")
        conn.close()
    except Exception as e:
        print(f"Error (column might already exist): {e}")

if __name__ == "__main__":
    add_column()
