FROM alpine:3.23
LABEL image.authors="Victor Fernandez III, @cyberphor"
WORKDIR /home/inference/
COPY squidfall/ squidfall/
COPY requirements.txt requirements.txt
RUN apk add --no-cache --update python3 py3-pip uvicorn &&\
    pip install --break-system-packages -r requirements.txt &&\
    adduser -D squidfall -h /home/inference/ &&\
    chown -R squidfall:squidfall /home/inference/
USER squidfall
EXPOSE 8001
CMD [ "uvicorn",  "squidfall.main:api", "--host", "0.0.0.0", "--port", "8001" ]