# ---------------------------------------------------------
# Default settings.
# ---------------------------------------------------------

# Use Bash as the default shell.
SHELL := /bin/bash

# Set the default Make target.
.DEFAULT_GOAL := test-containers

# Tell Docker Compose to use Bake for builds.
export COMPOSE_BAKE := true

# Set the default Docker Compose profile.
DOCKER_COMPOSE_PROFILE ?= all

# Set app metadata.
APP := squidfall

# Set container metadata.
DATABASE_BUILD_CONTEXT := database
DATABASE_DOCKERFILE_PATH := $(DATABASE_BUILD_CONTEXT)/Dockerfile
DATABASE_CONTAINER_IMAGE := $(APP)/$(DATABASE_BUILD_CONTEXT):latest
DATABASE_CONTAINER := $(APP)_$(DATABASE_BUILD_CONTEXT)
DATABASE_SBOM_PATH := $(APP)-$(DATABASE_BUILD_CONTEXT)-sbom.json
DATABASE_VEX_YAML_PATH := $(DATABASE_BUILD_CONTEXT)/vex.yaml
DATABASE_VEX_JSON_PATH := $(DATABASE_BUILD_CONTEXT)/vex.json

BACKEND_BUILD_CONTEXT := backend
BACKEND_DOCKERFILE_PATH := $(BACKEND_BUILD_CONTEXT)/Dockerfile
BACKEND_CONTAINER_IMAGE := $(APP)/$(BACKEND_BUILD_CONTEXT):latest
BACKEND_CONTAINER := $(APP)_$(BACKEND_BUILD_CONTEXT)
BACKEND_SBOM_PATH := $(APP)-$(BACKEND_BUILD_CONTEXT)-sbom.json
BACKEND_VEX_YAML_PATH := $(BACKEND_BUILD_CONTEXT)/vex.yaml
BACKEND_VEX_JSON_PATH := $(BACKEND_BUILD_CONTEXT)/vex.json

TOOLS_BUILD_CONTEXT := tools
TOOLS_DOCKERFILE_PATH := $(TOOLS_BUILD_CONTEXT)/Dockerfile
TOOLS_CONTAINER_IMAGE := $(APP)/$(TOOLS_BUILD_CONTEXT):latest
TOOLS_CONTAINER := $(APP)_$(TOOLS_BUILD_CONTEXT)
TOOLS_SBOM_PATH := $(APP)-$(TOOLS_BUILD_CONTEXT)-sbom.json
TOOLS_VEX_YAML_PATH := $(TOOLS_BUILD_CONTEXT)/vex.yaml
TOOLS_VEX_JSON_PATH := $(TOOLS_BUILD_CONTEXT)/vex.json

INFERENCE_BUILD_CONTEXT := inference
INFERENCE_DOCKERFILE_PATH := $(INFERENCE_BUILD_CONTEXT)/Dockerfile
INFERENCE_CONTAINER_IMAGE := $(APP)/$(INFERENCE_BUILD_CONTEXT):latest
INFERENCE_CONTAINER := $(APP)_$(INFERENCE_BUILD_CONTEXT)
INFERENCE_SBOM_PATH := $(APP)-$(INFERENCE_BUILD_CONTEXT)-sbom.json
INFERENCE_VEX_YAML_PATH := $(INFERENCE_BUILD_CONTEXT)/vex.yaml
INFERENCE_VEX_JSON_PATH := $(INFERENCE_BUILD_CONTEXT)/vex.json

FRONTEND_BUILD_CONTEXT := frontend
FRONTEND_DOCKERFILE_PATH := $(FRONTEND_BUILD_CONTEXT)/Dockerfile
FRONTEND_CONTAINER_IMAGE := $(APP)/$(FRONTEND_BUILD_CONTEXT):latest
FRONTEND_CONTAINER := $(APP)_$(FRONTEND_BUILD_CONTEXT)
FRONTEND_SBOM_PATH := $(APP)-$(FRONTEND_BUILD_CONTEXT)-sbom.json
FRONTEND_VEX_YAML_PATH := $(FRONTEND_BUILD_CONTEXT)/vex.yaml
FRONTEND_VEX_JSON_PATH := $(FRONTEND_BUILD_CONTEXT)/vex.json

# Set VEX metadata.
VEX_AUTHOR ?= Victor Fernandez III
VEX_ID_BASE ?= $(APP)

# Set scanner configuration and thresholds.
SEMGREP_CONFIG ?= auto
HADOLINT_FAILURE_THRESHOLD ?= warning
GRYPE_FAILURE_THRESHOLD ?= medium

# ---------------------------------------------------------
# Update uv.lock.
# ---------------------------------------------------------

.PHONY: lock
.SILENT: lock
lock:
	echo "[*] Locking $(APP)'s backend Python dependencies"
	cd $(BACKEND_BUILD_CONTEXT) && uv lock
	echo "[*] Locking $(APP)'s inference Python dependencies"
	cd $(INFERENCE_BUILD_CONTEXT) && uv lock
	echo "[*] Locking $(APP)'s tools Python dependencies"
	cd $(TOOLS_BUILD_CONTEXT) && uv lock

# ---------------------------------------------------------
# Check the source code for quality.
# ---------------------------------------------------------

.PHONY: check
.SILENT: check
check:
	echo "[*] Checking $(APP)'s source code quality"
	ruff check --fix $(BACKEND_BUILD_CONTEXT)
	ruff check --fix $(INFERENCE_BUILD_CONTEXT)
	ruff check --fix $(TOOLS_BUILD_CONTEXT)

# ---------------------------------------------------------
# Format the source code.
# ---------------------------------------------------------

.PHONY: format
.SILENT: format
format:
	echo "[*] Formatting $(APP)'s source code"
	ruff format $(BACKEND_BUILD_CONTEXT)
	ruff format $(INFERENCE_BUILD_CONTEXT)
	ruff format $(TOOLS_BUILD_CONTEXT)

# ---------------------------------------------------------
# Check the repository for secrets.
# ---------------------------------------------------------

.PHONY: secrets
.SILENT: secrets
secrets:
	echo "[*] Checking $(APP)'s source code for hardcoded secrets"
	trufflehog filesystem \
		--no-update \
		--fail \
		--fail-on-scan-errors \
		--results=verified,unknown \
		--log-level=-1 \
		--exclude-paths trufflehog-exclusions.txt .

# ---------------------------------------------------------
# Check the Dockerfiles for quality.
# ---------------------------------------------------------

.PHONY: dockerfile-lint
.SILENT: dockerfile-lint
dockerfile-lint:
	echo "[*] Checking $(APP)'s Dockerfiles for lint"
	hadolint --failure-threshold "$(HADOLINT_FAILURE_THRESHOLD)" \
		"$(DATABASE_DOCKERFILE_PATH)" \
		"$(BACKEND_DOCKERFILE_PATH)" \
		"$(TOOLS_DOCKERFILE_PATH)" \
		"$(INFERENCE_DOCKERFILE_PATH)" \
		"$(FRONTEND_DOCKERFILE_PATH)"

# ---------------------------------------------------------
# Check for first-party vulnerabilities.
# ---------------------------------------------------------

.PHONY: sast
.SILENT: sast
sast:
	echo "[*] Checking $(APP)'s source code for first-party vulnerabilities"
	semgrep scan --config "$(SEMGREP_CONFIG)" \
		--include $(DATABASE_BUILD_CONTEXT) \
		--include $(BACKEND_BUILD_CONTEXT) \
		--include $(TOOLS_BUILD_CONTEXT) \
		--include $(INFERENCE_BUILD_CONTEXT) \
		--include $(FRONTEND_BUILD_CONTEXT)

# ---------------------------------------------------------
# Build the container images.
# ---------------------------------------------------------

.PHONY: build-container
.SILENT: build-container
build-containers: lock check format secrets dockerfile-lint sast
	echo "[*] Building $(APP)'s container image"
	docker compose --profile $(DOCKER_COMPOSE_PROFILE) build 

# ---------------------------------------------------------
# Generate a VEX file for the container images.
# ---------------------------------------------------------

define VEX_FILTER
{
  "@context": "https://openvex.dev/ns/v0.2.0",
  "@id": strenv(VEX_ID),
  "author": strenv(VEX_AUTHOR),
  "timestamp": strenv(VEX_TIMESTAMP),
  "version": 1,
  "statements": [
    .advisories[] | {
      "vulnerability": {
        "name": .vulnerability
      },
      "products": [
        .products[] | {
          "@id": .
        }
      ],
      "status": .status,
      "justification": .justification,
      "impact_statement": .impact_statement
    }
  ]
}
endef

export VEX_FILTER

.PHONY: vex
.SILENT: vex
vex:
	echo "[*] Generating VEX statements for $(APP)'s database"
	VEX_ID="$(VEX_ID_BASE)" \
	VEX_AUTHOR="$(VEX_AUTHOR)" \
	VEX_TIMESTAMP="$$(date -u +'%Y-%m-%dT%H:%M:%SZ')" \
	yq -o=json "$$VEX_FILTER" "$(DATABASE_VEX_YAML_PATH)" > "$(DATABASE_VEX_JSON_PATH)"
	echo "[*] Generating VEX statements for $(APP)'s backend"
	VEX_ID="$(VEX_ID_BASE)" \
	VEX_AUTHOR="$(VEX_AUTHOR)" \
	VEX_TIMESTAMP="$$(date -u +'%Y-%m-%dT%H:%M:%SZ')" \
	yq -o=json "$$VEX_FILTER" "$(BACKEND_VEX_YAML_PATH)" > "$(BACKEND_VEX_JSON_PATH)"
	echo "[*] Generating VEX statements for $(APP)'s tools"
	VEX_ID="$(VEX_ID_BASE)" \
	VEX_AUTHOR="$(VEX_AUTHOR)" \
	VEX_TIMESTAMP="$$(date -u +'%Y-%m-%dT%H:%M:%SZ')" \
	yq -o=json "$$VEX_FILTER" "$(TOOLS_VEX_YAML_PATH)" > "$(TOOLS_VEX_JSON_PATH)"
	echo "[*] Generating VEX statements for $(APP)'s inference"
	VEX_ID="$(VEX_ID_BASE)" \
	VEX_AUTHOR="$(VEX_AUTHOR)" \
	VEX_TIMESTAMP="$$(date -u +'%Y-%m-%dT%H:%M:%SZ')" \
	yq -o=json "$$VEX_FILTER" "$(INFERENCE_VEX_YAML_PATH)" > "$(INFERENCE_VEX_JSON_PATH)"
	echo "[*] Generating VEX statements for $(APP)'s frontend"
	VEX_ID="$(VEX_ID_BASE)" \
	VEX_AUTHOR="$(VEX_AUTHOR)" \
	VEX_TIMESTAMP="$$(date -u +'%Y-%m-%dT%H:%M:%SZ')" \
	yq -o=json "$$VEX_FILTER" "$(FRONTEND_VEX_YAML_PATH)" > "$(FRONTEND_VEX_JSON_PATH)"

# ---------------------------------------------------------
# Generate an SBOM for the container images.
# ---------------------------------------------------------

.PHONY: sbom
.SILENT: sbom
sbom: build-containers
	echo "[*] Generating $(APP)'s database SBOM"
	syft $(DATABASE_CONTAINER_IMAGE) -o cyclonedx-json="$(DATABASE_SBOM_PATH)"
	echo "[*] Generating $(APP)'s backend SBOM"
	syft $(BACKEND_CONTAINER_IMAGE) -o cyclonedx-json="$(BACKEND_SBOM_PATH)"
	echo "[*] Generating $(APP)'s tools SBOM"
	syft $(TOOLS_CONTAINER_IMAGE) -o cyclonedx-json="$(TOOLS_SBOM_PATH)"
	echo "[*] Generating $(APP)'s inference SBOM"
	syft $(INFERENCE_CONTAINER_IMAGE) -o cyclonedx-json="$(INFERENCE_SBOM_PATH)"
	echo "[*] Generating $(APP)'s frontend SBOM"
	syft $(FRONTEND_CONTAINER_IMAGE) -o cyclonedx-json="$(FRONTEND_SBOM_PATH)"

# ---------------------------------------------------------
# Check for third-party vulnerabilities.
# ---------------------------------------------------------

.PHONY: dependency-scan
.SILENT: dependency-scan
dependency-scan: sbom vex
	echo "[*] Updating the Grype vulnerability database"
	grype db update
	echo "[*] Checking $(APP)'s database SBOM for third-party vulnerabilities"
	grype sbom:"$(DATABASE_SBOM_PATH)" --vex "$(DATABASE_VEX_JSON_PATH)" --fail-on "$(GRYPE_FAILURE_THRESHOLD)"
	echo "[*] Checking $(APP)'s backend SBOM for third-party vulnerabilities"
	grype sbom:"$(BACKEND_SBOM_PATH)" --vex "$(BACKEND_VEX_JSON_PATH)" --fail-on "$(GRYPE_FAILURE_THRESHOLD)"
	echo "[*] Checking $(APP)'s tools SBOM for third-party vulnerabilities"
	grype sbom:"$(TOOLS_SBOM_PATH)" --vex "$(TOOLS_VEX_JSON_PATH)" --fail-on "$(GRYPE_FAILURE_THRESHOLD)"
	echo "[*] Checking $(APP)'s inference SBOM for third-party vulnerabilities"
	grype sbom:"$(INFERENCE_SBOM_PATH)" --vex "$(INFERENCE_VEX_JSON_PATH)" --fail-on "$(GRYPE_FAILURE_THRESHOLD)"
	echo "[*] Checking $(APP)'s frontend SBOM for third-party vulnerabilities"
	grype sbom:"$(FRONTEND_SBOM_PATH)" --vex "$(FRONTEND_VEX_JSON_PATH)" --fail-on "$(GRYPE_FAILURE_THRESHOLD)"

# ---------------------------------------------------------
# Start the containers.
# ---------------------------------------------------------

.PHONY: start-containers
.SILENT: start-containers
start-containers: dependency-scan
	docker compose --profile $(DOCKER_COMPOSE_PROFILE) up -d

# ---------------------------------------------------------
# Check the status of the containers.
# ---------------------------------------------------------

.PHONY: status
.SILENT: status
status:
	docker compose --profile $(DOCKER_COMPOSE_PROFILE) ps --format "table {{.Name}}\t{{.Ports}}\t{{.Status}}"

# ---------------------------------------------------------
# Test the containers.
# ---------------------------------------------------------

.PHONY: test-containers
.SILENT: test-containers
test-containers: start-containers
	echo "[*] Testing $(APP)"
#	cd tests && uv run python main.py

# ---------------------------------------------------------
# Stop the containers.
# ---------------------------------------------------------

.PHONY: stop-containers
.SILENT: stop-containers
stop-containers:
	docker compose --profile $(DOCKER_COMPOSE_PROFILE) down

# ---------------------------------------------------------
# Remove the container images.
# ---------------------------------------------------------

.PHONY: remove-container-images
.SILENT: remove-container-images
remove-container-images:
	docker compose --profile $(DOCKER_COMPOSE_PROFILE) down --rmi all
