#services/news_scraper.py
import os
import json
import requests
from datetime import datetime, timedelta
from groq import Groq
from config import settings
from utils.logger import Logger

class NewsScraper:
    def __init__(self):
        self.logger = Logger(__name__)
        self.api_key = settings.EVENT_REGISTRY_API_KEY
        self.api_url = "http://eventregistry.org/api/v1/article/getArticles"
        self.groq_client = Groq(api_key=settings.GROQ_API_KEY)
        
    def fetch_news(self, topic, days_back=1, language="eng"):
        """Fetch news articles about a topic from EventRegistry API using keyword search"""
        self.logger.info(f"Fetching news for topic: {topic}")
        
        # Calculate date range (from days_back days ago to today)
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
        
        # Prepare request parameters
        params = {
            'apiKey': self.api_key,
            'keyword': topic,
            'lang': language,
            'dateStart': start_date,
            'dateEnd': end_date,
            'sortBy': 'date',
            'sortByAsc': False
        }
        
        try:
            # Make the API request
            response = requests.get(self.api_url, params=params)
            response.raise_for_status()  # Raise exception for HTTP errors
            
            # Parse the response
            data = response.json()
            
            # Check if we have results
            if "articles" not in data or "results" not in data["articles"]:
                self.logger.warning(f"No news articles found for topic: {topic}")
                return []
            
            # Extract article information
            articles = []
            for article in data["articles"]["results"][:5]:  # Get top 5 articles
                if "body" in article and article["body"]:
                    articles.append({
                        "title": article.get("title", ""),
                        "date": article.get("date", ""),
                        "url": article.get("url", ""),
                        "body": article.get("body", "")
                    })
            
            self.logger.info(f"Retrieved {len(articles)} news articles for topic: {topic}")
            return articles
            
        except Exception as e:
            self.logger.error(f"Error fetching news: {e}")
            return []
    
    def consolidate_news(self, articles):
        """Consolidate multiple news articles into a single coherent summary using Groq"""
        if not articles:
            self.logger.warning("No articles to consolidate")
            return "No recent news available on this topic."
        
        # Prepare the articles text
        articles_text = ""
        for i, article in enumerate(articles, 1):
            articles_text += f"Article {i} - {article['title']} ({article['date']}):\n{article['body']}\n\n"
        
        # Prepare the prompt for Groq
        prompt = f"""
        I have the following news articles about a trending topic:
        
        {articles_text}
        
        Please consolidate these articles into a single coherent news summary that captures all the important information.
        The summary should be well-structured, factual, and comprehensive.
        Focus on the most important and recent developments.
        Aim for around 300-500 words.
        """
        
        try:
            # Call Groq API
            response = self.groq_client.chat.completions.create(
                model="deepseek-r1-distill-llama-70b",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=2048,
                top_p=0.9,
            )
            
            # Extract the consolidated news
            consolidated_news = response.choices[0].message.content
            
            self.logger.info("Successfully consolidated news articles")
            return consolidated_news
            
        except Exception as e:
            self.logger.error(f"Error consolidating news: {e}")
            return "Error consolidating news articles."
    
    def get_news_for_topic(self, topic):
        """Get consolidated news for a trending topic"""
        # Fetch news articles
        articles = self.fetch_news(topic)
        
        # If no articles found, return a message
        if not articles:
            self.logger.warning(f"No articles found for topic: {topic}")
            return f"No recent news found for '{topic}'."
        
        # Consolidate the articles
        consolidated_news = self.consolidate_news(articles)
        
        return consolidated_news