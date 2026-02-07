"""
Main orchestration script for Market News Collector.
Coordinates the entire workflow: fetch, clean, store, and report.
"""

import sys
from datetime import datetime
from typing import Tuple

from logger import logger
from config import DRY_RUN, DATA_RETENTION_DAYS
from api.fetch_news import fetch_news
from processing.cleaner import clean_articles
from database.db import NewsDatabase
from reports.generate_report import ReportGenerator


def main(dry_run: bool = DRY_RUN) -> Tuple[bool, dict]:
    """
    Main execution flow for news collection and processing.
    
    Args:
        dry_run: If True, don't save to database or generate report
        
    Returns:
        Tuple of (success_bool, summary_dict)
    """
    start_time = datetime.utcnow()
    summary = {
        'start_time': start_time.isoformat(),
        'status': 'running',
        'articles_fetched': 0,
        'articles_cleaned': 0,
        'articles_inserted': 0,
        'articles_skipped': 0,
        'report_file': None,
        'errors': []
    }
    
    try:
        logger.info("=" * 60)
        logger.info("Market News Collector - Starting Execution")
        logger.info("=" * 60)
        
        if dry_run:
            logger.warning("DRY RUN MODE - No data will be saved")
        
        # Step 1: Fetch articles
        logger.info("Step 1: Fetching articles from NewsAPI...")
        articles = fetch_articles()
        summary['articles_fetched'] = len(articles)
        logger.info(f"Fetched {len(articles)} articles")
        
        if not articles:
            logger.warning("No articles fetched")
            summary['status'] = 'completed_with_warnings'
            return False, summary
        
        # Step 2: Clean articles
        logger.info("Step 2: Cleaning and validating articles...")
        cleaned_articles = clean_articles(articles)
        summary['articles_cleaned'] = len(cleaned_articles)
        logger.info(f"Cleaned {len(cleaned_articles)} articles")
        
        if not cleaned_articles:
            logger.error("No articles after cleaning")
            summary['status'] = 'failed'
            summary['errors'].append("No articles after cleaning")
            return False, summary
        
        # Step 3: Store to database
        if not dry_run:
            logger.info("Step 3: Storing articles in database...")
            inserted, skipped = store_articles(cleaned_articles)
            summary['articles_inserted'] = inserted
            summary['articles_skipped'] = skipped
            logger.info(f"Inserted {inserted} articles, skipped {skipped} duplicates")
            
            # Step 4: Cleanup old articles
            logger.info("Step 4: Cleaning up old articles...")
            cleanup_old_articles(DATA_RETENTION_DAYS)
        else:
            logger.info("Step 3: [DRY RUN] Database storage skipped")
            summary['articles_inserted'] = len(cleaned_articles)
        
        # Step 5: Generate report
        logger.info("Step 5: Generating report...")
        if dry_run:
            logger.info("[DRY RUN] Report generation skipped")
        else:
            report_path = generate_report_file(cleaned_articles)
            if report_path:
                summary['report_file'] = str(report_path)
                logger.info(f"Report generated: {report_path}")
        
        # Calculate execution time
        end_time = datetime.utcnow()
        execution_time = (end_time - start_time).total_seconds()
        
        summary['end_time'] = end_time.isoformat()
        summary['execution_time_seconds'] = execution_time
        summary['status'] = 'completed'
        
        # Print summary
        print_execution_summary(summary)
        
        logger.info("=" * 60)
        logger.info("Market News Collector - Execution Completed Successfully")
        logger.info("=" * 60)
        
        return True, summary
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        summary['status'] = 'failed'
        summary['errors'].append(str(e))
        return False, summary


def fetch_articles(query: str = None, days_back: int = 7):
    """
    Fetch articles from NewsAPI.
    
    Args:
        query: Search query (uses default if None)
        days_back: Number of days back to fetch
        
    Returns:
        List of Article objects
    """
    try:
        if query:
            articles = fetch_news(query=query, days_back=days_back)
        else:
            articles = fetch_news(days_back=days_back)
        
        return articles
    except Exception as e:
        logger.error(f"Error fetching articles: {e}")
        return []


def store_articles(articles) -> Tuple[int, int]:
    """
    Store cleaned articles in database.
    
    Args:
        articles: List of cleaned Article objects
        
    Returns:
        Tuple of (inserted_count, skipped_count)
    """
    db = None
    try:
        db = NewsDatabase()
        inserted, skipped = db.insert_articles_bulk(articles)
        return inserted, skipped
    except Exception as e:
        logger.error(f"Error storing articles: {e}")
        return 0, len(articles)
    finally:
        if db:
            db.close()


def cleanup_old_articles(days: int) -> int:
    """
    Delete articles older than specified number of days.
    
    Args:
        days: Number of days to retain
        
    Returns:
        Number of deleted articles
    """
    db = None
    try:
        db = NewsDatabase()
        deleted = db.delete_old_articles(days)
        return deleted
    except Exception as e:
        logger.error(f"Error cleaning up old articles: {e}")
        return 0
    finally:
        if db:
            db.close()


def generate_report_file(articles) -> str:
    """
    Generate CSV report from articles.
    
    Args:
        articles: List of Article objects
        
    Returns:
        Path to report file or None
    """
    try:
        generator = ReportGenerator()
        report_path = generator.generate_daily_report(articles)
        
        # Get summary statistics
        summary = generator.get_report_summary(report_path)
        if summary:
            logger.info(f"Report summary: {summary['article_count']} articles, "
                       f"{summary['unique_sources']} sources, "
                       f"{summary['unique_authors']} authors")
        
        return report_path
    except Exception as e:
        logger.error(f"Error generating report: {e}")
        return None


def print_execution_summary(summary: dict) -> None:
    """
    Print execution summary to console.
    
    Args:
        summary: Execution summary dictionary
    """
    print("\n" + "=" * 60)
    print("EXECUTION SUMMARY")
    print("=" * 60)
    
    print(f"Status: {summary['status'].upper()}")
    print(f"Start Time: {summary['start_time']}")
    print(f"End Time: {summary.get('end_time', 'N/A')}")
    print(f"Duration: {summary.get('execution_time_seconds', 'N/A')} seconds")
    print()
    print(f"Articles Fetched: {summary['articles_fetched']}")
    print(f"Articles Cleaned: {summary['articles_cleaned']}")
    print(f"Articles Inserted: {summary['articles_inserted']}")
    print(f"Articles Skipped (Duplicates): {summary['articles_skipped']}")
    
    if summary['report_file']:
        print(f"Report File: {summary['report_file']}")
    
    if summary['errors']:
        print(f"\nErrors ({len(summary['errors'])}):")
        for error in summary['errors']:
            print(f"  - {error}")
    
    print("=" * 60 + "\n")


if __name__ == "__main__":
    """
    Entry point for the application.
    Can be run as:
        python main.py              # Normal execution
        python main.py --dry-run    # Dry run (no DB/report save)
        python main.py --help       # Show help
    """
    dry_run = False
    
    if len(sys.argv) > 1:
        if '--dry-run' in sys.argv:
            dry_run = True
            logger.info("Dry run mode enabled via command line argument")
        elif '--help' in sys.argv or '-h' in sys.argv:
            print(__doc__)
            print("\nUsage:")
            print("  python main.py              # Normal execution")
            print("  python main.py --dry-run    # Test without saving data")
            print("  python main.py --help       # Show this help message")
            sys.exit(0)
    
    success, summary = main(dry_run=dry_run)
    sys.exit(0 if success else 1)
