import os
from app import app, db

print(f"Current Working Directory: {os.getcwd()}")
print(f"App Root Path: {app.root_path}")
print(f"Instance Path: {app.instance_path}")
print(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")

with app.app_context():
    print(f"Engine URL: {db.engine.url}")
    # Try to insert a dummy student and see where it goes if we wanted to test, 
    # but strictly just checking path first.
    
    # Check if we can see students
    from models import Student
    count = Student.query.count()
    print(f"Student Count in DB: {count}")
    
    # Check file exists at expected location
    db_file = 'school.db'
    if os.path.exists(db_file):
        print(f"Found {db_file} in CWD")
    
    instance_db = os.path.join('instance', 'school.db')
    if os.path.exists(instance_db):
        print(f"Found {instance_db}")
