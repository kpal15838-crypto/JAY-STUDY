from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "jay-study-library-secret-key-2026"

DATABASE = "jay_study.db"


# ==========================================
# DATABASE CONNECTION
# ==========================================

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# ==========================================
# CREATE DATABASE TABLES
# ==========================================

def init_db():

    conn = get_db_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            roll_number TEXT NOT NULL,
            course TEXT NOT NULL,
            mobile TEXT NOT NULL
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS fees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            roll_number TEXT NOT NULL,
            total_fees REAL NOT NULL,
            submitted_fees REAL NOT NULL,
            remaining_fees REAL NOT NULL
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS question_papers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            subject TEXT NOT NULL,
            year TEXT NOT NULL,
            questions TEXT
        )
    """)

    # Existing database me questions column add karega
    try:
        conn.execute("""
            ALTER TABLE question_papers
            ADD COLUMN questions TEXT
        """)
    except sqlite3.OperationalError:
        pass

    conn.execute("""
        CREATE TABLE IF NOT EXISTS signatures (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT NOT NULL,
            roll_number TEXT NOT NULL,
            signature_data TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


# ==========================================
# HOME
# ==========================================

@app.route("/")
def home():
    return render_template("dashboard.html")


# ==========================================
# STUDENTS
# ==========================================

@app.route("/students", methods=["GET", "POST"])
def students():

    if request.method == "POST":

        name = request.form["name"]
        roll_number = request.form["roll_number"]
        course = request.form["course"]
        mobile = request.form["mobile"]

        conn = get_db_connection()

        conn.execute("""
            INSERT INTO students
            (name, roll_number, course, mobile)
            VALUES (?, ?, ?, ?)
        """, (name, roll_number, course, mobile))

        conn.commit()
        conn.close()

        if "admin" in session:
            return redirect(url_for("admin_panel"))

        return redirect(url_for("students"))

    conn = get_db_connection()

    students_data = conn.execute("""
        SELECT *
        FROM students
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    return render_template(
        "students.html",
        students=students_data
    )


# ==========================================
# EDIT STUDENT
# ==========================================

@app.route("/edit-student/<int:id>", methods=["GET", "POST"])
def edit_student(id):

    if "admin" not in session:
        return redirect(url_for("admin_login"))

    conn = get_db_connection()

    student = conn.execute(
        "SELECT * FROM students WHERE id = ?",
        (id,)
    ).fetchone()

    if student is None:
        conn.close()
        return "Student not found!"

    if request.method == "POST":

        name = request.form["name"]
        roll_number = request.form["roll_number"]
        course = request.form["course"]
        mobile = request.form["mobile"]

        conn.execute("""
            UPDATE students
            SET name = ?,
                roll_number = ?,
                course = ?,
                mobile = ?
            WHERE id = ?
        """, (
            name,
            roll_number,
            course,
            mobile,
            id
        ))

        conn.commit()
        conn.close()

        return redirect(url_for("admin_panel"))

    conn.close()

    return render_template(
        "edit.html",
        student=student
    )


# ==========================================
# DELETE STUDENT
# ==========================================

@app.route("/delete-student/<int:id>", methods=["POST"])
def delete_student(id):

    if "admin" not in session:
        return redirect(url_for("admin_login"))

    conn = get_db_connection()

    conn.execute(
        "DELETE FROM students WHERE id = ?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("admin_panel"))


# ==========================================
# FEES
# ==========================================

@app.route("/fees", methods=["GET", "POST"])
def fees():

    if request.method == "POST":

        name = request.form["name"]
        roll_number = request.form["roll_number"]

        total_fees = float(
            request.form["total_fees"]
        )

        submitted_fees = float(
            request.form["submitted_fees"]
        )

        remaining_fees = total_fees - submitted_fees

        conn = get_db_connection()

        conn.execute("""
            INSERT INTO fees
            (
                name,
                roll_number,
                total_fees,
                submitted_fees,
                remaining_fees
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            name,
            roll_number,
            total_fees,
            submitted_fees,
            remaining_fees
        ))

        conn.commit()
        conn.close()

        if "admin" in session:
            return redirect(url_for("admin_panel"))

        return redirect(url_for("fees"))

    conn = get_db_connection()

    fees_data = conn.execute("""
        SELECT *
        FROM fees
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    return render_template(
        "fees.html",
        fees=fees_data
    )


# ==========================================
# EDIT FEE
# ==========================================

@app.route("/edit-fee/<int:id>", methods=["GET", "POST"])
def edit_fee(id):

    if "admin" not in session:
        return redirect(url_for("admin_login"))

    conn = get_db_connection()

    fee = conn.execute(
        "SELECT * FROM fees WHERE id = ?",
        (id,)
    ).fetchone()

    if fee is None:
        conn.close()
        return "Fee record not found!"

    if request.method == "POST":

        name = request.form["name"]
        roll_number = request.form["roll_number"]

        total_fees = float(
            request.form["total_fees"]
        )

        submitted_fees = float(
            request.form["submitted_fees"]
        )

        remaining_fees = total_fees - submitted_fees

        conn.execute("""
            UPDATE fees
            SET name = ?,
                roll_number = ?,
                total_fees = ?,
                submitted_fees = ?,
                remaining_fees = ?
            WHERE id = ?
        """, (
            name,
            roll_number,
            total_fees,
            submitted_fees,
            remaining_fees,
            id
        ))

        conn.commit()
        conn.close()

        return redirect(url_for("admin_panel"))

    conn.close()

    return render_template(
        "edit_fee.html",
        fee=fee
    )


# ==========================================
# DELETE FEE
# ==========================================

@app.route("/delete-fee/<int:id>", methods=["POST"])
def delete_fee(id):

    if "admin" not in session:
        return redirect(url_for("admin_login"))

    conn = get_db_connection()

    conn.execute(
        "DELETE FROM fees WHERE id = ?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("admin_panel"))


# ==========================================
# SIGNATURE
# ==========================================

@app.route("/signature", methods=["GET", "POST"])
def signature():

    if request.method == "POST":

        student_name = request.form["student_name"]
        roll_number = request.form["roll_number"]
        signature_data = request.form["signature_data"]

        conn = get_db_connection()

        conn.execute("""
            INSERT INTO signatures
            (
                student_name,
                roll_number,
                signature_data
            )
            VALUES (?, ?, ?)
        """, (
            student_name,
            roll_number,
            signature_data
        ))

        conn.commit()
        conn.close()

        return redirect(url_for("user_panel"))

    return render_template("signature.html")


# ==========================================
# DELETE SIGNATURE
# ==========================================

@app.route("/delete-signature/<int:id>", methods=["POST"])
def delete_signature(id):

    if "admin" not in session:
        return redirect(url_for("admin_login"))

    conn = get_db_connection()

    conn.execute(
        "DELETE FROM signatures WHERE id = ?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("admin_panel"))


# ==========================================
# USER REGISTRATION
# ==========================================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        hashed_password = generate_password_hash(password)

        conn = get_db_connection()

        existing_user = conn.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        ).fetchone()

        if existing_user:

            conn.close()

            return "Username already exists!"

        conn.execute("""
            INSERT INTO users
            (username, password)
            VALUES (?, ?)
        """, (
            username,
            hashed_password
        ))

        conn.commit()
        conn.close()

        return redirect(url_for("login"))

    return render_template("register.html")


# ==========================================
# USER LOGIN
# ==========================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = get_db_connection()

        user = conn.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        ).fetchone()

        conn.close()

        if user and check_password_hash(
            user["password"],
            password
        ):

            session["user"] = user["username"]

            return redirect(
                url_for("user_panel")
            )

        return "Invalid Username or Password!"

    return render_template("login.html")


# ==========================================
# USER PANEL
# ==========================================

@app.route("/user-panel")
def user_panel():

    if "user" not in session:
        return redirect(url_for("login"))

    conn = get_db_connection()

    question_papers_data = conn.execute("""
        SELECT *
        FROM question_papers
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    return render_template(
        "user_panel.html",
        question_papers=question_papers_data,
        username=session["user"]
    )


# ==========================================
# VIEW QUESTION PAPER
# ==========================================

@app.route("/question-paper/<int:id>")
def view_question_paper(id):

    if "user" not in session and "admin" not in session:
        return redirect(url_for("login"))

    conn = get_db_connection()

    paper = conn.execute(
        "SELECT * FROM question_papers WHERE id = ?",
        (id,)
    ).fetchone()

    conn.close()

    if paper is None:
        return "Question Paper Not Found!"

    return render_template(
        "view_question_paper.html",
        paper=paper
    )


# ==========================================
# DELETE USER
# ==========================================

@app.route("/delete-user/<int:id>", methods=["POST"])
def delete_user(id):

    if "admin" not in session:
        return redirect(url_for("admin_login"))

    conn = get_db_connection()

    conn.execute(
        "DELETE FROM users WHERE id = ?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("admin_panel"))


# ==========================================
# ADMIN LOGIN
# ==========================================

@app.route("/admin", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        if (
            username == "admin"
            and password == "Jay@12345"
        ):

            session["admin"] = True

            return redirect(
                url_for("admin_panel")
            )

        return "Invalid Admin Username or Password!"

    return render_template("admin_login.html")


# ==========================================
# ADMIN PANEL
# ==========================================

@app.route("/admin-panel")
def admin_panel():

    if "admin" not in session:
        return redirect(url_for("admin_login"))

    conn = get_db_connection()

    users_data = conn.execute("""
        SELECT id, username
        FROM users
        ORDER BY id DESC
    """).fetchall()

    students_data = conn.execute("""
        SELECT *
        FROM students
        ORDER BY id DESC
    """).fetchall()

    fees_data = conn.execute("""
        SELECT *
        FROM fees
        ORDER BY id DESC
    """).fetchall()

    question_papers_data = conn.execute("""
        SELECT *
        FROM question_papers
        ORDER BY id DESC
    """).fetchall()

    signatures_data = conn.execute("""
        SELECT *
        FROM signatures
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    return render_template(
        "admin_panel.html",
        question_papers=question_papers_data,
        users=users_data,
        students=students_data,
        fees=fees_data,
        signatures=signatures_data
    )


# ==========================================
# ADD QUESTION PAPER
# ==========================================

@app.route("/add-question-paper", methods=["POST"])
def add_question_paper():

    if "admin" not in session:
        return redirect(url_for("admin_login"))

    title = request.form.get("title", "").strip()
    subject = request.form.get("subject", "").strip()
    year = request.form.get("year", "").strip()
    questions = request.form.get("questions", "").strip()

    if not title or not subject or not year or not questions:
        return "Please fill all Question Paper fields!"

    conn = get_db_connection()

    conn.execute("""
        INSERT INTO question_papers
        (
            title,
            subject,
            year,
            questions
        )
        VALUES (?, ?, ?, ?)
    """, (
        title,
        subject,
        year,
        questions
    ))

    conn.commit()
    conn.close()

    return redirect(
        url_for("admin_panel")
    )


# ==========================================
# EDIT QUESTION PAPER
# ==========================================

@app.route(
    "/edit-question-paper/<int:id>",
    methods=["GET", "POST"]
)
def edit_question_paper(id):

    if "admin" not in session:
        return redirect(url_for("admin_login"))

    conn = get_db_connection()

    paper = conn.execute(
        "SELECT * FROM question_papers WHERE id = ?",
        (id,)
    ).fetchone()

    if paper is None:
        conn.close()
        return "Question Paper Not Found!"

    if request.method == "POST":

        title = request.form.get("title", "").strip()
        subject = request.form.get("subject", "").strip()
        year = request.form.get("year", "").strip()
        questions = request.form.get("questions", "").strip()

        if not title or not subject or not year or not questions:
            conn.close()
            return "Please fill all fields!"

        conn.execute("""
            UPDATE question_papers
            SET
                title = ?,
                subject = ?,
                year = ?,
                questions = ?
            WHERE id = ?
        """, (
            title,
            subject,
            year,
            questions,
            id
        ))

        conn.commit()
        conn.close()

        return redirect(
            url_for("admin_panel")
        )

    conn.close()

    return render_template(
        "edit_question_paper.html",
        paper=paper
    )


# ==========================================
# DELETE QUESTION PAPER
# ==========================================

@app.route(
    "/delete-question-paper/<int:id>",
    methods=["POST"]
)
def delete_question_paper(id):

    if "admin" not in session:
        return redirect(url_for("admin_login"))

    conn = get_db_connection()

    conn.execute(
        "DELETE FROM question_papers WHERE id = ?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect(
        url_for("admin_panel")
    )


# ==========================================
# LOGOUT
# ==========================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("home")
    )


# ==========================================
# START APPLICATION
# ==========================================

if __name__ == "__main__":

    init_db()

    app.run(debug=True)