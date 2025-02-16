import mysql.connector
import pandas as pd

def init_db():
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="123456",
        database="employee_management"
    )
    cursor = db.cursor()
    
    # Create tables if they don't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS organization (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS org_group (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            organization_id INT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (organization_id) REFERENCES organization(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS business_unit (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            org_group_id INT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (org_group_id) REFERENCES org_group(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS subfunction (
            id INT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            business_unit_id INT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (business_unit_id) REFERENCES business_unit(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS faculties (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    db.commit()
    cursor.close()
    db.close()

def export_data():
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="123456",
        database="employee_management"
    )
    cursor = db.cursor()

    # Fetch Admin Data
    admin_queries = {
        "Organizations": "SELECT * FROM organization",
        "Facilities": "SELECT * FROM faculties",
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

if __name__ == "__main__":
    init_db()
    export_data()
