# AI Resume Analyser

An AI-powered web application that analyzes resumes and provides useful insights to help users improve their resumes and prepare for job opportunities.

## 🚀 Features

* 🔐 User Registration & Login
* 📄 Resume Upload
* 🤖 AI-powered Resume Analysis
* 📊 Resume Score & Analysis
* 💡 Skills and Resume Improvement Suggestions
* 📜 Analysis History
* 👨‍💼 Admin Dashboard
* 🗄️ MySQL Database
* 🔒 Secure environment variable configuration
* 📱 Responsive Web Interface

## 🛠️ Tech Stack

### Frontend

* HTML
* CSS
* JavaScript

### Backend

* Python
* Flask

### Database

* MySQL

### AI

* OpenAI API

### Other Tools

* PyMySQL
* PyPDF
* python-dotenv
* Gunicorn

## 📂 Project Structure

```text
AI-RESUME-ANALYSER/
│
├── sql/
│   └── schema.sql
│
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       ├── main.js
│       └── mascot.js
│
├── templates/
│   ├── admin.html
│   ├── analysis.html
│   ├── base.html
│   ├── dashboard.html
│   ├── history.html
│   ├── index.html
│   └── login.html
│
├── uploads/
│
├── app.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/sumitmandalwebdev-afk/AI-RESUME-ANALYSER.git
cd AI-RESUME-ANALYSER
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file and add your configuration:

```env
MYSQL_HOST=
MYSQL_PORT=
MYSQL_USER=
MYSQL_PASSWORD=
MYSQL_DATABASE=

OPENAI_API_KEY=
OPENAI_BASE_URL=
OPENAI_MODEL=

FLASK_SECRET_KEY=
FLASK_DEBUG=False
```

> Never upload your `.env` file or API keys to GitHub.

### 5. Setup MySQL

Create a MySQL database and run:

```text
sql/schema.sql
```

Then add your database credentials to the `.env` file.

### 6. Run the application

```bash
python app.py
```

Open your browser and visit:

```text
http://127.0.0.1:5000
```

## ☁️ Deployment

The application can be deployed using a Python-compatible hosting platform such as Render.

For production deployment, use:

```bash
gunicorn app:app
```

Make sure all required environment variables and the online MySQL database are configured on the hosting platform.

## 🔐 Security

* API keys are stored using environment variables.
* Database credentials are not included in the source code.
* `.env` is excluded from Git using `.gitignore`.

## 🎯 Purpose

The goal of this project is to build a practical AI-based resume analysis system while working with:

* Python Flask
* MySQL
* AI APIs
* Authentication
* File handling
* Database management
* Web development
* Cloud deployment

## 👨‍💻 Author

**Sumit Mandal**

B.Tech CSE Student | Python & Full Stack Web Development

---

⭐ If you find this project useful, consider giving the repository a star.
