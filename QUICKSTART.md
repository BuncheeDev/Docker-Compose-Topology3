# ⚡ Quick Start Guide

## 🚀 Get Started in 5 Minutes

### 1. Prerequisites
- Docker & Docker Compose installed
- Terminal/Command Prompt open

### 2. Start the Application

```bash
# Navigate to project directory
cd "D:\Mongkol.Drive\8.0_Computer Engineering\2026\CT519 - การประมวลผลคลาวด์\Homework\Docker compose"

# Start all services
docker-compose up -d
```

### 3. Access the Application

```
Frontend:  http://localhost:5173  👉 Main UI
Backend:   http://localhost:8000  👉 API
API Docs:  http://localhost:8000/docs  👉 Swagger
Database:  localhost:5432  👉 PostgreSQL
```

### 4. First Steps

1. **Open browser**: http://localhost:5173
2. **Click "Sample"** to load demo network
3. **Click "🔍 Scan LAN"** to discover real network
4. **Click on a node** to send message/ping
5. **Click "▶ Live Feed"** to simulate status changes

### 5. Stop Services

```bash
docker-compose down
```

---

## 📁 Project Structure

```
├── docker-compose.yml      ← Main configuration
├── README.md               ← Full documentation
├── USE_CASE.md            ← Architecture & use cases
│
├── frontend/               ← Vue.js 3 UI
│   ├── package.json
│   ├── vite.config.js
│   └── src/App.vue
│
├── backend/                ← Python FastAPI API
│   ├── main.py
│   └── requirements.txt
│
└── database/               ← PostgreSQL schema
    └── init.sql
```

---

## 🔧 Common Commands

```bash
# View all services
docker-compose ps

# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Restart services
docker-compose restart

# Clean up everything
docker-compose down -v
```

---

## 🐛 Troubleshooting

### Frontend Not Loading
```bash
# Check if container is running
docker-compose ps

# Check frontend logs
docker-compose logs frontend

# Rebuild and restart
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Backend API Not Responding
```bash
# Check if backend is running
docker-compose ps backend

# Check backend logs
docker-compose logs backend

# Test API
curl http://localhost:8000
```

### Database Connection Failed
```bash
# Check database health
docker-compose exec database pg_isready

# Check database logs
docker-compose logs database

# Verify credentials in docker-compose.yml
```

---

## 📚 Full Documentation

- **[README.md](README.md)** - Complete project documentation
- **[USE_CASE.md](USE_CASE.md)** - Architecture and use cases
- **[API Docs](http://localhost:8000/docs)** - Interactive API documentation (when running)

---

## 🎯 Features

✅ **Network Discovery** - Scan LAN and find all devices  
✅ **Real-time Visualization** - See network topology with animations  
✅ **Device Management** - Send messages, ping, wake devices  
✅ **Data Persistence** - Save scan results and action history  
✅ **Live Simulation** - Test with demo scenarios  
✅ **Responsive Design** - Works on desktop and tablet  

---

## 🏗️ Tech Stack

| Component | Technology |
|-----------|-----------|
| Frontend | Vue.js 3 + Tailwind CSS + Vite |
| Backend | Python FastAPI + SQLAlchemy |
| Database | PostgreSQL 16 |
| Container | Docker + Docker Compose |

---

## 📞 Quick Help

```bash
# See all available commands
make help

# Setup and start
make setup

# View service status
make health

# Open database shell
make sql

# Open backend shell
make bash-backend
```

---

**That's it! Enjoy your Live System Topology dashboard! 🎉**

For more details, see [README.md](README.md)
