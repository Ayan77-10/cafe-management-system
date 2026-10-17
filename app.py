"""
Online Café Management System - Flask Backend
This application provides REST API endpoints for managing the café system.
"""

from flask import Flask, request, jsonify, render_template, session
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
from datetime import datetime, timedelta
from functools import wraps
import secrets
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'change-this-development-secret-key')
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    SESSION_COOKIE_SECURE=os.getenv('COOKIE_SECURE', 'false').lower() == 'true',
    PERMANENT_SESSION_LIFETIME=timedelta(hours=8),
)
CORS(app, supports_credentials=True)

ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin123')


@app.before_request
def require_admin_for_api():
    # Authentication endpoints are public; all café data/API operations require an admin session.
    if request.path.startswith('/api/') and request.path not in ('/api/auth/login', '/api/auth/status', '/api/auth/logout'):
        if not session.get('admin_authenticated'):
            return jsonify({'success': False, 'error': 'Admin login required'}), 401


@app.route('/api/auth/login', methods=['POST'])
def admin_login():
    data = request.get_json(silent=True) or {}
    username = str(data.get('username', ''))
    password = str(data.get('password', ''))
    if secrets.compare_digest(username, ADMIN_USERNAME) and secrets.compare_digest(password, ADMIN_PASSWORD):
        session.clear()
        session.permanent = True
        session['admin_authenticated'] = True
        session['admin_username'] = ADMIN_USERNAME
        return jsonify({'success': True, 'username': ADMIN_USERNAME, 'message': 'Login successful'})
    return jsonify({'success': False, 'error': 'Invalid username or password'}), 401


@app.route('/api/auth/status', methods=['GET'])
def admin_auth_status():
    return jsonify({
        'authenticated': bool(session.get('admin_authenticated')),
        'username': session.get('admin_username')
    })


@app.route('/api/auth/logout', methods=['POST'])
def admin_logout():
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out successfully'})

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'cafe_management'),
    'port': os.getenv('DB_PORT', 3306)
}


def get_db_connection():
    """Create and return a database connection"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None


@app.route('/')
def index():
    """Render the homepage"""
    return render_template('index.html')


# ============================================
# FRONTEND QUERIES
# ============================================

@app.route('/api/stats/tables-booked', methods=['GET'])
def get_tables_booked():
    """Query 1: Get number of tables booked in the past two months"""
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = connection.cursor(dictionary=True)
        query = """
            SELECT COUNT(DISTINCT TableID) AS TablesBooked
            FROM BOOKED_TABLES
            WHERE SessionStartTime >= DATE_SUB(NOW(), INTERVAL 2 MONTH)
        """
        cursor.execute(query)
        result = cursor.fetchone()
        
        cursor.close()
        connection.close()
        
        return jsonify({
            'success': True,
            'tables_booked': result['TablesBooked'] if result else 0
        })
    except Error as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/stats/tables-booked-current', methods=['GET'])
def get_tables_booked_current():
    """Get number of tables currently booked (active rows in BOOKED_TABLES)"""
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = connection.cursor(dictionary=True)
        query = """
            SELECT COUNT(*) AS CurrentTables
            FROM BOOKED_TABLES
        """
        cursor.execute(query)
        result = cursor.fetchone()
        
        cursor.close()
        connection.close()
        
        return jsonify({
            'success': True,
            'current_tables': result['CurrentTables'] if result else 0
        })
    except Error as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats/most-popular-item', methods=['GET'])
def get_most_popular_item():
    """Query 2: Get the most frequently ordered item"""
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = connection.cursor(dictionary=True)
        query = """
            SELECT 
                mi.Name AS ItemName,
                SUM(oi.Quantity) AS TotalQuantity,
                COUNT(oi.OrderItemID) AS OrderCount
            FROM ORDER_ITEMS oi
            JOIN MENU_ITEMS mi ON oi.ItemID = mi.ItemID
            GROUP BY mi.ItemID, mi.Name
            ORDER BY TotalQuantity DESC
            LIMIT 1
        """
        cursor.execute(query)
        result = cursor.fetchone()
        
        cursor.close()
        connection.close()
        
        if result:
            return jsonify({
                'success': True,
                'item_name': result['ItemName'],
                'total_quantity': result['TotalQuantity'],
                'order_count': result['OrderCount']
            })
        else:
            return jsonify({
                'success': True,
                'item_name': 'No orders yet',
                'total_quantity': 0,
                'order_count': 0
            })
    except Error as e:
        return jsonify({'error': str(e)}), 500


# ============================================
# USER MANAGEMENT
# ============================================

@app.route('/api/users', methods=['GET'])
def get_users():
    """Get all users"""
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM USERS ORDER BY CreatedAt DESC")
        users = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        return jsonify({'success': True, 'users': users})
    except Error as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/users', methods=['POST'])
def create_user():
    """Create a new user"""
    try:
        data = request.json
        guest_identifier = data.get('guest_identifier')
        
        if not guest_identifier:
            return jsonify({'error': 'GuestIdentifier is required'}), 400
        
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = connection.cursor()
        query = "INSERT INTO USERS (GuestIdentifier) VALUES (%s)"
        cursor.execute(query, (guest_identifier,))
        connection.commit()
        user_id = cursor.lastrowid
        
        cursor.close()
        connection.close()
        
        return jsonify({
            'success': True,
            'user_id': user_id,
            'message': 'User created successfully'
        }), 201
    except Error as e:
        return jsonify({'error': str(e)}), 500


# ============================================
# MENU ITEMS MANAGEMENT
# ============================================

@app.route('/api/menu-items', methods=['GET'])
def get_menu_items():
    """Get all menu items"""
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM MENU_ITEMS WHERE IsAvailable = TRUE ORDER BY Category, Name")
        items = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        return jsonify({'success': True, 'menu_items': items})
    except Error as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/menu-items', methods=['POST'])
def create_menu_item():
    """Create a new menu item"""
    try:
        data = request.json
        name = data.get('name')
        price = data.get('price')
        stock = data.get('stock', 0)
        category = data.get('category')
        is_available = data.get('is_available', True)
        
        if not name or price is None:
            return jsonify({'error': 'Name and Price are required'}), 400
        
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = connection.cursor()
        query = """
            INSERT INTO MENU_ITEMS (Name, Price, Stock, Category, IsAvailable)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query, (name, price, stock, category, is_available))
        connection.commit()
        item_id = cursor.lastrowid
        
        cursor.close()
        connection.close()
        
        return jsonify({
            'success': True,
            'item_id': item_id,
            'message': 'Menu item created successfully'
        }), 201
    except Error as e:
        return jsonify({'error': str(e)}), 500


# ============================================
# TABLE MANAGEMENT
# ============================================

@app.route('/api/tables', methods=['GET'])
def get_booked_tables():
    """Get all currently booked tables"""
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = connection.cursor(dictionary=True)
        query = """
            SELECT bt.*, u.GuestIdentifier,
                   COUNT(oi.OrderItemID) AS ItemCount
            FROM BOOKED_TABLES bt
            LEFT JOIN USERS u ON bt.UserID = u.UserID
            LEFT JOIN ORDER_ITEMS oi ON bt.TableID = oi.TableID
            GROUP BY bt.TableID, bt.UserID, bt.SessionStartTime, bt.TotalAmount, u.GuestIdentifier
            ORDER BY bt.SessionStartTime DESC
        """
        cursor.execute(query)
        tables = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        return jsonify({'success': True, 'tables': tables})
    except Error as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/tables', methods=['POST'])
def book_table():
    """Book a new table (Trigger 1 will prevent double booking)"""
    try:
        data = request.json
        table_id = data.get('table_id')
        user_id = data.get('user_id')
        
        if not table_id or not user_id:
            return jsonify({'error': 'TableID and UserID are required'}), 400
        
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = connection.cursor()
        query = "INSERT INTO BOOKED_TABLES (TableID, UserID) VALUES (%s, %s)"
        
        try:
            cursor.execute(query, (table_id, user_id))
            connection.commit()
            cursor.close()
            connection.close()
            
            return jsonify({
                'success': True,
                'message': f'Table {table_id} booked successfully'
            }), 201
        except Error as e:
            connection.rollback()
            cursor.close()
            connection.close()
            
            # Check if it's the double booking error
            if 'This table is already in use' in str(e):
                return jsonify({
                    'success': False,
                    'error': 'This table is already in use.'
                }), 409
            else:
                return jsonify({'error': str(e)}), 500
            
    except Error as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/tables/<int:table_id>/clear', methods=['POST'])
def clear_table(table_id):
    """Clear a table after checkout (Trigger 2 functionality)"""
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = connection.cursor()
        
        # Call the stored procedure to clear the table
        cursor.callproc('ClearTable', [table_id])
        connection.commit()
        
        # Fetch the result message
        for result in cursor.stored_results():
            message = result.fetchone()
        
        cursor.close()
        connection.close()
        
        return jsonify({
            'success': True,
            'message': f'Table {table_id} cleared successfully'
        })
    except Error as e:
        return jsonify({'error': str(e)}), 500


# ============================================
# ORDER MANAGEMENT
# ============================================

@app.route('/api/orders', methods=['GET'])
def get_orders():
    """Get all order items"""
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = connection.cursor(dictionary=True)
        query = """
            SELECT oi.*, mi.Name AS ItemName, u.GuestIdentifier
            FROM ORDER_ITEMS oi
            JOIN MENU_ITEMS mi ON oi.ItemID = mi.ItemID
            JOIN USERS u ON oi.UserID = u.UserID
            ORDER BY oi.OrderedAt DESC
        """
        cursor.execute(query)
        orders = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        return jsonify({'success': True, 'orders': orders})
    except Error as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/orders', methods=['POST'])
def create_order():
    """Create a new order item"""
    try:
        data = request.json
        item_id = data.get('item_id')
        table_id = data.get('table_id')
        user_id = data.get('user_id')
        quantity = data.get('quantity', 1)
        
        if not item_id or not table_id or not user_id:
            return jsonify({'error': 'ItemID, TableID, and UserID are required'}), 400
        
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed'}), 500
        
        # Get the current price of the menu item
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT Price FROM MENU_ITEMS WHERE ItemID = %s", (item_id,))
        menu_item = cursor.fetchone()
        
        if not menu_item:
            cursor.close()
            connection.close()
            return jsonify({'error': 'Menu item not found'}), 404
        
        unit_price = menu_item['Price']
        
        # Insert the order item (Trigger will update TotalAmount)
        query = """
            INSERT INTO ORDER_ITEMS (ItemID, TableID, UserID, Quantity, UnitPrice)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query, (item_id, table_id, user_id, quantity, unit_price))
        connection.commit()
        order_id = cursor.lastrowid
        
        cursor.close()
        connection.close()
        
        return jsonify({
            'success': True,
            'order_id': order_id,
            'message': 'Order item created successfully'
        }), 201
    except Error as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/tables/<int:table_id>/orders', methods=['GET'])
def get_table_orders(table_id):
    """Get all orders for a specific table"""
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = connection.cursor(dictionary=True)
        query = """
            SELECT oi.*, mi.Name AS ItemName, mi.Category
            FROM ORDER_ITEMS oi
            JOIN MENU_ITEMS mi ON oi.ItemID = mi.ItemID
            WHERE oi.TableID = %s
            ORDER BY oi.OrderedAt DESC
        """
        cursor.execute(query, (table_id,))
        orders = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        return jsonify({'success': True, 'orders': orders})
    except Error as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

