# 🧠 Advanced Tracking & Predictive Attendance System (AT‑PAS)

[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![Flask Framework](https://img.shields.io/badge/Flask-Framework-green.svg)](https://flask.palletsprojects.com/)
[![SQLite DB](https://img.shields.io/badge/Database-SQLite-lightgrey.svg)](https://www.sqlite.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status: Stable](https://img.shields.io/badge/Status-Stable-success.svg)]()
[![Made with ❤️ by Team AT‑PAS](https://img.shields.io/badge/Made%20with-%E2%9D%A4-red.svg)]()

---

### A Flask‑based web application for automating attendance, predicting student risk, and ensuring transparency across academic roles.

---

## 📘 Overview
AT‑PAS is a **role‑based attendance management system** built with **Python (Flask)** and **SQLite**. It replaces manual registers with a secure, intelligent, and data‑driven platform for **Admins**, **Teachers**, and **Students**.

**Key Highlights**
- ⚙️ **Automation:** Bulk marking reduces attendance time by 90%.
- 🧩 **Predictive Analytics:** Flags students below 75% attendance.
- 🔐 **Security:** Role‑based login and database “Danger Zone” for safe resets.
- 📊 **Transparency:** Students can view attendance and leave status anytime.

---

## 🧱 Architecture
AT‑PAS follows the **MVC (Model‑View‑Controller)** pattern:

| Layer | Technology | Role |
|-------|-------------|------|
| **Model** | SQLAlchemy + SQLite | Database schema and ORM |
| **View** | Jinja2 + HTML/CSS | Dynamic UI templates |
| **Controller** | Flask | Routing, logic, and authentication |

---

## 🗂️ Folder Structure
ATPAS/
│
├── app.py                     # Main Flask application
├── extensions.py              # Database initialization
├── models.py                  # ORM models (User, Student, Attendance, Leave)
├── templates/                 # HTML templates (Admin, Teacher, Student)
│   ├── admin/
│   ├── teacher/
│   └── student/
├── static/                    # CSS, JS, and images
├── instance/                  # SQLite database and uploads
├── requirements.txt            # Dependencies
├── .gitignore                 # Ignored files
├── LICENSE                    # MIT License
└── README.md                  # Project documentation


---

## 🧩 Core Modules
| Module | Description |
|---------|--------------|
| **Admin Module – Danger Zone** | Factory Reset, VACUUM Optimization, Backup Download |
| **Teacher Module – 3‑Mode Attendance** | Manual ✔️ Roll No Entry ⌨️ Bulk Mark All 🧾 |
| **Student Module – Leave System** | Apply, Track, and View Leave Requests with Comments |
| **Predictive Risk Algorithm** | Calculates attendance % and flags “Critical Risk” students |

---

## 🧪 Testing Summary
| ID | Test Case | Expected Result | Status |
|----|------------|-----------------|--------|
| TC‑01 | Admin Login (Valid) | Redirect to Dashboard | ✅ Pass |
| TC‑02 | Admin Login (Invalid) | Show Error Message | ✅ Pass |
| TC‑03 | Bulk Attendance | All students marked Present | ✅ Pass |
| TC‑04 | Risk Alert | Red Box appears if < 75% | ✅ Pass |
| TC‑05 | Leave Application | Saved as Pending | ✅ Pass |
| TC‑06 | DB Factory Reset | All logs deleted | ✅ Pass |

---

## ⚙️ Installation & Setup
```bash
# Clone the repository
git clone https://github.com/HaroonKhurram/AT-PAS.git
cd AT-PAS

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Initialize database
flask shell
>>> from extensions import db
>>> db.create_all()

# Run the app
flask run
