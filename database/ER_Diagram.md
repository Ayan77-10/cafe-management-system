# ER Diagram for Online Café Management System

## Entity Relationship Diagram Description

```
┌─────────────────┐
│     USERS       │
├─────────────────┤
│ UserID (PK)     │◄──────────────┐
│ GuestIdentifier │               │
│ CreatedAt       │               │
└─────────────────┘               │
                                  │
                                  │
┌─────────────────┐               │
│  MENU_ITEMS     │               │
├─────────────────┤               │
│ ItemID (PK)     │               │
│ Name            │               │
│ Price           │               │
│ Stock           │               │
│ Category        │               │
│ IsAvailable     │               │
└─────────────────┘               │
        │                         │
        │ 1                       │ 1
        │                         │
        │ M                       │ M
        ▼                         ▼
┌─────────────────────────────────────────┐
│          ORDER_ITEMS                    │
├─────────────────────────────────────────┤
│ OrderItemID (PK)                        │
│ ItemID (FK) ────────────────────────────┘
│ TableID (FK) ───────────────────────────┐
│ UserID (FK) ────────────────────────────┘
│ Quantity                                 │
│ UnitPrice                                │
│ OrderedAt                                │
└─────────────────────────────────────────┘
        │
        │ M
        │
        │ 1
        ▼
┌─────────────────┐
│ BOOKED_TABLES   │
├─────────────────┤
│ TableID (PK)    │
│ UserID (FK) ────┘
│ SessionStartTime│
│ TotalAmount     │
└─────────────────┘
```

## Relationship Details

### 1. USERS → BOOKED_TABLES (One-to-Many)
- One user can book multiple tables (over time)
- Each booked table belongs to one user
- Foreign Key: `BOOKED_TABLES.UserID` → `USERS.UserID`

### 2. USERS → ORDER_ITEMS (One-to-Many)
- One user can place multiple order items
- Each order item belongs to one user
- Foreign Key: `ORDER_ITEMS.UserID` → `USERS.UserID`

### 3. MENU_ITEMS → ORDER_ITEMS (One-to-Many)
- One menu item can be ordered multiple times
- Each order item references one menu item
- Foreign Key: `ORDER_ITEMS.ItemID` → `MENU_ITEMS.ItemID`

### 4. BOOKED_TABLES → ORDER_ITEMS (One-to-Many)
- One booked table can have multiple order items
- Each order item belongs to one table
- Foreign Key: `ORDER_ITEMS.TableID` → `BOOKED_TABLES.TableID`

## Cardinalities

| Relationship | Cardinality | Description |
|-------------|-------------|-------------|
| USERS → BOOKED_TABLES | 1:M | One user can book many tables |
| USERS → ORDER_ITEMS | 1:M | One user can place many orders |
| MENU_ITEMS → ORDER_ITEMS | 1:M | One menu item can be in many orders |
| BOOKED_TABLES → ORDER_ITEMS | 1:M | One table can have many order items |

## Attributes Summary

### USERS
- **UserID**: Primary key, auto-increment
- **GuestIdentifier**: Unique identifier for guest/user
- **CreatedAt**: Timestamp of account creation

### MENU_ITEMS
- **ItemID**: Primary key, auto-increment
- **Name**: Item name
- **Price**: Item price
- **Stock**: Available stock quantity
- **Category**: Item category
- **IsAvailable**: Availability status

### BOOKED_TABLES
- **TableID**: Primary key
- **UserID**: Foreign key to USERS
- **SessionStartTime**: When the table was booked
- **TotalAmount**: Total amount for the session

### ORDER_ITEMS
- **OrderItemID**: Primary key, auto-increment
- **ItemID**: Foreign key to MENU_ITEMS
- **TableID**: Foreign key to BOOKED_TABLES
- **UserID**: Foreign key to USERS
- **Quantity**: Quantity ordered
- **UnitPrice**: Price per unit at time of order
- **OrderedAt**: Timestamp of order

## Constraints

1. **Primary Keys**: Each table has a unique primary key
2. **Foreign Keys**: All foreign keys reference valid primary keys
3. **Unique Constraints**: GuestIdentifier must be unique
4. **Check Constraints**: Quantity must be positive, Price must be non-negative
5. **Default Values**: CreatedAt, SessionStartTime, OrderedAt use CURRENT_TIMESTAMP

## Triggers

1. **prevent_double_booking**: Prevents booking a table that's already booked
2. **update_table_total**: Updates TotalAmount when orders are added
3. **update_table_total_on_update**: Updates TotalAmount when orders are modified
4. **update_table_total_on_delete**: Updates TotalAmount when orders are removed

