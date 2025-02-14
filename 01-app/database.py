import mysql.connector
import pandas as pd

# Connect to MySQL Database
db = mysql.connector.connect(
    host="localhost",      # Change to your MySQL host
    user="root",      # Change to your MySQL username
    password="123456",  # Change to your MySQL password
    database="employee_management"
)

cursor = db.cursor()

# Fetch Admin Data
admin_queries = {
    "Organizations": "SELECT * FROM Organizations",
    "Facilities": "SELECT * FROM Facilities",
    "Vendors": "SELECT * FROM Vendors",
    "Locations": "SELECT * FROM Locations"
}

admin_writer = pd.ExcelWriter("admin_data.xlsx", engine="openpyxl")

for sheet_name, query in admin_queries.items():
    cursor.execute(query)
    data = cursor.fetchall()
    columns = [i[0] for i in cursor.description]
    df = pd.DataFrame(data, columns=columns)
    df.to_excel(admin_writer, sheet_name=sheet_name, index=False)

admin_writer.close()

# Fetch User Data
user_queries = {
    "Users": "SELECT * FROM Users",
    "BCM_Users": "SELECT * FROM BCM_Users",
    "BCM_Policies": "SELECT * FROM BCM_Policies"
}

user_writer = pd.ExcelWriter("user_data.xlsx", engine="openpyxl")

for sheet_name, query in user_queries.items():
    cursor.execute(query)
    data = cursor.fetchall()
    columns = [i[0] for i in cursor.description]
    df = pd.DataFrame(data, columns=columns)
    df.to_excel(user_writer, sheet_name=sheet_name, index=False)

user_writer.close()

cursor.close()
db.close()

print("Excel files created: admin_data.xlsx & user_data.xlsx")