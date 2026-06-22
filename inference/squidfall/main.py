# Standard library imports.
from contextlib import asynccontextmanager
from os import environ

# Third party imports.
from ag_ui_langgraph import add_langgraph_fastapi_endpoint
from copilotkit import LangGraphAGUIAgent
from fastapi import FastAPI
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent

# Local imports.
from 
**Step 19.** In the `backend` directory, create a file called `entrypoint.sh` and add the content below to it. 
```bash
#!/usr/bin/env sh

set -e

python manage.py migrate

uvicorn squidfall.asgi:application --host 0.0.0.0 --port 8000

```checkpoint_saver import DjangoCheckpointSaver
from 
**Step 19.** In the `backend` directory, create a file called `entrypoint.sh` and add the content below to it. 
```bash
#!/usr/bin/env sh

set -e

python manage.py migrate

uvicorn squidfall.asgi:application --host 0.0.0.0 --port 8000

```model_providers.openai import (
    get_openai_model,
    get_openai_model_from_azure,
)

# Get environment variables.
MODEL_PROVIDER = environ["MODEL_PROVIDER"]
TOOLS_ENDPOINT = environ["TOOLS_ENDPOINT"]

# Get a model handler.
match MODEL_PROVIDER:
    case "openai":
        model = get_openai_model()
    case "azure_openai":
        model = get_openai_model_from_azure()
    case _:
        print("Invalid MODEL_PROVIDER (options: openai or azure_openai).")
        exit(1)


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
