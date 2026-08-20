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

    # ==========================================
    # TEST SYSTEM TABLES
    # ==========================================

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
            percentage REAL NOT NULL,
            submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    try:
        conn.execute("""
            ALTER TABLE test_results
            ADD COLUMN timeout_answers INTEGER NOT NULL DEFAULT 0
        """)
    except sqlite3.OperationalError:
        pass

    conn.execute("""
        CREATE TABLE IF NOT EXISTS test_answer_details (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            result_id INTEGER NOT NULL,
            question_id INTEGER NOT NULL,
            question TEXT NOT NULL,
            selected_answer TEXT,
            correct_answer TEXT NOT NULL,
            is_correct INTEGER NOT NULL
        )
    """)

    try:
        conn.execute("""
            ALTER TABLE test_answer_details
            ADD COLUMN is_timeout INTEGER NOT NULL DEFAULT 0
        """)
    except sqlite3.OperationalError:
        pass

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
        """, (
            name,
            roll_number,
            course,
            mobile
        ))

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

        total_fees = float(request.form["total_fees"])
        submitted_fees = float(request.form["submitted_fees"])

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

        total_fees = float(request.form["total_fees"])
        submitted_fees = float(request.form["submitted_fees"])

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

    tests_data = conn.execute("""
        SELECT
            tests.*,
            COUNT(test_questions.id) AS question_count
        FROM tests
        LEFT JOIN test_questions
        ON tests.id = test_questions.test_id
        GROUP BY tests.id
        ORDER BY tests.id DESC
    """).fetchall()

    conn.close()

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

    tests_data = conn.execute("""
        SELECT
            tests.*,
            COUNT(test_questions.id) AS question_count
        FROM tests
        LEFT JOIN test_questions
        ON tests.id = test_questions.test_id
        GROUP BY tests.id
        ORDER BY tests.id DESC
    """).fetchall()

    test_results_data = conn.execute("""
        SELECT
            test_results.*,
            tests.title,
            tests.subject
        FROM test_results
        JOIN tests
        ON test_results.test_id = tests.id
        ORDER BY test_results.id DESC
    """).fetchall()

    conn.close()

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

        return redirect(url_for("admin_panel"))

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

    cursor = conn.execute("""
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

        if (
            not option_a[i].strip()
            or not option_b[i].strip()
            or not option_c[i].strip()
            or not option_d[i].strip()
            or correct_answers[i].strip().upper()
            not in ["A", "B", "C", "D"]
        ):
            continue

        conn.execute("""
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
            correct_answers[i].strip().upper()
        ))

        valid_question_count += 1

    if valid_question_count == 0:

        conn.execute(
            "DELETE FROM tests WHERE id = ?",
            (test_id,)
        )

        conn.commit()
        conn.close()

        return "Please add at least one complete question with options!"

    conn.commit()
    conn.close()

    return redirect(url_for("admin_panel"))


# ==========================================
# START TEST
# ==========================================

@app.route("/start-test/<int:id>")
def start_test(id):

    if "user" not in session:
        return redirect(url_for("login"))

    conn = get_db_connection()

    test = conn.execute(
        "SELECT * FROM tests WHERE id = ?",
        (id,)
    ).fetchone()

    questions = conn.execute("""
        SELECT *
        FROM test_questions
        WHERE test_id = ?
        ORDER BY id ASC
    """, (id,)).fetchall()

    conn.close()

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

@app.route("/submit-test/<int:test_id>", methods=["POST"])
def submit_test(test_id):

    if "user" not in session:
        return redirect(url_for("login"))

    conn = get_db_connection()

    test = conn.execute(
        "SELECT * FROM tests WHERE id = ?",
        (test_id,)
    ).fetchone()

    if test is None:
        conn.close()
        return "Test Not Found!"

    questions = conn.execute("""
        SELECT *
        FROM test_questions
        WHERE test_id = ?
        ORDER BY id ASC
    """, (test_id,)).fetchall()

    total_questions = len(questions)

    correct_answers = 0
    wrong_answers = 0
    timeout_answers = 0


    # ==========================================
    # GET TIMEOUT QUESTION IDs
    # ==========================================

    timed_out_question_ids = request.form.getlist(
        "timed_out_question"
    )

    timed_out_question_ids = {
        str(question_id)
        for question_id in timed_out_question_ids
    }


    # ==========================================
    # COUNT RESULTS
    # ==========================================

    for question in questions:

        question_id = str(question["id"])

        selected_answer = request.form.get(
            f"answer_{question['id']}",
            ""
        ).strip().upper()


        # TIME OUT
        if question_id in timed_out_question_ids:

            timeout_answers += 1
            continue


        # CORRECT
        if (
            selected_answer
            and selected_answer ==
            question["correct_answer"].upper()
        ):

            correct_answers += 1


        # WRONG
        elif selected_answer:

            wrong_answers += 1


        # UNATTEMPTED
        # Isko wrong_answers mein count nahi kiya jayega.
        else:

            pass


    percentage = 0

    if total_questions > 0:

        percentage = round(
            (correct_answers / total_questions) * 100,
            2
        )


    # ==========================================
    # SAVE MAIN RESULT
    # ==========================================

    cursor = conn.execute("""
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


    # ==========================================
    # SAVE EVERY QUESTION DETAIL
    # ==========================================

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
            if question_id in timed_out_question_ids
            else 0
        )


        if is_timeout:

            selected_answer = ""


        is_correct = (
            1
            if (
                not is_timeout
                and selected_answer
                and selected_answer == correct_answer
            )
            else 0
        )


        conn.execute("""
            INSERT INTO test_answer_details
            (
                result_id,
                question_id,
                question,
                selected_answer,
                correct_answer,
                is_correct,
                is_timeout
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            result_id,
            question["id"],
            question["question"],
            selected_answer,
            correct_answer,
            is_correct,
            is_timeout
        ))


    conn.commit()
    conn.close()


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

    if "user" not in session and "admin" not in session:
        return redirect(url_for("login"))

    conn = get_db_connection()

    result = conn.execute("""
        SELECT
            test_results.*,
            tests.title,
            tests.subject
        FROM test_results
        JOIN tests
        ON test_results.test_id = tests.id
        WHERE test_results.id = ?
    """, (id,)).fetchone()

    if result is None:

        conn.close()

        return "Result Not Found!"


    if (
        "user" in session
        and result["username"] != session["user"]
    ):

        conn.close()

        return "You are not allowed to view this result!"


    # ==========================================
    # CORRECT QUESTIONS
    # ==========================================

    correct_questions = conn.execute("""
        SELECT *
        FROM test_answer_details
        WHERE result_id = ?
        AND is_correct = 1
        AND is_timeout = 0
        ORDER BY id ASC
    """, (id,)).fetchall()


    # ==========================================
    # INCORRECT QUESTIONS
    # ==========================================

    wrong_questions = conn.execute("""
        SELECT *
        FROM test_answer_details
        WHERE result_id = ?
        AND is_correct = 0
        AND is_timeout = 0
        AND selected_answer IS NOT NULL
        AND selected_answer != ''
        ORDER BY id ASC
    """, (id,)).fetchall()


    # ==========================================
    # UNATTEMPTED QUESTIONS
    # ==========================================

    unattempted_questions = conn.execute("""
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
    """, (id,)).fetchall()


    # ==========================================
    # TIME OUT QUESTIONS
    # ==========================================

    timeout_questions = conn.execute("""
        SELECT *
        FROM test_answer_details
        WHERE result_id = ?
        AND is_timeout = 1
        ORDER BY id ASC
    """, (id,)).fetchall()


    conn.close()


    return render_template(
        "test_result.html",
        result=result,
        correct_questions=correct_questions,
        wrong_questions=wrong_questions,
        unattempted_questions=unattempted_questions,
        timeout_questions=timeout_questions
    )


# ==========================================
# DELETE TEST
# ==========================================

@app.route("/delete-test/<int:id>", methods=["POST"])
def delete_test(id):

    if "admin" not in session:
        return redirect(url_for("admin_login"))

    conn = get_db_connection()

    conn.execute(
        "DELETE FROM test_questions WHERE test_id = ?",
        (id,)
    )

    conn.execute("""
        DELETE FROM test_answer_details
        WHERE result_id IN (
            SELECT id
            FROM test_results
            WHERE test_id = ?
        )
    """, (id,))

    conn.execute(
        "DELETE FROM test_results WHERE test_id = ?",
        (id,)
    )

    conn.execute(
        "DELETE FROM tests WHERE id = ?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("admin_panel"))


# ==========================================
# LOGOUT
# ==========================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("home"))


# ==========================================
# START APPLICATION
# ==========================================

if __name__ == "__main__":

    init_db()

    app.run(debug=True)