# 🛡️ Software Design Inspection & Defect Tracker

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/framework-Flask-lightgrey.svg)](https://flask.palletsprojects.com/)
[![Database](https://img.shields.io/badge/database-SQLite-blueviolet.svg)](https://www.sqlite.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

An enterprise-grade, full-stack web application designed for **Software Quality Engineering & Assurance (SQA/SEQA)** teams. This platform automates software design inspections, streamlines formal architectural review checklists, tracks design defects, and provides real-time analytics with printable executive PDF reports.

---

## ✨ Key Features

- **🔐 Authentication & Role Management**: Secure user registration, authentication, session management, and role-based permissions (Admin, Lead Inspector, Inspector, Reviewer).
- **📁 Project Portfolio Management**: Organize design inspection assets across multiple software engineering projects with real-time status metrics.
- **📄 Document Upload & Version Control**: Manage architecture diagrams, design specifications, requirements documents, and version histories.
- **📋 Formal Design Inspection Checklist Workflow**: Execute structured inspection sessions using standardized checklists, scoring rules, and severity levels.
- **📌 Interactive Defect Tracking & Kanban**: Track design bugs and architectural flaws using list views and a drag-and-drop Kanban triage board.
- **📊 Analytics & Executive PDF Reports**: Dynamic charts powered by interactive frontend visualizations and downloadable executive PDF inspection summaries.
- **🔌 RESTful API Endpoints**: Scalable REST APIs for seamless integration with external dev tools and CI/CD pipelines.

---

## 🛠️ Technology Stack

| Layer | Technology / Library |
| :--- | :--- |
| **Backend** | Python 3, Flask, Flask-SQLAlchemy, Werkzeug |
| **Database** | SQLite (SQLAlchemy ORM) |
| **Frontend** | HTML5, Modern CSS3 (CSS Variables, Flexbox/Grid), Vanilla JavaScript |
| **Visualizations** | Canvas / SVG Dynamic Charts |
| **PDF Generation** | HTML-to-PDF Print Engine |

---

## 🚀 Getting Started

### Prerequisites

- Python `3.9` or higher
- `pip` (Python package manager)

### Installation & Setup

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/ashwinibarapatre28/Software-Design-Inspection-Tracker.git
   cd Software-Design-Inspection-Tracker
   ```

2. **Create and Activate Virtual Environment**:
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate

   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Seed Initial Database (Optional)**:
   ```bash
   python seed.py
   ```

5. **Run the Application**:
   ```bash
   python app.py
   ```
   Access the dashboard at `http://127.0.0.1:5000`.

---

## 📂 Directory Structure

```text
SEQA Project/
├── app.py                  # Flask Application Entry Point
├── config.py               # Centralized Configuration & Settings
├── models.py               # SQLAlchemy Database Schemas & Models
├── seed.py                 # Initial Database Seeder Script
├── requirements.txt        # Python Dependencies
├── .gitignore              # Ignored Files & Folders
├── README.md               # Project Documentation
├── routes/                 # Application Blueprints & Controllers
│   ├── analytics.py        # Analytics & Metric Handlers
│   ├── api.py              # REST API Route Handlers
│   ├── auth.py             # Authentication & User Sessions
│   ├── dashboard.py        # Main Dashboard Overview
│   ├── defects.py          # Defect Tracking & Kanban Board
│   ├── documents.py        # Document Uploads & Versioning
│   ├── help.py             # System User Guide & FAQs
│   ├── inspections.py      # Inspection Session Workflows
│   ├── projects.py         # Project Management
│   ├── reports.py          # PDF & Executive Report Generators
│   ├── settings.py         # App & Profile Settings
│   └── team.py             # Team Member & Role Management
├── static/                 # Static Frontend Assets (CSS, JS, Uploads)
└── templates/              # Jinja2 HTML Templates
```

---

## 🌐 REST API Documentation

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/api/projects` | `GET` / `POST` | Retrieve all projects or create a new project |
| `/api/inspections` | `GET` / `POST` | List design inspection sessions or record a new inspection |
| `/api/defects` | `GET` / `POST` | List design defects or log a new defect |
| `/api/defects/<id>` | `GET` / `PUT` / `DELETE` | Retrieve, update status/priority, or delete a defect |
| `/api/stats` | `GET` | Get aggregated project quality metrics and defect counts |

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).
