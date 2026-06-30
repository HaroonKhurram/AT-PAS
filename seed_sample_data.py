from app import app
from extensions import db
from models import User, Student, Subject, Attendance, LeaveRequest
import random

def seed_sample_data():
    with app.app_context():
        print("Starting sample data generation...")

        # ---------------------------------------------------------
        # 0. Clean up existing data (Optional: based on user intent to "edit" / "replace")
        # ---------------------------------------------------------
        print("Cleaning up old sample data...")
        # Be careful not to delete 'admin'
        try:
            # Delete dependent tables first to avoid foreign key constraints if not cascading
            Attendance.query.delete()
            LeaveRequest.query.delete()
            Subject.query.delete()
            Student.query.delete()
            # Delete teachers (keep admin)
            User.query.filter(User.role != 'admin').delete()
            db.session.commit()
            print("Old data cleared.")
        except Exception as e:
            db.session.rollback()
            print(f"Error clearing data: {e}")
            return

        # ---------------------------------------------------------
        # Data Lists
        # ---------------------------------------------------------
        male_names = [
            "Ali", "Ahmed", "Bilal", "Hamza", "Usama", "Saad", "Hassan", "Hussain", "Umar", "Zain",
            "Danish", "Fahad", "Noman", "Kashif", "Rizwan", "Imran", "Kamran", "Salman", "Adnan", "Waqas",
            "Zeeshan", "Nasir", "Yasir", "Junaid", "Shahid", "Farhan", "Amir", "Sohail", "Rashid", "Talha",
            "Faisal", "Arslan", "Asad", "Umer", "Haris", "Waleed", "Raza", "Shoaib", "Tariq", "Naveed"
        ]
        female_names = [
            "Ayesha", "Fatima", "Zainab", "Maryam", "Sana", "Hina", "Sadia", "Zara", "Nimra", "Iqra",
            "Mahnoor", "Laiba", "Anam", "Rabia", "Sidra", "Kiran", "Nida", "Saba", "Uzma", "Hira",
            "Noor", "Aleena", "Momal", "Sania", "Kinza", "Areeba", "Sundas", "Farwa", "Javeria", "Maha",
            "Amna", "Bushra", "Farah", "Hafsa", "Mehwish", "Saima", "Shaista", "Tahira", "Warda", "Zunaira"
        ]
        
        last_names = ["Khan", "Ahmed", "Ali", "Hussain", "Shah", "Iqbal", "Butt", "Raja", "Malik", "Sheikh", "Chaudhry", "Ansari", "Qureshi"]

        def get_random_name():
            if random.random() < 0.5:
                first = random.choice(male_names)
            else:
                first = random.choice(female_names)
            last = random.choice(last_names)
            return f"{first} {last}"

        # ---------------------------------------------------------
        # 1. Create 10 Teachers
        # ---------------------------------------------------------
        teachers = []
        print("Creating Teachers...")
        for i in range(1, 11):
            username = f'teacher{i}' # Keeping username simple for login
            full_name = get_random_name() # You might want to store this if User model had a name field, but it only has username. 
            # Wait, User model only has username. The prompt asked for "teachers name". 
            # Looking at models.py: User only has username. 
            # So I can't store a "Real Name" for teachers unless the schema changes or I use username as the name.
            # Let's use the Pakistani name as the username, formatted to be login-able (e.g., Ali.Khan)
            # OR just keep 'teacherX' and maybe the user meant "Student names"?
            # "give the mixture of pakistani male and female stydents and teachers name"
            # It implies teachers should also have these names.
            # I will change the username to be the name (e.g., ali_khan).
            
            # Re-generating name to ensure uniqueness or retry
            while True:
                name_parts = get_random_name().split()
                u_name = f"{name_parts[0].lower()}.{name_parts[1].lower()}"
                if not User.query.filter_by(username=u_name).first():
                    break
            
            security_code = f"{random.randint(1000, 9999)}"
            teacher = User(username=u_name, password='password123', role='teacher', security_code=security_code)
            db.session.add(teacher)
            teachers.append(teacher)
            print(f"Created Teacher: {u_name}") # using u_name as username

        db.session.commit() 
        # Reload teachers to get IDs
        teachers = User.query.filter_by(role='teacher').all()

        # ---------------------------------------------------------
        # 2. Create 50 Students
        # ---------------------------------------------------------
        print("Creating Students...")
        for i in range(1, 51):
            reg_no = f'2025-DS-{i}'
            full_name = get_random_name()
            security_code = f"{random.randint(1000, 9999)}"
            
            student = Student(
                registration_no=reg_no, 
                name=full_name,
                password='password123',
                security_code=security_code
            )
            db.session.add(student)
            print(f"Created Student: {full_name} ({reg_no})")
        
        db.session.commit()

        # ---------------------------------------------------------
        # 3. Create 10 Data Science Subjects
        # ---------------------------------------------------------
        print("Creating Subjects...")
        ds_subjects = [
            ("DS101", "Introduction to Data Science"),
            ("DS201", "Machine Learning"),
            ("DS202", "Data Visualization"),
            ("DS301", "Big Data Analytics"),
            ("DS302", "Deep Learning"),
            ("DS303", "Natural Language Processing"),
            ("STAT201", "Probability and Statistics"),
            ("CS305", "Database Systems"),
            ("DS304", "Computer Vision"),
            ("DS305", "Data Mining and Warehousing")
        ]

        if not teachers:
            print("Warning: No teachers found! Subjects will be created without assigned teachers.")

        for code, name in ds_subjects:
            # Assign a random teacher
            assigned_teacher = random.choice(teachers) if teachers else None
            
            subject = Subject(
                code=code,
                name=name,
                schedule=f"{random.choice(['Mon/Wed', 'Tue/Thu'])} {random.choice(['09:00-10:30', '11:00-12:30', '02:00-03:30'])}",
                teacher=assigned_teacher
            )
            db.session.add(subject)
            print(f"Created Subject: {name} assigned to {assigned_teacher.username if assigned_teacher else 'None'}")

        try:
            db.session.commit()
            print("Sample data updated successfully!")
        except Exception as e:
            db.session.rollback()
            print(f"Error seeding database: {e}")

if __name__ == '__main__':
    seed_sample_data()
