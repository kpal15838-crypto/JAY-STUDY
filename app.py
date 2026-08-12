from flask import Flask, render_template, request

app = Flask(__name__)

students_list = []
fees_list = []


@app.route("/")
def home():
    return render_template("dashboard.html")


@app.route("/students", methods=["GET", "POST"])
def students():

    if request.method == "POST":
        name = request.form["name"]
        roll_number = request.form["roll_number"]
        course = request.form["course"]
        mobile = request.form["mobile"]

        student = {
            "name": name,
            "roll_number": roll_number,
            "course": course,
            "mobile": mobile
        }

        students_list.append(student)

    return render_template("students.html", students=students_list)


@app.route("/fees", methods=["GET", "POST"])
def fees():

    if request.method == "POST":
        name = request.form["name"]
        roll_number = request.form["roll_number"]
        total_fees = float(request.form["total_fees"])
        submitted_fees = float(request.form["submitted_fees"])

        remaining_fees = total_fees - submitted_fees

        fee = {
            "name": name,
            "roll_number": roll_number,
            "total_fees": total_fees,
            "submitted_fees": submitted_fees,
            "remaining_fees": remaining_fees
        }

        fees_list.append(fee)

    return render_template("fees.html", fees=fees_list)
@app.route("/signature")
def signature():
    return render_template("signature.html")


if __name__ == "__main__":
    app.run(debug=True)


if __name__ == "__main__":
    app.run(debug=True)