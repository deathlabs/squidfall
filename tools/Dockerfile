FROM alpine:3.24
LABEL image.authors="Victor Fernandez III, @cyberphor"
SHELL ["/bin/ash", "-o", "pipefail", "-c"]
WORKDIR /home/tools/
COPY squidfall/ squidfall/
COPY pyproject.toml pyproject.toml
COPY uv.lock uv.lock
ENV UV_PYTHON_INSTALL_DIR=/home/tools/.uv-python
RUN apk add --no-cache python3=3.14.7-r1 uv=0.11.19-r0 && \
    uv sync --frozen --python /usr/bin/python3 && \
    uv run python -m pip uninstall pip -y || true &&\
    addgroup -g 1000 squidfall &&\
    adduser -D -G squidfall -u 1000 squidfall -h /home/tools/ &&\
    chown -R squidfall:squidfall /home/tools/
ENV PATH="/home/tools/.venv/bin:$PATH"
USER 1000
EXPOSE 8002
CMD [ "uv", "run", "python", "-m", "squidfall.main" ]
