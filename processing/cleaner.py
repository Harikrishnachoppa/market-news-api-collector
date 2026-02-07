"""
Data cleaning and validation module.
Handles text normalization, emoji removal, null value handling, and validation.
"""

import re
from typing import Optional
from datetime import datetime

from logger import logger
from config import (
    EMOJI_PATTERN,
    MAX_TITLE_LENGTH,
    MAX_AUTHOR_LENGTH,
    MAX_DESCRIPTION_LENGTH,
    DEFAULT_AUTHOR
)
from database.models import Article


class ArticleCleaner:
    """
    Cleans and validates news article data.
    Removes emojis, normalizes text, handles nulls, and validates fields.
    """
    
    def __init__(self):
        """Initialize cleaner with compiled regex patterns."""
        self.emoji_regex = re.compile(EMOJI_PATTERN)
        self.whitespace_regex = re.compile(r'\s+')
        self.url_regex = re.compile(r'https?://\S+')
    
    def clean_article(self, article: Article) -> Article:
        """
        Clean all fields of an article.
        
        Args:
            article: Article object to clean
            
        Returns:
            Cleaned Article object
        """
        try:
            article.title = self.clean_title(article.title)
            article.description = self.clean_description(article.description)
            article.author = self.clean_author(article.author)
            article.source = self.clean_source(article.source)
            article.url = self.clean_url(article.url)
            article.published_date = self.normalize_datetime(article.published_date)
            
            # Validate required fields
            if not self._validate_article(article):
                logger.warning(f"Article validation failed: {article.url}")
                return None
            
            return article
            
        except Exception as e:
            logger.error(f"Error cleaning article: {e}")
            return None
    
    def clean_title(self, title: str) -> str:
        """
        Clean article title.
        
        Args:
            title: Raw title
            
        Returns:
            Cleaned title
        """
        if not title:
            return ""
        
        # Remove HTML entities
        title = self._remove_html_entities(title)
        
        # Remove emojis
        title = self.emoji_regex.sub('', title)
        
        # Normalize whitespace
        title = self.whitespace_regex.sub(' ', title).strip()
        
        # Limit length
        if len(title) > MAX_TITLE_LENGTH:
            title = title[:MAX_TITLE_LENGTH].rstrip()
        
        return title
    
    def clean_description(self, description: str) -> str:
        """
        Clean article description.
        
        Args:
            description: Raw description
            
        Returns:
            Cleaned description
        """
        if not description:
            return ""
        
        # Remove HTML entities
        description = self._remove_html_entities(description)
        
        # Remove emojis
        description = self.emoji_regex.sub('', description)
        
        # Normalize whitespace
        description = self.whitespace_regex.sub(' ', description).strip()
        
        # Limit length
        if len(description) > MAX_DESCRIPTION_LENGTH:
            description = description[:MAX_DESCRIPTION_LENGTH].rstrip()
        
        return description
    
    def clean_author(self, author: str) -> str:
        """
        Clean author name.
        
        Args:
            author: Raw author name
            
        Returns:
            Cleaned author name
        """
        if not author or not author.strip():
            return DEFAULT_AUTHOR
        
        # Remove HTML entities
        author = self._remove_html_entities(author)
        
        # Remove emojis
        author = self.emoji_regex.sub('', author)
        
        # Normalize whitespace
        author = self.whitespace_regex.sub(' ', author).strip()
        
        # Limit length
        if len(author) > MAX_AUTHOR_LENGTH:
            author = author[:MAX_AUTHOR_LENGTH].rstrip()
        
        # Check if still empty after cleaning
        if not author:
            return DEFAULT_AUTHOR
        
        return author
    
    def clean_source(self, source: str) -> str:
        """
        Clean source name.
        
        Args:
            source: Raw source name
            
        Returns:
            Cleaned source name
        """
        if not source:
            return "Unknown"
        
        # Remove HTML entities
        source = self._remove_html_entities(source)
        
        # Normalize whitespace
        source = self.whitespace_regex.sub(' ', source).strip()
        
        return source if source else "Unknown"
    
    def clean_url(self, url: str) -> str:
        """
        Clean and validate URL.
        
        Args:
            url: Raw URL
            
        Returns:
            Cleaned URL
        """
        if not url:
            return ""
        
        url = url.strip()
        
        # Extract URL if text contains multiple URLs
        url_match = self.url_regex.match(url)
        if url_match:
            url = url_match.group(0)
        
        return url
    
    def normalize_datetime(self, dt: Optional[datetime]) -> Optional[datetime]:
        """
        Normalize datetime to UTC format.
        
        Args:
            dt: Datetime object or None
            
        Returns:
            Normalized datetime or None
        """
        if dt is None:
            return None
        
        try:
            # If timezone-aware, convert to UTC and remove timezone info
            if dt.tzinfo is not None:
                dt = dt.replace(tzinfo=None)
            
            return dt
        except Exception as e:
            logger.warning(f"Error normalizing datetime: {e}")
            return None
    
    @staticmethod
    def _remove_html_entities(text: str) -> str:
        """
        Remove HTML entities from text.
        
        Args:
            text: Text containing HTML entities
            
        Returns:
            Text without HTML entities
        """
        html_entity_regex = re.compile(r'&[a-z]+;')
        text = html_entity_regex.sub('', text)
        
        # Handle numeric entities
        text = re.sub(r'&#\d+;', '', text)
        text = re.sub(r'&#x[0-9a-f]+;', '', text)
        
        return text
    
    @staticmethod
    def _validate_article(article: Article) -> bool:
        """
        Validate that article has required fields.
        
        Args:
            article: Article to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Check required fields
        if not article.title or not article.title.strip():
            logger.debug("Article missing title")
            return False
        
        if not article.url or not article.url.strip():
            logger.debug("Article missing URL")
            return False
        
        if not article.source or not article.source.strip():
            logger.debug("Article missing source")
            return False
        
        return True


def clean_articles(articles: list) -> list:
    """
    Convenience function to clean multiple articles.
    
    Args:
        articles: List of Article objects
        
    Returns:
        List of cleaned Article objects
    """
    cleaner = ArticleCleaner()
    cleaned = []
    
    for article in articles:
        cleaned_article = cleaner.clean_article(article)
        if cleaned_article:
            cleaned.append(cleaned_article)
    
    logger.info(f"Cleaned {len(cleaned)} out of {len(articles)} articles")
    return cleaned
