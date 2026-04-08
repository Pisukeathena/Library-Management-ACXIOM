# 📚 Library Management System

A full-stack Library Management System built with **Python (Flask)**, **HTML**, **CSS**, and **SQLite**. Developed as a task for Acxiom Drive 2026 (ERP domain).

---

## 🚀 Features

- 🔐 **Authentication** — Login / Register with role-based access (Admin / Librarian / Member)
- 📚 **Book Management** — Add, edit, delete, search books with category tagging
- 👥 **Member Management** — Register members, set membership type and expiry
- 🔄 **Issue & Return** — Issue books to members, track due dates, handle returns
- 💰 **Fine Calculation** — Auto-calculate ₹5/day overdue fines, mark as paid
- 📊 **Reports & Analytics** — Dashboard KPIs, most borrowed books, active members
- 🏷️ **Categories** — Manage book categories

---

## 🛠️ Tech Stack

| Layer     | Technology                    |
|-----------|-------------------------------|
| Frontend  | HTML5, CSS3 (custom dark theme) |
| Backend   | Python 3.10+, Flask 3.0       |
| Database  | SQLite (via SQLAlchemy ORM)   |
| Auth      | Flask-Login + Werkzeug        |

---

## ⚙️ Setup & Run Locally

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/library-management-system.git
cd library-management-system
```

### 2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the app
```bash
python app.py
```

### 5. Open in browser
```
http://127.0.0.1:5000
```

### 6. Default login credentials
```
Email:    admin@library.com
Password: admin123
```

---

## 📁 Project Structure

```
library_ms/
├── app.py               # Main Flask app (routes + models)
├── config.py            # Configuration
├── requirements.txt     # Python dependencies
├── library.db           # SQLite database (auto-created)
├── templates/
│   ├── base.html        # Shared layout with sidebar
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── books.html
│   ├── add_book.html
│   ├── members.html
│   ├── add_member.html
│   ├── transactions.html
│   ├── issue_book.html
│   ├── reports.html
│   └── categories.html
└── static/
    └── css/
        └── style.css    # Dark theme stylesheet
```

---

## 📸 Pages

- **Dashboard** — KPI cards, recent transactions, quick actions
- **Books** — Full catalogue with search, availability indicator
- **Members** — Member registry with membership type and status
- **Transactions** — Issue/Return tracking with fine management
- **Reports** — Analytics with bar charts for popular books and active members
- **Categories** — Manage book classification

---

## 👩‍💻 Developer

Built by **Harsh Gupta** | Terna Engineering College |

---

## 📄 License
MIT
