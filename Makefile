COMPOSE_FILE = docker-compose.yml

# Caminho corrigido para o código e dependências dentro da pasta 'app/'

PYTHON_FILES = app/products.py app/users.py tests/test_products.py tests/test_users.py
REQUIREMENTS_PATH = app/requirements.txt

.PHONY: all build up start stop down clean lint test_dev

all: build up
	@echo "Project built and containers started successfully."

#--- Development & Setup Commands ---

build:
	@echo "Building microservice images..."
	docker compose -f $(COMPOSE_FILE) build
	@echo "Images built: users and products."

up:
	@echo "Starting containers in detached mode..."
	docker compose -f $(COMPOSE_FILE) up -d
	@echo "Services are running. Access Products at http://localhost:5000 and Users at http://localhost:5001"

start: up

stop:
	@echo "Stopping containers..."
	docker compose -f $(COMPOSE_FILE) stop

down:
	@echo "Stopping and removing containers, networks, and volumes..."
	docker compose -f $(COMPOSE_FILE) down -v

clean: down
	@echo "Removing dangling Docker images and containers..."

# Substitua pelos nomes reais das suas imagens, se diferentes

docker rmi projecto_final_users:latest || true

docker rmi projecto_final_products:latest || true
	docker system prune -f
	@echo "Cleanup complete."

#-- Quality Assurance Commands ---

lint:
	@echo "Running Flake8 Linter for code quality..."
# CORREÇÃO: Instalação a partir do novo caminho
	pip install -r $(REQUIREMENTS_PATH) || true
# Linting em todos os ficheiros
	flake8 $(PYTHON_FILES) --max-line-length=120
	@echo "Linting complete."

test_dev: lint
	@echo "Running Development Stage tests (Unit, Integration, Sanity)..."
# CORREÇÃO: Instalação a partir do novo caminho
	pip install -r $(REQUIREMENTS_PATH) || true
	pytest -m "dev"
	@echo "Development tests complete."

#--- Usage Help ---

help:
	@echo ""
	@echo "--------------------------------------------------------"
	@echo "  Microservices Project Management (Makefile) "
	@echo "--------------------------------------------------------"
	@echo "  make build         : Builds Docker images for both services."	
	@echo "  make up (or start) : Builds (if necessary) and runs containers in the background."
	@echo "  make stop          : Stops running containers gracefully."
	@echo "  make down          : Stops and removes containers, networks, and volumes."
	@echo "  make clean         : Executes 'down' and removes dangling images."
	@echo "  make lint          : Runs the Flake8 linter locally."
	@echo "  make test_dev      : Runs local Pytest suite marked for 'dev'."
	@echo "--------------------------------------------------------"