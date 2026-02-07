"""
Configuration module for Market News Collector.
Loads settings from environment variables and defines application constants.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    load_dotenv(env_path)

# Base paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
REPORTS_DIR = DATA_DIR / "reports"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)
REPORTS_DIR.mkdir(exist_ok=True)

# API Configuration
NEWS_API_KEY = os.getenv("NEWS_API_KEY", "demo")
NEWS_API_BASE_URL = "https://newsapi.org/v2"
NEWS_API_ENDPOINT = f"{NEWS_API_BASE_URL}/everything"

# Search parameters
SEARCH_QUERY = os.getenv("SEARCH_QUERY", "market OR finance OR business")
SORT_BY = "publishedAt"
PAGE_SIZE = 100
LANGUAGE = "en"

# API Request Configuration
REQUEST_TIMEOUT = 15  # seconds
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds

# Database Configuration
DATABASE_PATH = DATA_DIR / "news.db"
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# Logging Configuration
LOG_FILE = LOGS_DIR / "collector.log"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_MAX_BYTES = 10 * 1024 * 1024  # 10 MB
LOG_BACKUP_COUNT = 5

# Report Configuration
REPORT_DATE_FORMAT = "%Y_%m_%d"
REPORT_FILE_PREFIX = "news"

# Data Cleaning Configuration
EMOJI_PATTERN = r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\U00002702-\U000027B0\U000024C2-\U0001F251]+'
MAX_TITLE_LENGTH = 500
MAX_AUTHOR_LENGTH = 200
MAX_DESCRIPTION_LENGTH = 5000
DEFAULT_AUTHOR = "Unknown"

# Data retention (days)
DATA_RETENTION_DAYS = 90

# Execution
DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() == "true"
DRY_RUN = os.getenv("DRY_RUN", "False").lower() == "true"
