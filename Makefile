# Makefile for Sovereign's Edict

# Variables
PYTHON=python3
PIP=pip3
NODE=npm
DOCKER=docker
DOCKER_COMPOSE=docker-compose

# Default target
.PHONY: help
help:
	@echo "Sovereign's Edict - Makefile"
	@echo ""
	@echo "Usage:"
	@echo "  make install-backend     Install backend dependencies"
	@echo "  make install-frontend    Install frontend dependencies"
	@echo "  make run-backend         Run backend server"
	@echo "  make run-frontend        Run Streamlit frontend (default)"
	@echo "  make run-react           Run React frontend"
	@echo "  make run-all             Run both backend and Streamlit frontend (default)"
	@echo "  make run-react-all       Run both backend and React frontend"
	@echo "  make docker-build        Build Docker images"
	@echo "  make docker-run          Run application with Docker"
	@echo "  make test                Run backend tests"
	@echo "  make clean               Clean temporary files"

# Install backend dependencies
.PHONY: install-backend
install-backend:
	$(PIP) install -r requirements.txt

# Install frontend dependencies
.PHONY: install-frontend
install-frontend:
	cd frontend && $(NODE) install

# Run backend server
.PHONY: run-backend
run-backend:
	cd backend && $(PYTHON) main.py

# Run Streamlit frontend (default)
.PHONY: run-frontend
run-frontend:
	$(PYTHON) -m streamlit run streamlit_app.py

# Run React frontend
.PHONY: run-react
run-react:
	cd frontend && $(NODE) start

# Run both backend and Streamlit frontend (default)
.PHONY: run-all
run-all:
	@echo "Starting backend and Streamlit frontend servers..."
	@echo "Backend API: http://localhost:8001"
	@echo "Streamlit UI: http://localhost:8503"
	$(PYTHON) start_streamlit.py

# Run both backend and React frontend
.PHONY: run-react-all
run-react-all:
	@echo "Starting backend and React frontend servers..."
	@echo "Backend: http://localhost:8000"
	@echo "Frontend: http://localhost:3000"
	cd backend && $(PYTHON) main.py & cd frontend && $(NODE) start

# Build Docker images
.PHONY: docker-build
docker-build:
	$(DOCKER) build -t sovereigns-edict-backend .
	cd frontend && $(DOCKER) build -t sovereigns-edict-frontend -f Dockerfile.frontend .

# Run application with Docker
.PHONY: docker-run
docker-run:
	$(DOCKER_COMPOSE) up

# Run backend tests
.PHONY: test
test:
	cd backend && $(PYTHON) -m pytest tests/

# Clean temporary files
.PHONY: clean
clean:
	rm -rf *.pyc
	rm -rf __pycache__
	cd backend && rm -rf *.pyc
	cd backend && rm -rf __pycache__
	cd frontend && rm -rf node_modules/.cache

# Install all dependencies
.PHONY: install-all
install-all: install-backend install-frontend

# Setup development environment
.PHONY: setup
setup: install-all
	@echo "Development environment setup complete!"
