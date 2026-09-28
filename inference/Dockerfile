FROM alpine:3.24
LABEL image.authors="Victor Fernandez III, @cyberphor"
SHELL ["/bin/ash", "-o", "pipefail", "-c"]
WORKDIR /home/inference/
COPY squidfall/ squidfall/
COPY pyproject.toml pyproject.toml
COPY uv.lock uv.lock
ENV UV_PYTHON_INSTALL_DIR=/home/inference/.uv-python
RUN apk add --no-cache python3=3.14.7-r1 uv=0.11.19-r0 && \
    uv sync --frozen --python /usr/bin/python3 && \
    uv run python -m pip uninstall pip -y || true &&\
    addgroup -g 1000 squidfall &&\
    adduser -D -G squidfall -u 1000 squidfall -h /home/inference/ &&\
    chown -R squidfall:squidfall /home/inference/
ENV PATH="/home/inference/.venv/bin:$PATH"
USER 1000
EXPOSE 8001
CMD [ "uv", "run", "uvicorn",  "squidfall.main:api", "--host", "0.0.0.0", "--port", "8001" ]
