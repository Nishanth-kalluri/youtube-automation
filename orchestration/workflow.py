#orchestration/workflow.py
from langgraph.graph import StateGraph
from .schema import WorkflowState
from .nodes import news_nodes, script_nodes, media_nodes, video_nodes, upload_nodes, trend_nodes

def create_workflow_graph():
    """Create the workflow graph with all nodes and edges"""
    # Create a new graph with our state type
    graph = StateGraph(WorkflowState)
    
    # Define all nodes (grouped by logical function)
    
    # Trending topics node
    graph.add_node("fetch_trending_topics", trend_nodes.fetch_trending_topics)
    
    # News related nodes
    graph.add_node("fetch_and_consolidate_news", news_nodes.fetch_and_consolidate_news)
    graph.add_node("check_pause_news", news_nodes.check_pause_news)
    
    # Script related nodes
    graph.add_node("generate_script_and_prompts", script_nodes.generate_script_and_prompts)
    graph.add_node("check_pause_script", script_nodes.check_pause_script)
    
    # Media generation nodes
    graph.add_node("generate_audio", media_nodes.generate_audio)
    graph.add_node("generate_images", media_nodes.generate_images)
    graph.add_node("check_pause_media", media_nodes.check_pause_media)
    
    # Video creation nodes
    graph.add_node("assemble_video", video_nodes.assemble_video)
    graph.add_node("check_pause_video", video_nodes.check_pause_video)
    
    # Upload related nodes
    graph.add_node("upload_video", upload_nodes.upload_video)
    
    # Final node
    graph.add_node("finish_workflow", lambda state: {**state.dict(), "status_message": "Workflow completed"})
    
    # Define conditional edges
    
    # Define the workflow path with trending topics
    graph.add_edge("fetch_trending_topics", "fetch_and_consolidate_news")
    graph.add_edge("fetch_and_consolidate_news", "check_pause_news")
    
    # From check_pause_news
    graph.add_conditional_edges(
        "check_pause_news",
        lambda state: "paused" if state.is_paused else "continue",
        {
            "paused": "check_pause_news",  # Loop back to self until unpaused
            "continue": "generate_script_and_prompts"
        }
    )
    
    # Script generation
    graph.add_edge("generate_script_and_prompts", "check_pause_script")
    
    # From check_pause_script
    graph.add_conditional_edges(
        "check_pause_script",
        lambda state: "paused" if state.is_paused else "continue",
        {
            "paused": "check_pause_script",  # Loop back to self until unpaused
            "continue": "generate_audio"
        }
    )
    
    # Media generation flow
    graph.add_edge("generate_audio", "generate_images")
    graph.add_edge("generate_images", "check_pause_media")
    
    # From check_pause_media
    graph.add_conditional_edges(
        "check_pause_media",
        lambda state: "paused" if state.is_paused else "continue",
        {
            "paused": "check_pause_media",  # Loop back to self until unpaused
            "continue": "assemble_video"
        }
    )
    
    # Video creation flow
    graph.add_edge("assemble_video", "check_pause_video")
    
    # From check_pause_video
    graph.add_conditional_edges(
        "check_pause_video",
        lambda state: "paused" if state.is_paused else "continue",
        {
            "paused": "check_pause_video",  # Loop back to self until unpaused
            "continue": "upload_video"
        }
    )
    
    # Final edge
    graph.add_edge("upload_video", "finish_workflow")
    
    # Set the entry point
    graph.set_entry_point("fetch_trending_topics")
    
    # Compile the graph
    return graph.compile()

# Create the workflow
workflow = create_workflow_graph()