# Setup

**Step 1.** Create a `.gitignore`.
```bash
vim .gitignore
```

Text goes here.
```
.env
.venv
```

**Step 2.** Text goes here.
```bash
vim Makefile
```

Text goes here.
```makefile
# ---------------------------------------------------------
# Misc.
# ---------------------------------------------------------
 
# Set the default goal.
.DEFAULT_GOAL := build
 
# Tell Docker to build images in parallel.
COMPOSE_BAKE := true
 
# Set the Docker Compose profile to "all" if an argument is not provided.
DOCKER_COMPOSE_PROFILE ?= all
 
# ---------------------------------------------------------
# Build the containers.
# ---------------------------------------------------------
 
.PHONY: build
.SILENT: build
 
build:
	docker compose --profile $(DOCKER_COMPOSE_PROFILE) build
 
# ---------------------------------------------------------
# Start the containers.
# ---------------------------------------------------------
 
.PHONY: start
.SILENT: start
 
start:
	docker compose --profile $(DOCKER_COMPOSE_PROFILE) up -d
 
# ---------------------------------------------------------
# Stop the containers.
# ---------------------------------------------------------
 
.PHONY: stop
.SILENT: stop
 
stop:
	docker compose --profile $(DOCKER_COMPOSE_PROFILE) down

# ---------------------------------------------------------
# Check the status of the containers.
# ---------------------------------------------------------
.PHONY: status
.SILENT: status

status:
	docker compose --profile $(DOCKER_COMPOSE_PROFILE) ps --format "table {{.Name}}\t{{.Ports}}\t{{.Status}}"
```

**Step 3.** Text goes here.
```bash
vim compose.yml
```

Text goes here.
```yaml
services:

  backend:
    profiles: [ all, backend ]
    build: backend
    image: squidfall/backend:latest
    container_name: squidfall-backend
    env_file:
      - backend/.env

  database:
    profiles: [ all, database ]
    build: database
    image: squidfall/database:latest
    container_name: squidfall-database
    env_file:
      - database/.env

  frontend:
    profiles: [ all, frontend ]
    build: frontend
    image: squidfall/frontend:latest
    container_name: squidfall-frontend
    env_file:
      - frontend/.env

  inference:
    profiles: [ all, inference ]
    build: inference
    image: squidfall/inference:latest
    container_name: squidfall-inference
    env_file:
      - inference/.env

  tools:
     profiles: [ all, tools ]
     build: tools
     image: squidfall/tools:latest
     container_name: squidfall-tools
     env_file:
       - tools/.env
```
