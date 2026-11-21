# AcxiomCRM – Customer Relationship Management System

A web-based Customer Relationship Management (CRM) system developed using **Python, FastAPI, MongoDB, HTML, CSS, JavaScript, and Bootstrap**.

AcxiomCRM helps organizations manage customers, track potential leads, monitor sales opportunities, schedule follow-ups, record activities, and analyze business performance through a centralized dashboard.

---

## 1. Project Overview

AcxiomCRM is designed to simplify customer relationship management through a role-based system with centralized data storage and reporting.

The application provides three user roles: Admin, Manager, and Sales Executive. Each role has different access permissions according to its responsibilities.

### Key Objectives

- Centralize customer information.
- Manage and track potential customers (leads).
- Monitor sales opportunities and pipeline values.
- Schedule and manage customer follow-ups.
- Record business activities.
- Provide role-based access control.
- Maintain audit logs of important operations.
- Generate reports and visualize CRM performance.

---

## 2. Technology Stack

| Component | Technology |
|---|---|
| Frontend | HTML5, CSS3, JavaScript |
| UI Framework | Bootstrap 5 |
| Backend | Python, FastAPI |
| Database | MongoDB Atlas |
| Database Driver | PyMongo |
| Authentication | JWT |
| Password Hashing | Argon2 |
| Data Validation | Pydantic |
| Data Visualization | Chart.js |
| Environment Configuration | Python-dotenv |
| API Documentation | Swagger UI |

---

## 3. Main Features and Modules

### 3.1 Authentication
- User login and logout.
- JWT-based authentication.
- Password hashing.
- Role-based authorization.

### 3.2 Dashboard
- Total customers.
- Total leads.
- Open opportunities.
- Sales pipeline value.
- Weighted pipeline value.
- Won and lost opportunities.
- Pending follow-ups.
- Visual charts.

### 3.3 Customer Management
- Add new customers.
- View customer records.
- Update customer information.
- Search customers.
- Deactivate customer records.
- Prevent duplicate email addresses and phone numbers.

### 3.4 Lead Management
- Create and manage leads.
- Record lead contact information.
- Track lead sources.
- Manage lead status.
- Record expected sales value.
- Update and track lead progress.

### 3.5 Opportunity Management
- Create sales opportunities.
- Associate opportunities with customers.
- Track opportunity stages.
- Record opportunity amounts.
- Set expected closing dates.
- Calculate weighted pipeline values.

**Weighted Pipeline Formula:**

Weighted Value = Opportunity Amount × Probability / 100

### 3.6 Follow-up Management
- Schedule customer follow-ups.
- Manage follow-up types: Call, Meeting, Email, Task.
- Track follow-up status.
- Record follow-up remarks.

### 3.7 Activity Management
- Record calls, meetings, emails, and tasks.
- Associate activities with customers or leads.
- Maintain activity descriptions and dates.

### 3.8 User Management
- Create new users.
- Assign user roles.
- Update user information.
- Activate or deactivate accounts.

### 3.9 Audit Logs
- Record important system operations.
- Track user actions.
- Maintain records of changes and administrative activities.

### 3.10 Reports and Analytics
- CRM performance overview.
- Customer and lead statistics.
- Opportunity distribution.
- Sales pipeline summary.
- Weighted pipeline analysis.
- Chart-based visualization.

---

## 4. User Roles and Permissions

| Feature | Admin | Manager | Sales Executive |
|---|:---:|:---:|:---:|
| Dashboard | Yes | Yes | Yes |
| Customer Management | Yes | Yes | Assigned Records |
| Lead Management | Yes | Yes | Assigned Records |
| Opportunity Management | Yes | Yes | Assigned Records |
| Follow-ups | Yes | Yes | Assigned Records |
| Activities | Yes | Yes | Assigned Records |
| User Management | Yes | No | No |
| Audit Logs | Yes | No | No |
| Reports | Yes | Yes | No |

---

## 5. Project Structure

```text
AcxiomCRM/
│
├── backend/
│   ├── routes/
│   │   ├── auth.py
│   │   ├── customers.py
│   │   ├── leads.py
│   │   ├── opportunities.py
│   │   ├── followups.py
│   │   ├── activities.py
│   │   ├── dashboard.py
│   │   ├── audit.py
│   │   └── users.py
│   │
│   └── utils/
│       ├── security.py
│       ├── dependencies.py
│       └── audit.py
│
├── database/
│   ├── connection.py
│   ├── init_db.py
│   ├── seed_users.py
│   ├── seed_demo_customers.py
│   └── seed_demo_data.py
│
├── frontend/
│   ├── pages/
│   │   ├── login.html
│   │   ├── dashboard.html
│   │   ├── customers.html
│   │   ├── leads.html
│   │   ├── opportunities.html
│   │   ├── followups.html
│   │   ├── activities.html
│   │   ├── users.html
│   │   ├── audit.html
│   │   └── reports.html
│   │
│   ├── css/
│   │   └── style.css
│   │
│   └── js/
│       ├── login.js
│       ├── dashboard.js
│       ├── customers.js
│       ├── leads.js
│       ├── opportunities.js
│       ├── followups.js
│       ├── activities.js
│       ├── users.js
│       ├── audit.js
│       └── reports.js
│
├── main.py
├── config.py
├── requirements.txt
├── .env
├── .gitignore
└── README.md
```

---

## 6. Installation and Setup

### Prerequisites

Install the following before running the project:

- Python 3.10 or later.
- MongoDB Atlas account.
- Git.
- Visual Studio Code.

### Step 1: Clone the Repository

```bash
git clone <YOUR_REPOSITORY_URL>
cd AcxiomCRM
```

Alternatively, open the existing project folder in VS Code.

### Step 2: Create a Virtual Environment

```bash
python -m venv venv
```

Activate it using Git Bash:

```bash
source venv/Scripts/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure MongoDB

Create a MongoDB Atlas cluster and configure the database connection.

Create a `.env` file in the project root:

```env
MONGODB_URI=your_mongodb_connection_string
DATABASE_NAME=AcxiomCRM
```

Replace the placeholder with your actual MongoDB connection string.

**Important:** Never upload your `.env` file or database credentials to a public GitHub repository.

### Step 5: Initialize the Database

```bash
python -m database.init_db
```

### Step 6: Create Initial Users

```bash
python -m database.seed_users
```

### Step 7: Add Demonstration Data (Optional)

Add sample customers:

```bash
python -m database.seed_demo_customers
```

Add sample leads, opportunities, follow-ups, and activities:

```bash
python -m database.seed_demo_data
```

These scripts use fictional demonstration records.

### Step 8: Run the Application

```bash
python -m uvicorn main:app --reload
```

---

## 7. Accessing the Application

After starting the server, open the following URLs:

| Resource | URL |
|---|---|
| Login Page | http://127.0.0.1:8000/ |
| Dashboard | http://127.0.0.1:8000/dashboard |
| Customers | http://127.0.0.1:8000/customers |
| Leads | http://127.0.0.1:8000/leads |
| Opportunities | http://127.0.0.1:8000/opportunities |
| Follow-ups | http://127.0.0.1:8000/followups |
| Activities | http://127.0.0.1:8000/activities |
| User Management | http://127.0.0.1:8000/users |
| Audit Logs | http://127.0.0.1:8000/audit |
| Reports | http://127.0.0.1:8000/reports |
| API Documentation | http://127.0.0.1:8000/docs |

---

## 8. REST API Endpoints

| Module | Endpoint | Methods |
|---|---|---|
| Authentication | `/api/auth/login` | POST |
| Authentication | `/api/auth/me` | GET |
| Customers | `/api/customers/` | GET, POST |
| Customers | `/api/customers/{customer_id}` | GET, PUT, DELETE |
| Leads | `/api/leads/` | GET, POST |
| Leads | `/api/leads/{lead_id}` | GET, PUT, DELETE |
| Opportunities | `/api/opportunities/` | GET, POST |
| Opportunities | `/api/opportunities/{opportunity_id}` | GET, PUT, DELETE |
| Follow-ups | `/api/followups/` | GET, POST |
| Follow-ups | `/api/followups/{followup_id}` | PUT |
| Activities | `/api/activities/` | GET, POST |
| Activities | `/api/activities/{activity_id}` | PUT |
| Users | `/api/users/` | GET, POST |
| Users | `/api/users/{user_id}` | PUT, DELETE |
| Dashboard | `/api/dashboard/stats` | GET |
| Audit Logs | `/api/audit/` | GET |

The API documentation is available through FastAPI Swagger UI at `/docs`.

---

## 9. Database Collections

The application uses MongoDB collections for storing CRM data.

- `users`
- `roles`
- `customers`
- `leads`
- `opportunities`
- `followups`
- `activities`
- `audit_logs`

---

## 10. Security

The application incorporates the following security mechanisms:

- JWT-based authentication.
- Argon2 password hashing.
- Role-based access control.
- Protected API endpoints.
- Server-side validation using Pydantic.
- MongoDB database integration.
- Audit logging of important operations.

Security controls should be tested before production deployment.

---

## 11. Future Improvements

Potential future enhancements include:

- CSV and Excel bulk customer import.
- Advanced filtering and date-based reports.
- Email notifications and automated reminders.
- Customer interaction history.
- Improved audit history with before-and-after values.
- Sales forecasting and predictive analytics.
- Advanced analytics dashboards.
- Automated lead scoring.

---

## 12. Project Information

**Project Name:** AcxiomCRM  
**Project Type:** Web-Based Customer Relationship Management System  
**Backend:** Python – FastAPI  
**Frontend:** HTML, CSS, JavaScript, Bootstrap  
**Database:** MongoDB Atlas  
**API Documentation:** FastAPI Swagger UI

---

## 13. License

This project is developed for educational and demonstration purposes.