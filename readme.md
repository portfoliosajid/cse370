==========================================================================
DRUGWEB - ONLINE PHARMACY MANAGEMENT SYSTEM
==========================================================================

1. PROJECT OVERVIEW
--------------------------------------------------------------------------
DrugWeb is a web-based pharmacy management system designed to facilitate 
medicine purchasing, order tracking, and delivery management. The system 
connects three key Admins, Customers, and Deliverymen through a 
centralized platform built with Python (Flask) and MySQL.

2. USER ROLES & KEY FEATURES
--------------------------------------------------------------------------

[A] ADMIN PANEL
   - Dashboard Overview: View total list of medicines, customer reviews, and
     pending medicine requests.
   - Inventory Viewing: Monitor medicine stock levels, prices, and generic 
     names (Read-Only access).
   - Order Management: View all completed customer payments and orders.
   - Delivery Assignment: Assign specific orders to available Deliverymen 
     directly from the Payments page.
   - Request Handling: Accept or Decline special medicine requests from 
     customers.

[B] CUSTOMER PORTAL
   - Account Management: Register and manage profile details (Name, Address, 
     Phone).
   - Loyalty Program: Earn 1 point for every 10 Taka spent. View points 
     history in the profile.
   - Shopping Experience: 
     * Search medicines by Name or Generic Name.
     * Filter medicines by Price or Name.
     * Browse by Category (Pain Relief, Antibiotic, etc.).
   - Cart System: Add items to cart, update quantities, and view total cost.
   - Checkout & Payment: Place orders using Cash on Delivery or Digital 
     Payment (Bkash/Nagad simulation).
   - Notifications: Receive alerts for order acceptance, delivery updates, 
     and request status changes.
   - Reviews: Write reviews for services/products.
   - Special Requests: Request medicines that are currently out of stock 
     and track the request status.

[C] DELIVERYMAN PANEL
   - Dashboard: View list of orders assigned specifically to them by the Admin.
   - Order Actions:
     * Accept Order: Confirm availability to deliver and set a date.
     * Decline Order: Send the order back to the Admin for reassignment.
     * Mark as Delivered: Confirm successful delivery to the customer.
   - Profile: View personal details.

3. TECHNICAL ARCHITECTURE
--------------------------------------------------------------------------

[A] TECHNOLOGY STACK
   - Backend: Python (Flask Framework)
   - Frontend: HTML, CSS, JavaScript
   - Database: MySQL

[B] DATABASE SCHEMA (11 Tables)
   1. user: Base table for login credentials and common info.
   2. customer: Extends User, stores loyalty points.
   3. admin: Extends User.
   4. deliveryman: Extends User, stores delivery area info.
   5. medicine: Stores product details (Code, Name, Price, Stock, Category).
   6. cart: Temporary storage for items before purchase.
   7. payment: Stores order details, payment status, deliveryman assignment, 
      and delivery status (Assigned/Accepted/Delivered).
   8. notifications: Stores alert messages for customers.
   9. customer_request: Stores user requests for unavailable meds.
   10. customer_review: Stores feedback from customers.
   11. points_history: Logs history of loyalty points earned.

4. SYSTEM WORKFLOW
--------------------------------------------------------------------------
1. Customer Workflow:
   Register/Login -> Browse Medicines -> Add to Cart -> Checkout (Payment) 
   -> Order is Created in 'payment' table with status 'Assigned' (initially unassigned).

2. Admin Workflow:
   Login -> View Payments -> Select an Order -> Select a Deliveryman from 
   dropdown -> Click "Assign".

3. Delivery Workflow:
   Deliveryman Login -> See Assigned Order -> Click "Accept" (Status becomes 
   'Accepted for Delivery') -> Delivers Item -> Click "Mark as Delivered" 
   (Status becomes 'Delivered').

5. INSTALLATION & SETUP
--------------------------------------------------------------------------
1. Install Python and MySQL.
2. Install required libraries:
   pip install flask mysql-connector-python
3. Run the application:
   python app.py
4. Initialize Database:
   Visit http://127.0.0.1:5000/setup_db in your browser once to create 
   tables and dummy data.
5. Login Credentials (Test Data):
   - Admin: admin@test.com / admin123
   - Customer: customer@test.com / password123
   - Deliveryman: delivery@test.com / delivery123
