from flask import Flask, render_template, request,redirect,url_for
from database.connection import get_connection
from werkzeug.security import generate_password_hash,check_password_hash


app = Flask(__name__)
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        connection = get_connection()
        cursor = connection.cursor()

        query = "SELECT * FROM users WHERE username = %s"
        cursor.execute(query, (username,))
        user = cursor.fetchone()
        cursor.close()
        connection.close()
        if user:
            if check_password_hash(user[3],password):
                return redirect(url_for("admin"))
            else:
                return "Login Failed"
        else:
            return "User not found"

    return render_template("login.html")

@app.route("/admin")
def admin():
    return render_template("admin_dashboard.html")

@app.route("/add_employee")
def add_employee():
    return render_template("add_employee.html")



if __name__ == "__main__":
    app.run(debug=True)