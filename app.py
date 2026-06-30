from flask import Flask, render_template, request, redirect, url_for, flash, send_file, abort
from datetime import datetime, timedelta
import os
import csv
import io
from functools import wraps
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

from extensions import db


# 1. App Configuration
app = Flask(__name__)

# This tells Flask to create a file named 'database.db' in your project folder
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///school.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Use absolute path for upload folder to avoid relative path issues
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['UPLOAD_FOLDER'] = os.path.join(basedir, 'instance', 'uploads')
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
app.secret_key = 'super_secret_key_for_dev_only' # TODO: Change this in production

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize the Database
db.init_app(app)

# ---------------------------------------------------------
# SECURITY DECORATOR
# ---------------------------------------------------------
def role_required(*allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from flask import session
            # Check for Admin/Teacher
            if 'user_id' in session:
                user = User.query.get(session['user_id'])
                if user and user.role in allowed_roles:
                    return f(*args, **kwargs)
            
            # Check for Student
            if 'student_id' in session and 'student' in allowed_roles:
                student = Student.query.get(session['student_id'])
                if student:
                    return f(*args, **kwargs)
            
            abort(404)
        return decorated_function
    return decorator

from models import User, Student, Subject, LeaveRequest, Attendance

# Route for the Home / Landing Page
@app.route('/')
def home():
    # Make sure your HTML file is actually at templates/home/home.html
    return render_template('home/home.html')

@app.route('/features')
def features():
    return render_template('home/features.html')

@app.route('/about')
def about():
    return render_template('home/about.html')

@app.route('/admin_dashboard')
@role_required('admin')
def admin_dashboard():
    student_count = Student.query.count()
    teacher_count = User.query.filter_by(role='teacher').count()
    subject_count = Subject.query.count()
    current_date = datetime.now().strftime('%B %d, %Y')
    print(f"DEBUG: Current Date is {current_date}")
    return render_template('admin/admin_dashboard.html', 
                           student_count=student_count, 
                           teacher_count=teacher_count, 
                           subject_count=subject_count,
                           current_date=current_date)

@app.route('/admin/user_management', methods=['GET', 'POST'])
@role_required('admin')
def admin_user_management():
    if request.method == 'POST':
        name = request.form.get('name')
        registration_no = request.form.get('registration_no')
        
        # Basic validation
        if name and registration_no:
            existing_student = Student.query.filter_by(registration_no=registration_no).first()
            if not existing_student:
                new_student = Student(name=name, registration_no=registration_no)
                db.session.add(new_student)
                db.session.commit()
        
        return redirect(url_for('admin_user_management'))

    students = Student.query.all()
    
    # Search Filter
    query = request.args.get('q')
    if query:
        students = Student.query.filter((Student.name.ilike(f'%{query}%')) | (Student.registration_no.ilike(f'%{query}%'))).all()
    else:
        students = Student.query.all()
        
    # Assuming you might want teachers too later, but strictly for the task:
    return render_template('admin/admin_user-management.html', students=students)

@app.route('/delete_student/<int:id>')
@role_required('admin')
def delete_student(id):
    student = Student.query.get_or_404(id)
    db.session.delete(student)
    db.session.commit()
    return redirect(url_for('admin_user_management'))

@app.route('/update_student', methods=['POST'])
@role_required('admin')
def update_student():
    id = request.form.get('id')
    name = request.form.get('name')
    registration_no = request.form.get('registration_no')
    
    if id:
        student = Student.query.get(id)
        if student:
            student.name = name
            student.registration_no = registration_no
            db.session.commit()
            
    return redirect(url_for('admin_user_management'))

@app.route('/admin/manage_teachers')
def manage_teachers():
    # Search Filter
    query = request.args.get('q')
    if query:
        teachers = User.query.filter(User.role=='teacher', User.username.ilike(f'%{query}%')).all()
    else:
        teachers = User.query.filter_by(role='teacher').all()
        
    return render_template('admin/admin_teacher-management.html', teachers=teachers)

@app.route('/add_teacher', methods=['POST'])
@role_required('admin')
def add_teacher():
    username = request.form.get('username')
    password = request.form.get('password')
    
    if username and password:
        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            new_teacher = User(username=username, password=password, role='teacher')
            db.session.add(new_teacher)
            db.session.commit()
            
    return redirect(url_for('manage_teachers'))

@app.route('/delete_teacher/<int:id>')
@role_required('admin')
def delete_teacher(id):
    teacher = User.query.get_or_404(id)
    if teacher.role == 'teacher':
        db.session.delete(teacher)
        db.session.commit()
    return redirect(url_for('manage_teachers'))

@app.route('/update_teacher', methods=['POST'])
@role_required('admin')
def update_teacher():
    id = request.form.get('id')
    username = request.form.get('username')
    password = request.form.get('password')
    
    if id:
        teacher = User.query.get(id)
        if teacher and teacher.role == 'teacher':
            teacher.username = username
            if password: # Only update password if provided
                teacher.password = password
            db.session.commit()
            
    return redirect(url_for('manage_teachers'))

@app.route('/import_students', methods=['POST'])
@role_required('admin')
def import_students():
    if 'file' not in request.files:
        return redirect(url_for('admin_user_management'))
    
    file = request.files['file']
    if file.filename == '':
        return redirect(url_for('admin_user_management'))
    
    if file:
        stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
        csv_input = csv.reader(stream)
        # Skip header if exists? Assuming simple CSV: Name,RegNo
        # row: [Name, RegistrationNo]
        for row in csv_input:
            if len(row) >= 2:
                name = row[0]
                reg_no = row[1]
                if not Student.query.filter_by(registration_no=reg_no).first():
                    new_student = Student(name=name, registration_no=reg_no)
                    db.session.add(new_student)
        db.session.commit()
        
    return redirect(url_for('admin_user_management'))

@app.route('/import_teachers', methods=['POST'])
@role_required('admin')
def import_teachers():
    if 'file' not in request.files:
        return redirect(url_for('manage_teachers'))
        
    file = request.files['file']
    if file.filename == '':
        return redirect(url_for('manage_teachers'))
        
    if file:
        stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
        csv_input = csv.reader(stream)
        # Assuming CSV: Username,Password
        for row in csv_input:
            if len(row) >= 2:
                username = row[0]
                password = row[1]
                if not User.query.filter_by(username=username).first():
                    new_teacher = User(username=username, password=password, role='teacher')
                    db.session.add(new_teacher)
        db.session.commit()
        
    return redirect(url_for('manage_teachers'))

@app.route('/reset_password_student/<int:id>')
@role_required('admin')
def reset_password_student(id):
    student = Student.query.get_or_404(id)
    student.password = 'student123'
    db.session.commit()
    return redirect(url_for('admin_user_management'))

@app.route('/reset_password_teacher/<int:id>')
@role_required('admin')
def reset_password_teacher(id):
    teacher = User.query.get_or_404(id)
    if teacher.role == 'teacher':
        teacher.password = 'teacher123'
        db.session.commit()
    return redirect(url_for('manage_teachers'))

@app.route('/admin/subject_allocation')
@role_required('admin')
def admin_subject_allocation():
    subjects = Subject.query.all()
    teachers = User.query.filter_by(role='teacher').all()
    unassigned_subjects = [s for s in subjects if s.teacher_id is None]
    
    return render_template('admin/admin_subject-coniguration.html', 
                           subjects=subjects, 
                           teachers=teachers, 
                           unassigned_subjects=unassigned_subjects)

@app.route('/add_subject', methods=['POST'])
@role_required('admin')
def add_subject():
    code = request.form.get('code')
    name = request.form.get('name')
    schedule = request.form.get('schedule')
    
    if code and name and schedule:
        new_subject = Subject(code=code, name=name, schedule=schedule)
        db.session.add(new_subject)
        db.session.commit()
    
    return redirect(url_for('admin_subject_allocation'))

@app.route('/assign_teacher', methods=['POST'])
@role_required('admin')
def assign_teacher():
    subject_id = request.form.get('subject_id')
    teacher_id = request.form.get('teacher_id')
    
    if subject_id and teacher_id:
        subject = Subject.query.get(subject_id)
        if subject:
            subject.teacher_id = teacher_id
            db.session.commit()
            
    return redirect(url_for('admin_subject_allocation'))

@app.route('/update_subject', methods=['POST'])
@role_required('admin')
def update_subject():
    subject_id = request.form.get('subject_id')
    code = request.form.get('code')
    name = request.form.get('name')
    schedule = request.form.get('schedule')
    teacher_id = request.form.get('teacher_id')
    
    if subject_id:
        subject = Subject.query.get(subject_id)
        if subject:
            subject.code = code
            subject.name = name
            subject.schedule = schedule
            if teacher_id:
                subject.teacher_id = teacher_id
            
            db.session.commit()
            
    return redirect(url_for('admin_subject_allocation'))

@app.route('/admin/database_management')
@role_required('admin')
def admin_database_management():
    return render_template('admin/admin_database-management.html')

@app.route('/admin/download_backup')
@role_required('admin')
def download_backup():
    # Assuming DB is at instance/school.db based on config
    # app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///school.db' usually implies slightly different things depending on context
    # but based on file list it's in instance/
    path = 'instance/school.db'
    return send_file(path, as_attachment=True)

@app.route('/admin/reset_attendance', methods=['POST'])
@role_required('admin')
def reset_attendance():
    try:
        # Delete using query logic for safety instead of raw delete all if possible, but delete query works.
        num_attendance = Attendance.query.delete()
        num_leaves = LeaveRequest.query.delete()
        db.session.commit()
        flash(f'All attendance data ({num_attendance} records) and leave requests ({num_leaves} records) have been wiped for the new semester.')
    except Exception as e:
        db.session.rollback()
        flash(f'Error resetting data: {str(e)}')
        
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/export_db')
@role_required('admin')
def export_db():
    path = 'instance/school.db'
    return send_file(path, as_attachment=True)

@app.route('/admin/restore_db', methods=['POST'])
@role_required('admin')
def restore_db():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(url_for('admin_database_management'))
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('admin_database_management'))
    if file:
        file.save('instance/school.db')
        flash('Database restored successfully. Please restart the server if needed.')
    return redirect(url_for('admin_database_management'))

@app.route('/admin/optimize_db/<action>')
@role_required('admin')
def optimize_db(action):
    try:
        if action == 'integrity':
            result = db.session.execute(text('PRAGMA integrity_check')).scalar()
            flash(f'Integrity Check Result: {result}')
        elif action == 'vacuum':
            db.session.execute(text('VACUUM'))
            db.session.commit()
            flash('Database compacted and optimized.')
    except Exception as e:
        flash(f'Error optimizing: {str(e)}')
    return redirect(url_for('admin_database_management'))

@app.route('/admin/reset_data/<action>', methods=['POST'])
@role_required('admin')
def reset_data(action):
    try:
        if action == 'clear_logs':
            Attendance.query.delete()
            LeaveRequest.query.delete()
            db.session.commit()
            flash('All attendance logs cleared.')
        elif action == 'factory_reset':
            db.drop_all()
            db.create_all()
            # Restore default admin
            admin = User(username='admin', password='password123', role='admin')
            db.session.add(admin)
            db.session.commit()
            flash('System reset to factory settings.')
    except Exception as e:
        db.session.rollback()
        flash(f'Error resetting data: {str(e)}')
    return redirect(url_for('admin_database_management'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


# Helper for counting student notifications (Approved/Rejected)
def get_student_notification_count(student_id):
    # Count leaves that are NOT 'Pending' (i.e., Approved or Rejected)
    # The user specifically asked for "stats of 'Approved' or 'Rejected'"
    return LeaveRequest.query.filter(
        LeaveRequest.student_id == student_id,
        LeaveRequest.status.in_(['Approved', 'Rejected'])
    ).count()

@app.route('/student_dashboard')
@role_required('student')
def student_dashboard():
    student = Student.query.get(session['student_id'])
    
    # Calculate Overall Percentage
    total_attendance = Attendance.query.filter_by(student_id=student.id).count()
    present_count = Attendance.query.filter_by(student_id=student.id, status='Present').count()
    
    overall_percentage = 0
    if total_attendance > 0:
        overall_percentage = round((present_count / total_attendance) * 100, 1)
        
    current_date = datetime.now().strftime('%B %d, %Y')
    
    # Notification Count
    notification_count = get_student_notification_count(student.id)
        
    return render_template('student/student_dashboard.html', 
                           student=student, 
                           overall_percentage=overall_percentage,
                           current_date=current_date,
                           notification_count=notification_count)

@app.route('/student/my_dashboard')
@role_required('student')
def student_my_dashboard():
    student = Student.query.get(session['student_id'])
    
    # Notification Count
    notification_count = get_student_notification_count(student.id)
    
    return render_template('student/student_my_dashboard.html', 
                           student=student, 
                           notification_count=notification_count)

@app.route('/student/attendance')
@role_required('student')
def student_attendance():
    student = Student.query.get(session['student_id'])
    
    # Metric 1: Subject Breakdown
    subjects = Subject.query.all()
    subject_metrics = []
    
    for subject in subjects:
        # Filter attendance by student and subject
        total_classes = Attendance.query.filter_by(student_id=student.id, subject_id=subject.id).count() 
        present_count = Attendance.query.filter_by(student_id=student.id, subject_id=subject.id, status='Present').count()
        
        percentage = 0
        if total_classes > 0:
            percentage = round((present_count / total_classes) * 100, 1)
            
        subject_metrics.append({
            'subject_name': subject.name,
            'subject_code': subject.code,
            'percentage': percentage,
            'total_classes': total_classes,
            'present_count': present_count,
            'subject_id': subject.id
        })
        
    # Metric 2: Detailed Log with Filtering
    query = Attendance.query.filter_by(student_id=student.id)
    
    # Get Filters
    subject_filter = request.args.get('subject_filter')
    status_filter = request.args.get('status_filter')
    
    if subject_filter and subject_filter != 'all':
        query = query.filter_by(subject_id=subject_filter)
        
    if status_filter and status_filter != 'all':
        query = query.filter_by(status=status_filter)
    
    attendance_log = query.order_by(Attendance.date.desc()).all()
    
    # Notification Count
    notification_count = get_student_notification_count(student.id)
    
    
    # Graph Generation
    attendance_graph = get_student_attendance_chart(student.id)

    return render_template('student/student_attendence.html', 
                           student=student,
                           subject_metrics=subject_metrics, 
                           attendance_log=attendance_log,
                           notification_count=notification_count,
                           subjects=subjects,
                           current_subject_filter=subject_filter,
                           current_status_filter=status_filter,
                           attendance_graph=attendance_graph)

@app.route('/student/leave')
@role_required('student')
def student_leave():
    return redirect(url_for('student_apply_leave'))

@app.route('/student/apply_leave', methods=['GET', 'POST'])
@role_required('student')
def student_apply_leave():
    student = Student.query.get(session['student_id'])
    
    if request.method == 'POST':
        date = request.form.get('date')
        reason = request.form.get('reason')
        subject_name = request.form.get('subject')
        
        file = request.files.get('attachment')
        attachment_filename = None
        if file and file.filename != '':
            attachment_filename = file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
        
        if date and reason:
            # Append subject to reason for visibility since no subject_id column
            final_reason = f"[{subject_name}] {reason}" if subject_name else reason
            
            new_request = LeaveRequest(
                student_id=student.id,
                date=date,
                reason=final_reason, # Storing subject in reason as per current model limitations
                status='Pending',
                attachment=attachment_filename
            )
            db.session.add(new_request)
            db.session.commit()
            flash('Leave Request Submitted Successfully')
            
        return redirect(url_for('student_apply_leave'))

    # GET: Fetch history and subjects
    history = LeaveRequest.query.filter_by(student_id=student.id).order_by(LeaveRequest.id.desc()).all()
    subjects = Subject.query.all()
    
    # Notification Count
    notification_count = get_student_notification_count(student.id)
    
    return render_template('student/student_apply_leave.html', 
                           student=student, 
                           history=history, 
                           subjects=subjects,
                           notification_count=notification_count)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        return send_file(file_path)
    else:
        return "File not found on server (possibly deleted or not saved correctly).", 404

# Helper for counting subject-specific pending leaves
def get_teacher_pending_leave_count(teacher):
    all_pending = LeaveRequest.query.filter_by(status='Pending').all()
    teacher_subject_names = [s.name for s in teacher.subjects]
    
    count = 0
    for req in all_pending:
        if req.reason.startswith('['):
            end_bracket = req.reason.find(']')
            if end_bracket != -1:
                subject_tag = req.reason[1:end_bracket]
                if subject_tag in teacher_subject_names or subject_tag == 'Full Day':
                    count += 1
        else:
            # Count untagged requests
            count += 1
    return count

@app.route('/teacher_dashboard')
@role_required('teacher')
def teacher_dashboard():
    from flask import session
    user_id = session['user_id']
    teacher = User.query.get(user_id)
    
    if not teacher or teacher.role != 'teacher':
        return redirect(url_for('login'))
        
    # Fetch Data
    assigned_subject = teacher.subjects[0] if teacher.subjects else None
    
    # Correctly filtered leave count
    leave_count = get_teacher_pending_leave_count(teacher)
    
    # At Risk Students Calculation
    students = Student.query.all()
    at_risk_students = []
    
    # Get teacher's subject IDs
    teacher_subject_ids = [s.id for s in teacher.subjects]

    for student in students:
        # If teacher has no subjects, we can't calculate subject-specific risk, assume safe
        if not teacher_subject_ids:
            continue

        total = Attendance.query.filter(
            Attendance.student_id == student.id,
            Attendance.subject_id.in_(teacher_subject_ids)
        ).count()
        
        present = Attendance.query.filter(
            Attendance.student_id == student.id, 
            Attendance.subject_id.in_(teacher_subject_ids),
            Attendance.status == 'Present'
        ).count()
        
        if total > 0:
            percentage = (present / total) * 100
        else:
            percentage = 100 # No classes held/attended for this teacher yet
            
        if percentage < 75:
            at_risk_students.append({
                'name': student.name,
                'registration_no': student.registration_no,
                'attendance_percentage': round(percentage, 1),
                'id': student.id
            })
            
    current_date = datetime.now().strftime('%B %d, %Y')
    
    return render_template('teacher/teacher_dashboard.html',
                           teacher=teacher,
                           assigned_subject=assigned_subject,
                           leave_count=leave_count,
                           at_risk_students=at_risk_students,
                           current_date=current_date)

@app.route('/teacher/mark_attendance', methods=['GET', 'POST'])
@role_required('teacher')
def teacher_mark_attendance():
    user_id = session['user_id']
    teacher = User.query.get(user_id)
    
    if not teacher or teacher.role != 'teacher':
        return redirect(url_for('login'))
        
    if request.method == 'POST':
        date = request.form.get('date')
        subject_id = request.form.get('subject_id')
        submission_mode = request.form.get('submission_mode', 'manualMode')

        if submission_mode == 'rollMode':
            # 1. Parse Absent Roll Numbers
            absent_text = request.form.get('absent_roll_nos', '')
            # Split by comma or newline, strip whitespace, remove empty strings
            absent_roll_nos = [r.strip() for r in absent_text.replace('\n', ',').split(',') if r.strip()]
            
            # 2. Validate that all entered roll numbers exist in database
            all_students = Student.query.all()
            valid_roll_nos = {student.registration_no for student in all_students}
            invalid_roll_nos = [roll_no for roll_no in absent_roll_nos if roll_no not in valid_roll_nos]
            
            if invalid_roll_nos:
                flash(f'Error: The following roll numbers do not exist in the database: {", ".join(invalid_roll_nos)}', 'error')
                return redirect(url_for('teacher_mark_attendance'))
            
            # 3. Iterate ALL students (we need to mark everyone)
            for student in all_students:
                status = 'Absent' if student.registration_no in absent_roll_nos else 'Present'
                
                # Update/Create Record
                existing_record = Attendance.query.filter_by(student_id=student.id, date=date).first()
                if existing_record:
                    existing_record.status = status
                else:
                    new_record = Attendance(student_id=student.id, date=date, status=status, subject_id=subject_id)
                    db.session.add(new_record)
                    
        else: 
            # Manual Mode (and Bulk Mode which uses the same form structure)
            # Loop through form data to find status_studentID keys
            for key, value in request.form.items():
                if key.startswith('status_'):
                    student_id = key.split('_')[1]
                    status = value # Present, Absent, Leave
                    
                    # Check if record exists
                    existing_record = Attendance.query.filter_by(student_id=student_id, date=date).first()
                    if existing_record:
                        existing_record.status = status
                    else:
                        new_record = Attendance(student_id=student_id, date=date, status=status, subject_id=subject_id)
                        db.session.add(new_record)
        
        db.session.commit()
        # In a real app, we would flash a message here
        return redirect(url_for('teacher_dashboard'))

    # GET Request
    assigned_subject = teacher.subjects[0] if teacher.subjects else None
    students = Student.query.order_by(Student.registration_no).all()
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Calculate leave count for navbar
    leave_count = get_teacher_pending_leave_count(teacher)
    
    return render_template('teacher/teacher_mark-attendence.html', 
                           students=students, 
                           assigned_subject=assigned_subject, 
                           today=today,
                           teacher=teacher,
                           leave_count=leave_count)

from graph import get_attendance_trend_chart
from graph2 import get_correlation_chart
from graphs3 import get_student_attendance_chart

@app.route('/teacher/class_insights')
@role_required('teacher')
def teacher_class_insights():
    user_id = session['user_id']
    teacher = User.query.get(user_id)
        
    leave_count = get_teacher_pending_leave_count(teacher)
    
    # Generate Graphs
    attendance_trend_graph = get_attendance_trend_chart(teacher.id)
    correlation_graph = get_correlation_chart(teacher.id)
    
    return render_template('teacher/teacher_class-insights.html', 
                           teacher=teacher, 
                           leave_count=leave_count,
                           attendance_trend_graph=attendance_trend_graph,
                           correlation_graph=correlation_graph)

@app.route('/teacher/leave_requests')
@role_required('teacher')
def teacher_leave_requests():
    user_id = session['user_id']
    teacher = User.query.get(user_id)

    # Fetch pending requests
    all_requests = LeaveRequest.query.filter_by(status='Pending').all()
    
    # Filter requests for this teacher's subjects
    teacher_subject_names = [s.name for s in teacher.subjects]
    
    filtered_requests = []
    for req in all_requests:
        # Check if reason starts with [Subject Name] which implies it's subject-specific
        if req.reason.startswith('['):
            end_bracket = req.reason.find(']')
            if end_bracket != -1:
                subject_tag = req.reason[1:end_bracket]
                
                # Check if this subject belongs to teacher
                if subject_tag in teacher_subject_names or subject_tag == 'Full Day':
                    filtered_requests.append(req)
                # Else: Exclude (belongs to another teacher)
        else:
            # Legacy/Untagged requests - show to be safe
            filtered_requests.append(req)
            
    # Recalculate count for consistency
    leave_count = len(filtered_requests)
    
    return render_template('teacher/teacher_leave-request.html', requests=filtered_requests, teacher=teacher, leave_count=leave_count)

@app.route('/approve_leave/<int:id>')
@role_required('teacher')
def approve_leave(id):
    leave_request = LeaveRequest.query.get_or_404(id)
    leave_request.status = 'Approved'
    leave_request.admin_comment = "Approved" # Good practice to set something
    
    # Create Attendance Record
    # Check if a record already exists for that date (though logic says if they applied, maybe not marked yet?)
    # But usually applying for leave is for future or today.
    existing_attendance = Attendance.query.filter_by(student_id=leave_request.student_id, date=leave_request.date).first()
    
    if existing_attendance:
        existing_attendance.status = 'Leave'
    else:
        new_attendance = Attendance(student_id=leave_request.student_id, date=leave_request.date, status='Leave')
        db.session.add(new_attendance)
        
    db.session.commit()
    return redirect(url_for('teacher_leave_requests'))

@app.route('/reject_leave/<int:id>', methods=['POST'])
@role_required('teacher')
def reject_leave(id):
        
    reason = request.form.get('rejection_reason')
    
    leave_request = LeaveRequest.query.get_or_404(id)
    leave_request.status = 'Rejected'
    leave_request.rejection_reason = reason
    leave_request.admin_comment = reason # Ensure it shows on student dashboard
    db.session.commit()
    
    return redirect(url_for('teacher_leave_requests'))

from flask import session
# Route for the Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        role = request.form.get('role')
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember')
        
        # Simple validation
        if not username or not password:
             return render_template('home/login.html', error="Please enter both username and password")

        if role in ['admin', 'teacher']:
            user = User.query.filter_by(username=username, role=role).first()
            if user and user.password == password: # In real app, use password hashing!
                # Login success
                if remember:
                    session.permanent = True
                session['user_id'] = user.id
                if role == 'admin':
                    return redirect(url_for('admin_dashboard'))
                elif role == 'teacher':
                    return redirect(url_for('teacher_dashboard'))
            else:
                 return render_template('home/login.html', error="Invalid credentials")
        
        elif role == 'student':
             # Try finding by Registration Number first
             student = Student.query.filter_by(registration_no=username).first()
             
             # If not found, try finding by Name
             if not student:
                 student = Student.query.filter_by(name=username).first()

             if student and student.password == password:
                 if remember:
                     session.permanent = True
                 session['student_id'] = student.id
                 return redirect(url_for('student_dashboard'))
             else:
                 return render_template('home/login.html', error="Invalid Student credentials")

    return render_template('home/login.html')

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        role = request.form.get('role')
        username = request.form.get('username') # For students this is Reg No
        security_code = request.form.get('security_code')
        new_password = request.form.get('new_password')
        
        if role in ['admin', 'teacher']:
            user = User.query.filter_by(username=username, role=role, security_code=security_code).first()
            if user:
                if user.password == new_password:
                    flash('New password cannot be the same as your current password.', 'error')
                    return render_template('home/forgot_password.html')
                user.password = new_password
                db.session.commit()
                flash('Password updated successfully. Please login.', 'success')
                return redirect(url_for('login'))
            else:
                flash('Invalid credentials or security code.', 'error')
        
        elif role == 'student':
            student = Student.query.filter_by(registration_no=username, security_code=security_code).first()
            if student:
                if student.password == new_password:
                    flash('New password cannot be the same as your current password.', 'error')
                    return render_template('home/forgot_password.html')
                student.password = new_password
                db.session.commit()
                flash('Password updated successfully. Please login.', 'success')
                return redirect(url_for('login'))
            else:
                flash('Invalid student credentials or security code.', 'error')
                
    return render_template('home/forgot_password.html')

# ---------------------------------------------------------
# DATABASE CREATION
# ---------------------------------------------------------
# Import models here to avoid circular import issues
# The models need 'db' to be defined in app.py first
with app.app_context():
    db.create_all()

# ---------------------------------------------------------
# RUN THE APP
# ---------------------------------------------------------
if __name__ == '__main__':
    # 'debug=True' means the server restarts automatically when you change code
    app.run(debug=True)
