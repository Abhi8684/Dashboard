# 📊 Kannetn Task Management Dashboard

A Python web application that accepts Excel file uploads and generates an interactive analytics dashboard for workshop daily activity tracking.

Built with **Flask**, **Plotly Dash**, and **Pandas** — featuring a modern dark-themed UI with drag-and-drop file uploads and real-time KPI analytics.

---

## 🚀 Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/Dashboard.git
cd Dashboard

# 2. Create a virtual environment (recommended)
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the application
python app.py

# 5. Open your browser
# http://localhost:5000
```

Upload your Excel file → Dashboard auto-generates at `/dashboard/`

---

## 📁 Project Structure

```
Dashboard/
├── app.py                # Flask entry point + file upload handler
├── dashboard.py          # Plotly Dash app (all charts + KPI cards)
├── data_processor.py     # Excel parsing, KPI calculations, chart data
├── templates/
│   └── upload.html       # Upload UI (drag-and-drop + progress bar)
├── static/
│   └── style.css         # Dark-theme styles with animations
├── test_data/            # Sample Excel files for testing
├── uploads/              # Auto-created, stores uploaded files
├── requirements.txt      # Python dependencies
├── Procfile              # Gunicorn start command for deployment
├── runtime.txt           # Python version pin (3.11.9)
└── README.md
```

---

## 📊 Dashboard Features

| Feature              | Description                                                      |
| -------------------- | ---------------------------------------------------------------- |
| **KPI Cards**        | Total Tasks, Completed, Delayed, Today's Tasks, Completed Today  |
| **Bar Chart**        | Completed tasks grouped by asset/panel type for the month        |
| **Horizontal Bar**   | Today's ongoing tasks by asset type                              |
| **Pie Chart**        | Overall status distribution (Completed / Ongoing / Hold)         |
| **Stacked Bar**      | Daily breakdown of task statuses over time                       |

### Upload Page

- Modern drag-and-drop file upload interface
- File type validation (`.xlsx`, `.xls`)
- Upload progress bar with animated spinner
- Expandable column hint guide
- Max file size: **16 MB**

---

## 📋 Expected Excel Columns

The application expects a **Daily Activity Tracker** Excel file with these columns:

| Column                     | Description                                    |
| -------------------------- | ---------------------------------------------- |
| `Area`                     | Work area / bay                                |
| `Date`                     | Task date (dd-mm-yyyy)                         |
| `Employee Name`            | Assigned worker                                |
| `Panel`                    | Asset / equipment type                         |
| `Fleet Number`             | Equipment ID                                   |
| `Task Description`         | Work performed                                 |
| `Task Start Time (Today)`  | HH:MM format                                   |
| `Task End Time (Today)`    | HH:MM format                                   |
| `Total Hours`              | Numeric hours                                  |
| `Current Status`           | `Completed` / `Ongoing` / `Hold`               |

> [!NOTE]
> For multi-sheet workbooks, the app looks for a sheet named **`Daily_Activity_Tracker`**. Single-sheet files are read directly.

---

## 🛠️ Tech Stack

| Technology      | Purpose                              |
| --------------- | ------------------------------------ |
| **Flask**       | Web server, routing, file uploads    |
| **Plotly Dash** | Interactive dashboard & charting     |
| **Pandas**      | Data processing & KPI computation   |
| **openpyxl**    | Excel file parsing                   |
| **Gunicorn**    | Production WSGI server               |
| **Inter Font**  | Modern UI typography (Google Fonts)  |

---

## ☁️ Deployment

### Deploy to Render.com

1. Push your code to GitHub
2. Go to [render.com](https://render.com) → **New** → **Web Service**
3. Connect your GitHub repo and configure:
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:server`
   - **Plan**: Free
4. Add environment variable: `SECRET_KEY` = *(any long random string)*
5. Click **Create Web Service** — live in ~2 minutes

### Deploy to Railway.app

1. Go to [railway.app](https://railway.app) → **New Project** → **Deploy from GitHub repo**
2. Select your repo (auto-detects Python via `Procfile`)
3. Add environment variable: `SECRET_KEY`
4. Click **Deploy** — live in ~1 minute

---

## 🔧 Environment Variables

| Variable     | Default                            | Description                               |
| ------------ | ---------------------------------- | ----------------------------------------- |
| `SECRET_KEY` | `kannetn-dashboard-secret-2026`    | Flask session secret (change in production!) |
| `PORT`       | `5000`                             | Server port (auto-set by hosting platforms)  |

---

## 📝 Notes

- The dashboard always displays data from the **most recently uploaded** file
- Uploaded files are stored in the `uploads/` folder
- The `/dashboard/` route is powered by **Plotly Dash**, mounted inside Flask
- For multi-user production use, consider adding a database to store per-session file paths

---

## 📄 License

Kannetn Project © 2026
