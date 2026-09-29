# Third party imports.
from langchain.tools import ToolRuntime, tool

# Local imports.
from squidfall.memory.context_schema import ContextSchema


@tool
async def check_semantic_memory(env: ToolRuntime[ContextSchema]) -> str:
    """Retrieve semantic facts about the current subject from memory."""
    namespace = ("semantic", env.context.subject)
    memories = await env.store.asearch(namespace, limit=100)
    if not memories:
        return None
    return "\n".join(memory.value["fact"] for memory in memories)


@tool
async def update_semantic_memory(env: ToolRuntime[ContextSchema], fact: str) -> str:
    """Save a semantic fact about the current subject to memory."""
    namespace = ("semantic", env.context.subject)
    key = f"fact-{fact[:32].replace(' ', '-').lower()}"
    value = {"fact": fact}
    await env.store.aput(namespace, key, value)
    return f"Saved: {fact}"


@tool
async def check_procedural_memory(env: ToolRuntime[ContextSchema]) -> str:
    """Retrieve procedural instructions from memory."""
    namespace = ("procedural", "squidfall")
    memories = await env.store.asearch(namespace, limit=100)
    if not memories:
        return None
    return "\n".join(memory.value["instruction"] for memory in memories)


@tool
async def update_procedural_memory(
    env: ToolRuntime[ContextSchema], instruction: str
) -> str:
    """Save a procedural instruction to memory."""
    namespace = ("procedural", "squidfall")
    key = f"procedure-{instruction[:32].replace(' ', '-').lower()}"
    value = {"instruction": instruction}
    await env.store.aput(namespace, key, value)
    return f"Saved: {instruction}"


def get_memory_tools() -> list:
    """Get a list of memory tools."""
    return [
        check_procedural_memory,
        check_semantic_memory,
        update_procedural_memory,
        update_semantic_memory,
    ]
