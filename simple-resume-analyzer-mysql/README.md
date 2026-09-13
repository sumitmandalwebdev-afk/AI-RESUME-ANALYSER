# ResumeIQ — Local MySQL Version

**Sirf yeh use hota hai:**
- HTML + CSS + Vanilla JS (frontend)
- Python Flask (backend)
- **Local MySQL** (database)
- Local folder `uploads/` (PDF storage)
- OpenAI-compatible AI (Groq free recommended)

Koi cloud account (Supabase) nahi chahiye.

---

## Folder structure

```
simple-resume-analyzer-mysql/
├── app.py              ← Poora backend
├── requirements.txt
├── .env.example
├── README.md
├── sql/schema.sql      ← MySQL tables
├── uploads/            ← PDFs yahan save hote hain (auto banega)
├── templates/          ← HTML pages
└── static/
    ├── css/style.css
    └── js/main.js
```

---

## STEP-BY-STEP SETUP (detail me)

### STEP 1 — MySQL start karo

**Windows (MySQL Installer se install kiya ho):**
1. Start Menu → **MySQL 8.0 Command Line Client** kholo
   (password maangega jo install time set kiya tha)
2. Ya Services me jaake **MySQL80** service Running hai confirm karo

**Agar MySQL Workbench use karte ho:**
- Workbench kholo → apne connection pe click karo

---

### STEP 2 — Database + tables banao

MySQL me yeh SQL chalao (schema.sql ka content):

**Option A — Command Line:**
```bash
mysql -u root -p < sql/schema.sql
```
(password daalo jab maange)

**Option B — MySQL Workbench / phpMyAdmin:**
1. `sql/schema.sql` file kholo
2. Pura content copy karo
3. Workbench me naya Query tab → paste → ⚡ Execute

Successfully run hone ke baad `resume_iq` database ban jayega + 2 tables.

---

### STEP 3 — Free AI key lo (Groq recommended)

1. Browser me jao: https://console.groq.com
2. Free account banao (Google se login chalega)
3. **API Keys** → Create API Key
4. Key copy kar lo (ek baar dikhegi)

Groq free me bahut strong model milta hai (`llama-3.3-70b-versatile`).

---

### STEP 4 — Project setup

```bash
# 1. Zip extract karo, folder me jao
cd simple-resume-analyzer-mysql

# 2. Virtual environment (recommended)
python -m venv venv

# Windows:
venv\Scripts\activate

# Mac / Linux:
source venv/bin/activate

# 3. Packages install
pip install -r requirements.txt
```

---

### STEP 5 — `.env` file banao

```bash
# Windows (PowerShell / CMD):
copy .env.example .env

# Mac / Linux:
cp .env.example .env
```

Ab `.env` file Notepad se kholo aur values daalo:

```
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=tumhara_mysql_password_yahan
MYSQL_DATABASE=resume_iq

OPENAI_API_KEY=gsk_xxxxxxxxxxxx          ← Groq key
OPENAI_BASE_URL=https://api.groq.com/openai/v1
OPENAI_MODEL=llama-3.3-70b-versatile

FLASK_SECRET_KEY=kuch-bhi-random-likh-do-123
FLASK_DEBUG=1
```

**Important:**
- `MYSQL_PASSWORD` = jo password MySQL install time set kiya tha
- Agar password blank hai to `MYSQL_PASSWORD=` (khali chhod do)

---

### STEP 6 — App chalao

```bash
python app.py
```

Browser me kholo:

**http://127.0.0.1:5000**

---

### STEP 7 — Pehla user + Admin

1. Site pe **Login / Signup** → naya account banao
2. Admin banane ke liye MySQL me yeh chalao:

```sql
USE resume_iq;
UPDATE users SET is_admin = 1 WHERE email = 'tumhara@email.com';
```

Ab logout + login karo → header me **Admin** link dikhega.

---

## Features

- Signup / Login (local)
- PDF upload (drag & drop) — max 5 MB
- Optional Job Description
- AI ATS score (0–100)
- Section-wise scores
- Strengths / Weaknesses
- Missing keywords
- Suggestions
- History + Delete
- Admin dashboard (stats)

---

## Common problems & solutions

| Problem | Solution |
|---------|----------|
| `Access denied for user 'root'` | `.env` me sahi password daalo |
| `Unknown database 'resume_iq'` | `schema.sql` run nahi hua — dobara chalao |
| `ModuleNotFoundError` | `venv` activate karke `pip install -r requirements.txt` |
| PDF se text nahi aa raha | Scanned/image PDF mat use karo — text-based PDF chahiye |
| AI error / 401 | Groq key sahi hai? `OPENAI_BASE_URL` sahi hai? |
| Port already in use | `app.py` me port change karo ya dusra process band karo |

---

## Files ka short explanation (viva)

| File | Kaam |
|------|------|
| `app.py` | Flask routes, MySQL queries, PDF extract, AI call |
| `sql/schema.sql` | Database + tables create karta hai |
| `templates/*.html` | Saari web pages |
| `static/css/style.css` | Design + animations |
| `static/js/main.js` | Toast, logout, helpers |
| `uploads/` | Uploaded PDFs yahan save hote hain |
| `.env` | Passwords + API keys (git me mat daalna) |

---

Bas itna hi. Koi step pe atak jao to message bhej dena.
