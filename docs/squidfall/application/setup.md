# Setup

**Step 1.** Create a file called `Makefile` and add the content below to it.
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

**Step 2.** Create a file called `compose.yml` and add the content below to it.
```yaml
services:

  database:
    profiles: [ all, backend, database ]
    build: database
    image: squidfall/database:latest
    container_name: squidfall-database
    ports:
      - "5432:5432"
    volumes:
      - squidfall_database:/var/lib/postgresql/data
    env_file:
      - database/.env

  backend:
    profiles: [ all, backend ]
    build: backend
    image: squidfall/backend:latest
    container_name: squidfall-backend
    ports:
      - "8000:8000"
    env_file:
      - backend/.env

  tools:
    profiles: [ all, inference, tools ]
    build: tools
    image: squidfall/tools:latest
    container_name: squidfall-tools
    ports:
      - "8002:8002"
    env_file:
      - tools/.env

  inference:
    profiles: [ all, inference ]
    build: inference
    image: squidfall/inference:latest
    container_name: squidfall-inference
    ports:
      - "8001:8001"
    env_file:
      - inference/.env

  frontend:
    profiles: [ all, frontend ]
    build:
      context: frontend
      args:
        LANGGRAPH_DEPLOYMENT_URL: "http://squidfall-inference:8001"
    image: squidfall/frontend:latest
    container_name: squidfall-frontend
    ports:
      - "80:3000"
    env_file:
      - frontend/.env

volumes:
  squidfall_database:
```
