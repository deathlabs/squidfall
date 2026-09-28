FROM alpine:3.24
LABEL image.authors="Victor Fernandez III, @cyberphor"
WORKDIR /home/database/
COPY entrypoint.sh entrypoint.sh
RUN apk add --no-cache postgresql18=18.6-r0 postgresql18-contrib=18.6-r0 libpq-dev=18.6-r0 &&\
    chmod u+x /home/database/entrypoint.sh &&\
    mkdir /var/lib/postgresql/data &&\
    mkdir /run/postgresql &&\
    chown -R postgres:postgres /var/lib/postgresql/data &&\
    chown -R postgres:postgres /run/postgresql
USER 70
EXPOSE 5432
CMD [ "./entrypoint.sh" ]
