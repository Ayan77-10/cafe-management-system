-- ============================================
-- Online Café Management System
-- Database Schema for SQL Workbench
-- ============================================

-- Create Database (optional, uncomment if needed)
-- CREATE DATABASE IF NOT EXISTS cafe_management;
-- USE cafe_management;

-- ============================================
-- TABLE: USERS
-- ============================================
CREATE TABLE IF NOT EXISTS USERS (
    UserID INT AUTO_INCREMENT PRIMARY KEY,
    GuestIdentifier VARCHAR(100) UNIQUE NOT NULL,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_guest_identifier (GuestIdentifier)
);

-- ============================================
-- TABLE: MENU_ITEMS
-- ============================================
CREATE TABLE IF NOT EXISTS MENU_ITEMS (
    ItemID INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(255) NOT NULL,
    Price DECIMAL(10, 2) NOT NULL,
    Stock INT DEFAULT 0,
    Category VARCHAR(100),
    IsAvailable BOOLEAN DEFAULT TRUE,
    INDEX idx_category (Category),
    INDEX idx_available (IsAvailable)
);

-- ============================================
-- TABLE: BOOKED_TABLES
-- ============================================
CREATE TABLE IF NOT EXISTS BOOKED_TABLES (
    TableID INT PRIMARY KEY,
    UserID INT NOT NULL,
    SessionStartTime TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    TotalAmount DECIMAL(10, 2) DEFAULT 0.00,
    FOREIGN KEY (UserID) REFERENCES USERS(UserID) ON DELETE CASCADE,
    INDEX idx_user (UserID),
    INDEX idx_session_time (SessionStartTime)
);

-- ============================================
-- TABLE: ORDER_ITEMS
-- ============================================
CREATE TABLE IF NOT EXISTS ORDER_ITEMS (
    OrderItemID INT AUTO_INCREMENT PRIMARY KEY,
    ItemID INT NOT NULL,
    TableID INT NOT NULL,
    UserID INT NOT NULL,
    Quantity INT NOT NULL DEFAULT 1,
    UnitPrice DECIMAL(10, 2) NOT NULL,
    OrderedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ItemID) REFERENCES MENU_ITEMS(ItemID) ON DELETE CASCADE,
    FOREIGN KEY (TableID) REFERENCES BOOKED_TABLES(TableID) ON DELETE CASCADE,
    FOREIGN KEY (UserID) REFERENCES USERS(UserID) ON DELETE CASCADE,
    INDEX idx_table (TableID),
    INDEX idx_user (UserID),
    INDEX idx_item (ItemID),
    INDEX idx_ordered_at (OrderedAt)
);

-- ============================================
-- TRIGGERS
-- ============================================

-- Trigger 1: Prevent double booking
-- This trigger prevents booking a table that is already booked
DELIMITER $$

CREATE TRIGGER IF NOT EXISTS prevent_double_booking
BEFORE INSERT ON BOOKED_TABLES
FOR EACH ROW
BEGIN
    IF EXISTS (
        SELECT 1 FROM BOOKED_TABLES 
        WHERE TableID = NEW.TableID
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'This table is already in use.';
    END IF;
END$$

DELIMITER ;

-- Trigger 2: Update TotalAmount when order items are added
-- This trigger automatically updates the total amount for a booked table
DELIMITER $$

CREATE TRIGGER IF NOT EXISTS update_table_total
AFTER INSERT ON ORDER_ITEMS
FOR EACH ROW
BEGIN
    UPDATE BOOKED_TABLES
    SET TotalAmount = (
        SELECT COALESCE(SUM(Quantity * UnitPrice), 0)
        FROM ORDER_ITEMS
        WHERE TableID = NEW.TableID
    )
    WHERE TableID = NEW.TableID;
END$$

DELIMITER ;

-- Trigger 3: Update TotalAmount when order items are updated
DELIMITER $$

CREATE TRIGGER IF NOT EXISTS update_table_total_on_update
AFTER UPDATE ON ORDER_ITEMS
FOR EACH ROW
BEGIN
    UPDATE BOOKED_TABLES
    SET TotalAmount = (
        SELECT COALESCE(SUM(Quantity * UnitPrice), 0)
        FROM ORDER_ITEMS
        WHERE TableID = NEW.TableID
    )
    WHERE TableID = NEW.TableID;
END$$

DELIMITER ;

-- Trigger 4: Update TotalAmount when order items are deleted
DELIMITER $$

CREATE TRIGGER IF NOT EXISTS update_table_total_on_delete
AFTER DELETE ON ORDER_ITEMS
FOR EACH ROW
BEGIN
    UPDATE BOOKED_TABLES
    SET TotalAmount = (
        SELECT COALESCE(SUM(Quantity * UnitPrice), 0)
        FROM ORDER_ITEMS
        WHERE TableID = OLD.TableID
    )
    WHERE TableID = OLD.TableID;
END$$

DELIMITER ;

-- ============================================
-- STORED PROCEDURE: Clear Table (for checkout)
-- ============================================
-- This procedure handles clearing a table after checkout
-- It will be called from the Python backend when "Clear Table" button is clicked
DELIMITER $$

CREATE PROCEDURE IF NOT EXISTS ClearTable(IN p_TableID INT)
BEGIN
    -- Delete the booked table record
    -- This will cascade delete related ORDER_ITEMS due to ON DELETE CASCADE
    DELETE FROM BOOKED_TABLES WHERE TableID = p_TableID;
    
    SELECT CONCAT('Table ', p_TableID, ' has been cleared successfully.') AS Message;
END$$

DELIMITER ;

-- ============================================
-- SAMPLE DATA (for testing)
-- ============================================

-- Insert sample users
INSERT INTO USERS (GuestIdentifier) VALUES
('GUEST_001'),
('GUEST_002');

-- Insert sample menu items
INSERT INTO MENU_ITEMS (Name, Price, Stock, Category, IsAvailable) VALUES
('Espresso', 3.50, 100, 'Coffee', TRUE),
('Cappuccino', 4.50, 80, 'Coffee', TRUE),
('Latte', 4.75, 90, 'Coffee', TRUE),
('Mocha', 5.00, 70, 'Coffee', TRUE),
('Croissant', 3.00, 50, 'Pastry', TRUE),
('Chocolate Cake', 5.50, 30, 'Dessert', TRUE),
('Sandwich', 6.00, 40, 'Food', TRUE),
('Tea', 3.00, 100, 'Beverage', TRUE);

-- ============================================
-- VIEWS for common queries
-- ============================================

-- View: Active Bookings
CREATE OR REPLACE VIEW v_active_bookings AS
SELECT 
    bt.TableID,
    bt.UserID,
    u.GuestIdentifier,
    bt.SessionStartTime,
    bt.TotalAmount,
    COUNT(oi.OrderItemID) AS TotalItems
FROM BOOKED_TABLES bt
LEFT JOIN USERS u ON bt.UserID = u.UserID
LEFT JOIN ORDER_ITEMS oi ON bt.TableID = oi.TableID
GROUP BY bt.TableID, bt.UserID, u.GuestIdentifier, bt.SessionStartTime, bt.TotalAmount;

-- ============================================
-- QUERIES FOR FRONTEND
-- ============================================

-- Query 1: Number of tables booked in the past two months
-- This query will be used in the frontend
-- SELECT COUNT(DISTINCT TableID) AS TablesBooked
-- FROM BOOKED_TABLES
-- WHERE SessionStartTime >= DATE_SUB(NOW(), INTERVAL 2 MONTH);

-- Query 2: Most frequently ordered item
-- This query will be used in the frontend
-- SELECT 
--     mi.Name AS ItemName,
--     SUM(oi.Quantity) AS TotalQuantity,
--     COUNT(oi.OrderItemID) AS OrderCount
-- FROM ORDER_ITEMS oi
-- JOIN MENU_ITEMS mi ON oi.ItemID = mi.ItemID
-- GROUP BY mi.ItemID, mi.Name
-- ORDER BY TotalQuantity DESC
-- LIMIT 1;

--
--   CREATE DATABASE cafe_management;
-- USE cafe_management;
--
SHOW TRIGGERS;

SELECT * FROM USERS;
SELECT * FROM MENU_ITEMS;
SELECT * FROM BOOKED_TABLES;
SELECT * FROM ORDER_ITEMS;
INSERT INTO BOOKED_TABLES (TableID, UserID) VALUES (101, 1);
INSERT INTO ORDER_ITEMS (ItemID, TableID, UserID, Quantity, UnitPrice)
VALUES (1, 101, 1, 2, 3.50); -- Ordering 2 Espressos at $3.50 each
SELECT * FROM ORDER_ITEMS;
INSERT INTO ORDER_ITEMS (ItemID, TableID, UserID, Quantity, UnitPrice) VALUES (5, 101, 1, 1, 3.00);
INSERT INTO BOOKED_TABLES (TableID, UserID) VALUES (102, 2);
INSERT INTO ORDER_ITEMS (ItemID, TableID, UserID, Quantity, UnitPrice) 
VALUES (6, 102, 2, 3, 4.00);
INSERT INTO BOOKED_TABLES (TableID, UserID) VALUES (103, 3);
INSERT INTO ORDER_ITEMS (ItemID, TableID, UserID, Quantity, UnitPrice) 
VALUES (7, 103, 3 ,4, 5.00);
SELECT * FROM ORDER_ITEMS;

commit;

-- updating cost for menu items
UPDATE MENU_ITEMS
SET Price = 120
WHERE ItemID = 3;

-- Delete an item from menu 
DELETE FROM MENU_ITEMS 
WHERE ItemID = 7;

--  Add new menu item
INSERT INTO MENU_ITEMS (Name, Price, Stock, Category, IsAvailable) 
VALUES ('Green Tea', 2.50, 50, 'Beverage', TRUE);

-- Book a table 
-- first add the guest then the table
SELECT * FROM USERS;

INSERT INTO USERS (GuestIdentifier)
VALUES ('GUEST_123');

INSERT INTO BOOKED_TABLES (TableID, UserID) 
VALUES (105, 1); 

-- Show all available menu items 
SELECT * FROM MENU_ITEMS 
WHERE IsAvailable = TRUE; 

-- Show orders for a specific table 
SELECT * FROM ORDER_ITEMS 
WHERE TableID = 101; 

-- Show all tables booked by a user 
SELECT * FROM BOOKED_TABLES 
WHERE UserID = 1; 

-- Total orders per table 
SELECT TableID, COUNT(OrderItemID) AS TotalOrders 
FROM ORDER_ITEMS 
GROUP BY TableID;

-- Total revenue per item 
SELECT  
mi.Name, 
SUM(oi.Quantity * oi.UnitPrice) AS TotalRevenue 
FROM ORDER_ITEMS oi 
JOIN MENU_ITEMS mi ON oi.ItemID = mi.ItemID 
GROUP BY mi.ItemID, mi.Name;

-- Show booked tables with guest identifier 
SELECT  
bt.TableID, 
u.GuestIdentifier, 
bt.SessionStartTime 
FROM BOOKED_TABLES bt 
JOIN USERS u ON bt.UserID = u.UserID;

-- Show item name and quantity ordered 
SELECT  
mi.Name, 
oi.Quantity 
FROM ORDER_ITEMS oi 
JOIN MENU_ITEMS mi ON oi.ItemID = mi.ItemID;

--
-- Show tables with more than 5 orders 
SELECT  
TableID, 
COUNT(OrderItemID) AS TotalOrders 
FROM ORDER_ITEMS 
GROUP BY TableID 
HAVING COUNT(OrderItemID) > 5;


