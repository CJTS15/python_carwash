# 🚗 Velez Carwash Reservation System

A professional, mobile-friendly web application built with **Python** and **Django**. This system streamlines the car wash experience by allowing guests to book services instantly, customers to track their car's status, and staff to manage their daily commissions.

## ✨ Key Features

### 🔹 For Customers
- **Guest-First Booking**: No account needed. Quick booking with name, phone, and plate number.
- **Smart Scheduling**: Real-time time slot availability using AJAX (no page refreshes).
- **Booking Tracker**: Search via Plate Number to see real-time status (Pending, In Progress, Completed).
- **Service Add-ons**: Choose extra services (Engine Wash, Waxing, etc.) with automatic price updates.
- **Shop Locator**: Interactive Google Maps integration with custom Dark Mode support.
- **Modern UI**: Full Light/Dark/System theme support powered by Tailwind CSS.

### 🔹 For Staff (Washers)
- **Dedicated Task Dashboard**: Mobile-optimized list of assigned jobs for the day.
- **Job Timer/Workflow**: One-tap buttons to move jobs from "In Progress" to "Completed."
- **Commission Tracker**: Automatic calculation of earnings per wash based on final collected price.

### 🔹 For Admins (Owner)
- **Professional Dashboard**: High-end management interface using **Django Unfold**.
- **Role Management**: Distinguish between the Owner (Superuser) and Staff (Washers).
- **Dynamic Pricing**: Set price ranges (Min/Max) for different vehicle sizes.
- **Staff Assignment**: Easily assign specific washers to incoming bookings.

## 🛠️ Tech Stack

- **Backend:** Python 3.x, Django 5.x
- **Frontend:** Tailwind CSS, JavaScript (Vanilla AJAX)
- **UI Components:** Django Unfold (Admin Theme), Django Humanize
- **Database:** SQLite (Development) / PostgreSQL (Production ready)

## 🚀 Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/velez-carwash.git
cd velez-carwash
```

### 2. Set up a Virtual Environment
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install django django-unfold django-environ
```

### 4. Database Setup
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create an Admin Account
```bash
python manage.py createsuperuser
```

### 6. Run Server
```bash
python manage.py runserver
```

Visit http://127.0.0.1:8000 to see the app!

## 📂 Project Structure

- **config/:** Project settings and main URL routing.
- **reservations/:** Core app logic (Models, Views, AJAX endpoints).
- **templates/:** Professional HTML5 templates with Tailwind CSS.
- **static/:** Custom CSS and assets.

## 📝 License

This project is open-source and available under the MIT License.

Built with ❤️ for Velez Carwash.