import sqlite3
import os

db_path = os.path.join('instance', 'school.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

names_to_check = ['Muhammad Hamza', 'Muhammad Haroon', 'Abdullah', 'Ahmad Sajjad']

print(f"{'ID':<5} {'Name':<20} {'Reg No':<15}")
print("-" * 40)

for name in names_to_check:
    # Use LIKE for loose matching to find them even if there are spaces
    cursor.execute("SELECT id, name, registration_no FROM student WHERE name LIKE ?", (f'%{name}%',))
    rows = cursor.fetchall()
    for row in rows:
        print(f"{row[0]:<5} '{row[1]:<18}' {row[2]:<15}")

conn.close()
