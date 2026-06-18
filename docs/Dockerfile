FROM alpine:3.23
LABEL image.authors="Victor Fernandez III <@cyberphor>"
WORKDIR /home/docs/
COPY mkdocs.yml mkdocs.yml
COPY squidfall/ squidfall/
RUN apk add --no-cache --update mkdocs python3 py3-pip &&\
    adduser -D squidfall -h /home/docs &&\
    chown -R squidfall:squidfall /home/docs
USER squidfall
EXPOSE 5050
CMD [ "mkdocs", "serve", "--dev-addr=0.0.0.0:5050" ]
