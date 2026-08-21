from flask import Flask, render_template, request, redirect, url_for, session
import os
import sqlite3
import psycopg2
import psycopg2.extras
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)

app.secret_key = os.environ.get(
    "SECRET_KEY",
    "jay-study-library-secret-key-2026"
)


# ==========================================
# DATABASE CONFIGURATION
# PostgreSQL on Render
# SQLite for local development
# ==========================================

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

SQLITE_DATABASE = os.path.join(
    BASE_DIR,
    "jay_study.db"
)

DATABASE_URL = os.environ.get("DATABASE_URL")


# ==========================================
# DATABASE CONNECTION
# ==========================================

def is_postgres():

    return bool(DATABASE_URL)


def get_db_connection():

    if is_postgres():

        database_url = DATABASE_URL

        if database_url.startswith("postgres://"):

            database_url = database_url.replace(
                "postgres://",
                "postgresql://",
                1
            )

        conn = psycopg2.connect(
            database_url,
            sslmode="require"
        )

        return conn

    conn = sqlite3.connect(SQLITE_DATABASE)

    conn.row_factory = sqlite3.Row

    return conn


# ==========================================
# DATABASE HELPER
# Converts ? to %s for PostgreSQL
# ==========================================

def db_execute(conn, query, params=()):

    if is_postgres():

        query = query.replace("?", "%s")

        cursor = conn.cursor(
            cursor_factory=psycopg2.extras.RealDictCursor
        )

        cursor.execute(query, params)

        return cursor

    return conn.execute(query, params)


# ==========================================
# FETCH HELPERS
# ==========================================

def db_fetchone(conn, query, params=()):

    cursor = db_execute(conn, query, params)

    return cursor.fetchone()


def db_fetchall(conn, query, params=()):

    cursor = db_execute(conn, query, params)

    return cursor.fetchall()


# ==========================================
# DATABASE COMMIT / CLOSE
# ==========================================

def db_commit(conn):

    conn.commit()


def db_close(conn):

    conn.close()


# ==========================================
# CREATE / UPDATE DATABASE TABLES
# ==========================================

def init_db():

    conn = get_db_connection()

    if is_postgres():

        db_execute(conn, """
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        """)

        db_execute(conn, """
            CREATE TABLE IF NOT EXISTS students (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                roll_number TEXT NOT NULL,
                course TEXT NOT NULL,
                mobile TEXT NOT NULL
            )
        """)

        db_execute(conn, """
            CREATE TABLE IF NOT EXISTS fees (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                roll_number TEXT NOT NULL,
                total_fees DOUBLE PRECISION NOT NULL,
                submitted_fees DOUBLE PRECISION NOT NULL,
                remaining_fees DOUBLE PRECISION NOT NULL
            )
        """)

        db_execute(conn, """
            CREATE TABLE IF NOT EXISTS question_papers (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                subject TEXT NOT NULL,
                year TEXT NOT NULL,
                questions TEXT
            )
        """)

        db_execute(conn, """
            CREATE TABLE IF NOT EXISTS signatures (
                id SERIAL PRIMARY KEY,
                student_name TEXT NOT NULL,
                roll_number TEXT NOT NULL,
                signature_data TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        db_execute(conn, """
            CREATE TABLE IF NOT EXISTS tests (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                subject TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        db_execute(conn, """
            CREATE TABLE IF NOT EXISTS test_questions (
                id SERIAL PRIMARY KEY,
                test_id INTEGER NOT NULL,
                question TEXT NOT NULL,
                option_a TEXT NOT NULL,
                option_b TEXT NOT NULL,
                option_c TEXT NOT NULL,
                option_d TEXT NOT NULL,
                correct_answer TEXT NOT NULL
            )
        """)

        db_execute(conn, """
            CREATE TABLE IF NOT EXISTS test_results (
                id SERIAL PRIMARY KEY,
                test_id INTEGER NOT NULL,
                username TEXT NOT NULL,
                total_questions INTEGER NOT NULL,
                correct_answers INTEGER NOT NULL,
                wrong_answers INTEGER NOT NULL,
                timeout_answers INTEGER NOT NULL DEFAULT 0,
                percentage DOUBLE PRECISION NOT NULL,
                submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        db_execute(conn, """
            CREATE TABLE IF NOT EXISTS test_answer_details (
                id SERIAL PRIMARY KEY,
                result_id INTEGER NOT NULL,
                question_id INTEGER NOT NULL,
                question TEXT NOT NULL,
                option_a TEXT,
                option_b TEXT,
                option_c TEXT,
                option_d TEXT,
                selected_answer TEXT,
                correct_answer TEXT NOT NULL,
                is_correct INTEGER NOT NULL,
                is_timeout INTEGER NOT NULL DEFAULT 0
            )
        """)

    else:

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

        conn.execute("""
            CREATE TABLE IF NOT EXISTS signatures (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_name TEXT NOT NULL,
                roll_number TEXT NOT NULL,
                signature_data TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS tests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                subject TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS test_questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                test_id INTEGER NOT NULL,
                question TEXT NOT NULL,
                option_a TEXT NOT NULL,
                option_b TEXT NOT NULL,
                option_c TEXT NOT NULL,
                option_d TEXT NOT NULL,
                correct_answer TEXT NOT NULL
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS test_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                test_id INTEGER NOT NULL,
                username TEXT NOT NULL,
                total_questions INTEGER NOT NULL,
                correct_answers INTEGER NOT NULL,
                wrong_answers INTEGER NOT NULL,
                timeout_answers INTEGER NOT NULL DEFAULT 0,
                percentage REAL NOT NULL,
                submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS test_answer_details (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                result_id INTEGER NOT NULL,
                question_id INTEGER NOT NULL,
                question TEXT NOT NULL,
                option_a TEXT,
                option_b TEXT,
                option_c TEXT,
                option_d TEXT,
                selected_answer TEXT,
                correct_answer TEXT NOT NULL,
                is_correct INTEGER NOT NULL,
                is_timeout INTEGER NOT NULL DEFAULT 0
            )
        """)

    db_commit(conn)
    db_close(conn)


# ==========================================
# HOME
# ==========================================

@app.route("/")
def home():

    return render_template("dashboard.html")


# ==========================================
# DATABASE CHECK
# ==========================================

@app.route("/db-check")
def db_check():

    if is_postgres():

        return "POSTGRESQL DATABASE CONNECTED"

    return "SQLITE DATABASE ACTIVE"


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

        db_execute(conn, """
            INSERT INTO students
            (name, roll_number, course, mobile)
            VALUES (?, ?, ?, ?)
        """, (
            name,
            roll_number,
            course,
            mobile
        ))

        db_commit(conn)
        db_close(conn)

        if "admin" in session:

            return redirect(url_for("admin_panel"))

        return redirect(url_for("students"))

    conn = get_db_connection()

    students_data = db_fetchall(conn, """
        SELECT *
        FROM students
        ORDER BY id DESC
    """)

    db_close(conn)

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

    student = db_fetchone(
        conn,
        "SELECT * FROM students WHERE id = ?",
        (id,)
    )

    if student is None:

        db_close(conn)

        return "Student not found!"

    if request.method == "POST":

        db_execute(conn, """
            UPDATE students
            SET name = ?,
                roll_number = ?,
                course = ?,
                mobile = ?
            WHERE id = ?
        """, (
            request.form["name"],
            request.form["roll_number"],
            request.form["course"],
            request.form["mobile"],
            id
        ))

        db_commit(conn)
        db_close(conn)

        return redirect(url_for("admin_panel"))

    db_close(conn)

    return render_template("edit.html", student=student)


# ==========================================
# DELETE STUDENT
# ==========================================

@app.route("/delete-student/<int:id>", methods=["POST"])
def delete_student(id):

    if "admin" not in session:

        return redirect(url_for("admin_login"))

    conn = get_db_connection()

    db_execute(
        conn,
        "DELETE FROM students WHERE id = ?",
        (id,)
    )

    db_commit(conn)
    db_close(conn)

    return redirect(url_for("admin_panel"))


# ==========================================
# FEES
# ==========================================

@app.route("/fees", methods=["GET", "POST"])
def fees():

    if request.method == "POST":

        name = request.form["name"]
        roll_number = request.form["roll_number"]

        total_fees = float(request.form["total_fees"])

        submitted_fees = float(request.form["submitted_fees"])

        remaining_fees = total_fees - submitted_fees

        conn = get_db_connection()

        db_execute(conn, """
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

        db_commit(conn)
        db_close(conn)

        if "admin" in session:

            return redirect(url_for("admin_panel"))

        return redirect(url_for("fees"))

    conn = get_db_connection()

    fees_data = db_fetchall(conn, """
        SELECT *
        FROM fees
        ORDER BY id DESC
    """)

    db_close(conn)

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

    fee = db_fetchone(
        conn,
        "SELECT * FROM fees WHERE id = ?",
        (id,)
    )

    if fee is None:

        db_close(conn)

        return "Fee record not found!"

    if request.method == "POST":

        name = request.form["name"]
        roll_number = request.form["roll_number"]

        total_fees = float(request.form["total_fees"])
        submitted_fees = float(request.form["submitted_fees"])

        remaining_fees = total_fees - submitted_fees

        db_execute(conn, """
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

        db_commit(conn)
        db_close(conn)

        return redirect(url_for("admin_panel"))

    db_close(conn)

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

    db_execute(
        conn,
        "DELETE FROM fees WHERE id = ?",
        (id,)
    )

    db_commit(conn)
    db_close(conn)

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

        db_execute(conn, """
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

        db_commit(conn)
        db_close(conn)

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

    db_execute(
        conn,
        "DELETE FROM signatures WHERE id = ?",
        (id,)
    )

    db_commit(conn)
    db_close(conn)

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

        existing_user = db_fetchone(
            conn,
            "SELECT * FROM users WHERE username = ?",
            (username,)
        )

        if existing_user:

            db_close(conn)

            return "Username already exists!"

        db_execute(conn, """
            INSERT INTO users
            (username, password)
            VALUES (?, ?)
        """, (
            username,
            hashed_password
        ))

        db_commit(conn)
        db_close(conn)

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

        user = db_fetchone(
            conn,
            "SELECT * FROM users WHERE username = ?",
            (username,)
        )

        db_close(conn)

        if (
            user
            and check_password_hash(
                user["password"],
                password
            )
        ):

            session["user"] = user["username"]

            return redirect(url_for("user_panel"))

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

    question_papers_data = db_fetchall(
        conn,
        """
        SELECT *
        FROM question_papers
        ORDER BY id DESC
        """
    )

    tests_data = db_fetchall(
        conn,
        """
        SELECT
            tests.*,
            COUNT(test_questions.id)
            AS question_count
        FROM tests
        LEFT JOIN test_questions
        ON tests.id = test_questions.test_id
        GROUP BY tests.id
        ORDER BY tests.id DESC
        """
    )

    db_close(conn)

    return render_template(
        "user_panel.html",
        question_papers=question_papers_data,
        tests=tests_data,
        username=session["user"]
    )


# ==========================================
# VIEW QUESTION PAPER
# ==========================================

@app.route("/question-paper/<int:id>")
def view_question_paper(id):

    if (
        "user" not in session
        and "admin" not in session
    ):

        return redirect(url_for("login"))

    conn = get_db_connection()

    paper = db_fetchone(
        conn,
        "SELECT * FROM question_papers WHERE id = ?",
        (id,)
    )

    db_close(conn)

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

    db_execute(
        conn,
        "DELETE FROM users WHERE id = ?",
        (id,)
    )

    db_commit(conn)
    db_close(conn)

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

            return redirect(url_for("admin_panel"))

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

    users_data = db_fetchall(conn, """
        SELECT id, username
        FROM users
        ORDER BY id DESC
    """)

    students_data = db_fetchall(conn, """
        SELECT *
        FROM students
        ORDER BY id DESC
    """)

    fees_data = db_fetchall(conn, """
        SELECT *
        FROM fees
        ORDER BY id DESC
    """)

    question_papers_data = db_fetchall(conn, """
        SELECT *
        FROM question_papers
        ORDER BY id DESC
    """)

    signatures_data = db_fetchall(conn, """
        SELECT *
        FROM signatures
        ORDER BY id DESC
    """)

    tests_data = db_fetchall(conn, """
        SELECT
            tests.*,
            COUNT(test_questions.id)
            AS question_count
        FROM tests
        LEFT JOIN test_questions
        ON tests.id = test_questions.test_id
        GROUP BY tests.id
        ORDER BY tests.id DESC
    """)

    test_results_data = db_fetchall(conn, """
        SELECT
            test_results.*,
            tests.title,
            tests.subject
        FROM test_results
        JOIN tests
        ON test_results.test_id = tests.id
        ORDER BY test_results.id DESC
    """)

    db_close(conn)

    return render_template(
        "admin_panel.html",
        question_papers=question_papers_data,
        users=users_data,
        students=students_data,
        fees=fees_data,
        signatures=signatures_data,
        tests=tests_data,
        test_results=test_results_data
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

    if (
        not title
        or not subject
        or not year
        or not questions
    ):

        return "Please fill all Question Paper fields!"

    conn = get_db_connection()

    db_execute(conn, """
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

    db_commit(conn)
    db_close(conn)

    return redirect(url_for("admin_panel"))


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

    paper = db_fetchone(
        conn,
        "SELECT * FROM question_papers WHERE id = ?",
        (id,)
    )

    if paper is None:

        db_close(conn)

        return "Question Paper Not Found!"

    if request.method == "POST":

        title = request.form.get("title", "").strip()
        subject = request.form.get("subject", "").strip()
        year = request.form.get("year", "").strip()
        questions = request.form.get("questions", "").strip()

        if (
            not title
            or not subject
            or not year
            or not questions
        ):

            db_close(conn)

            return "Please fill all fields!"

        db_execute(conn, """
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

        db_commit(conn)
        db_close(conn)

        return redirect(url_for("admin_panel"))

    db_close(conn)

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

    db_execute(
        conn,
        "DELETE FROM question_papers WHERE id = ?",
        (id,)
    )

    db_commit(conn)
    db_close(conn)

    return redirect(url_for("admin_panel"))


# ==========================================
# ADD TEST
# ==========================================

@app.route("/add-test", methods=["POST"])
def add_test():

    if "admin" not in session:

        return redirect(url_for("admin_login"))

    title = request.form.get("title", "").strip()
    subject = request.form.get("subject", "").strip()

    questions = request.form.getlist("question[]")
    option_a = request.form.getlist("option_a[]")
    option_b = request.form.getlist("option_b[]")
    option_c = request.form.getlist("option_c[]")
    option_d = request.form.getlist("option_d[]")
    correct_answers = request.form.getlist("correct_answer[]")

    if not title or not subject:

        return "Please enter Test Title and Subject!"

    if not questions:

        return "Please add at least one question!"

    conn = get_db_connection()

    if is_postgres():

        cursor = db_execute(conn, """
            INSERT INTO tests
            (title, subject)
            VALUES (?, ?)
            RETURNING id
        """, (
            title,
            subject
        ))

        test_id = cursor.fetchone()["id"]

    else:

        cursor = db_execute(conn, """
            INSERT INTO tests
            (title, subject)
            VALUES (?, ?)
        """, (
            title,
            subject
        ))

        test_id = cursor.lastrowid

    valid_question_count = 0

    for i in range(len(questions)):

        question = questions[i].strip()

        if not question:

            continue

        if (
            i >= len(option_a)
            or i >= len(option_b)
            or i >= len(option_c)
            or i >= len(option_d)
            or i >= len(correct_answers)
        ):

            continue

        correct_answer = correct_answers[i].strip().upper()

        if (
            not option_a[i].strip()
            or not option_b[i].strip()
            or not option_c[i].strip()
            or not option_d[i].strip()
            or correct_answer not in ["A", "B", "C", "D"]
        ):

            continue

        db_execute(conn, """
            INSERT INTO test_questions
            (
                test_id,
                question,
                option_a,
                option_b,
                option_c,
                option_d,
                correct_answer
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            test_id,
            question,
            option_a[i].strip(),
            option_b[i].strip(),
            option_c[i].strip(),
            option_d[i].strip(),
            correct_answer
        ))

        valid_question_count += 1

    if valid_question_count == 0:

        db_execute(
            conn,
            "DELETE FROM tests WHERE id = ?",
            (test_id,)
        )

        db_commit(conn)
        db_close(conn)

        return "Please add at least one complete question!"

    db_commit(conn)
    db_close(conn)

    return redirect(url_for("admin_panel"))


# ==========================================
# EDIT TEST
# ==========================================

@app.route(
    "/edit-test/<int:id>",
    methods=["GET", "POST"]
)
def edit_test(id):

    if "admin" not in session:

        return redirect(url_for("admin_login"))

    conn = get_db_connection()

    test = db_fetchone(
        conn,
        "SELECT * FROM tests WHERE id = ?",
        (id,)
    )

    if test is None:

        db_close(conn)

        return "Test Not Found!"

    questions = db_fetchall(conn, """
        SELECT *
        FROM test_questions
        WHERE test_id = ?
        ORDER BY id ASC
    """, (
        id,
    ))

    if request.method == "POST":

        title = request.form.get("title", "").strip()
        subject = request.form.get("subject", "").strip()

        question_ids = request.form.getlist("question_id[]")
        questions_list = request.form.getlist("question[]")
        option_a_list = request.form.getlist("option_a[]")
        option_b_list = request.form.getlist("option_b[]")
        option_c_list = request.form.getlist("option_c[]")
        option_d_list = request.form.getlist("option_d[]")
        correct_answers = request.form.getlist("correct_answer[]")

        if not title or not subject:

            db_close(conn)

            return "Please enter Test Title and Subject!"

        db_execute(conn, """
            UPDATE tests
            SET title = ?,
                subject = ?
            WHERE id = ?
        """, (
            title,
            subject,
            id
        ))

        for i in range(len(question_ids)):

            if (
                i >= len(questions_list)
                or i >= len(option_a_list)
                or i >= len(option_b_list)
                or i >= len(option_c_list)
                or i >= len(option_d_list)
                or i >= len(correct_answers)
            ):

                continue

            question = questions_list[i].strip()
            option_a = option_a_list[i].strip()
            option_b = option_b_list[i].strip()
            option_c = option_c_list[i].strip()
            option_d = option_d_list[i].strip()

            correct_answer = correct_answers[i].strip().upper()

            if (
                not question
                or not option_a
                or not option_b
                or not option_c
                or not option_d
                or correct_answer not in ["A", "B", "C", "D"]
            ):

                continue

            db_execute(conn, """
                UPDATE test_questions
                SET
                    question = ?,
                    option_a = ?,
                    option_b = ?,
                    option_c = ?,
                    option_d = ?,
                    correct_answer = ?
                WHERE id = ?
                AND test_id = ?
            """, (
                question,
                option_a,
                option_b,
                option_c,
                option_d,
                correct_answer,
                question_ids[i],
                id
            ))

        db_commit(conn)
        db_close(conn)

        return redirect(url_for("admin_panel"))

    db_close(conn)

    return render_template(
        "edit_test.html",
        test=test,
        questions=questions
    )


# ==========================================
# START TEST
# ==========================================

@app.route("/start-test/<int:id>")
def start_test(id):

    if "user" not in session:

        return redirect(url_for("login"))

    conn = get_db_connection()

    test = db_fetchone(
        conn,
        "SELECT * FROM tests WHERE id = ?",
        (id,)
    )

    questions = db_fetchall(conn, """
        SELECT *
        FROM test_questions
        WHERE test_id = ?
        ORDER BY id ASC
    """, (
        id,
    ))

    db_close(conn)

    if test is None:

        return "Test Not Found!"

    if not questions:

        return "No questions available for this test!"

    return render_template(
        "start_test.html",
        test=test,
        questions=questions
    )


# ==========================================
# SUBMIT TEST
# ==========================================

@app.route(
    "/submit-test/<int:test_id>",
    methods=["POST"]
)
def submit_test(test_id):

    if "user" not in session:

        return redirect(url_for("login"))

    conn = get_db_connection()

    test = db_fetchone(
        conn,
        "SELECT * FROM tests WHERE id = ?",
        (test_id,)
    )

    if test is None:

        db_close(conn)

        return "Test Not Found!"

    questions = db_fetchall(conn, """
        SELECT *
        FROM test_questions
        WHERE test_id = ?
        ORDER BY id ASC
    """, (
        test_id,
    ))

    total_questions = len(questions)

    correct_answers = 0
    wrong_answers = 0
    timeout_answers = 0

    timed_out_question_ids = request.form.getlist(
        "timed_out_question"
    )

    timed_out_question_ids = {
        str(question_id)
        for question_id
        in timed_out_question_ids
    }

    for question in questions:

        question_id = str(question["id"])

        selected_answer = request.form.get(
            f"answer_{question['id']}",
            ""
        ).strip().upper()

        if question_id in timed_out_question_ids:

            timeout_answers += 1

            continue

        if (
            selected_answer
            and selected_answer
            == question["correct_answer"].upper()
        ):

            correct_answers += 1

        elif selected_answer:

            wrong_answers += 1

    percentage = 0

    if total_questions > 0:

        percentage = round(
            (
                correct_answers
                / total_questions
            ) * 100,
            2
        )

    if is_postgres():

        cursor = db_execute(conn, """
            INSERT INTO test_results
            (
                test_id,
                username,
                total_questions,
                correct_answers,
                wrong_answers,
                timeout_answers,
                percentage
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            RETURNING id
        """, (
            test_id,
            session["user"],
            total_questions,
            correct_answers,
            wrong_answers,
            timeout_answers,
            percentage
        ))

        result_id = cursor.fetchone()["id"]

    else:

        cursor = db_execute(conn, """
            INSERT INTO test_results
            (
                test_id,
                username,
                total_questions,
                correct_answers,
                wrong_answers,
                timeout_answers,
                percentage
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            test_id,
            session["user"],
            total_questions,
            correct_answers,
            wrong_answers,
            timeout_answers,
            percentage
        ))

        result_id = cursor.lastrowid

    for question in questions:

        question_id = str(question["id"])

        selected_answer = request.form.get(
            f"answer_{question['id']}",
            ""
        ).strip().upper()

        correct_answer = question[
            "correct_answer"
        ].upper()

        is_timeout = (
            1
            if question_id
            in timed_out_question_ids
            else 0
        )

        if is_timeout:

            selected_answer = ""

        is_correct = (
            1
            if (
                not is_timeout
                and selected_answer
                and selected_answer
                == correct_answer
            )
            else 0
        )

        db_execute(conn, """
            INSERT INTO test_answer_details
            (
                result_id,
                question_id,
                question,
                option_a,
                option_b,
                option_c,
                option_d,
                selected_answer,
                correct_answer,
                is_correct,
                is_timeout
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            result_id,
            question["id"],
            question["question"],
            question["option_a"],
            question["option_b"],
            question["option_c"],
            question["option_d"],
            selected_answer,
            correct_answer,
            is_correct,
            is_timeout
        ))

    db_commit(conn)
    db_close(conn)

    return redirect(
        url_for(
            "test_result",
            id=result_id
        )
    )


# ==========================================
# TEST RESULT
# ==========================================

@app.route("/test-result/<int:id>")
def test_result(id):

    if (
        "user" not in session
        and "admin" not in session
    ):

        return redirect(url_for("login"))

    conn = get_db_connection()

    result = db_fetchone(conn, """
        SELECT
            test_results.*,
            tests.title,
            tests.subject
        FROM test_results
        JOIN tests
        ON test_results.test_id = tests.id
        WHERE test_results.id = ?
    """, (
        id,
    ))

    if result is None:

        db_close(conn)

        return "Result Not Found!"

    if (
        "user" in session
        and result["username"]
        != session["user"]
    ):

        db_close(conn)

        return "You are not allowed to view this result!"

    correct_questions = db_fetchall(conn, """
        SELECT *
        FROM test_answer_details
        WHERE result_id = ?
        AND is_correct = 1
        AND is_timeout = 0
        ORDER BY id ASC
    """, (
        id,
    ))

    wrong_questions = db_fetchall(conn, """
        SELECT *
        FROM test_answer_details
        WHERE result_id = ?
        AND is_correct = 0
        AND is_timeout = 0
        AND selected_answer IS NOT NULL
        AND selected_answer != ''
        ORDER BY id ASC
    """, (
        id,
    ))

    unattempted_questions = db_fetchall(conn, """
        SELECT *
        FROM test_answer_details
        WHERE result_id = ?
        AND is_correct = 0
        AND is_timeout = 0
        AND (
            selected_answer IS NULL
            OR selected_answer = ''
        )
        ORDER BY id ASC
    """, (
        id,
    ))

    timeout_questions = db_fetchall(conn, """
        SELECT *
        FROM test_answer_details
        WHERE result_id = ?
        AND is_timeout = 1
        ORDER BY id ASC
    """, (
        id,
    ))

    db_close(conn)

    return render_template(
        "test_result.html",
        result=result,
        correct_questions=correct_questions,
        wrong_questions=wrong_questions,
        unattempted_questions=unattempted_questions,
        timeout_questions=timeout_questions
    )


# ==========================================
# EDIT TEST RESULT
# ==========================================

@app.route(
    "/edit-test-result/<int:id>",
    methods=["GET", "POST"]
)
def edit_test_result(id):

    if "admin" not in session:

        return redirect(url_for("admin_login"))

    conn = get_db_connection()

    result = db_fetchone(conn, """
        SELECT
            test_results.*,
            tests.title,
            tests.subject
        FROM test_results
        JOIN tests
        ON test_results.test_id = tests.id
        WHERE test_results.id = ?
    """, (
        id,
    ))

    if result is None:

        db_close(conn)

        return "Result Not Found!"

    if request.method == "POST":

        correct_answers = int(
            request.form["correct_answers"]
        )

        wrong_answers = int(
            request.form["wrong_answers"]
        )

        timeout_answers = int(
            request.form["timeout_answers"]
        )

        total_questions = result["total_questions"]

        correct_answers = max(0, correct_answers)
        wrong_answers = max(0, wrong_answers)
        timeout_answers = max(0, timeout_answers)

        percentage = 0

        if total_questions > 0:

            percentage = round(
                (
                    correct_answers
                    / total_questions
                ) * 100,
                2
            )

        db_execute(conn, """
            UPDATE test_results
            SET
                correct_answers = ?,
                wrong_answers = ?,
                timeout_answers = ?,
                percentage = ?
            WHERE id = ?
        """, (
            correct_answers,
            wrong_answers,
            timeout_answers,
            percentage,
            id
        ))

        db_commit(conn)
        db_close(conn)

        return redirect(url_for("admin_panel"))

    db_close(conn)

    return render_template(
        "edit_test_result.html",
        result=result
    )


# ==========================================
# DELETE TEST RESULT
# ==========================================

@app.route(
    "/delete-test-result/<int:id>",
    methods=["POST"]
)
def delete_test_result(id):

    if "admin" not in session:

        return redirect(url_for("admin_login"))

    conn = get_db_connection()

    db_execute(conn, """
        DELETE FROM test_answer_details
        WHERE result_id = ?
    """, (
        id,
    ))

    db_execute(conn, """
        DELETE FROM test_results
        WHERE id = ?
    """, (
        id,
    ))

    db_commit(conn)
    db_close(conn)

    return redirect(url_for("admin_panel"))


# ==========================================
# DELETE TEST
# ==========================================

@app.route(
    "/delete-test/<int:id>",
    methods=["POST"]
)
def delete_test(id):

    if "admin" not in session:

        return redirect(url_for("admin_login"))

    conn = get_db_connection()

    db_execute(conn, """
        DELETE FROM test_answer_details
        WHERE result_id IN (
            SELECT id
            FROM test_results
            WHERE test_id = ?
        )
    """, (
        id,
    ))

    db_execute(
        conn,
        "DELETE FROM test_results WHERE test_id = ?",
        (id,)
    )

    db_execute(
        conn,
        "DELETE FROM test_questions WHERE test_id = ?",
        (id,)
    )

    db_execute(
        conn,
        "DELETE FROM tests WHERE id = ?",
        (id,)
    )

    db_commit(conn)
    db_close(conn)

    return redirect(url_for("admin_panel"))


# ==========================================
# LOGOUT
# ==========================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("home"))


# ==========================================
# INITIALIZE DATABASE
# ==========================================

init_db()


# ==========================================
# START APPLICATION
# ==========================================

if __name__ == "__main__":

    app.run(
        debug=True,
        host="0.0.0.0",
        port=int(
            os.environ.get(
                "PORT",
                5000
            )
        )
    )