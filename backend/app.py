import os
import re
import sqlite3
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
DB_FILE = os.path.join(BASE_DIR, "applications.db")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["MAX_CONTENT_LENGTH"] = MAX_FILE_SIZE + (1024 * 1024)


def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            department TEXT NOT NULL,
            date_of_birth TEXT NOT NULL,
            bio TEXT,
            photo_filename TEXT,
            created_at TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


def allowed_file(filename):
    if "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()
    return ext in ALLOWED_EXTENSIONS


EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PHONE_REGEX = re.compile(r"^\+?[0-9\-\s]{7,15}$")
VALID_DEPARTMENTS = {"engineering", "design", "marketing", "sales", "hr", "finance"}


def validate_form(data):
    errors = {}

    full_name = (data.get("full_name") or "").strip()
    if not full_name:
        errors["full_name"] = "Full name is required."
    elif len(full_name) < 3:
        errors["full_name"] = "Full name must be at least 3 characters."
    elif len(full_name) > 80:
        errors["full_name"] = "Full name must be under 80 characters."

    email = (data.get("email") or "").strip()
    if not email:
        errors["email"] = "Email is required."
    elif not EMAIL_REGEX.match(email):
        errors["email"] = "Enter a valid email address."

    phone = (data.get("phone") or "").strip()
    if not phone:
        errors["phone"] = "Phone number is required."
    elif not PHONE_REGEX.match(phone):
        errors["phone"] = "Enter a valid phone number (7-15 digits)."

    department = (data.get("department") or "").strip().lower()
    if not department:
        errors["department"] = "Please select a department."
    elif department not in VALID_DEPARTMENTS:
        errors["department"] = "Selected department is not valid."

    dob = (data.get("date_of_birth") or "").strip()
    if not dob:
        errors["date_of_birth"] = "Date of birth is required."
    else:
        try:
            dob_date = datetime.strptime(dob, "%Y-%m-%d").date()
            today = datetime.today().date()
            age = today.year - dob_date.year - (
                (today.month, today.day) < (dob_date.month, dob_date.day)
            )
            if dob_date > today:
                errors["date_of_birth"] = "Date of birth cannot be in the future."
            elif age < 16:
                errors["date_of_birth"] = "You must be at least 16 years old."
            elif age > 100:
                errors["date_of_birth"] = "Enter a valid date of birth."
        except ValueError:
            errors["date_of_birth"] = "Date must be in YYYY-MM-DD format."

    bio = (data.get("bio") or "").strip()
    if bio and len(bio) > 500:
        errors["bio"] = "Bio must be under 500 characters."

    return errors


@app.route("/api/applications", methods=["POST"])
def create_application():
    data = request.form.to_dict()
    errors = validate_form(data)

    photo = request.files.get("photo")
    photo_filename = None

    if not photo or photo.filename == "":
        errors["photo"] = "A profile photo is required."
    else:
        if not allowed_file(photo.filename):
            errors["photo"] = "Only PNG, JPG, JPEG, GIF, or WEBP files are allowed."
        else:
            photo.seek(0, os.SEEK_END)
            size = photo.tell()
            photo.seek(0)
            if size > MAX_FILE_SIZE:
                errors["photo"] = "Photo must be under 5MB."

    if errors:
        return jsonify({"success": False, "errors": errors}), 400

    safe_name = secure_filename(photo.filename)
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
    photo_filename = f"{timestamp}_{safe_name}"
    photo.save(os.path.join(UPLOAD_FOLDER, photo_filename))

    conn = get_db()
    conn.execute(
        """
        INSERT INTO applications
        (full_name, email, phone, department, date_of_birth, bio, photo_filename, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            data.get("full_name", "").strip(),
            data.get("email", "").strip(),
            data.get("phone", "").strip(),
            data.get("department", "").strip().lower(),
            data.get("date_of_birth", "").strip(),
            data.get("bio", "").strip(),
            photo_filename,
            datetime.utcnow().isoformat(),
        ),
    )
    conn.commit()
    new_id = conn.execute("SELECT last_insert_rowid() as id").fetchone()["id"]
    conn.close()

    return jsonify({
        "success": True,
        "message": "Application submitted successfully!",
        "id": new_id,
    }), 201


@app.route("/api/applications", methods=["GET"])
def list_applications():
    conn = get_db()
    rows = conn.execute(
        "SELECT id, full_name, email, phone, department, date_of_birth, bio, photo_filename, created_at "
        "FROM applications ORDER BY id DESC"
    ).fetchall()
    conn.close()
    return jsonify({"success": True, "applications": [dict(r) for r in rows]})


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5000)
