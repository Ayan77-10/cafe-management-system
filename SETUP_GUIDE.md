# Quick Setup Guide

## Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

## Step 2: Set Up Database in MySQL Workbench

1. Open MySQL Workbench
2. Connect to your MySQL server
3. Create database:
   ```sql
   CREATE DATABASE cafe_management;
   USE cafe_management;
   ```
4. Open `database/schema.sql` in MySQL Workbench
5. Execute the entire script (Run all statements)
6. Verify triggers were created:
   ```sql
   SHOW TRIGGERS;
   ```

## Step 3: Configure Environment

1. Copy `env.example` to `.env`
2. Edit `.env` with your MySQL credentials:
   ```
   DB_HOST=localhost
   DB_USER=root
   DB_PASSWORD=your_password
   DB_NAME=cafe_management
   DB_PORT=3306
   ```

## Step 4: Run the Application

```bash
python app.py
```

Open browser: `http://localhost:5000`

## Testing the Triggers

### Test Trigger 1 (Double Booking Prevention):
1. Book Table #1 with User ID 1
2. Try to book Table #1 again with any user
3. You should see: "This table is already in use."

### Test Trigger 2 (Clear Table):
1. Book a table
2. Place some orders
3. Click "Clear Table" button
4. Table and all orders should be removed

## Sample Data

The schema includes sample data:
- 4 sample users (GUEST_001, GUEST_002, ADMIN_001, STAFF_001)
- 8 sample menu items (Coffee, Pastries, Desserts, etc.)

You can start testing immediately!

