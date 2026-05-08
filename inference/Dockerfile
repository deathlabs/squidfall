FROM alpine:3.23
LABEL image.authors="Victor Fernandez III <@cyberphor>"
WORKDIR /home/inference/
COPY requirements.txt requirements.txt
COPY squidfall/ squidfall/
RUN apk add --no-cache --update python3 py3-pip &&\
    pip install --break-system-packages -r requirements.txt &&\
    adduser -D squidfall -h /home/inference &&\
    chown -R squidfall:squidfall /home/inference
USER squidfall
CMD [ "python", "-m", "squidfall.main" ]
