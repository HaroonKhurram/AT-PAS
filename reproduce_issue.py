from app import app, db
from models import Student
import sys

def reproduce():
    with app.app_context():
        initial_count = Student.query.count()
        print(f"Initial Student Count: {initial_count}")
        
        # Test Data
        reg_no = "TEST_99999"
        name = "Test Student"
        
        # Check if already exists from previous run
        existing = Student.query.filter_by(registration_no=reg_no).first()
        if existing:
            print(f"Test student {reg_no} already exists. Deleting...")
            db.session.delete(existing)
            db.session.commit()
            print("Deleted.")
            initial_count = Student.query.count() # Update count
        
        print(f"Adding student: {name} ({reg_no})")
        new_student = Student(name=name, registration_no=reg_no)
        db.session.add(new_student)
        db.session.commit()
        
        final_count = Student.query.count()
        print(f"Final Student Count: {final_count}")
        
        check_student = Student.query.filter_by(registration_no=reg_no).first()
        if check_student:
             print("SUCCESS: Student found in DB.")
        else:
             print("FAILURE: Student NOT found in DB.")

if __name__ == "__main__":
    reproduce()
