from app import app
from extensions import db
from models import User, Student

def seed_data():
    with app.app_context():
        print("Starting database seeding...")

        # 1. Create Admin User
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(username='admin', password='password123', role='admin')
            db.session.add(admin)
            print("Created Admin user.")
        else:
            print("Admin user already exists.")

        # 2. Create Teachers
        for i in range(1, 6):
            username = f'teacher{i}'
            teacher = User.query.filter_by(username=username).first()
            if not teacher:
                # Using a default password for simplicity
                teacher = User(username=username, password='password123', role='teacher')
                db.session.add(teacher)
                print(f"Created Teacher: {username}")
            else:
                print(f"Teacher {username} already exists.")

        # 3. Create Students
        for i in range(1, 11):
            reg_no = f'REG-{2025}-{i:03d}' # e.g., REG-2025-001
            student = Student.query.filter_by(registration_no=reg_no).first()
            if not student:
                student = Student(
                    registration_no=reg_no, 
                    name=f"Student Name {i}",
                    password='password123'
                )
                db.session.add(student)
                print(f"Created Student: {reg_no}")
            else:
                print(f"Student {reg_no} already exists.")

        # Commit all changes
        try:
            db.session.commit()
            print("Database seeding completed successfully!")
        except Exception as e:
            db.session.rollback()
            print(f"Error seeding database: {e}")

if __name__ == '__main__':
    seed_data()
