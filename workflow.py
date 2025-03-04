# Importing Python Libraries.
from typing import Any, List, Tuple
from typing_extensions import TypedDict
# Importing LangGraph Libraries.
from langgraph.graph import StateGraph, START
from langgraph.checkpoint.memory import MemorySaver
# from IPython.display import Image, display
from PIL import Image

from src.agents import PlatformAgent


class AnalyticState(TypedDict):
    messages: List[Tuple[str, Any]] = []

    platform_id: str

    question: str
    answer: str


def get_answer(state: AnalyticState):
    question = state["question"]
    platform_id = state["platform_id"]
    messages = state["messages"] if "messages" in state else list([state["question"]])

    platform_agent = PlatformAgent(platform_id = platform_id, messages = messages)
    answer = platform_agent.acknowledge(question)

    messages.append((question, answer))

    return {
        "question": question,
        "answer": answer,
        "messages": messages
    }


workflow = StateGraph(AnalyticState)

workflow.add_node("get_answer", get_answer)


workflow.add_edge(START, "get_answer")

checkpointer = MemorySaver()

graph = workflow.compile(checkpointer = checkpointer)

# with open("graph.png", "wb") as f:
#     f.write(graph.get_graph().draw_mermaid_png())

# img = Image.open("graph.png")
# img.show()