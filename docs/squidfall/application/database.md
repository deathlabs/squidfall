# Database

**Step 1.** Create a directory called `database`.
```bash
mkdir database
```

**Step 2.** Change your working directory to the directory you just created.
```bash
cd database
```

**Step 3.** Create a file called `.env` and add the content below to it.
```bash
export PGPASSWORD=postgres
export PGDATABASE=squidfall
```

**Step 4.** Create a file called `Dockerfile` and add the content below it. Feel free to modify the `image.authors` label.
```dockerfile
FROM alpine:3.23
LABEL image.authors="Victor Fernandez III, @cyberphor"
WORKDIR /home/postgres
COPY entrypoint.sh entrypoint.sh
RUN apk add --no-cache postgresql postgresql-contrib libpq-dev &&\
    chmod u+x /home/postgres/entrypoint.sh &&\
    mkdir /var/lib/postgresql/data &&\
    mkdir /run/postgresql &&\
    chown -R postgres:postgres /var/lib/postgresql/data &&\
    chown -R postgres:postgres /run/postgresql
USER postgres
EXPOSE 5432
CMD [ "./entrypoint.sh" ]
```

**Step 5.** Create a file called `entrypoint.sh` and add the content below it. 
```bash
#!/usr/bin/env sh

set -e

# Initialize Postgres.
if [ ! -f "/var/lib/postgresql/data/PG_VERSION" ]; then
  # Create the prerequisite databases.
  initdb -D /var/lib/postgresql/data -A md5 --pwfile=<(echo "$PGPASSWORD")

  # Start Postgres as a background process.
  postgres -D /var/lib/postgresql/data &
  POSTGRES_PID=$!

  # Wait for Postgres to start.
  until pg_isready -h 127.0.0.1 -p 5432 -U postgres; do
    sleep 1
  done

  # Create the app's database.
  createdb -U postgres "$PGDATABASE"

  # Stop Postgres.
  kill "$POSTGRES_PID"
  wait "$POSTGRES_PID" 2>/dev/null || true
fi

# Configure Postgres to listen on all network interfaces.
echo "listen_addresses = '*'" >>/var/lib/postgresql/data/postgresql.conf

# Configure Postgres to authenticate every user of every database from every IP address using MD5.
echo "host  all all 0.0.0.0/0 md5" >>/var/lib/postgresql/data/pg_hba.conf

# Start Postgres in the foreground.
exec postgres -D /var/lib/postgresql/data
```

**Step 6.** From the root of the repository, run the command below to build the container using the Dockerfile you just created.
```bash
make DOCKER_COMPOSE_PROFILE=database
```

**Step 7.** Run the command below to start the container you just created.
```bash
make DOCKER_COMPOSE_PROFILE=database start
```

**Step 8.** Run the command below to confirm the container has started.
```bash
make DOCKER_COMPOSE_PROFILE=database status
```

**Step 9.** If the container has started, run the commands below to interact with it. These commands will load the container's environment variables into memory and then query the container to list (`\l`) the databases under the Postgres server. The purpose of this step is to confirm the container's authentication is correct. 
```bash
source database/.env && psql -h localhost -U postgres -c "\l"
```

**Step 10.** Run the command below to stop the container.
```bash
make DOCKER_COMPOSE_PROFILE=database stop
```
