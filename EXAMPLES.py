"""
EXAMPLE USAGE - Market News API Collector

This file shows how to use the Market News Collector in different scenarios.
"""

# ============================================================================
# EXAMPLE 1: Basic Usage - Run the entire pipeline
# ============================================================================

from main import main

# Run the complete workflow
success, summary = main()

print(f"Status: {summary['status']}")
print(f"Articles fetched: {summary['articles_fetched']}")
print(f"Articles inserted: {summary['articles_inserted']}")
print(f"Report file: {summary['report_file']}")


# ============================================================================
# EXAMPLE 2: Just fetch articles
# ============================================================================

from api.fetch_news import fetch_news

# Fetch articles
articles = fetch_news(
    query="technology stocks",
    days_back=7
)

print(f"Fetched {len(articles)} articles")
for article in articles[:3]:
    print(f"- {article.title} ({article.source})")


# ============================================================================
# EXAMPLE 3: Clean and validate data
# ============================================================================

from processing.cleaner import clean_articles

# Assuming you have articles from fetch_news()
cleaned = clean_articles(articles)

print(f"Cleaned {len(cleaned)} out of {len(articles)} articles")
for article in cleaned[:3]:
    print(f"✓ {article.title}")


# ============================================================================
# EXAMPLE 4: Database operations
# ============================================================================

from database.db import NewsDatabase
from database.models import Article

db = NewsDatabase()

# Insert a single article
article = Article(
    title="Apple stock rises 5%",
    source="Reuters",
    author="John Doe",
    description="Apple shares surge on strong earnings...",
    url="https://example.com/article123"
)
article_id = db.insert_article(article)
print(f"Inserted article with ID: {article_id}")

# Get all articles
all_articles = db.get_all_articles(limit=10)
print(f"Total articles in database: {db.get_article_count()}")

# Get articles from specific source
reuters_articles = db.get_articles_by_source("Reuters")
print(f"Reuters articles: {len(reuters_articles)}")

# Check if article exists
exists = db.article_exists("https://example.com/article123")
print(f"Article exists: {exists}")

# Delete old articles
deleted = db.delete_old_articles(days=90)
print(f"Deleted {deleted} articles older than 90 days")

db.close()


# ============================================================================
# EXAMPLE 5: Generate reports
# ============================================================================

from reports.generate_report import ReportGenerator

generator = ReportGenerator()

# Generate daily report
report_path = generator.generate_daily_report(articles)
print(f"Report saved to: {report_path}")

# Get report summary
summary = generator.get_report_summary(report_path)
print(f"Articles in report: {summary['article_count']}")
print(f"Unique sources: {summary['unique_sources']}")
print(f"Unique authors: {summary['unique_authors']}")


# ============================================================================
# EXAMPLE 6: Scheduled execution
# ============================================================================

# For scheduling, run from command line:
#
# Linux/macOS Cron:
#    0 * * * * cd /path/to/market_news_collector && python main.py
#
# Windows Task Scheduler:
#    Program: C:\path\to\venv\Scripts\python.exe
#    Arguments: C:\path\to\market_news_collector\main.py


# ============================================================================
# EXAMPLE 7: Dry run (testing)
# ============================================================================

# Run in dry-run mode (doesn't save to database or generate reports):
from main import main

success, summary = main(dry_run=True)
print("Dry run completed - no data was saved")


# ============================================================================
# EXAMPLE 8: Custom search query
# ============================================================================

from api.fetch_news import fetch_news
from processing.cleaner import clean_articles
from database.db import NewsDatabase

# Fetch articles with custom query
articles = fetch_news(query="electric vehicles market", days_back=30)

# Clean them
cleaned = clean_articles(articles)

# Store in database
db = NewsDatabase()
inserted, skipped = db.insert_articles_bulk(cleaned)
print(f"Inserted: {inserted}, Skipped (duplicates): {skipped}")
db.close()


# ============================================================================
# EXAMPLE 9: Error handling
# ============================================================================

from api.fetch_news import NewsAPIFetcher

try:
    fetcher = NewsAPIFetcher()
    articles = fetcher.fetch_articles()
    print(f"Successfully fetched {len(articles)} articles")
except Exception as e:
    print(f"Error: {e}")
finally:
    fetcher.close()


# ============================================================================
# EXAMPLE 10: Check logs
# ============================================================================

# View application logs:
#
# Linux/macOS:
#    tail -f logs/collector.log
#    tail -20 logs/collector.log
#
# Windows PowerShell:
#    Get-Content logs\collector.log -Tail 20
#    Get-Content logs\collector.log -Tail 20 -Wait

# Or in Python:
with open('logs/collector.log', 'r') as f:
    last_lines = f.readlines()[-20:]
    for line in last_lines:
        print(line.rstrip())


# ============================================================================
# EXAMPLE 11: Query database by source
# ============================================================================

from database.db import NewsDatabase

db = NewsDatabase()

# Get articles from specific sources
sources = ["BBC News", "Reuters", "Bloomberg"]

for source in sources:
    articles = db.get_articles_by_source(source)
    print(f"{source}: {len(articles)} articles")

db.close()


# ============================================================================
# EXAMPLE 12: Bulk insert with duplicate handling
# ============================================================================

from database.db import NewsDatabase
from database.models import Article

articles = [
    Article(
        title="Market news 1",
        source="Reuters",
        description="News about markets",
        url="https://example.com/article1"
    ),
    Article(
        title="Market news 2",
        source="Bloomberg",
        description="Another news",
        url="https://example.com/article2"
    ),
]

db = NewsDatabase()
inserted, skipped = db.insert_articles_bulk(articles)

print(f"Results: {inserted} inserted, {skipped} duplicates skipped")

db.close()


# ============================================================================
# EXAMPLE 13: Custom logging
# ============================================================================

from logger import logger

logger.info("Application started")
logger.warning("This is a warning")
logger.error("This is an error")
logger.debug("Debug information")


# ============================================================================
# EXAMPLE 14: Data cleaning examples
# ============================================================================

from processing.cleaner import ArticleCleaner

cleaner = ArticleCleaner()

# Clean various fields
title = "🎉 Amazing News!!! with   excessive   spaces"
cleaned_title = cleaner.clean_title(title)
print(f"Original: {title}")
print(f"Cleaned: {cleaned_title}")

# Clean author
author = "   John Doe 👨‍💻   "
cleaned_author = cleaner.clean_author(author)
print(f"Original author: '{author}'")
print(f"Cleaned author: '{cleaned_author}'")

# Handle missing author
empty_author = cleaner.clean_author("")
print(f"Empty author becomes: '{empty_author}'")


# ============================================================================
# EXAMPLE 15: Get execution summary
# ============================================================================

from main import main

success, summary = main()

print(f"""
Execution Report:
================
Status: {summary['status']}
Duration: {summary.get('execution_time_seconds', 0):.2f} seconds
Fetched: {summary['articles_fetched']} articles
Cleaned: {summary['articles_cleaned']} articles
Inserted: {summary['articles_inserted']} articles
Duplicates: {summary['articles_skipped']} articles
Report: {summary['report_file']}
""")


# ============================================================================
# NOTES
# ============================================================================

"""
Configuration:
- API key: Set in .env file (get from https://newsapi.org)
- Search query: Modify SEARCH_QUERY in .env or config.py
- Log level: Set LOG_LEVEL in .env (DEBUG, INFO, WARNING, ERROR)
- Timeout: Modify REQUEST_TIMEOUT in config.py
- Retries: Modify MAX_RETRIES in config.py

Database:
- Auto-created in data/news.db on first run
- SQLite format
- Duplicate prevention via UNIQUE constraint on URL
- Indexes on: URL, source, published_date

Reports:
- Generated in data/reports/
- Filename format: news_YYYY_MM_DD.csv
- UTF-8 encoding

Logs:
- Located in logs/collector.log
- Rotates at 10 MB
- Keeps 5 backup files

Scheduling:
- Use cron (Linux/macOS) or Task Scheduler (Windows)
- Run `python main.py` from project directory
- Use absolute paths in scheduled tasks
"""
