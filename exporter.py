"""
LinkedIn Job Scraper - Data Export Module
Exports scraped job data to CSV / Excel files.
"""

import logging
import os
from datetime import datetime

import pandas as pd

from config import Config
from scraper import JobListing

logger = logging.getLogger(__name__)


class DataExporter:
    """Exports job listings to CSV or Excel."""

    def __init__(self, config: Config | None = None):
        self.config = config or Config()
        os.makedirs(self.config.OUTPUT_DIR, exist_ok=True)

    def _generate_filename(self, extension: str) -> str:
        """Generate a timestamped output filename."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return os.path.join(self.config.OUTPUT_DIR, f"jobs_{timestamp}.{extension}")

    def export(self, jobs: list[JobListing]) -> str | None:
        """Export jobs to the configured format. Returns the file path."""
        if not jobs:
            logger.warning("No jobs to export.")
            return None

        df = pd.DataFrame([job.to_dict() for job in jobs])

        # Reorder columns for readability
        columns = [
            "title", "company", "location", "date_posted",
            "job_url", "description_snippet", "keyword_used", "scraped_at",
        ]
        df = df.reindex(columns=[c for c in columns if c in df.columns])

        fmt = self.config.OUTPUT_FORMAT.lower()

        if fmt == "csv":
            filepath = self._generate_filename("csv")
            df.to_csv(filepath, index=False, encoding="utf-8-sig")
        elif fmt in ("xlsx", "excel"):
            filepath = self._generate_filename("xlsx")
            df.to_excel(filepath, index=False, engine="openpyxl")
        else:
            # default to csv
            filepath = self._generate_filename("csv")
            df.to_csv(filepath, index=False, encoding="utf-8-sig")

        logger.info(f"💾 Exported {len(jobs)} jobs to: {filepath}")
        return filepath

    def export_csv(self, jobs: list[JobListing]) -> str | None:
        """Force export to CSV."""
        old_fmt = self.config.OUTPUT_FORMAT
        self.config.OUTPUT_FORMAT = "csv"
        result = self.export(jobs)
        self.config.OUTPUT_FORMAT = old_fmt
        return result

    def export_excel(self, jobs: list[JobListing]) -> str | None:
        """Force export to Excel."""
        old_fmt = self.config.OUTPUT_FORMAT
        self.config.OUTPUT_FORMAT = "xlsx"
        result = self.export(jobs)
        self.config.OUTPUT_FORMAT = old_fmt
        return result
