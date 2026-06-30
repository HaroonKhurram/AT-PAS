import sqlite3

def add_subject_column():
    try:
        conn = sqlite3.connect('instance/school.db')
        cursor = conn.cursor()
        cursor.execute("ALTER TABLE attendance ADD COLUMN subject_id INTEGER REFERENCES subject(id)")
        conn.commit()
        print("Column 'subject_id' added successfully.")
        conn.close()
    except Exception as e:
        print(f"Error (column might already exist): {e}")

if __name__ == "__main__":
    add_subject_column()
