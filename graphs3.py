import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
from models import Attendance, Subject

def get_student_attendance_chart(student_id):
    """
    Generates a bar chart showing attendance % per subject for a specific student.
    """
    subjects = Subject.query.all()
    
    subject_names = []
    attendance_percentages = []
    colors = []
    
    for subject in subjects:
        total = Attendance.query.filter_by(student_id=student_id, subject_id=subject.id).count()
        present = Attendance.query.filter_by(student_id=student_id, subject_id=subject.id, status='Present').count()
        
        if total > 0:
            pct = (present / total) * 100
        else:
            pct = 0
            
        subject_names.append(subject.code) # Using code for shorter labels
        attendance_percentages.append(pct)
        
        # Color coding
        if pct >= 75:
            colors.append('#4CAF50') # Green
        elif pct >= 60:
            colors.append('#FFC107') # Amber
        else:
            colors.append('#F44336') # Red

    # Plotting
    plt.figure(figsize=(10, 5))
    bars = plt.bar(subject_names, attendance_percentages, color=colors)
    
    plt.title('Attendance Percentage by Subject')
    plt.xlabel('Subjects')
    plt.ylabel('Attendance %')
    plt.ylim(0, 100)
    plt.grid(axis='y', linestyle='--', alpha=0.6)
    
    # Add value labels
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                 f'{height:.1f}%',
                 ha='center', va='bottom')
    
    # Save to IO
    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)
    plt.close()
    
    return base64.b64encode(img.getvalue()).decode('utf-8')
