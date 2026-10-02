"""
LinkedIn Job Scraper - Configuration Module
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration loaded from environment variables."""

    # Telegram
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_CHAT_ID: str = os.getenv("TELEGRAM_CHAT_ID", "")

    SEARCH_KEYWORDS: list[str] = [
        kw.strip()
        for kw in os.getenv(
            "SEARCH_KEYWORDS",
            "fresh graduate administration,data entry staff,management trainee,operational staff,junior project coordinator,general affairs staff"
        ).split(",")
    ]
    SEARCH_LOCATION: str = os.getenv("SEARCH_LOCATION", "Indonesia")

    # Scheduling
    SCRAPE_INTERVAL_MINUTES: int = int(os.getenv("SCRAPE_INTERVAL_MINUTES", "60"))

    # Output
    OUTPUT_DIR: str = os.getenv("OUTPUT_DIR", "output")
    OUTPUT_FORMAT: str = os.getenv("OUTPUT_FORMAT", "csv")

    # LinkedIn base URL for job search
    LINKEDIN_JOBS_URL: str = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"

    # Request settings
    REQUEST_TIMEOUT: int = 30
    MAX_RETRIES: int = 3
    DELAY_BETWEEN_REQUESTS: tuple[float, float] = (2.0, 5.0)  # random delay range in seconds
    MAX_PAGES: int = 10  # max pages to scrape per keyword (25 jobs per page)
