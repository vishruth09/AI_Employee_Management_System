from flask import Flask, render_template, request
from database.connection import get_connection

app = Flask(__name__)
connection = get_connection()
cursor = connection.cursor()

cursor.execute("SELECT * FROM users")

users = cursor.fetchall()


@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        return f"Username: {username}<br>Password: {password}"

    return render_template("login.html")


if __name__ == "__main__":
    app.run(debug=True)