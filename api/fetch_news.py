"""
API module for fetching news from NewsAPI.
Handles HTTP requests, retries, timeouts, and response validation.
"""

import requests
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from time import sleep
import json

from logger import logger
from config import (
    NEWS_API_KEY,
    NEWS_API_ENDPOINT,
    SEARCH_QUERY,
    SORT_BY,
    PAGE_SIZE,
    LANGUAGE,
    REQUEST_TIMEOUT,
    MAX_RETRIES,
    RETRY_DELAY
)
from database.models import Article


class NewsAPIFetcher:
    """
    Fetch news articles from NewsAPI.org.
    Includes retry logic, timeout handling, and response validation.
    """
    
    def __init__(
        self,
        api_key: str = NEWS_API_KEY,
        base_url: str = NEWS_API_ENDPOINT,
        timeout: int = REQUEST_TIMEOUT,
        max_retries: int = MAX_RETRIES
    ):
        """
        Initialize the API fetcher.
        
        Args:
            api_key: NewsAPI.org API key
            base_url: API endpoint URL
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
        """
        self.api_key = api_key
        self.base_url = base_url
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = requests.Session()
        
        if not self.api_key or self.api_key == "demo":
            logger.warning("Using demo API key - limited to 100 requests/day")
    
    def fetch_articles(
        self,
        query: str = SEARCH_QUERY,
        sort_by: str = SORT_BY,
        language: str = LANGUAGE,
        page_size: int = PAGE_SIZE,
        days_back: int = 7
    ) -> List[Article]:
        """
        Fetch news articles from NewsAPI.
        
        Args:
            query: Search query string
            sort_by: Sort order (publishedAt, relevancy, popularity)
            language: ISO 639-1 language code
            page_size: Number of articles to fetch
            days_back: How many days back to fetch articles
            
        Returns:
            List of Article objects
        """
        try:
            logger.info(f"Fetching articles with query: '{query}'")
            
            # Calculate date range
            to_date = datetime.utcnow().date()
            from_date = to_date - timedelta(days=days_back)
            
            # Prepare request parameters
            params = {
                'q': query,
                'sortBy': sort_by,
                'language': language,
                'pageSize': page_size,
                'from': from_date.isoformat(),
                'to': to_date.isoformat(),
                'apiKey': self.api_key
            }
            
            # Fetch with retry logic
            response = self._make_request_with_retry(params)
            
            if response is None:
                logger.error("Failed to fetch articles after retries")
                return []
            
            # Parse and validate response
            articles = self._parse_response(response)
            logger.info(f"Successfully fetched {len(articles)} articles")
            
            return articles
            
        except Exception as e:
            logger.error(f"Unexpected error during fetch: {e}")
            return []
    
    def _make_request_with_retry(self, params: Dict) -> Optional[requests.Response]:
        """
        Make HTTP request with retry logic.
        
        Args:
            params: Query parameters
            
        Returns:
            Response object or None if all retries failed
        """
        last_exception = None
        
        for attempt in range(1, self.max_retries + 1):
            try:
                logger.debug(f"Request attempt {attempt}/{self.max_retries}")
                
                response = self.session.get(
                    self.base_url,
                    params=params,
                    timeout=self.timeout
                )
                
                # Check status code
                if response.status_code == 200:
                    logger.debug("Request successful")
                    return response
                
                elif response.status_code == 401:
                    logger.error("Unauthorized: Invalid API key")
                    return None
                
                elif response.status_code == 429:
                    logger.warning("Rate limited - waiting before retry")
                    sleep(RETRY_DELAY * attempt)  # Exponential backoff
                    continue
                
                elif response.status_code >= 500:
                    logger.warning(f"Server error ({response.status_code}) - retrying")
                    sleep(RETRY_DELAY)
                    continue
                
                else:
                    logger.warning(f"Unexpected status code: {response.status_code}")
                    return None
                    
            except requests.Timeout:
                last_exception = "Request timeout"
                logger.warning(f"Timeout on attempt {attempt} - retrying")
                if attempt < self.max_retries:
                    sleep(RETRY_DELAY)
                    
            except requests.ConnectionError:
                last_exception = "Connection error"
                logger.warning(f"Connection error on attempt {attempt} - retrying")
                if attempt < self.max_retries:
                    sleep(RETRY_DELAY)
                    
            except Exception as e:
                last_exception = str(e)
                logger.warning(f"Error on attempt {attempt}: {e}")
                if attempt < self.max_retries:
                    sleep(RETRY_DELAY)
        
        logger.error(f"All retries exhausted. Last error: {last_exception}")
        return None
    
    def _parse_response(self, response: requests.Response) -> List[Article]:
        """
        Parse JSON response and convert to Article objects.
        
        Args:
            response: HTTP response object
            
        Returns:
            List of Article objects
        """
        try:
            data = response.json()
            
            # Validate response structure
            if data.get('status') != 'ok':
                error_msg = data.get('message', 'Unknown error')
                logger.error(f"API error: {error_msg}")
                return []
            
            articles = []
            articles_data = data.get('articles', [])
            logger.debug(f"Parsing {len(articles_data)} articles from response")
            
            for article_data in articles_data:
                try:
                    article = self._parse_article(article_data)
                    if article:
                        articles.append(article)
                except Exception as e:
                    logger.warning(f"Error parsing article: {e}")
                    continue
            
            return articles
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            return []
        except Exception as e:
            logger.error(f"Error parsing response: {e}")
            return []
    
    def _parse_article(self, article_data: Dict) -> Optional[Article]:
        """
        Parse article data from API response.
        
        Args:
            article_data: Raw article data from API
            
        Returns:
            Article object or None if parsing failed
        """
        try:
            # Validate required fields
            url = article_data.get('url', '').strip()
            if not url:
                logger.debug("Article missing URL - skipping")
                return None
            
            # Parse datetime
            published_str = article_data.get('publishedAt', '')
            try:
                published_date = datetime.fromisoformat(published_str.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                published_date = None
            
            # Extract source
            source_obj = article_data.get('source', {})
            source = source_obj.get('name', 'Unknown')
            
            # Create Article object
            article = Article(
                title=article_data.get('title', '').strip(),
                source=source,
                author=article_data.get('author', '').strip() or 'Unknown',
                published_date=published_date,
                description=article_data.get('description', '').strip(),
                url=url,
                fetched_at=datetime.utcnow()
            )
            
            return article
            
        except Exception as e:
            logger.error(f"Error parsing individual article: {e}")
            return None
    
    def close(self) -> None:
        """Close session."""
        if self.session:
            self.session.close()
            logger.debug("API session closed")
    
    def __del__(self):
        """Cleanup on deletion."""
        self.close()


def fetch_news(
    query: str = SEARCH_QUERY,
    days_back: int = 7
) -> List[Article]:
    """
    Convenience function to fetch news articles.
    
    Args:
        query: Search query
        days_back: Days back to fetch
        
    Returns:
        List of Article objects
    """
    fetcher = NewsAPIFetcher()
    try:
        return fetcher.fetch_articles(query=query, days_back=days_back)
    finally:
        fetcher.close()
