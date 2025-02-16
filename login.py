# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import os
import jwt
from functools import wraps
from datetime import datetime, timedelta
import mysql.connector
from flask import send_file
from mysql.connector import Error
from pymongo import MongoClient
import gridfs
from bson import ObjectId
from datetime import datetime
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from datetime import datetime, timedelta
import pandas as pd
from io import BytesIO
import pandas as pd
from werkzeug.utils import secure_filename
import tempfile

app = Flask(__name__)
CORS(app)

# Enable CORS for all origins and methods
# CORS(app, supports_credentials=True, resources={
#     r"/*": {
#         "origins": ["http://localhost:3000"],  # Replace with your React app's URL
#         "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
#         "allow_headers": ["Content-Type", "Authorization","Access-Control-Allow-Headers"],
#         "expose_headers": ["Content-Type", "Authorization","Access-Control-Allow-Headers"],
#         "supports_credentials": True
#     }
# })

# Replace existing CORS config with:
from flask_cors import CORS

# Enable CORS for all origins and methods
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:3000", "http://localhost:3001", "http://localhost:3002", "http://localhost:3003"],
        "allow_headers": ["Content-Type", "Authorization", "Access-Control-Allow-Headers"],
        "supports_credentials": True,
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    }
})


# Configuration
app.config['SECRET_KEY'] = os.urandom(24)
app.config['JWT_EXPIRATION_HOURS'] = 24

# Database configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Rr_130425',
    'database': 'employee_management'
}


def init_db():
    conn = None
    try:
        # Establish database connection
        conn = mysql.connector.connect(**db_config)
        if conn.is_connected():
            print("Connected to MySQL database")

        cursor = conn.cursor()

        # Create 'users' table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                name VARCHAR(255) NOT NULL,
                position ENUM('CEO', 'Employee', 'Manager', 'Admin') DEFAULT 'Employee',
                department ENUM('Sales', 'Finance', 'Logistics') NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Create other required tables based on the application's needs
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS organization (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS org_group (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS business_unit (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS subfunction (
                id INT PRIMARY KEY,
                business_unit_id INT NOT NULL,
                name VARCHAR(255) NOT NULL,
                FOREIGN KEY (business_unit_id) REFERENCES business_unit(id) ON DELETE CASCADE
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS faculties (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL
            )
        ''')

        conn.commit()
        print("Database tables initialized successfully!")

    except Error as err:
        print(f"Error: {err}")
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

# Initialize database on startup
init_db()


def get_db_connection():
    return mysql.connector.connect(**db_config)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        
        try:
            token = token.split(" ")[1]  # Remove 'Bearer ' prefix
            
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            
            current_user_id = data.get('user_id')
            if current_user_id is None:
                return jsonify({"error": "User ID is missing"}), 400
            
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token'}), 401

        return f(current_user_id, *args, **kwargs)
    
    return decorated


# User Registration Endpoint
@app.route('/api/register', methods=['POST'])
def register():
    if request.method == 'OPTIONS':
        # Handle preflight request
        response = jsonify({'message': 'Preflight request received'})
        response.headers.add('Access-Control-Allow-Origin', 'http://localhost:3000')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response
    data = request.json
    required_fields = ['email', 'password', 'name']
    
    if data.get('position') in ['Manager', 'Employee']:
        required_fields.append('department')
    
    if not all(k in data for k in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Check if user already exists
        cursor.execute('SELECT id FROM users WHERE email = %s', (data['email'],))
        if cursor.fetchone():
            return jsonify({'error': 'Email already registered'}), 409
        
        # Hash password and create user
        password_hash = generate_password_hash(data['password'])
        
        if 'department' in data:
            cursor.execute(
                'INSERT INTO users (email, password_hash, name, department) VALUES (%s, %s, %s, %s)',
                (data['email'], password_hash, data['name'], data['department'])
            )
        else:
            cursor.execute(
                'INSERT INTO users (email, password_hash, name) VALUES (%s, %s, %s)',
                (data['email'], password_hash, data['name'])
            )
        
        conn.commit()
        return jsonify({
            'message': 'User registered successfully',
            'user_id': cursor.lastrowid
        }), 201
            
    except Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()


VALID_ENTITIES = ["organization", "org_group", "business_unit", "subfunction", "faculties", "vendor", "location"]

@app.route('/api/create_<entity>', methods=['POST'])
@token_required
def create_entity(user_id, entity):
    if entity not in VALID_ENTITIES:
        return jsonify({'error': 'Invalid entity'}), 400

    data = request.json

    if entity == "subfunction":
        subfunction_id = data.get('id')
        business_unit_id = data.get('business_unit_id')
        name = data.get('name')

        if not all([subfunction_id, business_unit_id, name]):
            return jsonify({'error': 'id, business_unit_id, and name are required'}), 400

        query = 'INSERT INTO subfunction (id, business_unit_id, name) VALUES (%s, %s, %s)'
        values = (subfunction_id, business_unit_id, name)
    
    else:
        name = data.get('name')
        if not name:
            return jsonify({'error': 'Name is required'}), 400

        query = f'INSERT INTO {entity} (name) VALUES (%s)'
        values = (name,)

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, values)
        conn.commit()
        return jsonify({'message': f'{entity} created successfully'}), 201
    except Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/create_vendor', methods=['POST'])
def create_vendor():
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'message': 'Unauthorized'}), 403

    data = request.json
    vendor_name = data['vendor_name']
    vendor_email = data['vendor_email']

    cursor = mysql.connection.cursor()
    cursor.execute("INSERT INTO vendors (vendor_name, vendor_email) VALUES (%s, %s)", (vendor_name, vendor_email))
    mysql.connection.commit()
    cursor.close()

    return jsonify({'message': 'Vendor created successfully'}), 201

@app.route('/manage_vendor', methods=['GET'])
def manage_vendor():
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'message': 'Unauthorized'}), 403

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM vendors")
    vendors = cursor.fetchall()
    cursor.close()

    return jsonify(vendors), 200

@app.route('/create_location', methods=['POST'])
def create_location():
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'message': 'Unauthorized'}), 403

    data = request.json
    location_name = data['location_name']
    location_address = data['location_address']

    cursor = mysql.connection.cursor()
    cursor.execute("INSERT INTO locations (location_name, location_address) VALUES (%s, %s)", (location_name, location_address))
    mysql.connection.commit()
    cursor.close()

    return jsonify({'message': 'Location created successfully'}), 201

@app.route('/manage_location', methods=['GET'])
def manage_location():
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'message': 'Unauthorized'}), 403

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM locations")
    locations = cursor.fetchall()
    cursor.close()

    return jsonify(locations), 200

@app.route('/api/manage_<entity>', methods=['GET'])
@token_required
def manage_entity(user_id, entity):
    if entity not in VALID_ENTITIES:
        return jsonify({'error': 'Invalid entity'}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(f'SELECT * FROM {entity}')
        entities = cursor.fetchall()
        return jsonify(entities), 200
    except Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()


@app.route('/api/delete_<entity>', methods=['DELETE'])
@token_required
def delete_entity(user_id, entity):
    if entity not in VALID_ENTITIES:
        return jsonify({'error': 'Invalid entity'}), 400

    data = request.json
    entity_id = data.get('id')

    if not entity_id:
        return jsonify({'error': 'ID is required'}), 400
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(f'DELETE FROM {entity} WHERE id = %s', (entity_id,))
        conn.commit()
        return jsonify({'message': f'{entity} deleted successfully'}), 200
    except Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()


@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    
    if not all(k in data for k in ['email', 'password']):
        return jsonify({'error': 'Missing email or password'}), 400
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute(
            'SELECT id, password_hash, name, position, department FROM users WHERE email = %s',
            (data['email'],)
        )
        user = cursor.fetchone()
        
        if user and check_password_hash(user['password_hash'], data['password']):
            # Generate JWT token
            token = jwt.encode({
                'user_id': user['id'],
                'email': data['email'],
                'name': user['name'],
                'position': user['position'],
                'department': user['department'],
                'exp': datetime.utcnow() + timedelta(hours=app.config['JWT_EXPIRATION_HOURS'])
            }, app.config['SECRET_KEY'], algorithm="HS256")
            
            return jsonify({
                'token': token,
                'user': {
                    'id': user['id'],
                    'email': data['email'],
                    'name': user['name'],
                    'position': user['position'],
                    'department': user['department']
                }
            })
        else:
            return jsonify({'error': 'Invalid email or password'}), 401
                
    except Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/reset-password-request', methods=['POST'])
def reset_password_request():
    data = request.json
    
    if 'email' not in data:
        return jsonify({'error': 'Email is required'}), 400
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Check if user exists
        cursor.execute('SELECT id FROM users WHERE email = %s', (data['email'],))
        user = cursor.fetchone()
        
        if user:
            # Generate reset token
            reset_token = jwt.encode({
                'user_id': user['id'],
                'email': data['email'],
                'exp': datetime.utcnow() + timedelta(hours=1)
            }, app.config['SECRET_KEY'], algorithm="HS256")
            
            # In a production environment, send this token via email
            return jsonify({
                'message': 'Password reset link sent',
                'reset_token': reset_token  # Remove this in production
            })
        else:
            # Don't reveal if email exists or not
            return jsonify({'message': 'If email exists, reset link will be sent'}), 200
                
    except Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# Password Reset Endpoint for Users
@app.route('/api/reset-password', methods=['POST'])
def reset_password():
    data = request.json
    
    if not all(k in data for k in ['reset_token', 'new_password']):
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        # Verify reset token
        token_data = jwt.decode(data['reset_token'], app.config['SECRET_KEY'], algorithms=["HS256"])
        user_id = token_data['user_id']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Update password
        password_hash = generate_password_hash(data['new_password'])
        cursor.execute(
            'UPDATE users SET password_hash = %s WHERE id = %s',
            (password_hash, user_id)
        )
        
        conn.commit()
        return jsonify({'message': 'Password updated successfully'})
            
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Reset token has expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid reset token'}), 401
    except Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()


@app.route('/api/update_<entity>', methods=['PUT'])
@token_required
def update_entity(user_id, entity):
    if entity not in VALID_ENTITIES:
        return jsonify({'error': 'Invalid entity'}), 400

    data = request.json
    entity_id = data.get('id')
    new_name = data.get('name')

    if not all([entity_id, new_name]):
        return jsonify({'error': 'ID and name are required'}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Special handling for subfunction
        if entity == "subfunction":
            cursor.execute(
                f'UPDATE {entity} SET name = %s WHERE id = %s AND business_unit_id = %s',
                (new_name, entity_id, data.get('business_unit_id'))
            )
        else:
            cursor.execute(
                f'UPDATE {entity} SET name = %s WHERE id = %s',
                (new_name, entity_id)
            )
            
        conn.commit()
        return jsonify({'message': f'{entity} updated successfully'}), 200
    except Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/export_<entity>', methods=['GET'])
@token_required
def export_entity(user_id, entity):
    if entity not in VALID_ENTITIES:
        return jsonify({'error': 'Invalid entity'}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get all data for the entity
        cursor.execute(f'SELECT * FROM {entity}')
        data = cursor.fetchall()
        
        # Convert to DataFrame
        df = pd.DataFrame(data)
        
        # Create Excel file in memory
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name=entity, index=False)
        
        output.seek(0)
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'{entity}_data.xlsx'
        )
    except Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/bulk_create_<entity>', methods=['POST'])
@token_required
def bulk_create_entity(user_id, entity):
    if entity not in VALID_ENTITIES:
        return jsonify({'error': 'Invalid entity'}), 400

    if 'data' not in request.json:
        return jsonify({'error': 'No data provided'}), 400

    data = request.json['data']
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        success_count = 0
        error_count = 0
        
        for item in data:
            try:
                if entity == "subfunction":
                    if all(k in item for k in ['id', 'business_unit_id', 'name']):
                        cursor.execute(
                            'INSERT INTO subfunction (id, business_unit_id, name) VALUES (%s, %s, %s)',
                            (item['id'], item['business_unit_id'], item['name'])
                        )
                        success_count += 1
                    else:
                        error_count += 1
                else:
                    if 'name' in item:
                        cursor.execute(
                            f'INSERT INTO {entity} (name) VALUES (%s)',
                            (item['name'],)
                        )
                        success_count += 1
                    else:
                        error_count += 1
            except Error:
                error_count += 1
                continue
        
        conn.commit()
        return jsonify({
            'message': f'Bulk import completed. {success_count} items imported successfully, {error_count} failed.',
            'success_count': success_count,
            'error_count': error_count
        }), 201
    except Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/search_<entity>', methods=['GET'])
@token_required
def search_entity(user_id, entity):
    if entity not in VALID_ENTITIES:
        return jsonify({'error': 'Invalid entity'}), 400

    search_term = request.args.get('q', '')
    if not search_term:
        return jsonify({'error': 'Search term is required'}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute(
            f'SELECT * FROM {entity} WHERE name LIKE %s',
            (f'%{search_term}%',)
        )
        results = cursor.fetchall()
        
        return jsonify(results), 200
    except Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# Add this function to handle validation of Excel files
def validate_excel_data(df, entity):
    required_columns = ['name']
    if entity == 'subfunction':
        required_columns.extend(['id', 'business_unit_id'])
    
    # Check if all required columns exist
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        return False, f"Missing required columns: {', '.join(missing_columns)}"
    
    # Check for empty values in required fields
    for col in required_columns:
        if df[col].isnull().any():
            return False, f"Empty values found in column: {col}"
    
    return True, "Data is valid"

    
if __name__ == '__main__':
    app.run(debug=True)