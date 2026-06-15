# Backend

**Step 1.** Create a directory called `backend`.
```bash
mkdir backend
```

**Step 2.** Change your working directory to the directory you just created.
```bash
cd backend
```

**Step 3.** Create a Python virtual environment called `.venv` in the `backend` directory.
```bash
python -m venv .venv
```

**Step 4.** Activate the Python virtual environment you just created.
```bash
source .venv/bin/activate
```

**Step 5.** Create a file called `requirements.txt` and add the content below to it.
```
django-ninja
psycopg2-binary
tzdata
```

**Step 6.** Install the Python packages defined in the `requirements.txt` file you just created.
```bash
pip install -r requirements.txt
```

**Step 7.** Create a Django project called `squidfall`.
```bash
django-admin startproject squidfall .
```

**Step 8.** In the `squidfall` Django project you just created, open the file called `settings.py` and replace the `from pathlib import Path` line with the content below.
```python
from pathlib import Path
from os import environ, getenv
```

**Step 9.** In the same `settings.py` file, set `DEBUG` to `False`.
```python
DEBUG = False
```

**Step 10.** In the same `settings.py` file, replace the `ALLOWED_HOSTS` with the content below.
```python
ALLOWED_HOSTS = ["localhost", "squidfall-backend"]
```

**Step 11.** In the same `settings.py` file, replace the `INSTALLED_APPS` with the content below.
```python
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "chats"
]
```

**Step 12.** In the same `settings.py` file, replace the `DATABASES` dictionary with the content below. The purpose the `else` block is to allow the container to be scanned in a Continuous Integration pipeline without the dependency of a real database (i.e., it will use a SQLite file if the `DB_ENGINE` environment variable isn't set).
```python
if getenv("DB_ENGINE") == "postgres":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "HOST": environ["PGHOST"],
            "NAME": environ["PGDATABASE"],
            "PORT": environ["PGPORT"],
            "USER": environ["PGUSER"],
            "PASSWORD": environ["PGPASSWORD"],
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
```

**Step 13.** In the `squidfall` Django project, open the file called `urls.py` and replace its contents with the code below. 
```python
# Third party imports
from django.contrib import admin
from django.urls import path

# Local imports.
from chats.api import api as chats_api

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/chats/", chats_api.urls),
]

```

**Step 14.** In the `backend` directory, create a Django application called `chats`.
```bash
django-admin startapp chats
```

**Step 15.** In the `chats` Django application, create a file called `api.py` and add the content below to it.
```python
# Standard library imports.
from typing import List, Optional

# Third party imports.
from ninja import NinjaAPI

# Local imports.
from .models import Chat
from .schema import ChatSchema, NotFoundSchema

# Init the chats API.
api = NinjaAPI()


@api.get("/{thread_id}/", response={200: ChatSchema, 404: NotFoundSchema})
def get_chat(request, thread_id: str, checkpoint_id: Optional[str] = None):
    try:
        chats = Chat.objects.filter(thread_id=thread_id)
        if checkpoint_id:
            chats = chats.filter(checkpoint_id=checkpoint_id)
        return 200, chats.latest("updated_at")
    except Chat.DoesNotExist:
        return 404, {"message": "chat not found"}


@api.get("/", response=List[ChatSchema])
def list_chats(request, thread_id: Optional[str] = None):
    chats = Chat.objects.all()
    if thread_id:
        chats = chats.filter(thread_id=thread_id)
    return chats.order_by("-updated_at")


@api.post("/", response={201: ChatSchema})
def create_chat(request, payload: ChatSchema):
    chat, _ = Chat.objects.update_or_create(
        checkpoint_id=payload.checkpoint_id,
        defaults=payload.dict(exclude={"checkpoint_id"}),
    )
    return 201, chat

```

**Step 16.** In the `chats` Django application, open the file called `models.py` and replace its content with the code below.
```python
# Third party imports.
from django.db import models


class Chat(models.Model):
    thread_id = models.CharField(max_length=255)
    checkpoint_ns = models.CharField(max_length=255, default="")
    checkpoint_id = models.CharField(max_length=255, unique=True)
    parent_checkpoint_id = models.CharField(max_length=255, null=True, blank=True)
    type = models.CharField(max_length=50)
    checkpoint = models.TextField()
    metadata_type = models.CharField(max_length=50)
    metadata = models.TextField()
    updated_at = models.DateTimeField(auto_now=True)

```

**Step 17.** In the `chats` Django application, create a file called `schema.py` and add the content below to it.
```python
# Third party imports.
from typing import Optional
from ninja import Schema


class ChatSchema(Schema):
    thread_id: str
    checkpoint_ns: str = ""
    checkpoint_id: str
    parent_checkpoint_id: Optional[str] = None
    type: str
    checkpoint: str
    metadata_type: str
    metadata: str


class NotFoundSchema(Schema):
    message: str

```

**Step 18.** In the `backend` directory, create a file called `entrypoint.sh` and add the content below to it. 
```bash
#!/usr/bin/env sh

set -e

python manage.py migrate

uvicorn squidfall.asgi:application --host 0.0.0.0 --port 8000

```

**Step 19.** In the `backend` directory, create a file called `.env` and add the content below to it.
```bash
export DB_ENGINE=postgres
export PGHOST=squidfall-database
export PGDATABASE=squidfall
export PGPORT=5432
export PGSSLMODE=disable 
export PGUSER=postgres
export PGPASSWORD=postgres
```

**Step 20.** Load the environment variables you just defined. Also, make sure to overide the value set in the `.env`. This is important to run the next few commands. But for the other containers, we will need to use the original value. So use `export PGHOST=localhost` for now, but understand when all the other containers are built, you will need to use `export PGHOST=squidfall-database`. 
```bash
source .env
export PGHOST=localhost
```

**Step 21.** From the root of the repository, run the command below to start the database container.
```bash
make DOCKER_COMPOSE_PROFILE=database start
```

**Step 22.** From the `backend` directory, run the command below to create the migration files Django will use to provision your app's database tables when your `backend` container starts. If you ever modify the models that represent the objects in your app, you'll need to manually re-run this command (separately from the `backend` container). Make sure the migration files are "checked-in" with the rest of your codebase and not "gitignored." Also, if you're doing local development, you may need to delete the volume associated with your `database` container between changes.
```bash
python manage.py makemigrations
```

**Step 23.** In the `backend` directory, create a file called `Dockerfile` and add the content below it. Feel free to modify the `image.authors` label.
```dockerfile
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
```

**Step 24.** From the root of the repository, run the command below to build the container using the Dockerfile you just created.
```bash
make DOCKER_COMPOSE_PROFILE=backend
```

**Step 25.** Run the command below to start the container you just created.
```bash
make DOCKER_COMPOSE_PROFILE=backend start
```

**Step 26.** Run the command below to confirm the container has started.
```bash
make DOCKER_COMPOSE_PROFILE=backend status
```

**Step 27.** If the container has started, run the command below to interact with it. 
```bash
curl -X POST http://localhost:8000/api/v1/chats/ \
    -H "Content-Type: application/json" \
    -d '{
        "thread_id": "test-thread-1",
        "checkpoint_ns": "",
        "checkpoint_id": "test-checkpoint-1",
        "parent_checkpoint_id": null,
        "type": "msgpack",
        "checkpoint": "deadbeef",
        "metadata_type": "msgpack",
        "metadata": "deadbeef"
    }'
```

You should get output similar to below. 
```json
{"thread_id": "test-thread-1", "checkpoint_ns": "", "checkpoint_id": "test-checkpoint-1", "parent_checkpoint_id": null, "type": "msgpack", "checkpoint": "deadbeef", "metadata_type": "msgpack", "metadata": "deadbeef"}
```

**Step 28.** Run the command below to stop the container.
```bash
make DOCKER_COMPOSE_PROFILE=backend stop
```

**Step 29.** Deactivate your Python virtual environment.
```bash
deactivate
```