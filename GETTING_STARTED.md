# 🚀 Getting Started with Live System Topology

## Step-by-Step Setup Guide

### 📌 Prerequisites Check

Before starting, ensure you have:

```bash
# Check Docker
docker --version
# Should output: Docker version 20.x or higher

# Check Docker Compose
docker-compose --version
# Should output: Docker Compose version 1.29 or higher

# Check Git (optional)
git --version
# Should output: git version 2.x or higher
```

If not installed:
- **Docker**: https://www.docker.com/products/docker-desktop
- **Docker Compose**: Included with Docker Desktop

---

## 🎯 Installation Steps

### Step 1: Navigate to Project Directory

```bash
cd "D:\Mongkol.Drive\8.0_Computer Engineering\2026\CT519 - การประมวลผลคลาวด์\Homework\Docker compose"
```

### Step 2: Verify Project Structure

```bash
# Check if all required files are present
ls -la docker-compose.yml backend/ frontend/ database/

# You should see:
# ✓ docker-compose.yml
# ✓ backend/ (with Dockerfile, main.py, requirements.txt)
# ✓ frontend/ (with Dockerfile, package.json, src/)
# ✓ database/ (with init.sql)
```

### Step 3: Build Docker Images

```bash
# Build all services
docker-compose build

# This will:
# 1. Build frontend image from Node.js 20
# 2. Build backend image from Python 3.11
# 3. Pull PostgreSQL 16 image

# ⏱️ This may take 2-5 minutes depending on internet speed
```

### Step 4: Start Services

```bash
# Start all services in background
docker-compose up -d

# Check if services are running
docker-compose ps

# You should see:
# ✓ topology_frontend    (healthy)
# ✓ topology_backend     (healthy)
# ✓ topology_db          (healthy)
```

### Step 5: Wait for Services to be Ready

```bash
# Check logs to see if services are ready
docker-compose logs -f

# Wait for messages like:
# backend  | 🚀 Topology Backend Starting...
# backend  | Uvicorn running on 0.0.0.0:8000
# frontend | VITE v5.0.0  ready in xxx ms
```

Press `Ctrl+C` to exit logs when ready.

### Step 6: Access the Application

Open your browser and navigate to:

```
🖥️  http://localhost:5173
```

You should see the **Live System Topology** dashboard with:
- Animated starfield background
- **Docker topology loaded by default** (Machine → Container → Image)
- Control buttons (🐳 Docker · 📊 Sample · ⚠️ Degraded · 🔍 Scan LAN)
- Node visualization with live status colors

---

## 🎮 First Time Usage

### 0. Docker Topology (loads automatically)

เมื่อเปิดหน้าเว็บ ระบบจะเรียก **"🐳 Docker"** ให้อัตโนมัติ แสดงโครงข่ายจริงของเครื่อง:
- **Machine** (host) ทางซ้าย
- **Containers** ตรงกลาง (สีเขียว = running, แดง = exited)
- **Images** ทางขวา โยงกลับไปยัง container ที่ใช้
- กด **🐳 Docker** ซ้ำเพื่อรีเฟรชข้อมูลล่าสุด

### 1. Load Sample Network

Click the **"📊 Sample"** button to load a demo network with:
- 5 nodes (User, Mac, VPS, Node A, Node B)
- 5 edges (connections between nodes)
- Different status colors
- Animated particles

### 2. Interact with Nodes

- **Click** a node → Opens action panel
- **Drag** a node → Move its position
- **Double-click** a node → Release from manual position

### 3. Send Test Message

```
1. Click on any node → Action panel opens
2. Type a message in the text field
3. Click "Send Message" button
4. Watch the status update
```

**Note**: To see actual messages on real machines, run `node agent.js` on target machines.

### 4. Scan Real Network

```
1. Click "🔍 Scan LAN" button
2. Backend discovers all devices
3. Nodes appear on the ring layout
4. Hub (gateway or this PC) at center
5. Other devices arranged in circle
```

### 5. Monitor Live Status

```
1. Click "▶ Live Feed" button
2. Devices change status randomly
3. Nodes pulse with activity
4. Data flows along edges
5. Click again to stop
```

---

## 🔧 Common Tasks

### View Service Logs

**All services**:
```bash
docker-compose logs -f
```

**Backend only**:
```bash
docker-compose logs -f backend
```

**Frontend only**:
```bash
docker-compose logs -f frontend
```

**Database only**:
```bash
docker-compose logs -f database
```

### Access API Documentation

Open in browser:
```
http://localhost:8001/docs
```

You'll see Swagger UI with all available endpoints.

### Connect to Database

```bash
# Open psql shell
docker-compose exec database psql -U topology_user -d topology_db

# Common commands:
\dt                          # List tables
SELECT * FROM hosts;         # View all hosts
SELECT * FROM action_history; # View action logs
\q                           # Exit
```

### Access Backend Console

```bash
# Open bash in backend container
docker-compose exec backend bash

# Inside container:
python -c "import fastapi; print(fastapi.__version__)"
```

### Access Frontend Console

```bash
# Open bash in frontend container
docker-compose exec frontend bash

# Inside container:
npm list
```

---

## 📊 Monitoring & Health Checks

### Quick Health Check

```bash
# Check all services
docker-compose ps

# Output should show:
# NAME                  STATUS
# topology_frontend     Up (healthy)
# topology_backend      Up (healthy)
# topology_db           Up (healthy)
```

### API Health Check

```bash
# Backend is running
curl http://localhost:8001

# Response:
# {"status": "ok", "service": "Topology Backend", "version": "1.0.0"}
```

### Database Health Check

```bash
# Database is accepting connections
docker-compose exec database pg_isready

# Response: accepting connections
```

---

## 🐛 Troubleshooting

### Frontend Not Loading (Blank Page)

**Problem**: Page shows blank or "Cannot GET /"

**Solution**:
```bash
# 1. Check if frontend is running
docker-compose ps frontend

# 2. Check frontend logs
docker-compose logs frontend

# 3. Verify port 5173 is not in use
netstat -an | grep 5173

# 4. Rebuild and restart
docker-compose restart frontend
```

### Backend API Error (500)

**Problem**: API returns 500 error or doesn't respond

**Solution**:
```bash
# 1. Check if backend is running
docker-compose ps backend

# 2. Check backend logs for errors
docker-compose logs backend

# 3. Restart backend
docker-compose restart backend

# 4. If issues persist, rebuild
docker-compose build --no-cache backend
docker-compose up -d backend
```

### Database Connection Error

**Problem**: "Cannot connect to database" error

**Solution**:
```bash
# 1. Check if database is running
docker-compose ps database

# 2. Test database connection
docker-compose exec database pg_isready

# 3. Check database logs
docker-compose logs database

# 4. Verify credentials in docker-compose.yml
# 5. Restart database (will reset data)
docker-compose restart database
```

### Ports Already in Use

**Problem**: "Error: bind: address already in use"

**Solution**:
```bash
# 1. Find what's using the port
lsof -i :5173      # Frontend
lsof -i :8001      # Backend (host port)
lsof -i :5433      # Database (host port)

# 2. Stop the service
kill -9 <PID>

# 3. Or change port in docker-compose.yml
# Change: "5173:5173" to "5174:5173"

# 4. Restart Docker Compose
docker-compose restart
```

---

## 🛑 Stopping & Cleaning Up

### Stop Services (Keep Data)

```bash
docker-compose down

# Services stop but data persists in volumes
```

### Stop Services (Remove Data)

```bash
docker-compose down -v

# Services stop and all data is deleted
# ⚠️ Use this to completely reset
```

### Remove Images

```bash
docker-compose down -v --rmi all

# Removes containers, volumes, AND images
# Next start will rebuild everything
```

### Clean Build

```bash
# Completely rebuild from scratch
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

---

## 🎓 Learning Resources

### Understand the Architecture

1. **Read**: [[README.md]] - Full technical documentation
2. **Read**: [[USE_CASE.md]] - Architecture and scenarios
3. **Read**: [[PROJECT_SUMMARY.md]] - Project overview

### Explore the Code

**Frontend** (Vue.js 3):
- `frontend/src/App.vue` - Main component
- `frontend/src/utils/topology.js` - Helper functions
- `frontend/src/style.css` - Styling

**Backend** (Python FastAPI):
- `backend/main.py` - API endpoints
- Line 175+ - `discover_network()` function (network scanning)
- Line 200+ - ARP table parsing

**Database** (PostgreSQL):
- `database/init.sql` - Schema definition
- Tables: hosts, scan_results, action_history

### API Exploration

1. Open: http://localhost:8001/docs
2. Try endpoints:
   - GET `/api/topology` - Docker graph (Machine → Container → Image)
   - GET `/api/hosts` - Scan network
   - POST `/api/action` - Send action
   - GET `/api/history` - View history

---

## 📈 Next Steps

### 1. Understand the System
- [ ] Read all documentation files
- [ ] Explore API endpoints in Swagger UI
- [ ] Check database schema with SQL

### 2. Customize the UI
- [ ] Modify colors in `tailwind.config.js`
- [ ] Edit animations in `frontend/src/style.css`
- [ ] Change node layout in `App.vue`

### 3. Extend Functionality
- [ ] Add authentication (JWT)
- [ ] Implement WebSocket for live updates
- [ ] Add more device types
- [ ] Create alert system

### 4. Deploy to Production
- [ ] Set up proper environment
- [ ] Add SSL/TLS certificates
- [ ] Configure firewall rules
- [ ] Set up monitoring/logging

---

## 💡 Pro Tips

### Use Makefile Commands

Instead of long docker-compose commands, use:

```bash
make setup              # Initial setup
make dev               # Start with logs
make logs              # View logs
make health            # Check health
make clean             # Full cleanup
make bash-backend      # Backend shell
make sql               # Database shell
```

### View Real-Time Logs

```bash
# Follow logs from all services
docker-compose logs -f

# Tail last 100 lines
docker-compose logs --tail=100

# Follow only backend
docker-compose logs -f backend | grep -v "^frontend"
```

### Quick Testing

```bash
# Test Docker topology endpoint
curl -s http://localhost:8001/api/topology | jq '.machine, (.containers | length)'

# Test API endpoint
curl -X GET http://localhost:8001/api/hosts

# Test with jq for pretty output
curl -s http://localhost:8001/api/hosts | jq '.'

# Send message
curl -X POST http://localhost:8001/api/action \
  -H "Content-Type: application/json" \
  -d '{"ip":"192.168.1.50","type":"message","text":"Hello"}'
```

---

## 📞 Getting Help

### Check Logs First

99% of issues show up in logs:
```bash
docker-compose logs -f --tail=50
```

### Common Issues & Fixes

| Issue | Command | Reason |
|-------|---------|--------|
| Service won't start | `docker-compose logs SERVICE` | See error message |
| Port in use | `lsof -i :PORT` | Find process using port |
| Stale data | `docker-compose down -v` | Reset everything |
| Build failed | `docker-compose build --no-cache` | Clear cache |

### Documentation Files

- 📖 [[README.md]] - Full documentation
- 🎯 [[USE_CASE.md]] - Architecture details
- 🚀 [[QUICKSTART.md]] - 5-minute setup
- 📊 [[PROJECT_SUMMARY.md]] - Project overview

---

## ✅ Success Checklist

- [ ] Docker and Docker Compose installed
- [ ] Project cloned/copied
- [ ] `docker-compose build` completed
- [ ] `docker-compose up -d` running
- [ ] Frontend accessible at localhost:5173
- [ ] Backend API responding at localhost:8001
- [ ] Database connected and healthy
- [ ] Sample network loads
- [ ] Network scanning works
- [ ] Messages can be sent

---

## 🎉 You're Ready!

Congratulations! Your Live System Topology is now running. 

**Next**: Explore the UI, read the documentation, and start experimenting!

```
🌐 Frontend:  http://localhost:5173
🔌 Backend:   http://localhost:8001/docs
🗄️ Database:  localhost:5433
```

**Happy exploring! 🚀**
