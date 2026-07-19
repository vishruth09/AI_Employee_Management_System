from flask import Flask, render_template, request,redirect,url_for,flash
from database.connection import get_connection
from werkzeug.security import generate_password_hash,check_password_hash


app = Flask(__name__)
app.secret_key = "employee_management_secret_key"
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



from datetime import date,time,datetime,timedelta

@app.route("/mark_attendance", methods=["GET", "POST"])
def mark_attendance():

    if request.method == "POST":
        today_date = date.today()
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        query = """
        SELECT attendance_id
        FROM attendance
        WHERE attendance_date = %s LIMIT 1
        """
        cursor.execute(query, (today_date,))
        attendance = cursor.fetchone()
        if attendance:
            cursor.close()
            connection.close()
            flash(
                "Today's attendance has already been marked.",
                "warning"
            )

            return redirect(url_for("view_attendance"))

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
        return redirect(url_for("view_attendance"))

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

    elif request.args.get("attendance_date"):
        attendance_date = request.args.get("attendance_date")

    else:
        attendance_date = date.today()

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    query = """
    SELECT
        attendance.attendance_id,
        attendance.employee_id,
        employees.name,
        employees.department,
        attendance.attendance_date,
        attendance.status,
        attendance.check_in,
        attendance.check_out,
        attendance.is_late,
        attendance.total_hours
    FROM attendance
    JOIN employees
        ON attendance.employee_id = employees.employee_id
    WHERE attendance.attendance_date = %s
    ORDER BY attendance.employee_id
    """

    cursor.execute(query, (attendance_date,))
    attendance = cursor.fetchall()

    present_count = 0
    absent_count = 0
    leave_count = 0
    half_day_count = 0

    for record in attendance:
        record["attendance_date_display"] = record["attendance_date"].strftime("%d-%b-%Y")
        if record["check_in"]:

            total_seconds = int(record["check_in"].total_seconds())

            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60

            am_pm = "AM"

            if hours >= 12:
                am_pm = "PM"

            display_hour = hours % 12

            if display_hour == 0:
                display_hour = 12

            record["check_in_display"] = f"{display_hour:02}:{minutes:02} {am_pm}"

        else:

            record["check_in_display"] = "-"

            # -------------------------
            # Check Out
            # -------------------------

        if record["check_out"]:

            total_seconds = int(record["check_out"].total_seconds())

            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60

            am_pm = "AM"

            if hours >= 12:
                am_pm = "PM"

            display_hour = hours % 12

            if display_hour == 0:
                display_hour = 12

            record["check_out_display"] = f"{display_hour:02}:{minutes:02} {am_pm}"

        else:

            record["check_out_display"] = "-"


        if record["status"] == "Present":
            present_count += 1

        elif record["status"] == "Absent":
            absent_count += 1

        elif record["status"] == "Leave":
            leave_count += 1

        elif record["status"] == "Half Day":
            half_day_count += 1


    cursor.close()
    connection.close()
    return render_template(
        "view_attendance.html",
        attendance=attendance,
        attendance_date=attendance_date,
        present_count=present_count,
        absent_count=absent_count,
        leave_count=leave_count,
        half_day_count=half_day_count
    )

@app.route("/check_in/<int:attendance_id>", methods=["POST"])
def check_in(attendance_id):

    current_time = datetime.now().time()

    office_time = time(9, 0)

    connection = get_connection()

    cursor = connection.cursor(dictionary=True)

    query = """
    SELECT *
    FROM attendance
    WHERE attendance_id=%s
    """

    cursor.execute(query, (attendance_id,))

    attendance = cursor.fetchone()

    if attendance is None:

        cursor.close()
        connection.close()

        return "Attendance record not found."

    if attendance["status"] != "Present":

        cursor.close()
        connection.close()

        return "Only Present employees can check in."

    if attendance["check_in"] is not None:

        cursor.close()
        connection.close()

        return "Employee already checked in."

    if current_time > office_time:

        is_late = True

    else:

        is_late = False

    query = """
    UPDATE attendance

    SET

    check_in=%s,

    is_late=%s

    WHERE attendance_id=%s
    """

    cursor.execute(

        query,

        (

            current_time,

            is_late,

            attendance_id

        )

    )

    connection.commit()

    attendance_date = attendance["attendance_date"]

    cursor.close()

    connection.close()

    return redirect(url_for("view_attendance",attendance_date=attendance_date))

@app.route("/check_out/<int:attendance_id>", methods=["POST"])
def check_out(attendance_id):

    current_time = datetime.now().time()

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    query = """
    SELECT *
    FROM attendance
    WHERE attendance_id = %s
    """

    cursor.execute(query, (attendance_id,))
    attendance = cursor.fetchone()

    if attendance is None:
        cursor.close()
        connection.close()
        return "Attendance record not found."

    if attendance["status"] != "Present":
        cursor.close()
        connection.close()
        return "Employee is not Present."

    if attendance["check_in"] is None:
        cursor.close()
        connection.close()
        return "Employee has not checked in."

    if attendance["check_out"] is not None:
        cursor.close()
        connection.close()
        return "Employee already checked out."

    # -----------------------------
    # Calculate Total Working Hours
    # -----------------------------

    check_in_timedelta = attendance["check_in"]

    current_seconds = (
        current_time.hour * 3600 +
        current_time.minute * 60 +
        current_time.second
    )

    check_out_timedelta = timedelta(seconds=current_seconds)

    difference = check_out_timedelta - check_in_timedelta

    total_hours = round(
        difference.total_seconds() / 3600,
        2
    )

    # -----------------------------
    # Update Database
    # -----------------------------

    query = """
    UPDATE attendance
    SET
        check_out = %s,
        total_hours = %s
    WHERE attendance_id = %s
    """

    cursor.execute(
        query,
        (
            current_time,
            total_hours,
            attendance_id
        )
    )

    connection.commit()

    attendance_date = attendance["attendance_date"]

    cursor.close()
    connection.close()

    return redirect(
        url_for(
            "view_attendance",
            attendance_date=attendance_date
        )
    )

@app.route("/edit_attendance/<int:employee_id>/<attendance_date>", methods=["GET", "POST"])
def edit_attendance(employee_id, attendance_date):

    if request.method == "POST":
        status = request.form["status"]

        connection = get_connection()
        cursor = connection.cursor()

        query = """
            UPDATE attendance
            SET status = %s
            WHERE employee_id = %s
            AND attendance_date = %s
        """

        cursor.execute(query, (status, employee_id, attendance_date))

        connection.commit()

        cursor.close()
        connection.close()

        return redirect(url_for("view_attendance",attendance_date=attendance_date))


    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    query = """
        SELECT
            e.employee_id,
            e.name,
            e.department,
            a.attendance_date,
            a.status
        FROM attendance AS a
        JOIN employees AS e
            ON a.employee_id = e.employee_id
        WHERE a.employee_id = %s
        AND a.attendance_date = %s
    """

    cursor.execute(query, (employee_id, attendance_date))

    attendance = cursor.fetchone()
    attendance["attendance_date_display"] = attendance["attendance_date"].strftime("%d-%b-%Y")
    cursor.close()
    connection.close()

    return render_template("edit_attendance.html",attendance=attendance)

@app.route("/monthly_report", methods=["GET", "POST"])
def monthly_report():
    if request.method == "POST":
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        employee_id = request.form["employee_id"]
        month = request.form["month"]
        year = request.form["year"]
        query = """
        SELECT attendance_date, status
        FROM attendance
        WHERE employee_id = %s
        AND MONTH(attendance_date) = %s
        AND YEAR(attendance_date) = %s
        ORDER BY attendance_date;
        """
        cursor.execute(query, (employee_id, month, year))

        attendance_records = cursor.fetchall()
        present_count = 0
        absent_count = 0
        half_day_count = 0
        for record in attendance_records:

            if record["status"] == "Present":
                present_count += 1

            elif record["status"] == "Absent":
                absent_count += 1

            elif record["status"] == "Half Day":
                half_day_count += 1
        working_days = len(attendance_records)
        if working_days > 0:
            attendance_percentage = ( (present_count + (half_day_count * 0.5))/ working_days) * 100
        else:
            attendance_percentage = 0
        query = """
        SELECT *
        FROM employees
        WHERE employee_id = %s
        """

        cursor.execute(query, (employee_id,))

        employee = cursor.fetchone()
        cursor.close()
        connection.close()
        return render_template(
            "monthly_report_view.html",
            employee=employee,
            attendance_records=attendance_records,
            present_count=present_count,
            absent_count=absent_count,
            half_day_count=half_day_count,
            working_days=working_days,
            attendance_percentage=attendance_percentage,
            month=month,
            year=year
        )

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    # Fetch all employees for the dropdown
    query = """
    SELECT employee_id, name
    FROM employees
    ORDER BY name;
    """
    cursor.execute(query)
    employees = cursor.fetchall()

    cursor.close()
    connection.close()
    return render_template("monthly_report.html", employees=employees)


if __name__ == "__main__":
    app.run(debug=True)