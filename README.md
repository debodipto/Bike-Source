# Bike Source

Bike Source is a full-stack Django-based used bike ecommerce marketplace.  
It supports buying, selling, inspections, financing, trade-in requests, wishlist, compare, reviews, order management, and admin approval workflows.

## Project Summary

This project is designed as a customer-friendly used bike platform where:

- Buyers can browse and purchase used bikes
- Sellers can submit bike listings
- Customers can compare bikes, save wishlist items, and book inspections
- Users can submit financing and trade-in requests
- Admin can approve listings and manage operational requests from the admin panel

## Tech Stack

- Backend: Django
- Database: SQLite
- Frontend: Django Templates, CSS
- Media Upload: Django `ImageField`

## Run Project

Use these commands from the project folder:

```powershell
cd "c:\Users\user\Downloads\Bike Source\Bike Source"
python manage.py migrate
python manage.py runserver
```

Permanent default admin (code thekei auto-create/update hoy):

```text
username: admin
email: admin@bikesource.local
password: Admin@12345
```

Manual admin user create korte chaile:

```powershell
python manage.py createsuperuser
```

Admin panel:

```text
http://127.0.0.1:8000/admin/
```

## Render Deployment Ready

This project is now prepared for Render deployment.

Added deployment files:

- `render.yaml`
- `build.sh`
- `.python-version`

Production-ready setup includes:

- environment-based `SECRET_KEY`
- environment-based `DEBUG`
- PostgreSQL support through `DATABASE_URL`
- WhiteNoise static file serving
- Gunicorn + Uvicorn start command
- automatic `collectstatic` and `migrate` during build

### Deploy on Render

1. Push the project to GitHub
2. Open Render Dashboard
3. Create a new Blueprint or connect the GitHub repo
4. Render will read `render.yaml`
5. Deploy the web service and PostgreSQL database
6. Deploy-er por build step automatic ei command run kore:

```powershell
python manage.py ensure_admin
```

7. If Render Shell is available, open it and run:

```powershell
python manage.py createsuperuser
```

If Render Shell is not available on your plan, default admin already create hoye jabe. Custom admin command diye override korte hole:

1. Add these environment variables in Render:
   - `ADMIN_USERNAME`
   - `ADMIN_EMAIL`
   - `ADMIN_PASSWORD`
2. Temporarily run this command during deploy or from a one-off command setup:

```powershell
python manage.py ensure_admin
```

This command creates the admin user if it does not exist, or updates the existing admin password and email if it already exists.

### Important Render Notes

- SQLite is not recommended for production on Render, so this project is configured to use PostgreSQL when `DATABASE_URL` is present
- Local development still works with SQLite if `DATABASE_URL` is not set
- Uploaded media on Render is not permanently stored unless you add external storage or persistent disk

## Main User Modules

- Home page
- Marketplace / Buy bike page
- Bike details page
- Sell bike page
- Seller listing management
- Cart and checkout
- Order history and order tracking
- Wishlist
- Compare page
- Financing application
- Trade-in request
- Inspection booking
- Service center page
- Contact page
- User dashboard
- Admin control panel

## URL Flow

Important routes:

- `/` home
- `/buy_list/` marketplace
- `/bike-details/<id>/` bike details
- `/sell/` seller submit page
- `/sell_list/` seller bike list
- `/cart-details/` cart
- `/checkout/` order checkout
- `/booking_list/` customer orders
- `/wishlist/` wishlist
- `/compare/` compare page
- `/financing/` financing application
- `/trade-in/` trade-in request
- `/inspection/` inspection booking
- `/service-centers/` service support
- `/contact-us/` contact form
- `/dashboard/` user dashboard
- `/admin/` admin panel

## Full Project Process Flow

### 1. Visitor Flow

1. Visitor lands on the Home page
2. Visitor browses featured bikes, categories, and service information
3. Visitor goes to Marketplace page
4. Visitor filters bikes by category, city, condition, and price
5. Visitor opens Bike Details page
6. Visitor can choose to:
   - add bike to cart
   - add bike to compare
   - add bike to wishlist after login
   - book inspection
   - read or submit reviews

### 2. User Authentication Flow

1. New user clicks Register
2. Account is created
3. User logs in from Login page
4. Logged-in user gets access to:
   - dashboard
   - wishlist
   - selling flow
   - order history
   - profile update
   - password change

### 3. Buyer Purchase Flow

1. User browses bikes from Marketplace
2. User opens Bike Details page
3. User adds bike to cart
4. User opens Cart page
5. User updates quantity or removes items
6. User proceeds to Checkout
7. User submits:
   - email
   - mobile
   - address
   - payment method
   - notes
8. Order is created
9. Order items are created
10. Product quantity is updated
11. User sees Order Created page
12. User tracks orders from:
   - Dashboard
   - Order history
   - Order detail page

### 4. Seller Flow

1. Logged-in user goes to Sell Bike page
2. Seller submits bike information:
   - name
   - brand
   - model year
   - mileage
   - engine capacity
   - location
   - price
   - quantity
   - condition
   - category
   - negotiable status
   - description
   - multiple images
3. Listing is saved with `Pending` status
4. Admin reviews the listing
5. After admin approval:
   - listing status becomes `Approved`
   - bike becomes visible in marketplace
6. Seller can view submitted listings from `sell_list`

### 5. Wishlist Flow

1. Logged-in user clicks Wishlist button from product card or details page
2. Wishlist entry is created
3. User can view saved bikes from Wishlist page
4. User can remove bike from wishlist
5. Admin can also review wishlist records from admin panel

### 6. Compare Flow

1. User clicks Compare from bike cards
2. Selected bike IDs are stored in session
3. Up to 3 bikes can be added for comparison
4. User visits Compare page
5. System shows bike information side by side
6. User can remove bikes from compare list

### 7. Review Flow

1. Logged-in user opens Bike Details page
2. User submits rating and review comment
3. Review is stored for that bike
4. Approved reviews appear on bike details page
5. Admin can approve or unapprove reviews

### 8. Financing Application Flow

1. User opens Financing page
2. User submits:
   - full name
   - email
   - phone
   - city
   - monthly income
   - down payment
   - employment type
   - preferred bike
   - notes
3. Financing request is saved
4. Admin reviews request
5. Admin can approve, unapprove, or delete request

### 9. Trade-In Flow

1. User opens Trade-In page
2. User submits old bike details
3. Trade-in request is saved
4. Admin reviews request
5. Admin can approve, unapprove, or delete request

### 10. Inspection Booking Flow

1. User opens Inspection page
2. User selects bike, date, slot, and note
3. Booking is saved
4. Admin reviews booking
5. Admin can approve, unapprove, or delete booking

### 11. Contact Message Flow

1. User opens Contact page
2. User submits support message
3. Message is stored in database
4. Admin reviews the message
5. Admin can approve, unapprove, or delete message

### 12. Service Center Flow

1. User visits Service Centers page
2. User sees available service/support locations
3. Admin can add or edit service centers from admin panel

### 13. Admin Flow

Admin panel is the operational control center of the project.

Admin can manage:

- Categories
- Bike listings
- Bike images
- Orders
- Order items
- Banners
- Reviews
- Wishlist
- Financing applications
- Trade-in requests
- Inspection bookings
- Contact messages
- Service centers

Admin actions include:

- Approve or reject bike listings
- Mark bikes as featured
- Mark bike stock availability
- Update order status
- Approve/unapprove reviews
- Approve/unapprove wishlist records
- Approve/unapprove financing applications
- Approve/unapprove trade-in requests
- Approve/unapprove inspection bookings
- Approve/unapprove contact messages
- Delete any record from admin panel

## Database Core Models

Main models used in this project:

- `Category`
- `BikeBuyAndSell`
- `BikeBuyAndSellImage`
- `Orders`
- `OrderItem`
- `Banner`
- `Wishlist`
- `Review`
- `FinancingApplication`
- `TradeInRequest`
- `ServiceCenter`
- `InspectionBooking`
- `ContactMessage`

## Business Logic Highlights

- Only approved bikes appear in marketplace
- Compare uses session storage
- Cart stores items in session
- Checkout decreases bike quantity
- Out-of-stock bikes become unavailable
- Wishlist and special request modules support admin approval flow
- Reviews can be moderated by admin

## Suggested Admin Usage Order

For best demo flow, admin should do these first:

1. Create categories
2. Add banners
3. Add or approve bikes
4. Mark some bikes as featured
5. Add service centers
6. Review new financing, trade-in, inspection, and contact submissions
7. Track orders and update delivery status

## Project Folder Overview

- `manage.py` Django command entry
- `core/` project settings and root URLs
- `bike_buy_and_sell/` app logic
- `templates/` frontend pages
- `media/` uploaded images
- `db.sqlite3` SQLite database

## Final Note

Bike Source is built as a used bike marketplace with both ecommerce and operations workflow support.  
It is not only a buy/sell website now, but a more complete platform including pre-sales, checkout, post-sales, and admin process management.
