import random
from app import app
from extensions import db
from models import User, Student

def randomize_codes():
    with app.app_context():
        print("Randomizing security codes...")
        
        # 1. Randomize Admins & Teachers
        users = User.query.all()
        for u in users:
            u.security_code = f"{random.randint(1000, 9999)}"
            print(f"Updated {u.role}: {u.username} -> {u.security_code}")
            
        # 2. Randomize Students
        students = Student.query.all()
        for s in students:
            s.security_code = f"{random.randint(1000, 9999)}"
            print(f"Updated student: {s.registration_no} -> {s.security_code}")
            
        db.session.commit()
        print("\nAll security codes randomized successfully!")
        print("IMPORTANT: Users must now use these codes for password recovery.")

if __name__ == "__main__":
    randomize_codes()
