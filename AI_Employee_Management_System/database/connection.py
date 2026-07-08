import mysql.connector


def get_connection():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Vishruth@7677",
        database="ai_employee_management"
    )

    return connection