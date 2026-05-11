# Wires together the LLM, tools, memory, and system prompt into a LangGraph ReAct agent.
# A new agent instance is created per run_agent() call -- MemorySaver state lives in
# the object, so thread history only persists within a single page session.

import time

from langchain_core.messages import AIMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

from src.config import DEFAULT_MODEL
from src.llm import get_llm
from src.logger import get_logger
from src.prompts import SYSTEM_PROMPT
from src.tools import get_tools, set_active_model

_log = get_logger("careerfit.agent")


def create_careerfit_agent(
    model_name: str = None,
    enable_company_research: bool = False,
    enable_job_search: bool = False,
    mode: str = "Ask Career Base",
    memory: MemorySaver = None,
):
    """Build a compiled LangGraph ReAct agent with tools and memory.

    memory is passed in from the caller rather than created here. This lets
    app.py store a single MemorySaver in st.session_state so conversation
    history persists across multiple run_agent() calls in the same browser
    session. Without this, each call gets a fresh MemorySaver and the agent
    has no memory of previous turns at all.

    MCP tools are only included when their flags are True. The mode parameter
    controls whether find_job_listings is included -- it's suppressed in the
    three JD modes where the user already has a job description.
    """
    llm = get_llm(model=model_name)
    tools = get_tools(
        enable_company_research=enable_company_research,
        enable_job_search=enable_job_search,
        mode=mode,
    )
    if memory is None:
        memory = MemorySaver()

    agent = create_react_agent(
        model=llm,
        tools=tools,
        checkpointer=memory,
        prompt=SYSTEM_PROMPT,
    )
    return agent


def run_agent(
    user_message: str,
    model_name: str = None,
    thread_id: str = "default",
    enable_company_research: bool = False,
    enable_job_search: bool = False,
    mode: str = "Ask Career Base",
    memory: MemorySaver = None,
) -> dict:
    """Run the agent on one user message and return the response and tool names called.

    memory should be a MemorySaver stored in st.session_state so it persists
    across turns. thread_id keys the checkpointer -- all turns in one browser
    session share the same thread so the agent can reference earlier messages.
    mode is passed through to get_tools() so the tool list matches the current
    UI mode (e.g. find_job_listings is suppressed in JD modes).
    """
    agent = create_careerfit_agent(
        model_name=model_name,
        enable_company_research=enable_company_research,
        enable_job_search=enable_job_search,
        mode=mode,
        memory=memory,
    )
    config = {"configurable": {"thread_id": thread_id}}

    # Propagate the user-selected model to the structured-output tools so they
    # don't silently fall back to DEFAULT_MODEL for the actual content generation.
    set_active_model(model_name)

    start = time.time()
    result = agent.invoke(
        {"messages": [{"role": "user", "content": user_message}]},
        config=config,
    )
    latency_ms = int((time.time() - start) * 1000)

    messages = result.get("messages", [])

    # pull tool names from every AIMessage that made a tool call this turn
    tool_calls: list[str] = []
    for msg in messages:
        if isinstance(msg, AIMessage) and getattr(msg, "tool_calls", []):
            for tc in msg.tool_calls:
                tool_calls.append(tc["name"])

    _log.info(
        "model=%s thread=%s tools=%s latency_ms=%d",
        model_name or DEFAULT_MODEL, thread_id, tool_calls, latency_ms,
    )

    # last message is always the final non-tool response
    response = messages[-1].content if messages else ""

    return {"response": response, "tool_calls": tool_calls}


if __name__ == "__main__":
    test_query = "What are the strongest proof points for an AI education role?"
    print(f"Query: {test_query!r}\n")
    print("Running agent (this may take a moment)...\n")

    result = run_agent(test_query)

    print("=== Agent Response ===")
    print(result["response"])
    print()
    print("=== Tools Called ===")
    if result["tool_calls"]:
        for name in result["tool_calls"]:
            print(f"  - {name}")
    else:
        print("  (none)")
