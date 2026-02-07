# Market News API Collector

A Python automation pipeline that fetches financial news from an external API, cleans real-world messy data, stores structured records in SQLite, and generates daily CSV reports.

---

## Problem
Teams often manually collect daily financial news and prepare reports.
This process is repetitive, slow, and error-prone.

## Solution
This project automates the workflow:

Fetch news from API → clean unreliable data → store structured records → generate daily report

---

## Why I Built This
To simulate a real internal company tool where recurring data collection is automated.
The focus was reliability — even if the API returns missing or inconsistent data, the pipeline continues without failure.

---

## What This Demonstrates
- External API integration using Python
- Handling incomplete / unreliable JSON data
- Automated data ingestion pipeline
- Database storage with duplicate prevention
- Reliable execution using logging and retry handling

---


## Architecture

```
NewsAPI.org
    ↓
[API Integration] (fetch_news.py)
    ↓ JSON articles
[Data Cleaning] (cleaner.py)
    ↓ cleaned articles
[SQLite Storage] (db.py)
    ↓ persist to database
[Report Generation] (generate_report.py)
    ↓ CSV file
[Logging] (logger.py)
    ↓ execution records
```

## Tech Stack

- **Language:** Python 3.7+
- **API Client:** requests (HTTP library)
- **Database:** SQLite3
- **Configuration:** python-dotenv (environment variables)
- **Logging:** Python logging module
- **CSV:** Python csv module (built-in)

## Folder Structure

```
market_news_collector/
│
├── main.py                    # Entry point - orchestrates workflow
├── config.py                  # Configuration & constants
├── logger.py                  # Logging setup with rotation
│
├── api/
│   └── fetch_news.py          # NewsAPI integration with retry logic
│
├── processing/
│   └── cleaner.py             # Data cleaning & validation module
│
├── database/
│   ├── db.py                  # SQLite operations
│   └── models.py              # Article data model
│
├── reports/
│   └── generate_report.py     # CSV report generation
│
├── data/
│   ├── news.db                # SQLite database (auto-created)
│   └── reports/               # Generated CSV files
│
├── logs/
│   └── collector.log          # Application logs (rotating)
│
├── requirements.txt           # Python dependencies
├── .env.example               # Environment template
└── README.md                  # This file
```

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/market-news-collector.git
cd market_news_collector
```

### 2. Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Get API Key

1. Visit [NewsAPI.org](https://newsapi.org)
2. Sign up for a free account
3. Copy your API key

### 5. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` and add your API key:
```
NEWS_API_KEY=your_api_key_here
SEARCH_QUERY=market OR finance OR business
LOG_LEVEL=INFO
```

## Running the Project

### Normal Execution

```bash
python main.py
```

Fetches articles, cleans data, stores in database, generates report.

### Test Mode (Dry Run)

```bash
python main.py --dry-run
```

Tests entire pipeline without saving to database or file. Perfect for debugging.

### Help

```bash
python main.py --help
```


## Example Output

### Console Output

```
============================================================
Market News Collector - Starting Execution
============================================================
Step 1: Fetching articles from NewsAPI...
Fetched 45 articles
Step 2: Cleaning and validating articles...
Cleaned 42 articles
Step 3: Storing articles in database...
Inserted 38 articles, skipped 4 duplicates
Step 4: Cleaning up old articles...
Step 5: Generating report...
Report generated: data/reports/news_2024_12_15.csv

============================================================
EXECUTION SUMMARY
============================================================
Status: completed
Articles Fetched: 45
Articles Cleaned: 42
Articles Inserted: 38
Articles Skipped (Duplicates): 4
Report File: data/reports/news_2024_12_15.csv
============================================================
```

### Database Output (news.db)

SQLite database with automatic schema. Articles deduplicated by unique URL constraint.

### Report Output (news_2024_12_15.csv)

```csv
id,title,source,author,published_date,description,url,fetched_at
1,Apple Stock Rises,Reuters,John Doe,2024-12-15T10:30:00,Apple shares surge...,https://...,2024-12-15T09:45:00
2,Market Analysis,Bloomberg,Jane Smith,2024-12-15T09:15:00,Markets show signs...,https://...,2024-12-15T09:45:00
```

