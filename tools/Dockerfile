FROM alpine:3.23
LABEL image.authors="Victor Fernandez III, @cyberphor"
WORKDIR /home/tools/
COPY requirements.txt requirements.txt
COPY squidfall/ squidfall/
RUN apk add --no-cache --update python3 py3-pip &&\
    pip install --break-system-packages -r requirements.txt &&\
    adduser -D squidfall -h /home/tools/ &&\
    chown -R squidfall:squidfall /home/tools/
USER squidfall
EXPOSE 8002
CMD [ "python", "-m", "squidfall.main" ]