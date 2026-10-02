"""
LinkedIn Job Scraper - Core Scraper Module
Scrapes LinkedIn public job listings without requiring authentication.
"""

import logging
import random
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime
from urllib.parse import urlencode

import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

from config import Config

logger = logging.getLogger(__name__)


@dataclass
class JobListing:
    """Represents a single job listing."""
    title: str = ""
    company: str = ""
    location: str = ""
    date_posted: str = ""
    job_url: str = ""
    description_snippet: str = ""
    keyword_used: str = ""
    scraped_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return asdict(self)

    def summary(self) -> str:
        """Return a short summary for Telegram notification."""
        return (
            f"💼 *{self.title}*\n"
            f"🏢 {self.company}\n"
            f"📍 {self.location}\n"
            f"📅 {self.date_posted}\n"
            f"🔗 [Lihat Lowongan]({self.job_url})"
        )


class LinkedInScraper:
    """Scrapes LinkedIn public job listings."""

    def __init__(self, config: Config | None = None):
        self.config = config or Config()
        self.session = requests.Session()
        self._ua = UserAgent(fallback="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        self._seen_urls: set[str] = set()

    def _get_headers(self) -> dict[str, str]:
        """Generate realistic browser headers."""
        return {
            "User-Agent": self._ua.random,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9,id;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
        }

    def _random_delay(self) -> None:
        """Add random delay between requests to avoid rate limiting."""
        delay = random.uniform(*self.config.DELAY_BETWEEN_REQUESTS)
        logger.debug(f"Waiting {delay:.1f}s before next request...")
        time.sleep(delay)

    def _build_search_url(self, keyword: str, start: int = 0) -> str:
        """Build LinkedIn job search URL."""
        params = {
            "keywords": keyword,
            "location": self.config.SEARCH_LOCATION,
            "start": start,
            "f_TPR": "r86400",   # last 24 hours
            "position": 1,
            "pageNum": 0,
        }
        return f"{self.config.LINKEDIN_JOBS_URL}?{urlencode(params)}"

    def _parse_job_card(self, card: BeautifulSoup, keyword: str) -> JobListing | None:
        """Parse a single job card HTML element into a JobListing."""
        try:
            # Title
            title_el = card.find("h3", class_="base-search-card__title")
            title = title_el.get_text(strip=True) if title_el else ""

            # Company
            company_el = card.find("h4", class_="base-search-card__subtitle")
            company = company_el.get_text(strip=True) if company_el else ""

            # Location
            location_el = card.find("span", class_="job-search-card__location")
            location = location_el.get_text(strip=True) if location_el else ""

            # Date posted
            date_el = card.find("time", class_="job-search-card__listdate")
            if not date_el:
                date_el = card.find("time", class_="job-search-card__listdate--new")
            date_posted = date_el.get_text(strip=True) if date_el else ""

            # URL
            link_el = card.find("a", class_="base-card__full-link")
            job_url = ""
            if link_el and link_el.get("href"):
                job_url = link_el["href"].split("?")[0]  # remove tracking params

            # Skip if we've already seen this URL
            if job_url in self._seen_urls:
                return None
            self._seen_urls.add(job_url)

            # Description snippet
            snippet_el = card.find("p", class_="job-search-card__snippet")
            description_snippet = snippet_el.get_text(strip=True) if snippet_el else ""

            if not title:
                return None

            return JobListing(
                title=title,
                company=company,
                location=location,
                date_posted=date_posted,
                job_url=job_url,
                description_snippet=description_snippet,
                keyword_used=keyword,
            )
        except Exception as e:
            logger.warning(f"Failed to parse job card: {e}")
            return None

    def scrape_keyword(self, keyword: str) -> list[JobListing]:
        """Scrape all available job listings for a single keyword."""
        logger.info(f"🔍 Scraping jobs for keyword: '{keyword}' in '{self.config.SEARCH_LOCATION}'")
        jobs: list[JobListing] = []

        for page in range(self.config.MAX_PAGES):
            start = page * 25
            url = self._build_search_url(keyword, start)
            logger.debug(f"  Page {page + 1}: {url}")

            for attempt in range(self.config.MAX_RETRIES):
                try:
                    response = self.session.get(
                        url,
                        headers=self._get_headers(),
                        timeout=self.config.REQUEST_TIMEOUT,
                    )

                    if response.status_code == 429:
                        wait = (attempt + 1) * 30
                        logger.warning(f"Rate limited! Waiting {wait}s...")
                        time.sleep(wait)
                        continue

                    if response.status_code != 200:
                        logger.warning(f"Got status {response.status_code} for page {page + 1}")
                        break

                    soup = BeautifulSoup(response.text, "html.parser")
                    cards = soup.find_all("div", class_="base-card")

                    if not cards:
                        logger.info(f"  No more results at page {page + 1}")
                        return jobs  # no more pages

                    for card in cards:
                        job = self._parse_job_card(card, keyword)
                        if job:
                            jobs.append(job)

                    logger.info(f"  Page {page + 1}: found {len(cards)} cards, total jobs: {len(jobs)}")
                    self._random_delay()
                    break  # success, go to next page

                except requests.RequestException as e:
                    logger.warning(f"Request error (attempt {attempt + 1}): {e}")
                    if attempt < self.config.MAX_RETRIES - 1:
                        time.sleep(5 * (attempt + 1))

        return jobs

    def scrape_all(self) -> list[JobListing]:
        """Scrape jobs for all configured keywords."""
        all_jobs: list[JobListing] = []
        self._seen_urls.clear()

        for keyword in self.config.SEARCH_KEYWORDS:
            jobs = self.scrape_keyword(keyword)
            all_jobs.extend(jobs)
            logger.info(f"✅ '{keyword}': {len(jobs)} jobs found")

            if keyword != self.config.SEARCH_KEYWORDS[-1]:
                self._random_delay()

        logger.info(f"📊 Total unique jobs found: {len(all_jobs)}")
        return all_jobs
