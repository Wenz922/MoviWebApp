# 🎬 Movie Web App

A Flask web application for managing users and their favorite movies.  
Each user can add movies via the OMDb API, rate them, and leave personal notes.

---

## 🚀 Features

- Add and manage users  
- Fetch movie details automatically from the [OMDb API](https://www.omdbapi.com/)  
- Update personal rating and notes  
- Delete movies from favorites  
- User-friendly web interface (HTML/CSS/Flask)  
- Logging system with rotating log files (`logs/app.log`)  
- Error handling with custom 404 and 500 pages  

---

## 🧰 Tech Stack

- **Backend:** Python, Flask, Flask-SQLAlchemy  
- **Frontend:** HTML, CSS (Jinja2 templates)  
- **Database:** SQLite  
- **API:** OMDb API  
- **Logging:** Python `logging` with `RotatingFileHandler`

---

## ⚙️ Installation & Setup

1. **Clone this repository**
   ```bash
   git clone https://github.com/Wenz922/MoviWebApp.git
   cd MovieWebApp
2. **Create and activate a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # macOS/Linux
   venv\Scripts\activate  # Windows
3. **Install dependencies**
   ```bash
   pip3 install -r requirements.txt
4. **Create an `.env` file in the project root:**
   ```bash
   SECRET_KEY='your_secret_key_here'
   API_KEY='your_omdb_api_key_here'
5. **Run the app**
   ```bash
   python3 app.py
6. **Open in your browser**
   ```bash
   http://127.0.0.1:5000

---

## 🗂️ Project Structure

    MovieWebApp/
    │
    ├── app.py
    ├── data_manager.py
    ├── models.py
    ├── requirements.txt
    ├── README.md
    ├── .env
    ├── /logs
    │   └── app.log
    ├── /data
    │   └── movies.sqlite
    ├── /templates
    │   ├── base.html
    │   ├── index.html
    │   ├── movies.html
    │   ├── 404.html
    │   └── 500.html
    └── /static
        └── styles.css

---

## 🧾 Logging

Logs are stored in `logs/app.log` with automatic rotation (max 1 MB per file, up to 5 backups).
Each action such as user creation, movie addition, and deletion is recorded with timestamps and error traces.

---

## 🧠 Example Usage

1. Go to `/` → create a new user
2. Click **View Movies** → add movies by title (and optionally year)
3. Rate, write notes, update, or delete movies

---

## 🛠️ Troubleshooting

| Problem                       | Solution                                               |
| ----------------------------- | ------------------------------------------------------ |
| **500 Internal Server Error** | Check `logs/app.log` for detailed traceback.           |
| **OMDb fetch fails**          | Verify your `API_KEY` in `.env`.                       |
| **Database locked**           | Stop Flask, delete `data/movies.sqlite`, then restart. |

---

## 📜 License

MIT License © 2025 Wenzheng Cai
---

## 💬 Acknowledgments

- [python-dotenv](https://pypi.org/project/python-dotenv/) – load API key from `.env`  
- [OMDb API](https://www.omdbapi.com/) for movie data
- [Flask](https://https://flask.palletsprojects.com/en/stable/) framework
- [Flask-SQLAlchemy](https://flask-sqlalchemy.readthedocs.io/en/stable/) for database handling  
