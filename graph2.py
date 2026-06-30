import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
from models import Attendance, Student
from datetime import datetime

def get_correlation_chart(teacher_id):
    """
    REPLACED: Now generates a Dark Themed Line Chart for Attendance Trend 
    (Daily/Per-entry granularity) to match the user's design image.
    Function name kept same to minimize app.py changes, but acts as 'Visual 2'.
    """
    
    # Fetch all attendance records for this teacher's subjects (or all for now as per previous logic)
    # Group by Date to get daily averages
    
    # 1. Get all unique dates from Attendance
    # In a real app with SQL, we'd do: db.session.query(Attendance.date).distinct()...
    # Here we'll fetch all and process in python for simplicity
    
    records = Attendance.query.all()
    
    date_map = {} # date_str -> {'total': 0, 'present': 0}
    
    for record in records:
        d = record.date
        if d not in date_map:
            date_map[d] = {'total': 0, 'present': 0}
            
        date_map[d]['total'] += 1
        if record.status == 'Present':
            date_map[d]['present'] += 1
            
    # Sort by date
    sorted_dates = sorted(date_map.keys())
    
    # Prepare data for plotting
    dates = []
    percentages = []
    
    for d in sorted_dates:
        stats = date_map[d]
        if stats['total'] > 0:
            pct = (stats['present'] / stats['total']) * 100
        else:
            pct = 0
            
        dates.append(d)
        percentages.append(pct)

    # -----------------------------
    # PLOTTING WITH DARK THEME
    # -----------------------------
    
    # Set style params
    plt.style.use('dark_background') # Use built-in dark style as base
    
    # Custom colors from image approximation
    bg_color = '#111827' # Dark navy/black
    plot_bg_color = '#1F2937' # Slightly lighter for plot area
    line_color = '#A78BFA' # Light purple/lilac
    text_color = '#9CA3AF' # Grayish text
    
    fig, ax = plt.subplots(figsize=(8, 4))
    
    # Set Figure and Axes Background
    fig.patch.set_facecolor(bg_color)
    ax.set_facecolor(plot_bg_color)
    
    # Plot Line
    ax.plot(dates, percentages, color=line_color, linewidth=2, marker='.', markersize=8)
    
    # Grid
    ax.grid(True, color='#374151', linestyle='-', linewidth=0.5, alpha=0.5)
    
    # Title inside chart (as per image "Class Attendance Insights")
    ax.set_title("Class Attendance Insights", color='white', fontsize=10, pad=10)
    
    # Axes Styling
    ax.spines['bottom'].set_color(text_color)
    ax.spines['top'].set_color(bg_color) 
    ax.spines['right'].set_color(bg_color)
    ax.spines['left'].set_color(text_color)
    
    ax.tick_params(axis='x', colors=text_color, rotation=0, labelsize=8)
    ax.tick_params(axis='y', colors=text_color, labelsize=8)
    
    # Limit X-axis labels if too many
    if len(dates) > 7:
        # Show roughly 5-7 ticks
        interval = len(dates) // 6
        ax.set_xticks(range(0, len(dates), interval if interval > 0 else 1))
        # This relies on index plotting if dates are strings, but matplotlib handles string dates by index usually
        # To be safe, let's limit the tick locator
        import matplotlib.ticker as ticker
        ax.xaxis.set_major_locator(ticker.MaxNLocator(nbins=6))

    plt.ylim(0, 105)
    
    plt.tight_layout()
    
    # Save to IO
    img = io.BytesIO()
    plt.savefig(img, format='png', facecolor=fig.get_facecolor(), edgecolor='none')
    img.seek(0)
    plt.close()
    
    return base64.b64encode(img.getvalue()).decode('utf-8')
