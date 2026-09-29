FROM alpine:3.24
LABEL image.authors="Victor Fernandez III, @cyberphor"
SHELL ["/bin/ash", "-o", "pipefail", "-c"]
WORKDIR /home/backend/
COPY entrypoint.sh entrypoint.sh
COPY checkpoints/ checkpoints/
COPY memories/ memories/
COPY squidfall/ squidfall/
COPY pyproject.toml pyproject.toml
COPY uv.lock uv.lock
COPY manage.py manage.py
ENV UV_PYTHON_INSTALL_DIR=/home/backend/.uv-python
RUN apk add --no-cache python3=3.14.7-r1 uv=0.11.19-r0 && \
    apk upgrade --no-cache libcrypto3 libssl3 zlib &&\
    uv sync --frozen --python /usr/bin/python3 && \
    uv run python -m pip uninstall pip -y || true &&\
    addgroup -g 1000 squidfall &&\
    adduser -D -G squidfall -u 1000 squidfall -h /home/backend/ &&\
    chmod u+x /home/backend/entrypoint.sh &&\
    chown -R squidfall:squidfall /home/backend/
ENV PATH="/home/backend/.venv/bin:$PATH"
USER 1000
EXPOSE 8000
CMD [ "./entrypoint.sh" ]
