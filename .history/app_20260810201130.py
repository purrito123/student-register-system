from flask import Flask, render_template, request

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("signup.html")


@app.route("/student-register", methods=["GET", "POST"])
def student_register():

    if request.method == "POST":

        name = request.form["name"]
        dob = request.form["dob"]
        course = request.form["course"]
        email = request.form["email"]
        password = request.form["password"]

        print("Name:", name)
        print("DOB:", dob)
        print("Course:", course)
        print("Email:", email)
        print("Password:", password)

        return "Registration received successfully!"

    return render_template("student_register.html")

@app.route("/admin-register")
def admin_register():
    return render_template("admin_register.html")


if __name__ == "__main__":
    app.run(debug=True)