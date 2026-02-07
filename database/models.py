"""
Database models for storing news articles.
Defines the Article data structure and SQLAlchemy ORM models.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Article:
    """
    Data class representing a news article.
    
    Attributes:
        id: Auto-generated primary key
        title: Article title (cleaned)
        source: News source name
        author: Article author
        published_date: Publication date
        description: Article description/summary
        url: Article URL
        fetched_at: Timestamp when article was fetched
    """
    id: Optional[int] = None
    title: str = ""
    source: str = ""
    author: str = "Unknown"
    published_date: Optional[datetime] = None
    description: str = ""
    url: str = ""
    fetched_at: Optional[datetime] = None
    
    def to_dict(self) -> dict:
        """Convert article to dictionary."""
        return {
            'id': self.id,
            'title': self.title,
            'source': self.source,
            'author': self.author,
            'published_date': self.published_date,
            'description': self.description,
            'url': self.url,
            'fetched_at': self.fetched_at
        }
    
    def __repr__(self) -> str:
        """String representation."""
        return f"Article(title='{self.title[:50]}...', source='{self.source}', url='{self.url}')"
