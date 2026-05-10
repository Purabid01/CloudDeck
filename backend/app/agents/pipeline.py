from langgraph.graph import StateGraph, END
from typing import TypedDict, Optional

# Define what state flows between agents
class PipelineState(TypedDict):
    task_id: str
    description: str
    intake_result: Optional[dict]
    classifier_result: Optional[dict]
    blueprint_result: Optional[dict]
    cost_result: Optional[dict]
    human_answer: Optional[str]   # ← waiting for user input
    error: Optional[str]

# Build the graph
graph = StateGraph(PipelineState)

# Add nodes (agents)
graph.add_node("intake", run_intake)
graph.add_node("classifier", run_classifier)
graph.add_node("blueprint_finder", run_blueprint_finder)
graph.add_node("ask_user", ask_sizing_questions)    # ← pauses for human
graph.add_node("cost_estimator", run_cost_estimator)
graph.add_node("code_generator", run_code_generator)
graph.add_node("verify", run_verification)

# Add edges (flow)
graph.add_edge("intake", "classifier")
graph.add_edge("classifier", "blueprint_finder")
graph.add_edge("blueprint_finder", "ask_user")
graph.add_edge("ask_user", "cost_estimator")
graph.add_edge("cost_estimator", "code_generator")

# Conditional edge — retry if verification fails
graph.add_conditional_edges(
    "verify",
    lambda state: "done" if state["verified"] else "code_generator",
    {"done": END, "code_generator": "code_generator"}
)

graph.set_entry_point("intake")
pipeline = graph.compile()