# SpentWise

SpentWise is a modern, full-stack personal finance and AI-powered expense tracking application. Built with Django and styled with a clean, light-mode minimalist aesthetic, SpentWise helps users log expenses, manage category-specific budgets, and leverages Machine Learning to automatically classify spending and detect unusual transactional anomalies.

# Demo <img width="1180" height="544" alt="Screenshot 2026-05-18 071230" src="https://github.com/user-attachments/assets/21d93294-da39-4c34-965d-2a3e6381154f" /> <img width="1282" height="614" alt="Screenshot 2026-05-18 071251" src="https://github.com/user-attachments/assets/bc04cdd2-2603-4a66-b61c-24b54e72f572" />

# Core Features

* Smart Dashboard & Metrics:** Real-time financial health summaries, including flagged anomalies, total spending vs. budget caps, and dynamic percentage trackers.
* AI Category Classification:** Automated categorization of new expense text descriptions using an embedded NLP pipeline (`TfidfVectorizer` + `LogisticRegression`).
* Machine Learning Anomaly Detection:** Real-time scanning of transaction histories utilizing an Isolation Forest and statistical pipeline to flag unusual deviations ($z$-score analysis).
* Interactive Controls:** Expandable risk cards detailing anomaly breakdowns, allowing users to instantly append context notes or dismiss flags seamlessly.
* Budget & Limits Management:** Dynamic tracking of spending ceilings across custom-configured transaction categories.


# The Tech Stack 
* Backend:** Python 3.13, Django Framework
* Database:** PostgreSQL 
* Machine Learning:** Scikit-learn, NumPy, Pandas
* Frontend :** Tailwind CSS, JavaScript , Django Template Engine


## 📂 Project Structure Overview

├── config/                  # Core Django project configuration settings & routing
├── expense/                 # Main application directory
│   ├── expense/
│   │   └── form.py          # Django model forms for adding and updating expenses
│   ├── migrations/          # Database migration files tracking schema changes
│   ├── ml/                  # Machine Learning Engines
│   │   ├── anomaly.py       # Isolation Forest & z-score metric scanning logic
│   │   ├── spending_predictor.py  # Models & regression pipelines for tracking dynamic future spending
│   │   ├── train.py         # Automated model fitting and calibration tasks
│   │   └── predictor.py     # Expense description NLP category predictor pipeline
│   ├── models.py            # Database schemas (User, Expense, Category, Budget)
│   ├── views.py             # Route controllers handling clean HTML & JSON API streams
│   ├── url.py               # Local application endpoint routing configurations
│   └── templates/           # Server-side HTML layout views
│       └── expenses/
│           ├── base.html            # Core global shell layout (Navbar, footer, global styles)
│           ├── dashboard.html       # Visual landing hub featuring aggregate tracking states
│           ├── expense.html         # Main overview interface displaying interactive logs
│           ├── expense_detail.html  # Dedicated deep-dive layout for focused transaction metrics
│           ├── add_expense.html     # Secure interface form wrapper to log raw transactions
│           ├── edit_expense.html    # Modification prompt to safely adjust item attributes
│           ├── delete_expense.html  # Modals / confirmation gates protecting table mutations
│           ├── manage_category.html # Clean configuration view to organize custom fields
│           ├── set_budget.html      # Threshold manager interface for capping periodic targets
│           ├── anomaly.html         # Bright, responsive AI outlier analytics dashboard grid
│           ├── login.html           # Secure user portal authentication entry page
│           └── signup.html          # New account registration and baseline onboarding view
└── manage.py                # Django administrative execution utility


# 🔧 Installation & Setup

1. Clone the Repository
   git clone (https://github.com/Nejat-33/Spent-Wisely-Using-Django.git)

2. Configure Your Virtual Environment
 # Create the environment
    python -m venv .venv
 # Activate on Windows:
    .venv\Scripts\activate
 # Activate on macOS/Linux:
    source .venv/bin/activate

3. Install Required Packages
pip install django scikit-learn pandas numpy joblib

5. Run Migrations & Initialize Database
python manage.py makemigrations
python manage.py migrate

5. Launch the Development Server
python manage.py runserver


## 🔒 Application Endpoints & Routing Reference

SpentWise utilizes a structured routing architecture to map clean frontend user interfaces, standard database mutations, and backend machine learning utilities:

###  Core Application & CRUD Routes

| Endpoint | Method | Template / View Function | Description |
| :--- | :--- | :--- | :--- |
| `/` | `GET` | `dashboard.html` | Core landing hub displaying aggregate account tracking states. |
| `/expense/` | `GET` | `expense.html` | Interactive historical logs panel listing full transaction history. |
| `/expense_detail/<id>/` | `GET` | `expense_detail.html` | Focused granular breakdown layout for a specific transaction ID. |
| `/add/` | `GET` / `POST` | `add_expense.html` | Form handler to register and validate a new expense entry. |
| `/edit/<pk>/` | `GET` / `POST` | `edit_expense.html` | Record mutation gateway to securely modify transaction parameters. |
| `/delete/<pk>/` | `POST` | `delete_expense.html` | Drop-action execution path to remove an item permanently. |
| `/set_budget/` | `GET` / `POST` | `set_budget.html` | Form interface for mapping and adjusting ceiling budget caps. |
| `/manage_category/` | `GET` / `POST` | `manage_category.html` | Clean panel layout to register, read, or manage custom spending fields. |

###  Intelligent Machine Learning & Analytics Pipeline Endpoints

| Endpoint | Method | Type | Description |
| :--- | :--- | :--- | :--- |
| `/anomalies/` | `GET` | **HTML Page** | Renders the bright, minimalist AI outlier tracking interface canvas. |
| `/anomalies/api/` | `GET` | **JSON API** | Streams live summary metrics and statistical anomaly datasets. |
| `/anomalies/retrain/` | `POST` | **JSON API** | Triggers an asynchronous training sweep to adjust Isolation Forest limits. |
| `/predict-category/` | `POST` | **JSON API** | Passes expense context strings to NLP pipeline for auto-classification. |
| `/weekly-prediction/` | `GET` / `POST` | **JSON API** | Generates future periodic financial velocity forecasts via regression models. |

###  Session & Access Management

| Endpoint | Method | Authentication Target | Functionality |
| :--- | :--- | :--- | :--- |
| `/login/` | `GET` / `POST` | `expenses/login.html` | Authenticates sessions (redirects active users straight to dashboard). |
| `/logout/` | `POST` | *System Action* | Destroys current session token and routes cleanly back to `/login/`. |
| `/signup/` | `GET` / `POST` | `expenses/signup.html` | Provisions a new profile and configures a pristine user ledger database entry. |
