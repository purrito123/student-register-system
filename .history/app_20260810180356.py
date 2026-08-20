from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("signup.html")

@app.route("/")
def student_register():
    return render_template("student_register.html")

@app.route("/admin")
def admin_register():
    return render_template("admin_register.html")

if __name__ == "__main__":
    app.run(debug=True)