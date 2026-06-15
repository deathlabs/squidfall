# Tools

**Step 1.** Create a directory called `tools`.
```bash
mkdir tools
```

**Step 2.** Change your working directory to the directory you just created.
```bash
cd tools
```

**Step 3.** Create a file called `requirements.txt` and add the content below to it.
```
fastmcp
```

**Step 4.** In the `tools` directory, create a directory called `squidfall`.
```bash
mkdir squidfall
```

**Step 5.** Inside the `squidfall` directory you just created, create a file called `__init__.py` 

**Step 6.** Inside the `squidfall` directory, create a file called `main.py` and add the content below to it.
```python
# Standard library imports.
from json import dumps
from logging import getLogger
from os import environ, getenv

# Third party imports.
from fastmcp import FastMCP
from fastmcp.utilities.logging import configure_logging
from httpx import AsyncClient
from starlette.requests import Request
from starlette.responses import PlainTextResponse

# Init a MCP server and set its logging level.
mcp = FastMCP(name="squidfall")
configure_logging(level="DEBUG")
logger = getLogger("squidfall")

GEOCODING_API_KEY = environ["GEOCODING_API_KEY"]


@mcp.custom_route("/api/v1/healthcheck", methods=["GET"])
async def health_check(request: Request) -> PlainTextResponse:
    return PlainTextResponse(dumps({"status": "ok"}))


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

**Step 7.** In the `tools` directory, create a file called `.env` and add the content below to it.
```bash
export GEOCODING_API_KEY=""
```

**Step 8.** In the `tools` directory, create a file called `Dockerfile` and add the content below it. Feel free to modify the `image.authors` label.
```dockerfile
FROM alpine:3.23
LABEL image.authors="Victor Fernandez III, @cyberphor"
WORKDIR /home/tools/
COPY requirements.txt requirements.txt
COPY squidfall/ squidfall/
RUN apk add --no-cache --update python3 py3-pip &&\
    pip install --break-system-packages -r requirements.txt &&\
    adduser -D squidfall -h /home/tools/ &&\
    chown -R squidfall:squidfall /home/tools/
USER squidfall
EXPOSE 8002
CMD [ "python", "-m", "squidfall.main" ]
```

**Step 9.** From the root of the repository, run the command below to start the `tools` container.
```bash
make DOCKER_COMPOSE_PROFILE=tools
```

**Step 10.** Run the command below to start the container you just created.
```bash
make DOCKER_COMPOSE_PROFILE=tools start
```

**Step 11.** Run the command below to confirm the container has started.
```bash
make DOCKER_COMPOSE_PROFILE=tools status
```

**Step 12.** If the container has started, run the commands below to interact with it. 
```bash
curl http://localhost:8002/api/v1/healthcheck && echo
```

You should get output similar to below. 
```json
{"status": "ok"}
```

**Step 13.** Run the command below to stop the container.
```bash
make DOCKER_COMPOSE_PROFILE=tools stop
```
