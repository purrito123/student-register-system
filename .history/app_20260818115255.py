from flask import Flask, render_template, request, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "student-registration-secret"


def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            dob TEXT NOT NULL,
            course TEXT NOT NULL,
            email TEXT NOT NULL,
            password TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


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

        password_hash = generate_password_hash(password)

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO students (name, dob, course, email, password)
            VALUES (?, ?, ?, ?, ?)
        """, (name, dob, course, email, password_hash))

        conn.commit()
        conn.close()

        return "Registration received successfully!"

    return render_template("student_register.html")


@app.route("/students")
def students():

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM students")

    students = cursor.fetchall()

    conn.close()

    return str(students)


@app.route("/admin-register")
def admin_register():
    return render_template("admin_register.html")


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM students WHERE email = ?",
            (email,)
        )

        student = cursor.fetchone()

        conn.close()

        if student:
            stored_password = student[5]

            if check_password_hash(stored_password, password):
                session["student_id"] = student[0]
            return render_template("student_dashboard.html", student=student)

        return "Invalid email or password"

    return render_template("login.html")

@app.route("/student-dashboard")
def student_dashboard():

    if "student_id" not in session:
        return "Please login first."

    student_id = session["student_id"]

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, name, dob, course, email FROM students WHERE id = ?",
        (student_id,)
    )

    student = cursor.fetchone()

    conn.close()

    if student is None:
        return "Student not found."

    return render_template("student_dashboard.html", student=student)

@app.route("/logout")
def logout():

    session.clear()

    return "You have been logged out."

@app.route("/apply-leave", methods=["GET", "POST"])
def apply_leave():

    if "student_id" not in session:
        return "Please login first."

    if request.method == "POST":

        start_date = request.form["start_date"]
        end_date = request.form["end_date"]
        reason = request.form["reason"]

        student_id = session["student_id"]

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO leaves
            (student_id, start_date, end_date, reason)
            VALUES (?, ?, ?, ?)
        """, (student_id, start_date, end_date, reason))

        conn.commit()
        conn.close()

        return "Leave request submitted successfully!"

    return render_template("apply_leave.html")

def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            dob TEXT NOT NULL,
            course TEXT NOT NULL,
            email TEXT NOT NULL,
            password TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leaves (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            reason TEXT NOT NULL,
            status TEXT DEFAULT 'Pending'
        )
    """)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    app.run(debug=True)