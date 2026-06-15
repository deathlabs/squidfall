# Inference

**Step 1.** Create a directory called `inference`.
```bash
mkdir inference
```

**Step 2.** Change your working directory to the directory you just created.
```bash
cd inference
```

**Step 3.** Create a file called `requirements.txt` and add the content below to it.
```
ag-ui-langgraph
azure-identity
copilotkit
fastapi
langchain
langchain-openai
langchain-mcp-adapters
langgraph
pydantic
uvicorn
```

**Step 4.** Create a directory called `squidfall` within the `inference` directory.
```bash
mkdir squidfall
```

**Step 5.** In the `squidfall` directory you just created, create a file called `__init__.py`.

**Step 6.** In the `squidfall` directory, create a file called `checkpoint_saver.py` .
```python
# Standard library imports.
from os import environ
from typing import Any, AsyncIterator, Optional, Sequence, Tuple

# Third party imports.
from httpx import AsyncClient
from langgraph.checkpoint.base import (
    BaseCheckpointSaver,
    Checkpoint,
    CheckpointMetadata,
    CheckpointTuple,
    get_checkpoint_id,
)

BACKEND_ENDPOINT = environ["BACKEND_ENDPOINT"]


class DjangoCheckpointSaver(BaseCheckpointSaver):

    async def aget_tuple(self, config: dict) -> Optional[CheckpointTuple]:
        thread_id = config["configurable"]["thread_id"]
        checkpoint_id = get_checkpoint_id(config)

        async with AsyncClient() as client:
            resp = await client.get(
                f"{BACKEND_ENDPOINT}/api/v1/chats/{thread_id}/",
                params={"checkpoint_id": checkpoint_id} if checkpoint_id else {},
            )

        if resp.status_code == 404:
            return None

        return self._row_to_tuple(config, resp.json())

    async def alist(self, config: dict, **kwargs) -> AsyncIterator[CheckpointTuple]:
        thread_id = config["configurable"]["thread_id"]

        async with AsyncClient() as client:
            resp = await client.get(
                f"{BACKEND_ENDPOINT}/api/v1/chats/", params={"thread_id": thread_id}
            )

        for row in resp.json():
            yield self._row_to_tuple(config, row)

    async def aput(
        self,
        config: dict,
        checkpoint: Checkpoint,
        metadata: CheckpointMetadata,
        new_versions: dict,
    ) -> dict:
        thread_id = config["configurable"]["thread_id"]
        checkpoint_ns = config["configurable"].get("checkpoint_ns", "")
        checkpoint_id = checkpoint["id"]
        parent_checkpoint_id = get_checkpoint_id(config)

        ctype, serialized = self.serde.dumps_typed(checkpoint)
        mtype, meta_serialized = self.serde.dumps_typed(metadata)

        async with AsyncClient() as client:
            await client.post(
                f"{BACKEND_ENDPOINT}/api/v1/chats/",
                json={
                    "thread_id": thread_id,
                    "checkpoint_ns": checkpoint_ns,
                    "checkpoint_id": checkpoint_id,
                    "parent_checkpoint_id": parent_checkpoint_id,
                    "type": ctype,
                    "checkpoint": serialized.hex(),
                    "metadata_type": mtype,
                    "metadata": meta_serialized.hex(),
                },
            )

        return {
            "configurable": {
                "thread_id": thread_id,
                "checkpoint_ns": checkpoint_ns,
                "checkpoint_id": checkpoint_id,
            }
        }

    async def aput_writes(
        self,
        config: dict,
        writes: Sequence[Tuple[str, Any]],
        task_id: str,
    ) -> None:
        pass

    def get_tuple(self, config: dict) -> Optional[CheckpointTuple]:
        raise NotImplementedError

    def list(self, config: dict, **kwargs):
        raise NotImplementedError

    def put(self, config, checkpoint, metadata, new_versions):
        raise NotImplementedError

    def put_writes(self, config, writes, task_id):
        raise NotImplementedError

    def _row_to_tuple(self, config: dict, row: dict) -> CheckpointTuple:
        return CheckpointTuple(
            config={
                "configurable": {
                    "thread_id": row["thread_id"],
                    "checkpoint_ns": row["checkpoint_ns"],
                    "checkpoint_id": row["checkpoint_id"],
                }
            },
            checkpoint=self.serde.loads_typed(
                (row["type"], bytes.fromhex(row["checkpoint"]))
            ),
            metadata=self.serde.loads_typed(
                (row["metadata_type"], bytes.fromhex(row["metadata"]))
            ),
            parent_config=(
                {
                    "configurable": {
                        "thread_id": row["thread_id"],
                        "checkpoint_ns": row["checkpoint_ns"],
                        "checkpoint_id": row["parent_checkpoint_id"],
                    }
                }
                if row.get("parent_checkpoint_id")
                else None
            ),
        )

```

**Step 6.** In the `squidfall` directory, create a file called `main.py` inside the `squidfall` directory and add the content below to it. 
```python
# Standard library imports.
from contextlib import asynccontextmanager
from os import environ

# Third party imports.
from azure.identity import (
    AzureAuthorityHosts,
    DefaultAzureCredential,
    get_bearer_token_provider,
)
from ag_ui_langgraph import add_langgraph_fastapi_endpoint
from copilotkit import LangGraphAGUIAgent
from fastapi import FastAPI
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import AzureChatOpenAI
from langchain.agents import create_agent

# Local imports.
from .checkpoint_saver import DjangoCheckpointSaver

# Get environment variables.
AZURE_OPENAI_API_VERSION = environ["AZURE_OPENAI_API_VERSION"]
AZURE_OPENAI_ENDPOINT = environ["AZURE_OPENAI_ENDPOINT"]
AZURE_OPENAI_DEPLOYMENT = environ["AZURE_OPENAI_DEPLOYMENT"]
AZURE_TOKEN_SCOPES = environ["AZURE_TOKEN_SCOPES"]
TOOLS_ENDPOINT = environ["TOOLS_ENDPOINT"]

# Get an authorization token provider.
token_provider = get_bearer_token_provider(
    DefaultAzureCredential(authority=AzureAuthorityHosts.AZURE_GOVERNMENT),
    AZURE_TOKEN_SCOPES,
)

# Authenticate with the Azure OpenAI service and get a model handler.
model = AzureChatOpenAI(
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    azure_deployment=AZURE_OPENAI_DEPLOYMENT,
    api_version=AZURE_OPENAI_API_VERSION,
    azure_ad_token_provider=token_provider,
)


# Identify the tools the agent has available.
async def get_tools():
    return await MultiServerMCPClient(
        {
            "squidfall": {
                "transport": "http",
                "url": TOOLS_ENDPOINT,
            }
        }
    ).get_tools()


# Init a FastAPI server.
api = FastAPI()


@asynccontextmanager
async def lifespan(app: FastAPI):
    tools = await get_tools()
    agent = create_agent(
        model=model,
        system_prompt="You are a helpful assistant.",
        checkpointer=DjangoCheckpointSaver(),
        tools=tools,
    )
    add_langgraph_fastapi_endpoint(
        app=app,
        agent=LangGraphAGUIAgent(
            name="squidfall",
            description="An agent.",
            graph=agent,
        ),
        path="/api/v1",
    )
    yield


api.router.lifespan_context = lifespan

```

**Step 7.** In the `inference` directory, create a file called `.env` and add the content below to it.
```bash
# Cloud-specific variables.
export AZURE_CLOUD="AZURE_US_GOVERNMENT"
export AZURE_AUTHORITY_HOSTS="login.microsoftonline.us"
export AZURE_TENANT_ID="xxx"
export AZURE_TOKEN_SCOPES="https://cognitiveservices.azure.us/.default"

# Subscription-specific variables.
export AZURE_CLIENT_ID="xxx"
export AZURE_CLIENT_SECRET="xxx"

# Endpoint-specific variables.
export AZURE_OPENAI_API_VERSION="2024-02-01"
export AZURE_OPENAI_ENDPOINT="https://<SERVICE>.openai.azure.us/"
export AZURE_OPENAI_DEPLOYMENT="squidfall"

# App-specific variables.
export TOOLS_ENDPOINT="http://squidfall-tools:8002/mcp"
export BACKEND_ENDPOINT="http://squidfall-backend:8000"
```

**Step 8.** In the `inference` directory, create a file called `Dockerfile` and add the content below it. Feel free to modify the `image.authors` label.
```dockerfile
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
```

**Step 9.** From the root of the repository, run the command below to start the `inference` container.
```bash
make DOCKER_COMPOSE_PROFILE=inference
```

**Step 10.** Run the command below to start the container you just created.
```bash
make DOCKER_COMPOSE_PROFILE=inference start
```

**Step 11.** Run the command below to confirm the container has started. If it hasn't (or failed), just re-run the previous command to restart it.
```bash
make DOCKER_COMPOSE_PROFILE=inference status
```

**Step 12.** If the container has started, run the command below to interact with it. 
```bash
curl localhost:8001/api/v1/health && echo
```

You should get output similar to below. 
```json
{"status":"ok","agent":{"name":"squidfall"}}
```

**Step 13.** Leave all the containers (`database`, `backend`, `tools`, and `inference`) running. 
