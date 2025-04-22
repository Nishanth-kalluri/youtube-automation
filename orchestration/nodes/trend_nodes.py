#nodes/trend_nodes.py
from services.trends_scraper import TrendsScraper
from utils.logger import Logger

logger = Logger(__name__)

def fetch_trending_topics(state):
    """Node to fetch trending topics and update state"""
    logger.info(f"Fetching trending topics for topic: {state.topic}")
    
    # Initialize the trends scraper
    trends_scraper = TrendsScraper()
    
    # If user didn't provide a topic, use the best trending topic
    if not state.topic or state.topic.strip() == "":
        best_topic = trends_scraper.get_best_trending_topic()
        logger.info(f"No topic provided by user. Using best trending topic: {best_topic}")
        return {
            **state.dict(),
            "topic": best_topic,
            "trending_topics": trends_scraper.get_trending_topics(),
            "status_message": f"Automatically selected trending topic: {best_topic}"
        }
    
    # User provided a topic, but we still fetch trending topics for display
    return {
        **state.dict(),
        "trending_topics": trends_scraper.get_trending_topics(),
        "status_message": f"Continuing with user-selected topic: {state.topic}"
    }
    
def check_pause_script(state):
    """Node to check if workflow should pause after script generation"""
    logger.info("Checking if workflow should pause after script generation")
    
    state_dict = state.dict()
    
    # If we're paused for script review, set the pause reason
    if state.is_paused and state.pause_reason == "review_script":
        state_dict["status_message"] = "Paused for script review. Click Continue when ready."
    
    return state_dict  # Add this return statement which was missing