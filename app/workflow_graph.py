"""
LangGraph workflow graph for website generation.
"""
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from app.workflow_state import WorkflowState
from app.workflow_nodes import (
    planning_node,
    image_description_node,
    image_generation_node,
    html_generation_node,
    file_storage_node
)


def create_website_workflow():
    """
    Create and compile the LangGraph workflow for website generation.
    
    Workflow:
    START -> planning -> image_description -> image_generation -> html_generation -> file_storage -> END
    """
    # Create workflow graph
    workflow = StateGraph(WorkflowState)
    
    # Add nodes
    workflow.add_node("planning", planning_node)
    workflow.add_node("image_description", image_description_node)
    workflow.add_node("image_generation", image_generation_node)
    workflow.add_node("html_generation", html_generation_node)
    workflow.add_node("file_storage", file_storage_node)
    
    # Define edges (simplified workflow)
    workflow.add_edge(START, "planning")
    workflow.add_edge("planning", "image_description")
    workflow.add_edge("image_description", "image_generation")
    workflow.add_edge("image_generation", "html_generation")
    workflow.add_edge("html_generation", "file_storage")
    workflow.add_edge("file_storage", END)
    
    # Compile with checkpointer for state persistence
    checkpointer = MemorySaver()
    compiled_workflow = workflow.compile(checkpointer=checkpointer)
    
    return compiled_workflow


# Create global workflow instance
website_workflow = create_website_workflow()

