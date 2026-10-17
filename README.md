# ☕ Online Café Management System

A comprehensive web-based café management system built with Flask, MySQL, HTML, CSS, and JavaScript. This system manages users, menu items, table bookings, and orders with automated triggers and real-time statistics.

## 📋 Features

- **User Management**: Create and manage guest users identified by a GuestIdentifier
- **Menu Management**: Add and manage menu items with categories, prices, and stock tracking
- **Table Booking**: Book tables with automatic conflict prevention
- **Order Management**: Place orders linked to tables and users
- **Real-time Statistics**: Dashboard showing tables booked in past 2 months and most popular items
- **Database Triggers**: Automated triggers for double-booking prevention and total amount calculation
- **Modern UI**: Beautiful, responsive design with smooth animations

## 🗄️ Database Schema

### Tables

1. **USERS**
   - UserID (Primary Key)
   - GuestIdentifier
   - CreatedAt

2. **MENU_ITEMS**
   - ItemID (Primary Key)
   - Name
   - Price
   - Stock
   - Category
   - IsAvailable

3. **BOOKED_TABLES**
   - TableID (Primary Key)
   - UserID (Foreign Key → USERS)
   - SessionStartTime
   - TotalAmount

4. **ORDER_ITEMS**
   - OrderItemID (Primary Key)
   - ItemID (Foreign Key → MENU_ITEMS)
   - TableID (Foreign Key → BOOKED_TABLES)
   - UserID (Foreign Key → USERS)
   - Quantity
   - UnitPrice
   - OrderedAt

### Relationships

- **USERS** → **BOOKED_TABLES** (1:M)
- **USERS** → **ORDER_ITEMS** (1:M)
- **MENU_ITEMS** → **ORDER_ITEMS** (1:M)
- **BOOKED_TABLES** → **ORDER_ITEMS** (1:M)

### Triggers

1. **prevent_double_booking**: Prevents booking a table that's already in use
   - Fires: BEFORE INSERT on BOOKED_TABLES
   - Error Message: "This table is already in use."

2. **update_table_total**: Updates TotalAmount when order items are added
   - Fires: AFTER INSERT on ORDER_ITEMS

3. **update_table_total_on_update**: Updates TotalAmount when order items are modified
   - Fires: AFTER UPDATE on ORDER_ITEMS

4. **update_table_total_on_delete**: Updates TotalAmount when order items are removed
   - Fires: AFTER DELETE on ORDER_ITEMS

### Stored Procedures

- **ClearTable**: Removes a booked table and all associated orders (cascading delete)

## 🚀 Installation & Setup

### Prerequisites

- Python 3.8 or higher
- MySQL Server (with MySQL Workbench or command line access)
- pip (Python package manager)

### Step 1: Clone/Download the Project

Navigate to the project directory:
```bash
cd dbms1
```

### Step 2: Install Python Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Set Up Database

1. Open MySQL Workbench (or MySQL command line)

2. Create the database:
```sql
CREATE DATABASE cafe_management;
```

3. Run the schema file:
   - Open `database/schema.sql` in MySQL Workbench
   - Execute the entire script
   - This will create all tables, triggers, and sample data

### Step 4: Configure Environment Variables

1. Copy `env.example` to `.env`:
```bash
copy env.example .env  # Windows
# or
cp env.example .env    # Linux/Mac
```

2. Edit `.env` and update with your MySQL credentials:
```
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password_here
DB_NAME=cafe_management
DB_PORT=3306
```

### Step 5: Run the Application

```bash
python app.py
```

The application will start on `http://localhost:5000`

## 🔐 Admin Login

The dashboard and all `/api/*` café data endpoints require an administrator session.

1. Copy `.env.example` to `.env` and set `ADMIN_USERNAME`, `ADMIN_PASSWORD`, and a long random `SECRET_KEY`.
2. Start the app with `python app.py`.
3. Open `http://localhost:5000` and sign in with the credentials from `.env`.
4. Use **Log Out** in the header to end the session.

For local testing only, if you have not created a `.env` file, the development defaults are username `admin` and password `admin123`. Change them before sharing or deploying the project. Never commit `.env` to Git. In production, use HTTPS and set `COOKIE_SECURE=true`.

## 📖 Usage

### Accessing the Application

1. Open your web browser
2. Navigate to `http://localhost:5000`
3. The homepage will display:
   - Dashboard statistics (tables booked, most popular item)
   - Currently booked tables
   - Menu items
   - Recent orders

### Key Operations

#### Book a Table
1. Click "Book New Table" button
2. Enter Table ID and User ID
3. Click "Book Table"
   - If table is already booked, you'll see: "This table is already in use."

#### Place an Order
1. Click "Place Order" on any booked table
2. Select menu item, enter quantity
3. Click "Place Order"
   - Total amount is automatically calculated

#### Clear a Table
1. Click "Clear Table" on any booked table
2. Confirm the action
   - Table and all associated orders will be removed

#### View Statistics
- **Tables Booked**: Shows count of tables booked in the past 2 months
- **Most Popular Item**: Shows the most frequently ordered item

## 🔍 Frontend Queries

### Query 1: Tables Booked in Past 2 Months
```sql
SELECT COUNT(DISTINCT TableID) AS TablesBooked
FROM BOOKED_TABLES
WHERE SessionStartTime >= DATE_SUB(NOW(), INTERVAL 2 MONTH);
```

### Query 2: Most Frequently Ordered Item
```sql
SELECT 
    mi.Name AS ItemName,
    SUM(oi.Quantity) AS TotalQuantity,
    COUNT(oi.OrderItemID) AS OrderCount
FROM ORDER_ITEMS oi
JOIN MENU_ITEMS mi ON oi.ItemID = mi.ItemID
GROUP BY mi.ItemID, mi.Name
ORDER BY TotalQuantity DESC
LIMIT 1;
```

## 📁 Project Structure

```
dbms1/
├── app.py                 # Flask backend application
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── README.md             # This file
├── database/
│   ├── schema.sql        # Database schema, triggers, sample data
│   └── ER_Diagram.md     # ER diagram documentation
├── templates/
│   └── index.html       # Main HTML template
└── static/
    ├── css/
    │   └── style.css    # CSS styling
    └── js/
        └── main.js      # JavaScript functionality
```

## 🎨 Technologies Used

- **Backend**: Python Flask
- **Database**: MySQL (via MySQL Workbench)
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Database Driver**: mysql-connector-python

## 🔧 API Endpoints

### Statistics
- `GET /api/stats/tables-booked` - Get tables booked in past 2 months
- `GET /api/stats/tables-booked-current` - Get number of tables currently booked
- `GET /api/stats/most-popular-item` - Get most popular menu item

### Users
- `GET /api/users` - Get all users
- `POST /api/users` - Create new user

### Menu Items
- `GET /api/menu-items` - Get all menu items
- `POST /api/menu-items` - Create new menu item

### Tables
- `GET /api/tables` - Get all booked tables
- `POST /api/tables` - Book a new table
- `POST /api/tables/<table_id>/clear` - Clear a table

### Orders
- `GET /api/orders` - Get all orders
- `POST /api/orders` - Create new order
- `GET /api/tables/<table_id>/orders` - Get orders for a table

## 🐛 Troubleshooting

### Database Connection Error
- Verify MySQL server is running
- Check `.env` file has correct credentials
- Ensure database `cafe_management` exists

### Trigger Not Working
- Verify triggers were created successfully:
```sql
SHOW TRIGGERS;
```

### Port Already in Use
- Change port in `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5001)
```

## 📝 Notes

- The system uses cascading deletes: When a table is cleared, all associated order items are automatically deleted
- Total amount for each table is automatically calculated via triggers
- Only available menu items are displayed for ordering
- Tables must be booked before orders can be placed

## 👨‍💻 Development

To modify the database schema:
1. Update `database/schema.sql`
2. Re-run the schema in MySQL Workbench
3. Restart the Flask application

## 📄 License

This project is created for educational purposes.

---

**Enjoy managing your café! ☕**

