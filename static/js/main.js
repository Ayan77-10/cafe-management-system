// ============================================
// Online Café Management System - JavaScript
// Frontend Functionality and API Integration
// ============================================

const API_BASE_URL = '/api';

async function checkAdminSession() {
    try {
        const response = await fetch(`${API_BASE_URL}/auth/status`);
        const data = await response.json();
        if (data.authenticated) {
            showAdminApp(data.username);
        } else {
            showLoginScreen();
        }
    } catch (error) {
        showLoginScreen();
        document.getElementById('login-error').textContent = 'Could not connect to the server. Make sure Flask is running.';
    }
}

function showLoginScreen() {
    document.getElementById('admin-login-screen').style.display = 'flex';
    document.getElementById('main-app').style.display = 'none';
    document.getElementById('admin-username').focus();
}

function showAdminApp(username) {
    document.getElementById('admin-login-screen').style.display = 'none';
    document.getElementById('main-app').style.display = 'block';
    document.getElementById('admin-welcome').textContent = `Signed in: ${username || 'Administrator'}`;
    loadDashboardStats();
    loadTables();
    loadMenuItems();
    loadOrders();
}

document.getElementById('admin-login-form').addEventListener('submit', async function(event) {
    event.preventDefault();
    const submit = document.getElementById('login-submit');
    const error = document.getElementById('login-error');
    submit.disabled = true;
    submit.textContent = 'Signing in...';
    error.textContent = '';
    try {
        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                username: document.getElementById('admin-username').value.trim(),
                password: document.getElementById('admin-password').value
            })
        });
        const data = await response.json();
        if (!response.ok || !data.success) {
            error.textContent = data.error || 'Login failed. Please try again.';
            return;
        }
        document.getElementById('admin-login-form').reset();
        showAdminApp(data.username);
    } catch (err) {
        error.textContent = 'Could not connect to the server. Make sure Flask is running.';
    } finally {
        submit.disabled = false;
        submit.textContent = 'Sign In';
    }
});

async function logoutAdmin() {
    try {
        await fetch(`${API_BASE_URL}/auth/logout`, {method: 'POST'});
    } finally {
        showLoginScreen();
        document.getElementById('admin-login-form').reset();
        document.getElementById('login-error').textContent = 'You have been logged out.';
    }
}

// ============================================
// UTILITY FUNCTIONS
// ============================================

function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast ${type} show`;
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

function formatCurrency(amount) {
    return `$${parseFloat(amount).toFixed(2)}`;
}

function formatDateTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString();
}

// ============================================
// DASHBOARD STATS LOADING
// ============================================

async function loadDashboardStats() {
    try {
        // Load Query 1: Tables Booked in Past 2 Months
        const tablesResponse = await fetch(`${API_BASE_URL}/stats/tables-booked`);
        const tablesData = await tablesResponse.json();
        
        if (tablesData.success) {
            document.getElementById('tables-booked').textContent = tablesData.tables_booked;
        }

        // Load Current Active Tables
        const currentResponse = await fetch(`${API_BASE_URL}/stats/tables-booked-current`);
        const currentData = await currentResponse.json();
        if (currentData.success) {
            const el = document.getElementById('tables-booked-current');
            if (el) el.textContent = currentData.current_tables;
        }

        // Load Query 2: Most Popular Item
        const popularResponse = await fetch(`${API_BASE_URL}/stats/most-popular-item`);
        const popularData = await popularResponse.json();
        
        if (popularData.success) {
            document.getElementById('popular-item').textContent = popularData.item_name || 'No orders yet';
            if (popularData.total_quantity > 0) {
                document.getElementById('popular-item-details').textContent = 
                    `${popularData.total_quantity} orders (${popularData.order_count} times)`;
            } else {
                document.getElementById('popular-item-details').textContent = '';
            }
        }
    } catch (error) {
        console.error('Error loading dashboard stats:', error);
        showToast('Failed to load dashboard statistics', 'error');
    }
}

// ============================================
// TABLES MANAGEMENT
// ============================================

async function loadTables() {
    try {
        const response = await fetch(`${API_BASE_URL}/tables`);
        const data = await response.json();
        
        const container = document.getElementById('tables-container');
        
        if (!data.success || !data.tables || data.tables.length === 0) {
            container.innerHTML = '<div class="loading">No tables currently booked</div>';
            return;
        }
        
        container.innerHTML = data.tables.map(table => `
            <div class="table-card">
                <div class="table-card-header">
                    <span class="table-id">Table #${table.TableID}</span>
                    <span class="table-status">Active</span>
                </div>
                <div class="table-info">
                    <div class="table-info-item">
                        <span class="table-info-label">Guest:</span>
                        <span class="table-info-value">${table.GuestIdentifier || 'N/A'}</span>
                    </div>
                    <div class="table-info-item">
                        <span class="table-info-label">Started:</span>
                        <span class="table-info-value">${formatDateTime(table.SessionStartTime)}</span>
                    </div>
                    <div class="table-info-item">
                        <span class="table-info-label">Items:</span>
                        <span class="table-info-value">${table.ItemCount || 0}</span>
                    </div>
                    <div class="table-info-item">
                        <span class="table-info-label">Total Amount:</span>
                        <span class="table-info-value">${formatCurrency(table.TotalAmount || 0)}</span>
                    </div>
                </div>
                <div class="table-actions">
                    <button class="btn btn-primary btn-small" onclick="showPlaceOrderModal(${table.TableID}, ${table.UserID})">
                        Place Order
                    </button>
                    <button class="btn btn-success btn-small" onclick="viewTableOrders(${table.TableID})">
                        View Orders
                    </button>
                    <button class="btn btn-danger btn-small" onclick="clearTable(${table.TableID})">
                        Clear Table
                    </button>
                </div>
            </div>
        `).join('');
        
    } catch (error) {
        console.error('Error loading tables:', error);
        showToast('Failed to load tables', 'error');
    }
}

function showBookTableModal() {
    document.getElementById('book-table-modal').style.display = 'block';
}

async function bookTable(event) {
    event.preventDefault();
    
    const formData = {
        table_id: parseInt(document.getElementById('table-id').value),
        user_id: parseInt(document.getElementById('user-id').value)
    };
    
    try {
        const response = await fetch(`${API_BASE_URL}/tables`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        const data = await response.json();
        
        if (data.success) {
            showToast(data.message, 'success');
            closeModal('book-table-modal');
            document.getElementById('book-table-form').reset();
            loadTables();
            loadDashboardStats();
        } else {
            showToast(data.error || 'Failed to book table', 'error');
        }
    } catch (error) {
        console.error('Error booking table:', error);
        showToast('Failed to book table', 'error');
    }
}

async function clearTable(tableId) {
    if (!confirm(`Are you sure you want to clear Table #${tableId}? This will remove all associated orders.`)) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/tables/${tableId}/clear`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            showToast(`Table #${tableId} cleared successfully`, 'success');
            loadTables();
            loadDashboardStats();
        } else {
            showToast(data.error || 'Failed to clear table', 'error');
        }
    } catch (error) {
        console.error('Error clearing table:', error);
        showToast('Failed to clear table', 'error');
    }
}

async function viewTableOrders(tableId) {
    try {
        const response = await fetch(`${API_BASE_URL}/tables/${tableId}/orders`);
        const data = await response.json();
        
        if (data.success) {
            if (data.orders && data.orders.length > 0) {
                const ordersList = data.orders.map(order => 
                    `• ${order.ItemName} (x${order.Quantity}) - ${formatCurrency(order.UnitPrice * order.Quantity)}`
                ).join('\n');
                alert(`Orders for Table #${tableId}:\n\n${ordersList}`);
            } else {
                alert(`No orders found for Table #${tableId}`);
            }
        }
    } catch (error) {
        console.error('Error loading table orders:', error);
        showToast('Failed to load table orders', 'error');
    }
}

// ============================================
// MENU ITEMS MANAGEMENT
// ============================================

async function loadMenuItems() {
    try {
        const response = await fetch(`${API_BASE_URL}/menu-items`);
        const data = await response.json();
        
        const container = document.getElementById('menu-container');
        
        if (!data.success || !data.menu_items || data.menu_items.length === 0) {
            container.innerHTML = '<div class="loading">No menu items available</div>';
            return;
        }
        
        container.innerHTML = data.menu_items.map(item => `
            <div class="menu-item-card">
                <div class="menu-item-name">${item.Name}</div>
                <div class="menu-item-category">${item.Category || 'Uncategorized'}</div>
                <div class="menu-item-price">${formatCurrency(item.Price)}</div>
                <div class="menu-item-stock">Stock: ${item.Stock}</div>
                ${item.IsAvailable ? 
                    '<div class="menu-item-available">Available</div>' : 
                    '<div class="menu-item-unavailable">Unavailable</div>'
                }
            </div>
        `).join('');
        
    } catch (error) {
        console.error('Error loading menu items:', error);
        showToast('Failed to load menu items', 'error');
    }
}

function showAddMenuItemModal() {
    document.getElementById('add-menu-item-modal').style.display = 'block';
}

async function addMenuItem(event) {
    event.preventDefault();
    
    const formData = {
        name: document.getElementById('item-name').value,
        price: parseFloat(document.getElementById('item-price').value),
        stock: parseInt(document.getElementById('item-stock').value) || 0,
        category: document.getElementById('item-category').value || '',
        is_available: true
    };
    
    try {
        const response = await fetch(`${API_BASE_URL}/menu-items`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        const data = await response.json();
        
        if (data.success) {
            showToast('Menu item added successfully', 'success');
            closeModal('add-menu-item-modal');
            document.getElementById('add-menu-item-form').reset();
            loadMenuItems();
        } else {
            showToast(data.error || 'Failed to add menu item', 'error');
        }
    } catch (error) {
        console.error('Error adding menu item:', error);
        showToast('Failed to add menu item', 'error');
    }
}

// ============================================
// ORDER MANAGEMENT
// ============================================

function showPlaceOrderModal(tableId, userId) {
    document.getElementById('order-table-id').value = tableId;
    document.getElementById('order-user-id').value = userId;
    
    // Load menu items into select
    loadMenuItemsForOrder();
    
    document.getElementById('place-order-modal').style.display = 'block';
}

async function loadMenuItemsForOrder() {
    try {
        const response = await fetch(`${API_BASE_URL}/menu-items`);
        const data = await response.json();
        
        const select = document.getElementById('order-item-id');
        select.innerHTML = '';
        
        if (data.success && data.menu_items) {
            data.menu_items.forEach(item => {
                if (item.IsAvailable) {
                    const option = document.createElement('option');
                    option.value = item.ItemID;
                    option.textContent = `${item.Name} - ${formatCurrency(item.Price)}`;
                    select.appendChild(option);
                }
            });
        }
    } catch (error) {
        console.error('Error loading menu items for order:', error);
    }
}

async function placeOrder(event) {
    event.preventDefault();
    
    const formData = {
        item_id: parseInt(document.getElementById('order-item-id').value),
        table_id: parseInt(document.getElementById('order-table-id').value),
        user_id: parseInt(document.getElementById('order-user-id').value),
        quantity: parseInt(document.getElementById('order-quantity').value) || 1
    };
    
    try {
        const response = await fetch(`${API_BASE_URL}/orders`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        const data = await response.json();
        
        if (data.success) {
            showToast('Order placed successfully', 'success');
            closeModal('place-order-modal');
            document.getElementById('place-order-form').reset();
            loadTables();
            loadOrders();
        } else {
            showToast(data.error || 'Failed to place order', 'error');
        }
    } catch (error) {
        console.error('Error placing order:', error);
        showToast('Failed to place order', 'error');
    }
}

async function loadOrders() {
    try {
        const response = await fetch(`${API_BASE_URL}/orders`);
        const data = await response.json();
        
        const container = document.getElementById('orders-container');
        
        if (!data.success || !data.orders || data.orders.length === 0) {
            container.innerHTML = '<div class="loading">No orders found</div>';
            return;
        }
        
        container.innerHTML = data.orders.slice(0, 10).map(order => `
            <div class="order-item">
                <div class="order-info">
                    <div class="order-item-name">${order.ItemName}</div>
                    <div class="order-item-details">
                        Table #${order.TableID} • ${order.GuestIdentifier} • ${formatDateTime(order.OrderedAt)}
                    </div>
                </div>
                <div style="display: flex; align-items: center; gap: 20px;">
                    <div class="order-item-quantity">Qty: ${order.Quantity}</div>
                    <div class="order-item-price">${formatCurrency(order.UnitPrice * order.Quantity)}</div>
                </div>
            </div>
        `).join('');
        
    } catch (error) {
        console.error('Error loading orders:', error);
        showToast('Failed to load orders', 'error');
    }
}

// ============================================
// MODAL MANAGEMENT
// ============================================

function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
}

// Close modal when clicking outside
window.onclick = function(event) {
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });
}

// ============================================
// SMOOTH SCROLLING
// ============================================

document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// ============================================
// INITIALIZATION
// ============================================

document.addEventListener('DOMContentLoaded', function() {
    // Load all data on page load
    loadDashboardStats();
    loadTables();
    loadMenuItems();
    loadOrders();
    
    // Refresh dashboard stats every 30 seconds
    setInterval(loadDashboardStats, 30000);
});

