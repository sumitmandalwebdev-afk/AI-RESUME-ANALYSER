"""
ResumeIQ — Local MySQL version
==============================
Stack: Flask + MySQL + pypdf + OpenAI-compatible API
No cloud, no Supabase. Everything local.
"""

import os
import json
import uuid
from datetime import datetime
from functools import wraps
from io import BytesIO

from flask import (
    Flask, render_template, request, jsonify,
    session, redirect, url_for
)
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
from pypdf import PdfReader
from openai import OpenAI
import pymysql
from pymysql.cursors import DictCursor

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret-change-me")

# ---------- MySQL connection helper ----------
def get_db():
    return pymysql.connect(
        host=os.getenv("MYSQL_HOST", "127.0.0.1"),
        port=int(os.getenv("MYSQL_PORT", 3306)),
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD", ""),
        database=os.getenv("MYSQL_DATABASE", "resume_iq"),
        charset="utf8mb4",
        cursorclass=DictCursor,
        autocommit=True,
    )

# ---------- AI client ----------
ai_client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
)
AI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

SECTION_NAMES = [
    "Contact", "Summary", "Experience", "Education",
    "Skills", "Projects", "Formatting"
]

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ============================================================
# Auth helpers
# ============================================================
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("user_id"):
            return redirect(url_for("login_page"))
        return f(*args, **kwargs)
    return decorated


def current_user():
    return {
        "id": session.get("user_id"),
        "email": session.get("email"),
        "full_name": session.get("full_name"),
        "is_admin": session.get("is_admin", False),
    }


# ============================================================
# PDF extraction
# ============================================================
def extract_pdf_text(file_bytes: bytes) -> str:
    reader = PdfReader(BytesIO(file_bytes))
    pages = []
    for page in reader.pages:
        text = page.extract_text() or ""
        pages.append(text)
    full = "\n".join(pages)
    full = "\n".join(line.strip() for line in full.splitlines() if line.strip())
    return full


# ============================================================
# AI Analysis
# ============================================================
def run_ai_analysis(resume_text: str, job_description: str | None) -> dict:
    has_jd = bool(job_description and job_description.strip())

    system_prompt = f"""You are an expert ATS (Applicant Tracking System) auditor and senior recruiter.
Evaluate the resume rigorously and return ONLY valid JSON (no markdown).

Rules:
- ats_score: integer 0-100 overall ATS compatibility and quality.
- job_match_score: integer 0-100 how well resume matches the job description; null if no JD given.
- sections: exactly these 7 names in order: {", ".join(SECTION_NAMES)}.
  Each has: name, score (0-100), feedback (1-2 specific sentences).
  If a section is missing from resume, give low score and say so.
- strengths: 3-6 concise bullet strings.
- weaknesses: 3-6 concise bullet strings.
- missing_keywords: 5-15 important skills/keywords absent from resume.
- suggestions: 4-8 concrete actionable improvements.
- summary: 2-3 sentence overall verdict.
Keep every string under 300 characters. Be specific to THIS resume; never generic.
"""

    user_prompt = f"""RESUME TEXT:
\"\"\"
{resume_text[:30000]}
\"\"\"

{"JOB DESCRIPTION:\n\"\"\"\n" + job_description[:10000] + "\n\"\"\"" if has_jd else "No job description provided."}
"""

    response = ai_client.chat.completions.create(
        model=AI_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        response_format={"type": "json_object"},
        temperature=0.3,
    )

    raw = response.choices[0].message.content
    data = json.loads(raw)

    def clamp(n):
        try:
            return max(0, min(100, int(round(float(n)))))
        except Exception:
            return 0

    by_name = {s.get("name", "").lower(): s for s in data.get("sections", [])}
    sections = []
    for name in SECTION_NAMES:
        found = by_name.get(name.lower(), {})
        sections.append({
            "name": name,
            "score": clamp(found.get("score", 0)),
            "feedback": (found.get("feedback") or "No feedback provided.").strip()[:300],
        })

    return {
        "ats_score": clamp(data.get("ats_score", 0)),
        "job_match_score": clamp(data["job_match_score"]) if has_jd and data.get("job_match_score") is not None else None,
        "summary": (data.get("summary") or "").strip()[:600],
        "sections": sections,
        "strengths": [str(s)[:300] for s in data.get("strengths", [])][:8],
        "weaknesses": [str(s)[:300] for s in data.get("weaknesses", [])][:8],
        "missing_keywords": list(dict.fromkeys(
            str(k).strip() for k in data.get("missing_keywords", []) if str(k).strip()
        ))[:20],
        "suggestions": [str(s)[:300] for s in data.get("suggestions", [])][:8],
    }


# ============================================================
# PAGE ROUTES
# ============================================================
@app.route("/")
def index():
    return render_template("index.html", user=current_user() if session.get("user_id") else None)


@app.route("/login")
def login_page():
    if session.get("user_id"):
        return redirect(url_for("dashboard"))
    return render_template("login.html")


@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", user=current_user())


@app.route("/history")
@login_required
def history_page():
    return render_template("history.html", user=current_user())


@app.route("/analysis/<analysis_id>")
@login_required
def analysis_page(analysis_id):
    return render_template("analysis.html", user=current_user(), analysis_id=analysis_id)


@app.route("/admin")
@login_required
def admin_page():
    return render_template("admin.html", user=current_user())


# ============================================================
# AUTH API
# ============================================================
@app.route("/api/auth/signup", methods=["POST"])
def api_signup():
    data = request.get_json() or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    full_name = (data.get("full_name") or "").strip()

    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400
    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400

    pw_hash = generate_password_hash(password)

    try:
        conn = get_db()
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO users (email, password_hash, full_name) VALUES (%s, %s, %s)",
                (email, pw_hash, full_name)
            )
            user_id = cur.lastrowid
        conn.close()
    except pymysql.err.IntegrityError:
        return jsonify({"error": "Email already registered"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    session["user_id"] = user_id
    session["email"] = email
    session["full_name"] = full_name or email
    session["is_admin"] = False

    return jsonify({
        "ok": True,
        "user": {"id": user_id, "email": email, "full_name": full_name or email}
    })


@app.route("/api/auth/login", methods=["POST"])
def api_login():
    data = request.get_json() or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    try:
        conn = get_db()
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, email, password_hash, full_name, is_admin FROM users WHERE email = %s",
                (email,)
            )
            row = cur.fetchone()
        conn.close()
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    if not row or not check_password_hash(row["password_hash"], password):
        return jsonify({"error": "Invalid email or password"}), 401

    session["user_id"] = row["id"]
    session["email"] = row["email"]
    session["full_name"] = row["full_name"] or row["email"]
    session["is_admin"] = bool(row["is_admin"])

    return jsonify({
        "ok": True,
        "user": {
            "id": row["id"],
            "email": row["email"],
            "full_name": row["full_name"] or row["email"],
        }
    })


@app.route("/api/auth/logout", methods=["POST"])
def api_logout():
    session.clear()
    return jsonify({"ok": True})


@app.route("/api/auth/me")
def api_me():
    if not session.get("user_id"):
        return jsonify({"user": None})
    user = current_user()
    return jsonify({"user": user})


# ============================================================
# ANALYSIS API
# ============================================================
@app.route("/api/analyze", methods=["POST"])
@login_required
def api_analyze():
    user_id = session["user_id"]

    if "file" not in request.files:
        return jsonify({"error": "No PDF file uploaded"}), 400

    file = request.files["file"]
    if not file.filename.lower().endswith(".pdf"):
        return jsonify({"error": "Only PDF files allowed"}), 400

    file_bytes = file.read()
    if len(file_bytes) > 5 * 1024 * 1024:
        return jsonify({"error": "PDF must be under 5 MB"}), 400

    job_description = (request.form.get("job_description") or "").strip() or None
    analysis_id = str(uuid.uuid4())
    safe_name = "".join(c if c.isalnum() or c in "._-" else "_" for c in file.filename)
    # Store under uploads/<user_id>/<uuid>-filename.pdf
    user_dir = os.path.join(UPLOAD_FOLDER, str(user_id))
    os.makedirs(user_dir, exist_ok=True)
    storage_path = os.path.join(user_dir, f"{analysis_id}-{safe_name}")

    # Save PDF to disk
    with open(storage_path, "wb") as f:
        f.write(file_bytes)

    # Insert pending row
    try:
        conn = get_db()
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO resume_analyses
                   (id, user_id, file_name, file_path, job_description, status)
                   VALUES (%s, %s, %s, %s, %s, 'pending')""",
                (analysis_id, user_id, file.filename, storage_path, job_description)
            )
        conn.close()
    except Exception as e:
        return jsonify({"error": f"DB error: {e}"}), 500

    # Mark processing
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute(
            "UPDATE resume_analyses SET status='processing' WHERE id=%s",
            (analysis_id,)
        )
    conn.close()

    # Extract text
    try:
        text = extract_pdf_text(file_bytes)
        if len(text.replace(" ", "")) < 80:
            raise ValueError("Very little text found. Scanned/image PDFs are not supported.")
    except Exception as e:
        conn = get_db()
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE resume_analyses SET status='failed', error_message=%s WHERE id=%s",
                (str(e)[:500], analysis_id)
            )
        conn.close()
        return jsonify({"error": str(e), "analysis_id": analysis_id}), 400

    conn = get_db()
    with conn.cursor() as cur:
        cur.execute(
            "UPDATE resume_analyses SET extracted_text=%s WHERE id=%s",
            (text, analysis_id)
        )
    conn.close()

    # AI analysis
    try:
        feedback = run_ai_analysis(text, job_description)
    except Exception as e:
        conn = get_db()
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE resume_analyses SET status='failed', error_message=%s WHERE id=%s",
                (f"AI error: {str(e)[:200]}", analysis_id)
            )
        conn.close()
        return jsonify({"error": f"AI analysis failed: {e}", "analysis_id": analysis_id}), 500

    # Save success
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute(
            """UPDATE resume_analyses
               SET status='completed', ats_score=%s, job_match_score=%s,
                   feedback=%s, updated_at=NOW()
               WHERE id=%s""",
            (
                feedback["ats_score"],
                feedback["job_match_score"],
                json.dumps(feedback),
                analysis_id,
            )
        )
    conn.close()

    return jsonify({
        "ok": True,
        "analysis_id": analysis_id,
        "feedback": feedback,
    })


@app.route("/api/analyses")
@login_required
def api_list_analyses():
    user_id = session["user_id"]
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute(
            """SELECT id, file_name, ats_score, job_match_score, status,
                      created_at, error_message
               FROM resume_analyses
               WHERE user_id = %s
               ORDER BY created_at DESC
               LIMIT 50""",
            (user_id,)
        )
        rows = cur.fetchall()
    conn.close()

    # Convert datetime to string
    for r in rows:
        if r.get("created_at"):
            r["created_at"] = r["created_at"].isoformat()
    return jsonify({"analyses": rows})


@app.route("/api/analyses/<analysis_id>")
@login_required
def api_get_analysis(analysis_id):
    user_id = session["user_id"]
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute(
            "SELECT * FROM resume_analyses WHERE id=%s AND user_id=%s",
            (analysis_id, user_id)
        )
        row = cur.fetchone()
    conn.close()

    if not row:
        return jsonify({"error": "Not found"}), 404

    if row.get("created_at"):
        row["created_at"] = row["created_at"].isoformat()
    if row.get("updated_at"):
        row["updated_at"] = row["updated_at"].isoformat()
    # feedback is already JSON from MySQL, but ensure dict
    if isinstance(row.get("feedback"), str):
        try:
            row["feedback"] = json.loads(row["feedback"])
        except Exception:
            pass
    return jsonify({"analysis": row})


@app.route("/api/analyses/<analysis_id>", methods=["DELETE"])
@login_required
def api_delete_analysis(analysis_id):
    user_id = session["user_id"]
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute(
            "SELECT file_path FROM resume_analyses WHERE id=%s AND user_id=%s",
            (analysis_id, user_id)
        )
        row = cur.fetchone()
        if row and row.get("file_path") and os.path.exists(row["file_path"]):
            try:
                os.remove(row["file_path"])
            except Exception:
                pass
        cur.execute(
            "DELETE FROM resume_analyses WHERE id=%s AND user_id=%s",
            (analysis_id, user_id)
        )
    conn.close()
    return jsonify({"ok": True})


# ============================================================
# ADMIN API
# ============================================================
@app.route("/api/admin/stats")
@login_required
def api_admin_stats():
    if not session.get("is_admin"):
        return jsonify({"error": "Forbidden — admin only"}), 403

    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("SELECT id, full_name, email, created_at FROM users ORDER BY created_at DESC")
        users = cur.fetchall()
        cur.execute(
            """SELECT id, user_id, file_name, ats_score, status, created_at
               FROM resume_analyses ORDER BY created_at DESC"""
        )
        analyses = cur.fetchall()
    conn.close()

    for u in users:
        if u.get("created_at"):
            u["created_at"] = u["created_at"].isoformat()
    for a in analyses:
        if a.get("created_at"):
            a["created_at"] = a["created_at"].isoformat()

    completed = [x for x in analyses if x.get("status") == "completed" and x.get("ats_score") is not None]
    avg_score = round(sum(x["ats_score"] for x in completed) / len(completed)) if completed else None

    return jsonify({
        "totals": {
            "users": len(users),
            "analyses": len(analyses),
            "completed": len(completed),
            "failed": len([x for x in analyses if x.get("status") == "failed"]),
            "avg_score": avg_score,
        },
        "recent": analyses[:15],
        "users": users,
    })


# ============================================================
# Run
# ============================================================
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    print(f"\n  ResumeIQ running → http://127.0.0.1:{port}\n")
    app.run(host="0.0.0.0", port=port, debug=os.getenv("FLASK_DEBUG") == "1")
