FROM node:lts-alpine3.24 AS build
ARG LANGGRAPH_DEPLOYMENT_URL
ENV LANGGRAPH_DEPLOYMENT_URL=${LANGGRAPH_DEPLOYMENT_URL}
WORKDIR /home/squidfall
COPY squidfall/ .
RUN npm install && npm run build

FROM golang:alpine AS compile
WORKDIR /home/squidfall
COPY main.go .
COPY --from=build /home/squidfall/out/ ./out/
RUN CGO_ENABLED=0 go build -o /server main.go

FROM scratch
LABEL image.authors="Victor Fernandez III, @cyberphor"
COPY --from=compile /server /server
USER 65532:65532
EXPOSE 8080
ENTRYPOINT ["/server"]
