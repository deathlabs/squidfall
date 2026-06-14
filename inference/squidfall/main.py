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
from langgraph.checkpoint.memory import MemorySaver

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
            "weather": {
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
        checkpointer=MemorySaver(),
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
