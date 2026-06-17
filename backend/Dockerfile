FROM alpine:3.23
LABEL image.authors="Victor Fernandez III, @cyberphor"
WORKDIR /home/backend/
COPY chats/ chats/
COPY entrypoint.sh entrypoint.sh
COPY squidfall/ squidfall/
COPY requirements.txt requirements.txt
COPY manage.py manage.py
RUN apk add --no-cache --update python3 py3-pip uvicorn &&\
    pip install --break-system-packages -r requirements.txt &&\
    adduser -D squidfall -h /home/backend/ &&\
    chmod u+x /home/backend/entrypoint.sh &&\
    chown -R squidfall:squidfall /home/backend/
USER squidfall
EXPOSE 8000
CMD [ "./entrypoint.sh" ]