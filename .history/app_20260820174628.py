from flask import Flask, render_template, request, session, redirect
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

        return render_template("registration_success.html")

    return render_template("student_register.html")


@app.route("/students")
def students():

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM students")

    students = cursor.fetchall()

    conn.close()

    return str(students)


@app.route("/admin-register", methods=["GET", "POST"])
def admin_register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        password_hash = generate_password_hash(password)

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO admins (name, email, password)
            VALUES (?, ?, ?)
        """, (name, email, password_hash))

        conn.commit()
        conn.close()

        return render_template("admin_registration_success.html")

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

    cursor.execute("""
        SELECT id, start_date, end_date, reason, status
        FROM leaves
        WHERE student_id = ?
    """, (student_id,))

    leaves = cursor.fetchall()

    conn.close()

    if student is None:
        return "Student not found."

    return render_template(
        "student_dashboard.html",
        student=student,
        leaves=leaves
    )

@app.route("/edit-profile", methods=["GET", "POST"])
def edit_profile():

    # Make sure student is logged in
    if "student_id" not in session:
        return redirect("/login")

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    student_id = session["student_id"]

    if request.method == "POST":

        name = request.form["name"]
        dob = request.form["dob"]
        course = request.form["course"]
        email = request.form["email"]

        cursor.execute("""
            UPDATE students
            SET name = ?, dob = ?, course = ?, email = ?
            WHERE id = ?
        """, (name, dob, course, email, student_id))

        conn.commit()
        conn.close()

        return redirect("/student-dashboard")

    cursor.execute(
        "SELECT * FROM students WHERE id = ?",
        (student_id,)
    )

    student = cursor.fetchone()

    conn.close()

    return render_template(
        "edit_profile.html",
        student=student
    )

@app.route("/logout")
def logout():
    session.clear()
    return render_template("logout.html")

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

        return render_template("leave_success.html")

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

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            password TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()

@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM admins WHERE email = ?",
            (email,)
        )

        admin = cursor.fetchone()

        conn.close()

        if admin:
            stored_password = admin[3]

        if check_password_hash(stored_password, password):

            session["admin_id"] = admin[0]

            return redirect("/admin-dashboard")

        return "Invalid admin email or password"

    return render_template("admin_login.html")

@app.route("/admin-dashboard")
def admin_dashboard():

    if "admin_id" not in session:
        return "Please login as admin first."

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            leaves.id,
            students.name,
            leaves.start_date,
            leaves.end_date,
            leaves.reason,
            leaves.status
        FROM leaves
        JOIN students
        ON leaves.student_id = students.id
    """)

    leaves = cursor.fetchall()

    conn.close()

    return render_template(
        "admin_dashboard.html",
        leaves=leaves
    )

@app.route("/student-database")
def student_database():

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM students
    """)

    students = cursor.fetchall()

    conn.close()

    return render_template(
        "student_database.html",
        students=students
    )

@app.route("/update-leave/<int:leave_id>", methods=["POST"])
def update_leave(leave_id):

    if "admin_id" not in session:
        return "Please login as admin first."

    status = request.form["status"]

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE leaves SET status = ? WHERE id = ?",
        (status, leave_id)
    )

    conn.commit()
    conn.close()

    return redirect("/admin-dashboard")

@app.route("/delete-all-leaves", methods=["POST"])
def delete_all_leaves():

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM leaves")

    conn.commit()
    conn.close()

    return redirect("/admin-dashboard")

@app.route("/delete-all-students", methods=["POST"])
def delete_all_students():

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # Delete leave requests first
    cursor.execute("DELETE FROM leaves")

    # Delete all student accounts
    cursor.execute("DELETE FROM students")

    conn.commit()
    conn.close()

    return redirect("/student-database")

init_db()

if __name__ == "__main__":
    app.run(debug=True)
