Project Title: DrugWeb
Overview

DrugWeb is an online pharmacy and medicine delivery management system designed to simplify medicine purchasing, stock tracking, payments, and delivery handling.
The system provides three distinct user roles, which are Admin, Customer, and Deliveryman. Each supported by a well-structured database model shown in the ER/EER diagrams.

The main PDF diagrams illustrate a system that handles medicines, carts, payments, requests, reviews, notifications, and delivery assignment in a relational, fully normalized model.

Key Features
Admin Panel
1. Medicine & Stock Management

Admin manages all medicines using attributes such as Med_Code, Generic_Name, Name, Price, and Stock.

Can update stock quantities and track availability in real time.

2. User & Deliveryman Management

Admin can manage Customers and Deliverymen, each identified with unique IDs and profile information.

3. Cart & Order Monitoring

Admin can view all customer carts through relationships:

Each cart links to Customer ID, Medicine Code, and Quantity.

Helps monitor orders before payment and delivery processing.

4. Payment Handling

Payments are linked to:

Payment_ID

Payment_Type (Online / COD)

Amount

Cart_ID

Deliveryman_ID

Admin verifies payments and ensures proper linking with delivery tasks.

5. Deliveryman Assignment

Admin assigns deliverymen to orders through the accept relationship table.

Assignment includes customer, deliveryman, payment, and date details.

6. Notification System

The notification entity links Customer, Medicine, and Cart for alerts like:

“Item added to cart”

“Stock updated”

“Order status update”

7. Review Management

Admin can monitor customer reviews through the review table.

Reviews are connected to customers and optionally medicines.

8. Customer Request Handling

Customers can request unavailable medicines through the customer_request entity.

Each request includes:

Request ID

Medicine Name

Expected Date

Customer Portal
1. Account Management

Customer has unique profile fields including ID, Name, Email, Address, Phone, etc.

2. Search & Browse Medicines

View medicine list (Name, Generic Name, Unit Price, Stock levels).

3. Add to Cart

Carts include:

Cart_ID

Medicine Code

Quantity

Customer ID

4. Proceed to Payment

User can choose between:

Online Payment

Cash on Delivery

Successful payments are logged in the payment entity.

5. Track Delivery

Delivery status managed via the accept table:

Deliveryman ID

Payment ID

Acceptance Date

6. Write Reviews

Customers can leave reviews for medicine/service using review entity.

7. Request Unavailable Medicines

Submit special requests using customer_request:

Requested medicine name

Expected need date

Deliveryman Panel
1. Assigned Orders

Deliveryman receives an order assigned by admin.

Each assigned order includes:

Customer ID

Payment ID

Date

Delivery acceptance

2. Delivery Status Updates

Deliveryman confirms acceptance and completion of deliveries.

Overall System Workflow (Based on PDF ER/EER)

Customer registers → browses medicines → adds items to cart

Customer proceeds to payment → system records payment

Admin assigns a deliveryman → deliveryman accepts

Customer receives delivery → leaves a review

Admin monitors stock, payments, deliveries, reviews, and medicine requests

