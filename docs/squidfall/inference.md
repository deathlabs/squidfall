# Inference

**Step 1.** Text goes here.
```bash
mkdir inference
```

**Step 2.** Text goes here.
```bash
cd inference
```

**Step 3.** Tex goes here.
```bash
python -m venv .venv
```

**Step 4.** Tex goes here.
```bash
source .venv/bin/activate
```

**Step 5.** Text goes here.
```bash
mkdir squidfall
```

**Step 6.** Text goes here.
```bash
touch squidfall/__init__.py
```

**Step 7.** Text goes here.
```bash
vim squidfall/main.py
```

**Step 7.** Text goes here. 
```python
import os

from dotenv import load_dotenv
from ag_ui_langgraph import add_langgraph_fastapi_endpoint
from copilotkit import LangGraphAGUIAgent
from fastapi import FastAPI
from langgraph.graph import END, START, MessagesState, StateGraph
from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
import uvicorn
load_dotenv()

async def mock_llm(state: MessagesState):
  model = ChatOpenAI(model="gpt-4.1-mini")
  system_message = SystemMessage(content="You are a helpful assistant.")
  response = await model.ainvoke(
    [
      system_message,
      *state["messages"],
    ]
  )
  return {"messages": response}


graph = StateGraph(MessagesState)
graph.add_node(mock_llm)
graph.add_edge(START, "mock_llm")
graph.add_edge("mock_llm", END)
graph = graph.compile(
  checkpointer=MemorySaver()
)

app = FastAPI()

add_langgraph_fastapi_endpoint(
  app=app,
  agent=LangGraphAGUIAgent(
    name="sample_agent",
    description="An example agent to use as a starting point for your own agent.",
    graph=graph,
  ),
  path="/",
)

def main():
  """Run the uvicorn server."""
  uvicorn.run(
    "main:app",
    host="0.0.0.0",
    port=8123,
    reload=True,
  )

if __name__ == "__main__":
  main()
```

**Step 8.** Text goes here.
```bash
vim requirements.txt
```

Text goes here.
```
ag-ui-langgraph
copilotkit
dotenv
fastapi
langchain_openai
uvicorn
```

**Step 9.** Text goes here.
```bash
pip install -r requirements.txt
```

**Step 9.** Text goes here.
```bash
echo "export OPENAI_API_KEY='AAA...'" > .env
```

**Step 10.** Text goes here.
```bash
python squidfall/main.py
```

**Step 11.** Text goes here.
```bash
vim Dockerfile
```

Text goes here.
```dockerfile
FROM alpine:3.23
LABEL image.authors="Victor Fernandez III <@cyberphor>"
WORKDIR /home/inference/
COPY requirements.txt requirements.txt
COPY squidfall/ squidfall/
RUN apk add --no-cache --update python3 py3-pip &&\
    pip install --break-system-packages -r requirements.txt &&\
    adduser -D squidfall -h /home/inference &&\
    chown -R squidfall:squidfall /home/inference
USER squidfall
CMD [ "python", "-m", "squidfall.main" ]
```
