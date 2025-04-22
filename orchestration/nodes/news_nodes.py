# orchestration/nodes/news_nodes.py
from services.news_scraper import NewsScraper
from utils.logger import Logger

logger = Logger(__name__)
news_scraper = NewsScraper()

def fetch_and_consolidate_news(state):
    """Node to fetch and consolidate news for the given topic"""
    logger.info(f"Starting news fetch for topic: {state.topic}")
    
    try:
        # Update status
        state_dict = state.dict()
        state_dict["status_message"] = f"Fetching news for: {state.topic}"
        
        # Get consolidated news
        consolidated_news = news_scraper.get_news_for_topic(state.topic)
        
        # Update state
        state_dict["consolidated_news"] = consolidated_news
        state_dict["status_message"] = "News fetched and consolidated successfully"
        
        return state_dict
        
    except Exception as e:
        logger.error(f"Error in fetch_and_consolidate_news: {e}")
        state_dict = state.dict()
        state_dict["error"] = f"Failed to fetch news: {str(e)}"
        state_dict["has_error"] = True
        state_dict["status_message"] = "Error fetching news"
        return state_dict

def check_pause_news(state):
    """Node to check if workflow should pause after news consolidation"""
    logger.info("Checking if workflow should pause after news consolidation")
    
    state_dict = state.dict()
    
    # If we're paused for news review, set the pause reason
    if state.is_paused and state.pause_reason == "review_news":
        state_dict["status_message"] = "Paused for news review. Click Continue when ready."
    
    return state_dict