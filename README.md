## 🌟 Overview

This project is organized for easy extension and experimentation with both backend and frontend chatbot technologies. The backend is primarily Python-based (with Flask and AI agent logic), and the frontend is organized under the `front` directory for web-based user interaction.

---

## 🗂️ Project Structure

```
chatbot/
│
├── front/                   # Frontend (React/Vue/Other JS framework)
│   ├── public/
│   └── src/
│
├── pythonagent/             # Backend AI agent & Flask server
│   └── flask_session/
│
├── .gitignore
└── README.md
```

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/darshankulkarni78/chatbot.git
cd chatbot
```

### 2. Backend Setup (Python)

```bash
cd pythonagent
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
# Start the Flask server (example, update as needed)
python app.py
```

### 3. Frontend Setup (Node.js/React)

```bash
cd front
npm install
npm start

---

## ✨ Features

- Modular codebase for both backend (Python) and frontend (JavaScript)
- Flask-based Python backend, ready for AI logic
- Modern frontend setup under `front/`
- Easy environment management with `.env` support
- Ready-to-use `.gitignore` for Python, Node.js, and secrets

---

## 🛡️ .gitignore Highlights

- Ignores Python caches and compiled files
- Ignores Node.js modules, build, and dist folders
- Ignores environment secrets and editor configs

---
