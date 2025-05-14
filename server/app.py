from typing import TypedDict, Annotated, Optional
from langgraph.graph import add_messages, StateGraph, END
from langchain_core.messages import HumanMessage, AIMessageChunk, ToolMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.checkpoint.memory import MemorySaver

from dotenv import load_dotenv
from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

import json
from uuid import uuid4

load_dotenv()

# Checkpoint memory
memory = MemorySaver()

# --- Define LangGraph state ---
class State(TypedDict):
    messages: Annotated[list, add_messages]

# --- Define tools ---
search_tool = TavilySearchResults(max_results=4)
tools = [search_tool]

# --- Gemini LLM with tool binding ---
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash", 
    convert_system_message_to_human=True
)
llm_with_tools = llm.bind_tools(tools=tools)

# --- Model Node ---
async def model(state: State):
    result = await llm_with_tools.ainvoke(state["messages"])
    return {"messages": [result]}

# --- Router Node ---
async def tools_router(state: State):
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tool_node"
    return END

# --- Tool Node ---
async def tool_node(state: State):
    tool_calls = state["messages"][-1].tool_calls
    tool_messages = []

    for tool_call in tool_calls:
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]
        tool_id = tool_call["id"]

        if tool_name == "tavily_search_results_json":
            search_results = await search_tool.ainvoke(tool_args)
            tool_messages.append(
                ToolMessage(
                    content=str(search_results),
                    tool_call_id=tool_id,
                    name=tool_name
                )
            )
    return {"messages": tool_messages}

# --- LangGraph setup ---
graph_builder = StateGraph(State)
graph_builder.add_node("model", model)
graph_builder.add_node("tool_node", tool_node)
graph_builder.set_entry_point("model")
graph_builder.add_conditional_edges("model", tools_router)
graph_builder.add_edge("tool_node", "model")

graph = graph_builder.compile(checkpointer=memory)

# --- FastAPI app ---
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Type"],
)

# --- SSE utility ---
def serialise_ai_message_chunk(chunk):
    if isinstance(chunk, AIMessageChunk):
        return chunk.content
    raise TypeError(f"Unsupported chunk type: {type(chunk).__name__}")

# --- Chat streaming generator ---
async def generate_chat_responses(message: str, checkpoint_id: Optional[str] = None):
    is_new_conversation = checkpoint_id is None
    new_checkpoint_id = str(uuid4()) if is_new_conversation else checkpoint_id
    config = {"configurable": {"thread_id": new_checkpoint_id}}

    if is_new_conversation:
        yield f"data: {{\"type\": \"checkpoint\", \"checkpoint_id\": \"{new_checkpoint_id}\"}}\n\n"

    events = graph.astream_events(
        {"messages": [HumanMessage(content=message)]},
        version="v2",
        config=config
    )

    async for event in events:
        event_type = event["event"]

        if event_type == "on_chat_model_stream":
            chunk_content = serialise_ai_message_chunk(event["data"]["chunk"])
            safe_content = chunk_content.replace("'", "\\'").replace("\n", "\\n")
            yield f"data: {{\"type\": \"content\", \"content\": \"{safe_content}\"}}\n\n"

        elif event_type == "on_chat_model_end":
            tool_calls = getattr(event["data"]["output"], "tool_calls", [])
            search_calls = [call for call in tool_calls if call["name"] == "tavily_search_results_json"]
            if search_calls:
                search_query = search_calls[0]["args"].get("query", "")
                safe_query = search_query.replace('"', '\\"').replace("'", "\\'").replace("\n", "\\n")
                yield f"data: {{\"type\": \"search_start\", \"query\": \"{safe_query}\"}}\n\n"

        elif event_type == "on_tool_end" and event["name"] == "tavily_search_results_json":
            output = event["data"]["output"]
            if isinstance(output, list):
                urls = [item["url"] for item in output if isinstance(item, dict) and "url" in item]
                urls_json = json.dumps(urls)
                yield f"data: {{\"type\": \"search_results\", \"urls\": {urls_json}}}\n\n"

    yield f"data: {{\"type\": \"end\"}}\n\n"

# --- Chat route ---
@app.get("/chat_stream/{message}")
async def chat_stream(message: str, checkpoint_id: Optional[str] = Query(None)):
    return StreamingResponse(
        generate_chat_responses(message, checkpoint_id),
        media_type="text/event-stream"
    )
