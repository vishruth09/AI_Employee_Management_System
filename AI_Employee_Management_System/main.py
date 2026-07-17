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

@app.route("/update_employee/<int:employee_id>",methods=['GET','POST'])
def update_employee(employee_id):
    if request.method == 'POST':
        name = request.form["name"]
        email = request.form["email"]
        department = request.form["department"]
        designation = request.form["designation"]
        salary = request.form["salary"]

        connection = get_connection()
        cursor = connection.cursor()
        query = """
            UPDATE employees
            SET
                name=%s,
                email=%s,
                department=%s,
                designation=%s,
                salary=%s
            WHERE employee_id=%s
            """
        cursor.execute(query,
            (
                name,
                email,
                department,
                designation,
                salary,
                employee_id
            )
        )
        connection.commit()
        cursor.close()
        connection.close()
        return redirect(url_for("view_employees"))


    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    query = "SELECT * FROM employees WHERE employee_id = %s"
    cursor.execute(query,(employee_id,))
    employee = cursor.fetchone()
    cursor.close()
    connection.close()
    return render_template("update_employee.html",
                           employee = employee
                           )

@app.route("/delete_employee/<int:employee_id>",methods=['GET','POST'])
def delete_employee(employee_id):
    if request.method == 'POST':
        connection = get_connection()
        cursor = connection.cursor()
        query = "DELETE FROM employees WHERE employee_id = %s"
        cursor.execute(query,(employee_id,))
        connection.commit()
        cursor.close()
        connection.close()
        return redirect(url_for('view_employees'))

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    query = "SELECT * FROM employees WHERE employee_id = %s"
    cursor.execute(query, (employee_id,))
    employee = cursor.fetchone()
    cursor.close()
    connection.close()
    return render_template("delete_employee.html",
                           employee = employee
                           )



@app.route("/upload_documents")
def upload_documents():
    return render_template("upload_documents.html")



from datetime import date

@app.route("/mark_attendance", methods=["GET", "POST"])
def mark_attendance():

    if request.method == "POST":
        today_date = date.today()
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        query = """
        SELECT *
        FROM attendance
        WHERE attendance_date = %s LIMIT 1
        """
        cursor.execute(query, (today_date,))
        attendance = cursor.fetchone()
        if attendance:
            cursor.close()
            connection.close()
            return "Today's attendance has already been marked."

        query = "SELECT * FROM employees"
        cursor.execute(query)
        employees = cursor.fetchall()
        for employee in employees:
            employee_id = employee["employee_id"]
            status = request.form[f"status_{employee_id}"]
            query = """
            INSERT INTO attendance
            (employee_id, attendance_date, status)
            VALUES
            (%s, %s, %s)
            """
            cursor.execute(
                query,
                (
                    employee_id,
                    today_date,
                    status
                )
            )
        connection.commit()
        cursor.close()
        connection.close()
        return redirect(url_for("admin"))

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    query = "SELECT * FROM employees"
    cursor.execute(query)
    employees = cursor.fetchall()
    cursor.close()
    connection.close()
    today_date = date.today()
    formatted_date = today_date.strftime("%d-%m-%Y")
    return render_template(
        "mark_attendance.html",
        employees=employees,
        formatted_date=formatted_date
    )


@app.route("/view_attendance", methods=["GET", "POST"])
def view_attendance():

    if request.method == "POST":
        attendance_date = request.form["attendance_date"]
    else:
        attendance_date = date.today()

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    query = """
        SELECT
            employees.employee_id,
            employees.name,
            employees.department,
            attendance.attendance_date,
            attendance.status
        FROM attendance
        JOIN employees
            ON employees.employee_id = attendance.employee_id
        WHERE attendance.attendance_date = %s
    """

    cursor.execute(query, (attendance_date,))
    attendance = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "view_attendance.html",
        attendance=attendance,
        today_date=attendance_date
    )


if __name__ == "__main__":
    app.run(debug=True)