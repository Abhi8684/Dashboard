# Task Management Dashboard

A Python web application that accepts Excel file uploads and generates an interactive analytics dashboard matching your task management data.

## 🚀 Quick Start (Local)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the app
python app.py

# 3. Open your browser
# http://localhost:5000
```

Upload your Excel file → Dashboard auto-generates at `/dashboard/`

---

## 📁 Project Structure

```
├── app.py               # Flask entry point + file upload handler
├── dashboard.py         # Plotly Dash app (all charts + KPI cards)
├── data_processor.py    # Excel parsing, KPI calculations, chart data
├── templates/
│   └── upload.html      # Upload UI page
├── static/
│   └── style.css        # Dark-theme styles
├── uploads/             # Auto-created, stores uploaded files
├── requirements.txt
├── Procfile             # For Render/Railway deployment
├── runtime.txt          # Python version pin
└── README.md
```

---

## 📊 Dashboard Features

| Feature | Description |
|---------|-------------|
| **KPI Cards** | Total Tasks, Completed, Delayed, Today's Tasks, Completed Today |
| **Bar Chart** | Monthly completed tasks by asset/panel type |
| **Horizontal Bar** | Today's ongoing tasks by asset type |
| **Pie Chart** | Overall status distribution (Completed / Ongoing / Hold) |
| **Stacked Bar** | Daily breakdown of task statuses over time |

---

## 📋 Expected Excel Columns

| Column | Description |
|--------|-------------|
| `Area` | Work area / bay |
| `Date` | Task date (dd-mm-yyyy) |
| `Employee Name` | Assigned worker |
| `Panel` | Asset / equipment type |
| `Fleet Number` | Equipment ID |
| `Task Description` | Work performed |
| `Task Start Time (Today)` | HH:MM format |
| `Task End Time (Today)` | HH:MM format |
| `Total Hours` | Numeric hours |
| `Current Status` | `Completed` / `Ongoing` / `Hold` |

---

## ☁️ Deploy to Render.com (Free, No Docker)

### Step 1 — Push to GitHub
```bash
git init
git add .
git commit -m "Initial dashboard"
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

### Step 2 — Create a Web Service on Render
1. Go to [render.com](https://render.com) → Sign up (free)
2. Click **New** → **Web Service**
3. Connect your GitHub repo
4. Fill in the settings:
   - **Name**: `task-dashboard` (or any name)
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:server`
   - **Plan**: `Free`
5. Add an **Environment Variable**:
   - Key: `SECRET_KEY` | Value: any long random string
6. Click **Create Web Service**
7. Wait ~2 minutes for the first deploy
8. Your app is live at `https://your-app.onrender.com` 🎉

### Alternative: Railway.app
1. Go to [railway.app](https://railway.app) → sign up with GitHub
2. Click **New Project** → **Deploy from GitHub repo**
3. Select your repo → it auto-detects Python and uses the `Procfile`
4. Add env var `SECRET_KEY`
5. Click **Deploy** → Live in ~1 minute

---

## 🔧 Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | `kannetn-dashboard-secret-2026` | Flask session secret (change in production!) |
| `PORT` | `5000` | Port (auto-set by Render/Railway) |

---

## 📝 Notes

- Uploaded files are stored in the `uploads/` folder. The dashboard always shows the **most recently uploaded** file.
- For multi-user production use, consider adding a database (SQLite) to store per-session file paths.
- The `/dashboard/` route is powered by Plotly Dash, mounted inside Flask.
