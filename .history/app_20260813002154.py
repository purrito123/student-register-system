from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)


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

        conn = sqlite3.connect("database.db")
cursor = conn.cursor()

cursor.execute("""
    INSERT INTO students (name, dob, course, email, password)
    VALUES (?, ?, ?, ?, ?)
""", (name, dob, course, email, password))

conn.commit()
conn.close()

return "Registration received successfully!"

    return render_template("student_register.html")


@app.route("/admin-register")
def admin_register():
    return render_template("admin_register.html")


init_db()


if __name__ == "__main__":
    app.run(debug=True)