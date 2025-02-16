import mysql.connector
from werkzeug.security import generate_password_hash

# Database configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '123456',
    'database': 'employee_management'
}

# Generate hashed password
plain_password = "Admin@123"  # Change as needed
hashed_password = generate_password_hash(plain_password)

# Insert the dummy admin user
query = """
INSERT INTO users (email, password_hash, name, position, department, created_at) 
VALUES (%s, %s, %s, %s, %s, NOW());
"""

values = ("admin@example.com", hashed_password, "Admin User", "Admin", None)

try:
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute(query, values)
    conn.commit()
    print("Admin user inserted successfully.")
except mysql.connector.Error as e:
    print(f"Error: {e}")
finally:
    cursor.close()
    conn.close()
