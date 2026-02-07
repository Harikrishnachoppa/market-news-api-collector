"""
Database module for Market News Collector.
Handles SQLite database operations and schema management.
"""

import sqlite3
from datetime import datetime
from typing import List, Optional, Tuple
from pathlib import Path
from logger import logger
from config import DATABASE_PATH
from database.models import Article


class NewsDatabase:
    """
    SQLite database manager for storing and retrieving news articles.
    Provides methods for initialization, insertion, and querying.
    """
    
    def __init__(self, db_path: Path = DATABASE_PATH):
        """
        Initialize database connection.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.connection = None
        self.cursor = None
        self._initialize_db()
    
    def _initialize_db(self) -> None:
        """Initialize database connection and create tables if not exist."""
        try:
            self.connection = sqlite3.connect(str(self.db_path))
            self.connection.row_factory = sqlite3.Row
            self.cursor = self.connection.cursor()
            self._create_tables()
            logger.info(f"Database initialized at {self.db_path}")
        except sqlite3.Error as e:
            logger.error(f"Database initialization error: {e}")
            raise
    
    def _create_tables(self) -> None:
        """Create necessary tables if they don't exist."""
        try:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS articles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    source TEXT NOT NULL,
                    author TEXT NOT NULL DEFAULT 'Unknown',
                    published_date TIMESTAMP,
                    description TEXT,
                    url TEXT NOT NULL UNIQUE,
                    fetched_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create index on URL for faster lookups
            self.cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_articles_url ON articles(url)
            """)
            
            # Create index on source for filtering
            self.cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_articles_source ON articles(source)
            """)
            
            # Create index on published_date for time-based queries
            self.cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_articles_published_date ON articles(published_date)
            """)
            
            self.connection.commit()
            logger.debug("Database tables created/verified")
        except sqlite3.Error as e:
            logger.error(f"Error creating tables: {e}")
            raise
    
    def insert_article(self, article: Article) -> int:
        """
        Insert a single article into the database.
        
        Args:
            article: Article object to insert
            
        Returns:
            ID of inserted article, or -1 if duplicate
        """
        try:
            article.fetched_at = article.fetched_at or datetime.utcnow()
            
            self.cursor.execute("""
                INSERT INTO articles 
                (title, source, author, published_date, description, url, fetched_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                article.title,
                article.source,
                article.author,
                article.published_date,
                article.description,
                article.url,
                article.fetched_at
            ))
            
            self.connection.commit()
            article_id = self.cursor.lastrowid
            logger.debug(f"Inserted article: {article.title[:50]}... (ID: {article_id})")
            return article_id
            
        except sqlite3.IntegrityError as e:
            if 'UNIQUE constraint failed' in str(e):
                logger.debug(f"Duplicate article skipped: {article.url}")
                return -1
            else:
                logger.error(f"Integrity error: {e}")
                raise
        except sqlite3.Error as e:
            logger.error(f"Error inserting article: {e}")
            raise
    
    def insert_articles_bulk(self, articles: List[Article]) -> Tuple[int, int]:
        """
        Insert multiple articles into the database.
        
        Args:
            articles: List of Article objects
            
        Returns:
            Tuple of (inserted_count, skipped_count)
        """
        inserted_count = 0
        skipped_count = 0
        
        for article in articles:
            try:
                article_id = self.insert_article(article)
                if article_id > 0:
                    inserted_count += 1
                else:
                    skipped_count += 1
            except Exception as e:
                logger.warning(f"Error inserting article {article.url}: {e}")
                skipped_count += 1
        
        return inserted_count, skipped_count
    
    def get_article_by_url(self, url: str) -> Optional[Article]:
        """
        Retrieve an article by URL.
        
        Args:
            url: Article URL
            
        Returns:
            Article object or None if not found
        """
        try:
            self.cursor.execute(
                "SELECT * FROM articles WHERE url = ?",
                (url,)
            )
            row = self.cursor.fetchone()
            
            if row:
                return self._row_to_article(row)
            return None
        except sqlite3.Error as e:
            logger.error(f"Error retrieving article by URL: {e}")
            raise
    
    def get_all_articles(self, limit: Optional[int] = None) -> List[Article]:
        """
        Retrieve all articles from database.
        
        Args:
            limit: Maximum number of articles to retrieve
            
        Returns:
            List of Article objects
        """
        try:
            query = "SELECT * FROM articles ORDER BY published_date DESC"
            if limit:
                query += f" LIMIT {limit}"
            
            self.cursor.execute(query)
            rows = self.cursor.fetchall()
            
            return [self._row_to_article(row) for row in rows]
        except sqlite3.Error as e:
            logger.error(f"Error retrieving articles: {e}")
            raise
    
    def get_articles_by_source(self, source: str) -> List[Article]:
        """
        Retrieve articles from a specific source.
        
        Args:
            source: Source name
            
        Returns:
            List of Article objects
        """
        try:
            self.cursor.execute(
                "SELECT * FROM articles WHERE source = ? ORDER BY published_date DESC",
                (source,)
            )
            rows = self.cursor.fetchall()
            
            return [self._row_to_article(row) for row in rows]
        except sqlite3.Error as e:
            logger.error(f"Error retrieving articles by source: {e}")
            raise
    
    def get_article_count(self) -> int:
        """
        Get total count of articles in database.
        
        Returns:
            Number of articles
        """
        try:
            self.cursor.execute("SELECT COUNT(*) FROM articles")
            return self.cursor.fetchone()[0]
        except sqlite3.Error as e:
            logger.error(f"Error counting articles: {e}")
            raise
    
    def delete_old_articles(self, days: int) -> int:
        """
        Delete articles older than specified number of days.
        
        Args:
            days: Number of days to retain
            
        Returns:
            Number of articles deleted
        """
        try:
            self.cursor.execute("""
                DELETE FROM articles 
                WHERE published_date < datetime('now', ? || ' days')
            """, (f'-{days}',))
            
            self.connection.commit()
            deleted_count = self.cursor.rowcount
            logger.info(f"Deleted {deleted_count} articles older than {days} days")
            
            return deleted_count
        except sqlite3.Error as e:
            logger.error(f"Error deleting old articles: {e}")
            raise
    
    def article_exists(self, url: str) -> bool:
        """
        Check if article already exists in database.
        
        Args:
            url: Article URL
            
        Returns:
            True if article exists, False otherwise
        """
        try:
            self.cursor.execute(
                "SELECT 1 FROM articles WHERE url = ? LIMIT 1",
                (url,)
            )
            return self.cursor.fetchone() is not None
        except sqlite3.Error as e:
            logger.error(f"Error checking article existence: {e}")
            raise
    
    @staticmethod
    def _row_to_article(row: sqlite3.Row) -> Article:
        """
        Convert database row to Article object.
        
        Args:
            row: SQLite row object
            
        Returns:
            Article object
        """
        return Article(
            id=row['id'],
            title=row['title'],
            source=row['source'],
            author=row['author'],
            published_date=row['published_date'],
            description=row['description'],
            url=row['url'],
            fetched_at=row['fetched_at']
        )
    
    def close(self) -> None:
        """Close database connection."""
        if self.connection:
            self.connection.close()
            logger.debug("Database connection closed")
    
    def __del__(self):
        """Cleanup on object deletion."""
        self.close()
