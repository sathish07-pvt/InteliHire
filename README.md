# IntelliHire — AI Mock Interview Platform
> *Practice Smarter. Interview Better.*  
> **B.Tech Information Technology Individual Capstone Project**

---

## 1. Project Overview

**IntelliHire** is an intelligent, evidence-based, adaptive web application designed to prepare engineering students for technical campus placements and corporate hiring. 

Unlike static quiz websites or ordinary MCQ portals, IntelliHire replicates authentic technical and HR interview rounds:
1. **Dynamic Question Delivery:** Delivers questions one-by-one from company-specific question banks or an autonomous synthesis engine.
2. **Offline NLP Answer Evaluation:** Leverages `scikit-learn`'s **TF-IDF Vector Space Model**, **Cosine Similarity**, and **Lexical Keyword Coverage** to evaluate candidate explanations against benchmark model answers.
3. **Adaptive Follow-Up Selection:** Adjusts question difficulty in real time (Easy &rarr; Medium &rarr; Hard) based on previous answer scores, omitted technical concepts, and linked question bank chains.
4. **PyMuPDF Resume Analysis:** Parses PDF resumes to detect skills across programming languages, databases, and frameworks, providing personalized domain track recommendations.
5. **No Paid External AI APIs:** 100% self-contained, offline-capable, reproducible, and cost-free—ideal for college evaluation, project exhibitions, and viva defense.

---

## 2. System Architecture

```
+-----------------------------------------------------------------------------------+
|                                  USER / BROWSER                                   |
|   HTML5 + CSS3 (Glassmorphic Dark Theme) + Bootstrap 5 + JavaScript + Chart.js   |
+-----------------------------------------+-----------------------------------------+
                                          | HTTP / JSON Fetch
                                          v
+-----------------------------------------------------------------------------------+
|                                FLASK BACKEND ENGINE                               |
|   app.py (Application Factory) | Blueprints: Auth, Main, Resume, Interview, Admin |
+--------------------+--------------------+--------------------+--------------------+
                     |                    |                    |
                     v                    v                    v
+-------------------------+ +-------------------------+ +-------------------------+
|   RESUME PROCESSING     | |     HYBRID QUESTION     | |     NLP EVALUATION      |
|         SERVICE         | |    SELECTION ENGINE     | |         SERVICE         |
|  - PyMuPDF (fitz)       | |  Tier 1: Linked Followup| |  - scikit-learn TF-IDF  |
|  - Scanned PDF Detection| |  Tier 2: Company Bank   | |  - Cosine Similarity    |
|  - Skill Dictionary     | |  Tier 3: General Bank   | |  - Keyword Coverage %   |
|  - Track Recommendation | |  Tier 4: Local Synthesiz| |  - Concept Gap Analysis|
+-------------------------+ +-------------------------+ +-------------------------+
                     |                    |                    |
                     +--------------------+--------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|                                 DATABASE LAYER                                    |
|   Flask-SQLAlchemy ORM | Portable SQLite (Default) OR MySQL 8.0+ / MariaDB        |
|   Tables: users, resumes, user_skills, questions, interview_sessions, reports     |
+-----------------------------------------------------------------------------------+
```

---

## 3. Technology Stack

| Layer | Technologies Used |
| :--- | :--- |
| **Frontend** | HTML5, CSS3 (Modern Glassmorphic Dark UI), Bootstrap 5, Vanilla JavaScript, Chart.js, Bootstrap Icons |
| **Backend** | Python 3.11+, Flask 3.0, Flask Blueprints (Modular routing), Werkzeug Security |
| **Database** | Flask-SQLAlchemy 3.1, SQLite (Plug-and-play local) & MySQL 8.0+ (Production relational schema via PyMySQL) |
| **AI / NLP** | `scikit-learn` (TF-IDF Vectorizer & Cosine Similarity), NumPy, Rule-Based Concept Matchers |
| **Resume Extraction** | `PyMuPDF` (`fitz`) for PDF text parsing & Scanned Document detection |
| **Testing** | `pytest` 8.2 (14 automated unit, integration, and security tests) |

---

## 4. Key Application Features

### A. Authentication & Role-Based Access Control (RBAC)
- Secure user registration with email regex validation and duplicate prevention.
- Passwords hashed using `werkzeug.security` (PBKDF2-SHA256).
- Role segregation: **Student** (default role; cannot escalate privileges via form tampering) and **Administrator**.
- Protected routes using custom `@login_required` and `@admin_required` decorators.
- Automatic seeding of initial system administrator account.

### B. Company-Specific Practice Banks
- Practice questions curated across:
  - **TCS** (OOP, Java 8 interfaces, HR / Wings1 growth)
  - **Infosys** (Python mutability, Pass-by-assignment)
  - **Zoho** (Data Structures, Floyd's Cycle Detection & Loop Removal)
  - **Accenture** (SQL WHERE vs HAVING, Joins)
  - **Amazon** (DBMS ACID Properties, Concurrency Isolation Levels, Leadership Principles)
  - **Google** (Balanced Trees, Red-Black / AVL trees)
  - **General** (JavaScript Event Loop, CSS Box Model, Spring Boot IoC, Recursion, HR STAR method)

### C. 4-Tier Hybrid Question Selection
When a candidate requests a question:
1. **Tier 1:** Linked follow-up question in the question bank (deep-dives into previous topic).
2. **Tier 2:** Unused question from the target company's question bank matching skill and adapted difficulty.
3. **Tier 3:** Unused question from the general question bank matching skill and adapted difficulty.
4. **Tier 4:** Dedicated template synthesizer (`QuestionGenerationService`) ensuring interviews never crash or run out of material.

### D. Evidence-Based NLP Evaluation Formula
The scoring formula is transparent and mathematically grounded:
$$\text{Final Score} = (\text{Cosine Sim} \times 0.35) + (\text{Keyword Coverage} \times 0.45) + (\text{Completeness} \times 0.20) + \text{Mastery Bonus}$$
- **TF-IDF Cosine Similarity:** Evaluates semantic vector alignment between candidate answer and benchmark answer.
- **Keyword Coverage:** Measures inclusion of critical architectural terms.
- **Omitted Concepts:** Identifies missing keywords for targeted revision.
- *Honest Viva Disclaimer:* The system honestly discloses that acoustic vocal analysis and computer-vision facial tracking are not simulated.

### E. PDF Resume Skill Parser
- Safe upload handling with filename sanitization and 5MB size limit.
- Resumes are stored in a protected private directory outside public static assets.
- Automatically flags image-scanned PDFs where OCR would be required, without claiming false OCR extraction.
- Candidate skill tagging: students can correct, add, or remove detected competencies.

### F. Performance Report & Interactive Charts
- Overall score (/100) and Placement Readiness percentage.
- Question-by-question score bar graph via Chart.js.
- Score progression trend line chart across sessions.
- Skill competency radar / distribution chart.
- Side-by-side answer inspection accordion displaying candidate response, benchmark answer, similarity %, coverage %, and feedback.
- One-click print / export to PDF.

---

## 5. Folder Structure

```
IntelliHire/
├── app.py                      # Flask Application Factory & seed runner
├── config.py                   # Configuration for SQLite, MySQL & uploads
├── requirements.txt            # Python dependencies
├── schema.sql                  # MySQL relational schema script
├── .env.example                # Sample environment variables
├── .env                        # Local environment configuration
├── .gitignore                  # Git ignore rules
├── README.md                   # Complete documentation
│
├── models/                     # SQLAlchemy Models
│   ├── __init__.py             # db instance & model exports
│   ├── user.py                 # User (Student & Admin)
│   ├── resume.py               # Resume & UserSkill
│   ├── question.py             # Question, Company, SkillCategory
│   └── interview.py            # InterviewSession, InterviewQuestion, PerformanceReport
│
├── routes/                     # Modular Flask Blueprints
│   ├── __init__.py             # Blueprint exports
│   ├── auth.py                 # Register, Login, Logout, RBAC decorators
│   ├── main.py                 # Landing page, Dashboard, History, Profile
│   ├── resume.py               # PDF Upload, PyMuPDF parsing, Skill tags
│   ├── interview.py            # Setup, Cockpit, Submit, Evaluation, Report
│   └── admin.py                # Question CRUD, User directory, Re-seed
│
├── services/                   # Business Logic & AI Services
│   ├── __init__.py
│   ├── resume_service.py       # PyMuPDF parser & skill dictionary matcher
│   ├── nlp_evaluation_service.py # TF-IDF & keyword scoring formula
│   ├── question_selection_service.py # 4-tier selection & difficulty adaptation
│   ├── question_generation_service.py # Autonomous template generator
│   └── report_service.py       # Performance aggregation & recommendation engine
│
├── templates/                  # Jinja2 HTML Templates
│   ├── base.html               # Master layout with responsive navbar & footer
│   ├── index.html              # SaaS Landing Page
│   ├── auth/
│   │   ├── login.html          # Login screen with viva demo credentials
│   │   └── register.html       # Student registration
│   ├── dashboard/
│   │   ├── dashboard.html      # KPI metrics & Chart.js visualizations
│   │   ├── history.html        # Comprehensive interview session logs
│   │   └── profile.html        # Profile & verified skill tags
│   ├── resume/
│   │   └── analyze.html        # Resume parser, OCR notice & skill corrections
│   ├── interview/
│   │   ├── setup.html          # Company, track, difficulty configuration
│   │   ├── session.html        # Live interview cockpit with evaluation modal
│   │   └── report.html         # Evidence-based report & printable breakdown
│   ├── admin/
│   │   ├── dashboard.html      # Admin overview & system counters
│   │   ├── questions.html      # Question bank repository & filters
│   │   ├── question_form.html  # Create/Edit question with follow-up link
│   │   └── users.html          # Student directory
│   └── errors/
│       ├── 403.html            # Access restricted
│       ├── 404.html            # Not found
│       ├── 413.html            # File size limit exceeded (>5MB)
│       └── 500.html            # Server exception
│
├── static/
│   ├── css/
│   │   └── styles.css          # Glassmorphic dark UI stylesheet
│   └── js/
│       ├── main.js             # Alert auto-dismiss, tooltip initializers
│       └── interview.js        # Live timer, word counter, submission fetch
│
├── data/
│   └── seed_questions.json     # Practice questions across companies & skills
│
├── uploads/
│   └── resumes/                # Private resume storage (protected from web access)
│
└── tests/                      # Automated Test Suite (Pytest)
    ├── __init__.py
    ├── conftest.py             # Fixtures for in-memory SQLite & test clients
    ├── test_auth.py            # Auth, duplicate email, RBAC
    ├── test_nlp.py             # TF-IDF, empty answer, off-topic detection
    ├── test_interview_engine.py# Adaptive selection, workflow, report
    └── test_resume.py          # PyMuPDF extraction & scanned PDF handling
```

---

## 6. Installation & Execution Guide

### Prerequisites
- Python 3.10, 3.11, or 3.12 installed on Windows.
- Git (optional).
- MySQL or XAMPP (optional; the platform runs out-of-the-box on SQLite).

### Step 1: Open PowerShell in Project Directory
```powershell
cd c:\Users\sathish\OneDrive\Desktop\IntelliHire
```

### Step 2: Activate Virtual Environment
```powershell
.\venv\Scripts\Activate.ps1
```
*(If script execution is disabled in PowerShell, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` first).*

### Step 3: Install Dependencies (Already Pre-installed)
```powershell
pip install -r requirements.txt
```

### Step 4: Run the Application
```powershell
python app.py
```

### Step 5: Open Browser
Navigate to:
```
http://127.0.0.1:5000
```

---

## 7. Connecting to MySQL (Optional for Viva Submission)

The application includes built-in dual database support. By default, it runs instantly on portable SQLite. To connect to MySQL:

1. Open XAMPP Control Panel and start **MySQL** (or start your local MySQL Windows Service).
2. Create the database:
   ```sql
   CREATE DATABASE intellihire CHARACTER SET utf8mb4;
   ```
   *(Alternatively, run the provided `schema.sql` file in phpMyAdmin or MySQL Workbench).*
3. Open the `.env` file in the project folder and modify:
   ```env
   DB_TYPE=mysql
   MYSQL_HOST=localhost
   MYSQL_PORT=3306
   MYSQL_USER=root
   MYSQL_PASSWORD=your_mysql_password
   MYSQL_DB=intellihire
   ```
4. Start the application:
   ```powershell
   python app.py
   ```
   Flask-SQLAlchemy will automatically connect to MySQL and seed initial administrator accounts and questions.

---

## 8. Demo & Viva Accounts

| Role | Email | Password | Access Level |
| :--- | :--- | :--- | :--- |
| **System Admin** | `admin@intellihire.com` | `Admin@12345` | Full access to Admin Panel, Question CRUD, User directory |
| **Student** | Any registered email (or click **Get Started Free**) | Registered password | Dashboard, Resume Analysis, Practice Interviews, Reports |

---

## 9. Running the Automated Test Suite

To verify system stability and demonstrate test-driven engineering during your project viva:

```powershell
.\venv\Scripts\python.exe -m pytest -v
```

**Expected Result:**
```
tests/test_auth.py::test_user_registration_success PASSED
tests/test_auth.py::test_registration_duplicate_email_prevented PASSED
tests/test_auth.py::test_login_and_logout PASSED
tests/test_auth.py::test_student_cannot_access_admin_portal PASSED
tests/test_auth.py::test_admin_can_access_admin_portal PASSED
tests/test_interview_engine.py::test_adaptive_difficulty_progression PASSED
tests/test_interview_engine.py::test_question_generator_safety PASSED
tests/test_interview_engine.py::test_full_interview_workflow PASSED
tests/test_interview_engine.py::test_report_generation PASSED
tests/test_nlp.py::test_empty_answer_handling PASSED
tests/test_nlp.py::test_high_quality_answer_evaluation PASSED
tests/test_nlp.py::test_off_topic_answer_evaluation PASSED
tests/test_resume.py::test_resume_skill_dictionary_extraction PASSED
tests/test_resume.py::test_resume_scanned_or_empty_detection PASSED

============================= 14 passed in 1.17s =============================
```

---

## 10. Viva Defense Cheat Sheet (Questions & Answers)

### Q1: Why use TF-IDF and Cosine Similarity instead of an OpenAI/ChatGPT API?
> **Answer:** 
> 1. **Offline Autonomy & Cost:** Commercial LLM APIs require recurring payments, internet connectivity, and API keys that can expire or fail during evaluation.
> 2. **Reproducibility & Determinism:** TF-IDF Cosine Similarity is a transparent, deterministic mathematical vector space model from information retrieval. It produces measurable, explainable scores that examiners can verify.
> 3. **Latency:** Local TF-IDF computation takes under 20 milliseconds, providing instant feedback without network latency.

### Q2: How does the Adaptive Interviewing mechanism work?
> **Answer:** 
> After each response, the candidate's score is evaluated:
> - **Score &ge; 80/100:** The engine promotes the difficulty to the next tier (e.g., Easy &rarr; Medium &rarr; Hard) or triggers a linked advanced follow-up question.
> - **Score 50–79/100:** The engine maintains the current difficulty level.
> - **Score < 50/100:** The engine dials back difficulty to a foundational concept or focuses on omitted keywords.
> - Furthermore, the 4-tier selection hierarchy ensures company questions take precedence over general questions, with a template synthesis engine preventing crashes if bank items are exhausted.

### Q3: How is resume extraction handled safely?
> **Answer:** 
> Using `PyMuPDF` (`fitz`), text streams are extracted directly from PDF binary objects without executing active content. Uploaded files are renamed using `secure_filename` with unique user prefixes, verified against a 5MB size ceiling, and kept in a protected private directory outside the web root to eliminate path traversal and arbitrary execution vulnerabilities. If a PDF contains only scanned bitmap images, the system explicitly informs the user that an OCR engine is required rather than simulating fake data.

### Q4: How is database security and privilege escalation prevented?
> **Answer:** 
> All passwords are cryptographically salted and hashed using PBKDF2-SHA256 (`generate_password_hash`). New user registrations are hardcoded to the `'student'` role on the backend—preventing attackers from tampering with HTML form inputs to gain administrative rights. Database operations use SQLAlchemy parameterized queries, preventing SQL injection.

---

## 11. Project Credit & License
Developed as an individual final-year capstone project for **B.Tech Information Technology**.  
Open for academic demonstration and placement training.
