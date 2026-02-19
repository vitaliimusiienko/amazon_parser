# 📦 Amazon Best Sellers Tracker

A robust full-stack application designed for automated monitoring of Amazon Best Sellers. The system leverages **Playwright** for real-time scraping, **FastAPI** for data orchestration, and **React (Vite)** for a modern user experience.

---

## 🚀 Key Features

* **Real-time Dynamic Scraping:** Extracts Top-5 products from any Amazon Best Sellers category on demand.
* **Intelligent Backend Caching:** Implements a "Lazy Loading" pattern—if data exists in the database, the system bypasses the heavy browser-based scraper to save resources.
* **Automated Syncing:** Integrated **APScheduler** updates root categories daily at midnight.
* **Data Persistence:** Full **Upsert** logic (Update or Insert) ensures product data (prices, ratings) is always current without duplicating entries based on ASIN.
* **Smart Filtering:** Client-side interface for instant sorting by price (ascending/descending) and customer ratings.

---

## 🛠 Tech Stack

| Component | Technology |
| :--- | :--- |
| **Backend** | Python 3.10+, FastAPI, SQLAlchemy (Async), PostgreSQL |
| **Scraper** | Playwright (Chromium) |
| **Frontend** | React 18+, Tailwind CSS, Vite |
| **Task Runner** | APScheduler (CronTrigger) |
| **Logging** | Python Logging Module (Custom Setup) |

---

## 📥 Installation

### 1. Clone the Repository
```bash
git clone [https://github.com/your-username/amazon-bestsellers-tracker.git](https://github.com/your-username/amazon-bestsellers-tracker.git)
cd amazon-bestsellers-tracker
```
### 2. Backend Setup
Navigate to the backend directory, create a virtual environment, and install dependencies:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```
Crucial: Install Playwright browser binaries:
```bash
playwright install chromium
```
### 3. Environment Configuration
Create a .env file in the backend/ directory:
```bash
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/amazon_db
DEBUG=True
LOG_LEVEL=INFO
BROWSER_HEADLESS=True
[OPTIONAL]PROXY_URL=http://username:password@ip:port
```
### 4. Frontend Setup
Install npm packages and start the development server:
```bash
cd ../frontend
npm install
npm run dev
```
🏃‍♂️ Running the Application
Start your PostgreSQL instance.

Launch the Backend:
```bash
python run.py
```
Access the Dashboard: Open http://localhost:5173 in your browser.

API Documentation: Explore the interactive Swagger UI at 
```bash
http://localhost:8000/docs
```
📂 Project Structure
```plaintext
├── backend
│   ├── app
│   │   ├── api          # FastAPI route handlers
│   │   ├── models       # SQLAlchemy DB models (Product, Category)
│   │   ├── services     # Business logic layer (ProductService, CategoryService)
│   │   └── utils        # Scraping logic (Playwright) & Loggers
│   └── main.py          # App entry point & Lifespan/Scheduler config
├── frontend
│   ├── src
│   │   ├── components   # UI Components (ProductCards, Navbar)
│   │   └── App.jsx      # Main application logic & State management
└── README.md
```
🔧 Development Insights
Service Layer Pattern: Database operations are decoupled from API routes into a dedicated Service layer, ensuring the code is maintainable and testable.

Concurrency: Utilizes Python's asyncio for non-blocking database I/O and scraping operations.

Resilience: Includes error handling for Amazon's anti-scraping measures and dynamic page layouts.

Developed by Vitalii Musiienko
Python Engineer | 2026
