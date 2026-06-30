from app import app, db
from models import User, Student, Attendance, LeaveRequest, Subject
import random

def seed_teacher_data():
    with app.app_context():
        print("Starting Teacher Dashboard Seeding...")
        
        # 1. Create Teacher
        teacher = User.query.filter_by(username='teacher1').first()
        if not teacher:
            teacher = User(username='teacher1', password='password', role='teacher')
            db.session.add(teacher)
            db.session.commit()
            print("Created 'teacher1'.")
        else:
            print("'teacher1' already exists.")

        # 2. Create Student 'Muhammad Haroon'
        haroon = Student.query.filter_by(registration_no='2025-CS-Risk').first()
        if not haroon:
            haroon = Student(name='Muhammad Haroon', registration_no='2025-CS-Risk')
            db.session.add(haroon)
            db.session.commit()
            print("Created student 'Muhammad Haroon'.")

        # 3. Mark Poor Attendance for Haroon (Below 75%)
        # Clear existing first
        Attendance.query.filter_by(student_id=haroon.id).delete()
        
        # 2 Present, 8 Absent = 20%
        for i in range(1, 3):
            att = Attendance(date=f"2025-01-{i:02d}", status='Present', student_id=haroon.id)
            db.session.add(att)
        for i in range(3, 11):
            att = Attendance(date=f"2025-01-{i:02d}", status='Absent', student_id=haroon.id)
            db.session.add(att)
        
        db.session.commit()
        print("Marked poor attendance for Haroon.")

        # 4. Create Random Leave Requests
        # Create a few more students for variety
        s2 = Student.query.filter_by(name='Student Two').first()
        if not s2:
            s2 = Student(name='Student Two', registration_no='S-002')
            db.session.add(s2)
        
        s3 = Student.query.filter_by(name='Student Three').first()
        if not s3:
            s3 = Student(name='Student Three', registration_no='S-003')
            db.session.add(s3)
        db.session.commit()

        # Clear existing leaves
        LeaveRequest.query.delete()

        l1 = LeaveRequest(student_id=haroon.id, date='2025-10-27', reason='Fever', status='Pending')
        l2 = LeaveRequest(student_id=s2.id if s2 else haroon.id, date='2025-10-28', reason='Urgent Piece of Work', status='Pending')
        l3 = LeaveRequest(student_id=s3.id if s3 else haroon.id, date='2025-10-29', reason='Wedding', status='Pending')
        
        db.session.add_all([l1, l2, l3])
        db.session.commit()
        print("Created 3 Pending Leave Requests.")

        print("Seeding Complete!")

if __name__ == '__main__':
    seed_teacher_data()
