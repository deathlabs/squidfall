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
azure-identity
ag-ui-langgraph
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

**Step 5.** Create a file called `__init__.py` inside the `squidfall` directory you just created.

**Step 6.** Create a file called `main.py` inside the `squidfall` directory and add the content below to it.
```python
# Standard library imports.
from logging import getLogger
from os import environ, getenv

# Third party imports.
from fastmcp import FastMCP
from fastmcp.utilities.logging import configure_logging
from httpx import AsyncClient

# Init a MCP server and set its logging level.
mcp = FastMCP(name="squidfall")
configure_logging(level="DEBUG")
logger = getLogger("squidfall")

GEOCODING_API_KEY = environ["GEOCODING_API_KEY"]


@mcp.tool(description="Get the latitude and longitude for a location.")
async def get_coordinates(location: str) -> dict:
    """Get the latitude and longitude for a location.

    Args:
        location: A city name, address, or ZIP code (e.g. 'Pittsburgh, PA').

    Returns:
        A dict with 'lat' and 'lon' keys, or an error message under 'error'.
    """
    async with AsyncClient(verify=False) as client:
        response = await client.get(
            "https://geocode.maps.co/search",
            params={
                "q": location,
                "api_key": GEOCODING_API_KEY,
            },
            follow_redirects=True,
        )
        response.raise_for_status()
        results = response.json()
        if not results:
            return {"error": f"No coordinates found for: {location}"}

        return {"lat": float(results[0]["lat"]), "lon": float(results[0]["lon"])}


@mcp.tool(description="Get the current weather forecast for a coordinate pair.")
async def get_forecast(lat: float, lon: float) -> str:
    """Get the current weather forecast for a coordinate pair.

    Args:
        lat: Latitude.
        lon: Longitude.

    Returns:
        The current forecast period as a plain text string.
    """
    async with AsyncClient(verify=False) as client:
        points_response = await client.get(
            url=f"https://api.weather.gov/points/{lat},{lon}",
            headers={
                "User-Agent": "(squidfall, contact@example.com)",
                "Accept": "application/geo+json",
            },
            follow_redirects=True,
        )
        points_response.raise_for_status()
        forecast_url = points_response.json()["properties"]["forecast"]
        forecast_response = await client.get(forecast_url)
        forecast_response.raise_for_status()
        periods = forecast_response.json()["properties"]["periods"]
        current = periods[0]

        return f"{current['name']}: {current['detailedForecast']}"


if __name__ == "__main__":
    mcp.run(
        transport="streamable-http",
        host="0.0.0.0",
        port=8002,
    )

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

**Step 11.** Run the command below to confirm the container has started.
```bash
make DOCKER_COMPOSE_PROFILE=inference status
```

**Step 12.** If the container has started, run the command below to interact with it. 
```bash
curl localhost:8001/api/v1/health && echo
```

**Step 13.** Run the command below to stop the container.
```bash
make DOCKER_COMPOSE_PROFILE=inference stop
```
