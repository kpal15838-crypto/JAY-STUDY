from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)

app.secret_key = "jay-study-library-secret-key-2026"


# ==========================================
# DATA STORAGE
# ==========================================

students_list = []
fees_list = []
users_list = []

question_papers_list = []


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

        student = {
            "name": request.form["name"],
            "roll_number": request.form["roll_number"],
            "course": request.form["course"],
            "mobile": request.form["mobile"]
        }

        students_list.append(student)

        # Admin panel se add karne ke baad wapas Admin Panel
        if "admin" in session:
            return redirect(url_for("admin_panel"))

    return render_template(
        "students.html",
        students=students_list
    )


# ==========================================
# FEES
# ==========================================

@app.route("/fees", methods=["GET", "POST"])
def fees():

    if request.method == "POST":

        total_fees = float(request.form["total_fees"])
        submitted_fees = float(request.form["submitted_fees"])

        fee = {
            "name": request.form["name"],
            "roll_number": request.form["roll_number"],
            "total_fees": total_fees,
            "submitted_fees": submitted_fees,
            "remaining_fees": total_fees - submitted_fees
        }

        fees_list.append(fee)

        # Admin panel se add karne ke baad wapas Admin Panel
        if "admin" in session:
            return redirect(url_for("admin_panel"))

    return render_template(
        "fees.html",
        fees=fees_list
    )


# ==========================================
# SIGNATURE
# ==========================================

@app.route("/signature")
def signature():
    return render_template("signature.html")


# ==========================================
# USER REGISTRATION
# ==========================================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        for user in users_list:
            if user["username"] == username:
                return "Username already exists!"

        users_list.append({
            "username": username,
            "password": password
        })

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

        for user in users_list:

            if user["username"] == username and user["password"] == password:

                session["user"] = username

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

    return render_template(
        "user_panel.html",
        question_papers=question_papers_list,
        username=session["user"]
    )


# ==========================================
# ADMIN LOGIN
# ==========================================

@app.route("/admin", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "Jay@12345":

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

    return render_template(
        "admin_panel.html",
        question_papers=question_papers_list,
        users=users_list,
        students=students_list,
        fees=fees_list
    )


# ==========================================
# ADD QUESTION PAPER
# ==========================================

@app.route("/add-question-paper", methods=["POST"])
def add_question_paper():

    if "admin" not in session:
        return redirect(url_for("admin_login"))

    question_paper = {
        "id": len(question_papers_list) + 1,
        "title": request.form["title"],
        "subject": request.form["subject"],
        "year": request.form["year"]
    }

    question_papers_list.append(question_paper)

    return redirect(url_for("admin_panel"))


# ==========================================
# LOGOUT
# ==========================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("home"))


# ==========================================
# RUN APPLICATION
# ==========================================

if __name__ == "__main__":
    app.run(debug=True)