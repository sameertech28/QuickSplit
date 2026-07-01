# QuickSplit - Smart Bill & Expense Splitter 💸

QuickSplit is a modern, beautiful, and intelligent application designed to make splitting bills instant and fair. Whether it's a dinner with friends, roommates sharing utility bills, or group travel expenses, QuickSplit takes the frustration out of "who owes who what."

## 🚀 Features (In Development)
- **Instant Group Creation**: Easily create groups for trips, roommates, or events.
- **Smart Splitting**: Split equally, by exact percentage, or item-by-item.
- **Multi-Currency**: Add expenses in any currency and auto-convert.
- **Smart Settlement Algorithm**: Minimizes the number of transactions required to settle debts.

## 🛠️ Tech Stack
- **Backend**: Django 4.2 + Django REST Framework
- **Frontend**: Bootstrap 5, Alpine.js, Custom CSS (Glassmorphism design)
- **Database**: SQLite (Development) / PostgreSQL (Production)
- **Background Tasks**: Celery & Redis (Pending)

## 💻 Local Development Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/sameertech28/QuickSplit.git
   cd QuickSplit
   ```

2. **Create a virtual environment and activate it:**
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On Mac/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   Copy the example environment file and update it with your own secret key.
   ```bash
   cp .env.example .env
   ```

5. **Apply database migrations:**
   ```bash
   python manage.py migrate
   ```

6. **Run the development server:**
   ```bash
   python manage.py runserver
   ```
   Navigate to `http://127.0.0.1:8000` in your browser.

## 📄 License
This project is proprietary and confidential.
