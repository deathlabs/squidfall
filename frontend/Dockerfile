FROM node:lts-alpine3.24 AS stage_1
WORKDIR /home/squidfall
COPY squidfall/package*.json ./
RUN npm ci
COPY squidfall/ .
RUN npm run build

FROM node:lts-alpine3.24
LABEL image.authors="Victor Fernandez III, @cyberphor"
WORKDIR /home/squidfall
ENV NODE_ENV=production
ENV PORT=8080
ENV HOSTNAME=0.0.0.0
ENV LANGGRAPH_DEPLOYMENT_URL=http://squidfall-inference:8001/api/v1
COPY --from=stage_1 /home/squidfall/.next/standalone ./
COPY --from=stage_1 /home/squidfall/.next/static ./.next/static
COPY --from=stage_1 /home/squidfall/public ./public
RUN rm -rf \
        /home/squidfall/node_modules/next/dist/compiled/tar \
        /usr/local/lib/node_modules/npm/node_modules/brace-expansion \
        /usr/local/lib/node_modules/npm/node_modules/ip-address \
        /usr/local/lib/node_modules/npm/node_modules/tar \
        /usr/local/lib/node_modules/npm/node_modules/undici 
USER 65532:65532
EXPOSE 8080
CMD ["node", "server.js"]
