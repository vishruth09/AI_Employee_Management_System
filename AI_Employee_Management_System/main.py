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

@app.route("/add_employee", methods=['GET','POST'])
def add_employee():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        department = request.form['department']
        designation = request.form['designation']
        salary = request.form['salary']

        connection = get_connection()
        cursor = connection.cursor()
        query = """
        INSERT INTO employees(name, email, department, designation, salary)
        VALUES (%s, %s, %s, %s, %s)
        """

        cursor.execute(query ,(name,email,department,designation,salary))
        connection.commit()

        cursor.close()
        connection.close()
        return redirect(url_for("view_employees"))

    return render_template("add_employee.html")

@app.route("/delete_employee")
def delete_employee():
    return render_template("delete_employee.html")

@app.route("/view_employees")
def view_employees():
    connection = get_connection()
    cursor = connection.cursor()

    query = "SELECT * FROM employees"
    cursor.execute(query)

    employees = cursor.fetchall()

    cursor.close()
    connection.close()
    return render_template("view_employees.html",
                           employees=employees
                           )

@app.route("/update_employee")
def update_employee():
    return render_template("update_employee.html")

@app.route("/upload_documents")
def upload_documents():
    return render_template("upload_documents.html")



if __name__ == "__main__":
    app.run(debug=True)