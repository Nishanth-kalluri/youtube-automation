# orchestration/schema.py
from typing import TypedDict, List, Optional, Dict, Any
from pydantic import BaseModel

class WorkflowState(BaseModel):
    """Schema for the workflow state"""
    # Input
    topic: str = ""
    
    # News data
    raw_articles: List[Dict[str, str]] = []
    consolidated_news: str = ""
    
    # Generated content
    script: str = ""
    narrator: str=""
    image_prompts: List[str] = []
    audio_path: str = ""
    image_paths: List[str] = []
    video_path: str = ""
    
    # Upload data
    upload_status: Dict[str, Any] = {}
    
    # Workflow state
    status_message: str = "Ready to start"
    is_paused: bool = False
    pause_reason: str = ""
    
    # Error handling
    error: str = ""
    has_error: bool = False