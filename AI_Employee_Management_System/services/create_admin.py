from werkzeug.security import generate_password_hash
from AI_Employee_Management_System.database.connection import get_connection

connection = get_connection()
cursor = connection.cursor()

username = "admin"
email = "admin@gmail.com"
password = generate_password_hash("admin123")
role = "Admin"

query = """
INSERT INTO users(username, email, password, role)
VALUES (%s, %s, %s, %s)
"""

cursor.execute(query, (username, email, password, role))

connection.commit()

cursor.close()
connection.close()

print("Admin created successfully!")