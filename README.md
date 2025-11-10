# GESTEM - Laboratory Inventory Management System

## Overview
GESTEM was born from a real need in academic research: streamlining laboratory supplies management. As a PhD researcher, I identified inefficiencies in our manual ordering process that were impacting our research workflow. With no prior programming experience, I took the initiative to learn web development and created a solution that has transformed how our lab handles inventory management.

Currently deployed on the university's local server, GESTEM serves approximately 20 active weekly users across different research units, demonstrating how a self-taught programming project can effectively solve real-world workplace challenges.

## Features and Technology Stack

- **Order Management**: Complete tracking system from request to reception, built with Django 3.1
- **Smart Notifications**: Automated email updates on order status using Celery
- **Product Catalog**: SQLite database managing products, suppliers, and storage locations
- **User Interface**: Responsive design with Bootstrap and jQuery for seamless experience
- **Role-Based Access**: Multiple access levels for researchers, administration, and managers
- **Process Automation**: Automatic order code generation and template system for frequent orders

## Core Features

### Product Management
- Complete product catalog with detailed information
- Product categorization (cell culture, viability kits, spheres, etc.)
- Manufacturer and distributor registry
- Reference and product code system

### Order System
- Order creation and tracking
- Order status management (pending, in process, received)
- Notes and annotations system per order
- Automatic order code generation
- Integration with CPM (Budget Control) system

### Storage Management
- Location and warehouse control
- Reception tracking
- Delivery address management
- Location notes system

### Administrative Features
- User authentication system
- Role-based permission management
- Cost center tracking
- Email notification system
- Administrative interface

### Additional Features
- Templates for frequent orders
- Advanced product and order search
- Self-management system
- Telegram integration (optional)

## Technical Requirements

### Main Dependencies
- Python 3.x
- Django 3.1.2
- Celery 5.0.3
- Django Crispy Forms 1.9.2
- Other dependencies listed in requirements.txt

### Database
- Compatible with Django backends
- Migrations included

## Installation

### Using Docker (Recommended)

1. Ensure Docker and Docker Compose are installed
2. Clone the repository:
```bash
git clone https://github.com/jpm92/gestem.git
```
3. Create `.env` file from template:
```bash
cp .env.example .env
```
4. Build and start containers:
```bash
docker-compose up --build
```
5. Run migrations:
```bash
docker-compose exec web python manage.py migrate
```
6. Create superuser:
```bash
docker-compose exec web python manage.py createsuperuser
```

The application will be available at `http://localhost:8000`

### Local Installation

1. Clone the repository
2. Create and activate Python 3.x virtual environment
3. Install dependencies:
```bash
pip install -r requirements.txt
```
4. Set up environment variables (copy `.env.example` to `.env`)
5. Run migrations:
```bash
python manage.py migrate
```
6. Create superuser:
```bash
python manage.py createsuperuser
```
7. Start the server:
```bash
python manage.py runserver
```

## Configuration

The project uses a split configuration system:
- Base configuration (`gestem/settings/base.py`)
- Production configuration (`gestem/settings/prod.py`)
- Environment variables for sensitive values

## Project Structure

```
gestem/
├── manage.py
├── requirements.txt
├── gestem/
│   ├── settings/
│   │   ├── base.py
│   │   └── prod.py
│   ├── urls.py
│   └── wsgi.py
└── gestion/
    ├── models.py
    ├── views.py
    ├── forms.py
    ├── admin.py
    ├── urls.py
    └── templates/
```

## Main Models

### Product
Manages information for available products for ordering.

### Order
Handles confirmed orders to suppliers.

### Item
Represents instances of products in orders or drafts.

### Note
Manages sets of items annotated simultaneously.

### Storage
Controls product storage locations.

## Docker Configuration

The project includes a complete Docker setup for development and production:

```yaml
version: '3.8'

services:
  web:
    build: .
    command: gunicorn gestem.wsgi:application --bind 0.0.0.0:8000
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    env_file:
      - .env
    depends_on:
      - redis

  redis:
    image: redis:6
    
  celery:
    build: .
    command: celery -A gestem worker -l info
    volumes:
      - .:/app
    env_file:
      - .env
    depends_on:
      - redis

volumes:
  sqlite_data:
```

## Author

Developed by [Jesús Peña] - [https://www.linkedin.com/in/jpema/]