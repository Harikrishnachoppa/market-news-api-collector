"""
Report generation module.
Creates CSV reports from collected news articles.
"""

import csv
from datetime import datetime
from pathlib import Path
from typing import List

from logger import logger
from config import REPORTS_DIR, REPORT_DATE_FORMAT, REPORT_FILE_PREFIX
from database.models import Article


class ReportGenerator:
    """
    Generate CSV reports from news articles.
    Creates timestamped report files with article data.
    """
    
    def __init__(self, reports_dir: Path = REPORTS_DIR):
        """
        Initialize report generator.
        
        Args:
            reports_dir: Directory to store report files
        """
        self.reports_dir = reports_dir
        self.reports_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_daily_report(self, articles: List[Article], report_date: datetime = None) -> Path:
        """
        Generate daily CSV report for articles.
        
        Args:
            articles: List of Article objects
            report_date: Date for report (defaults to today)
            
        Returns:
            Path to generated report file
        """
        try:
            if report_date is None:
                report_date = datetime.utcnow()
            
            # Generate filename
            date_str = report_date.strftime(REPORT_DATE_FORMAT)
            filename = f"{REPORT_FILE_PREFIX}_{date_str}.csv"
            filepath = self.reports_dir / filename
            
            logger.info(f"Generating report: {filename}")
            
            # Write CSV file
            self._write_csv_file(filepath, articles)
            
            logger.info(f"Report generated successfully: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error generating report: {e}")
            raise
    
    def _write_csv_file(self, filepath: Path, articles: List[Article]) -> None:
        """
        Write articles to CSV file.
        
        Args:
            filepath: Path to output CSV file
            articles: List of Article objects
        """
        try:
            # Define CSV columns
            fieldnames = [
                'id',
                'title',
                'source',
                'author',
                'published_date',
                'description',
                'url',
                'fetched_at'
            ]
            
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                # Write header
                writer.writeheader()
                
                # Write article rows
                for article in articles:
                    try:
                        row = self._article_to_csv_row(article)
                        writer.writerow(row)
                    except Exception as e:
                        logger.warning(f"Error writing article to CSV: {e}")
                        continue
            
            logger.debug(f"Wrote {len(articles)} articles to {filepath}")
            
        except IOError as e:
            logger.error(f"IO error writing CSV file: {e}")
            raise
    
    @staticmethod
    def _article_to_csv_row(article: Article) -> dict:
        """
        Convert Article object to CSV row dictionary.
        
        Args:
            article: Article object
            
        Returns:
            Dictionary representation of article
        """
        return {
            'id': article.id or '',
            'title': article.title or '',
            'source': article.source or '',
            'author': article.author or '',
            'published_date': article.published_date.isoformat() if article.published_date else '',
            'description': article.description or '',
            'url': article.url or '',
            'fetched_at': article.fetched_at.isoformat() if article.fetched_at else ''
        }
    
    def get_latest_report(self) -> Path:
        """
        Get path to the latest report file.
        
        Returns:
            Path to latest report or None if no reports exist
        """
        try:
            report_files = list(self.reports_dir.glob(f"{REPORT_FILE_PREFIX}_*.csv"))
            
            if not report_files:
                logger.debug("No reports found")
                return None
            
            # Sort by filename and get latest
            latest = sorted(report_files)[-1]
            logger.debug(f"Latest report: {latest.name}")
            
            return latest
            
        except Exception as e:
            logger.error(f"Error getting latest report: {e}")
            return None
    
    def get_report_summary(self, filepath: Path) -> dict:
        """
        Get summary statistics from a report file.
        
        Args:
            filepath: Path to report CSV file
            
        Returns:
            Dictionary with summary statistics
        """
        try:
            if not filepath.exists():
                logger.warning(f"Report file not found: {filepath}")
                return {}
            
            article_count = 0
            sources = set()
            authors = set()
            
            with open(filepath, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                
                for row in reader:
                    article_count += 1
                    if row.get('source'):
                        sources.add(row['source'])
                    if row.get('author'):
                        authors.add(row['author'])
            
            summary = {
                'file': filepath.name,
                'article_count': article_count,
                'unique_sources': len(sources),
                'unique_authors': len(authors),
                'sources': list(sources),
                'file_size_bytes': filepath.stat().st_size
            }
            
            logger.info(f"Report summary: {article_count} articles from {len(sources)} sources")
            
            return summary
            
        except Exception as e:
            logger.error(f"Error reading report summary: {e}")
            return {}


def generate_report(articles: List[Article]) -> Path:
    """
    Convenience function to generate a daily report.
    
    Args:
        articles: List of Article objects
        
    Returns:
        Path to generated report file
    """
    generator = ReportGenerator()
    return generator.generate_daily_report(articles)
