.PHONY: help build up down logs clean restart dev prod test lint

# Default target
help:
	@echo "Live System Topology - Docker Compose Commands"
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@echo "  build              Build Docker images"
	@echo "  up                 Start all services (background)"
	@echo "  down               Stop all services"
	@echo "  dev                Start services with logs (foreground)"
	@echo "  logs               Show logs from all services"
	@echo "  logs-backend       Show backend logs"
	@echo "  logs-frontend      Show frontend logs"
	@echo "  logs-db            Show database logs"
	@echo "  restart            Restart all services"
	@echo "  clean              Stop and remove containers/volumes"
	@echo "  ps                 Show running containers"
	@echo "  bash-backend       Open bash in backend container"
	@echo "  bash-frontend      Open bash in frontend container"
	@echo "  sql                Open psql in database container"
	@echo "  health             Check health of services"

# Build images
build:
	docker-compose build

# Start services (background)
up:
	docker-compose up -d

# Development mode (foreground with logs)
dev:
	docker-compose up

# Stop services
down:
	docker-compose down

# View logs
logs:
	docker-compose logs -f

logs-backend:
	docker-compose logs -f backend

logs-frontend:
	docker-compose logs -f frontend

logs-db:
	docker-compose logs -f database

# Restart services
restart:
	docker-compose restart

# Stop and remove everything
clean:
	docker-compose down -v
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name node_modules -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .venv -exec rm -rf {} + 2>/dev/null || true

# Show running containers
ps:
	docker-compose ps

# Execute bash in containers
bash-backend:
	docker-compose exec backend bash

bash-frontend:
	docker-compose exec frontend bash

# Connect to database
sql:
	docker-compose exec database psql -U topology_user -d topology_db

# Check service health
health:
	@echo "Checking service health..."
	@echo ""
	@echo "Frontend (5173):"
	@curl -s http://localhost:5173/ > /dev/null && echo "  ✓ Running" || echo "  ✗ Not responding"
	@echo ""
	@echo "Backend (8000):"
	@curl -s http://localhost:8000/ | grep -q "status" && echo "  ✓ Running" || echo "  ✗ Not responding"
	@echo ""
	@echo "Database (5432):"
	@docker-compose exec database pg_isready -U topology_user && echo "  ✓ Running" || echo "  ✗ Not responding"

# Development environment setup
setup: build up
	@echo "✓ Docker Compose setup complete"
	@echo ""
	@echo "Services:"
	@echo "  Frontend:  http://localhost:5173"
	@echo "  Backend:   http://localhost:8000"
	@echo "  API Docs:  http://localhost:8000/docs"
	@echo "  Database:  localhost:5432"
	@echo ""
	@echo "Use 'make logs' to view logs"
	@echo "Use 'make health' to check service health"

# Production build
prod: clean build
	docker-compose -f docker-compose.yml up -d
	@echo "✓ Production deployment complete"
