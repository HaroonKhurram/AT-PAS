from extensions import db

# ---------------------------------------------------------
# USER MODEL (Admin & Teachers)
# ---------------------------------------------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    role = db.Column(db.String(10), nullable=False) # 'admin' or 'teacher'
    security_code = db.Column(db.String(10), nullable=False, default='0000')

# ---------------------------------------------------------
# STUDENT MODEL
# ---------------------------------------------------------
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    registration_no = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(50), nullable=False, default='password123')
    security_code = db.Column(db.String(10), nullable=False, default='0000')

# ---------------------------------------------------------
# ATTENDANCE MODEL
# ---------------------------------------------------------
class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(10), nullable=False) # 'Present', 'Absent', 'Leave'
    
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=True) # Should be false but nullable for migration
    subject = db.relationship('Subject', backref='attendances')

# ---------------------------------------------------------
# SUBJECT MODEL
# ---------------------------------------------------------
class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    schedule = db.Column(db.String(100), nullable=False)
    
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    teacher = db.relationship('User', backref='subjects')

# ---------------------------------------------------------
# LEAVE REQUEST MODEL
# ---------------------------------------------------------
class LeaveRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(20), nullable=False)
    reason = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(20), default='Pending', nullable=False)
    rejection_reason = db.Column(db.String(255), nullable=True)
    
    admin_comment = db.Column(db.String(255), nullable=True)
    attachment = db.Column(db.String(255), nullable=True)
    
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    student = db.relationship('Student', backref='leave_requests')
