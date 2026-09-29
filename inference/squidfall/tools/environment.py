# Third party imports.
from langchain_mcp_adapters.client import MultiServerMCPClient


async def get_environment_tools(url: str):
    """Retrieve tools for interacting with the environment."""
    client = MultiServerMCPClient(
        {
            "squidfall": {
                "transport": "http",
                "url": url,
            }
        }
    )
    return await client.get_tools()
