#services/news_scraper.py
import os
import json
import requests
import tiktoken  # Add tiktoken for token counting
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
        # Initialize tokenizer for token counting
        try:
            self.tokenizer = tiktoken.get_encoding("cl100k_base")  # Using OpenAI's tokenizer as an approximation
        except (ImportError, AttributeError):
            self.logger.warning("tiktoken not available, falling back to approximate token counting")
            self.tokenizer = None
        self.max_input_tokens = 6000
        self.token_buffer = 1000  # Reserve 2000 tokens for prompt and overhead
        
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
            'sortBy': 'rel',
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
            
            # Get at most 10 articles - we'll filter down further in consolidate_news if needed
            max_articles_to_fetch = 10
            
            # Extract article information
            articles = []
            for article in data["articles"]["results"][:max_articles_to_fetch]:
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
    
    def count_tokens(self, text):
        """Count the number of tokens in the given text"""
        if self.tokenizer:
            return len(self.tokenizer.encode(text))
        else:
            # Fallback approximation if tiktoken is not available (about 4 chars per token)
            return len(text) // 4
    
    def consolidate_news(self, articles,topic):
        """Consolidate multiple news articles into a single coherent summary using Groq"""
        if not articles:
            self.logger.warning("No articles to consolidate")
            return "No recent news available on this topic."
        
        # Calculate available token space
        available_tokens = self.max_input_tokens - self.token_buffer
        
        # Prepare the articles text while monitoring token count
        selected_articles = []
        current_token_count = 0
        
        for article in articles:
            # Create article text to check token count
            article_text = f"Article - {article['title']} ({article['date']}):\n{article['body']}\n\n"
            article_tokens = self.count_tokens(article_text)
            
            # Check if adding this article would exceed our token limit
            if current_token_count + article_tokens <= available_tokens:
                selected_articles.append(article)
                current_token_count += article_tokens
            else:
                self.logger.info(f"Stopping at {len(selected_articles)} articles due to token limit")
                break
        
        if not selected_articles:
            # If even one article exceeds the limit, take a truncated version of the first article
            first_article = articles[0]
            article_text = f"Article - {first_article['title']} ({first_article['date']}):\n"
            
            # Truncate the body to fit within token limit
            body_tokens = available_tokens - self.count_tokens(article_text)
            truncated_body = first_article['body']
            while self.count_tokens(truncated_body) > body_tokens:
                truncated_body = truncated_body[:int(len(truncated_body) * 0.9)]  # Reduce by 10%
            
            article_text += truncated_body
            articles_text = article_text
            
            self.logger.warning("Using truncated version of first article due to token limitations")
        else:
            # Prepare the articles text
            articles_text = ""
            for i, article in enumerate(selected_articles, 1):
                articles_text += f"Article {i} - {article['title']} ({article['date']}):\n{article['body']}\n\n"
        
        self.logger.info(f"Using {len(selected_articles)} articles with approximately {current_token_count} tokens")
        
        # Prepare the prompt for Groq
        prompt = f"""
        I have the following news articles about {topic} :
        
        {articles_text}
        
        Please consolidate these articles into a single coherent news summary that captures all the important information about {topic}.
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
            import re
            cleaned_news = re.sub(r'<think>.*?</think>', '', consolidated_news, flags=re.DOTALL)
            self.logger.info("Successfully consolidated news articles")
            return cleaned_news
            
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
        consolidated_news = self.consolidate_news(articles,topic)
        
        return consolidated_news