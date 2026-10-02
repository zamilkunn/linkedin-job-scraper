"""
LinkedIn Job Scraper Bot - Main Entry Point

Usage:
    python main.py              # Run scraper once
    python main.py --schedule   # Run scraper on a schedule
    python main.py --help       # Show help
"""

import argparse
import asyncio
import logging
import sys
import io
from datetime import datetime

# Fix Windows console encoding for emoji/unicode characters
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

import schedule
import time as _time

from config import Config
from scraper import LinkedInScraper
from exporter import DataExporter
from notifier import TelegramNotifier

# ──────────────────────────────────────────────
# Logging setup
# ──────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s │ %(levelname)-8s │ %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("scraper.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)


def print_banner() -> None:
    banner = r"""
    ╔═══════════════════════════════════════════════════╗
    ║        🔍  LinkedIn Job Scraper Bot  🔍          ║
    ║     Cari lowongan kerja otomatis dari LinkedIn    ║
    ╚═══════════════════════════════════════════════════╝
    """
    print(banner)


async def run_scraper(config: Config) -> None:
    """Execute one full scraping cycle."""
    start_time = datetime.now()
    logger.info("=" * 50)
    logger.info(f"🚀 Starting scrape cycle at {start_time.strftime('%H:%M:%S')}")
    logger.info(f"   Keywords: {', '.join(config.SEARCH_KEYWORDS)}")
    logger.info(f"   Location: {config.SEARCH_LOCATION}")
    logger.info("=" * 50)

    scraper = LinkedInScraper(config)
    exporter = DataExporter(config)
    notifier = TelegramNotifier(config)

    try:
        # 1. Scrape
        jobs = scraper.scrape_all()

        # 2. Export
        if jobs:
            filepath = exporter.export(jobs)
            if filepath:
                logger.info(f"📁 Data saved to: {filepath}")

            # Print preview
            print("\n📋 Preview (top 10):")
            print("-" * 100)
            for i, job in enumerate(jobs[:10], 1):
                print(f"  {i:>2}. {job.title:<40} | {job.company:<25} | {job.location}")
            if len(jobs) > 10:
                print(f"  ... dan {len(jobs) - 10} lowongan lainnya")
            print("-" * 100)
        else:
            logger.info("😕 Tidak ada lowongan yang ditemukan.")

        # 3. Notify via Telegram
        if notifier.is_configured:
            await notifier.notify_jobs(jobs)
        else:
            logger.info("ℹ️  Telegram belum dikonfigurasi. Lewati notifikasi.")
            logger.info("   Set TELEGRAM_BOT_TOKEN dan TELEGRAM_CHAT_ID di file .env")

    except Exception as e:
        logger.error(f"❌ Scraper error: {e}", exc_info=True)
        if notifier.is_configured:
            await notifier.notify_error(str(e))

    elapsed = (datetime.now() - start_time).total_seconds()
    logger.info(f"⏱️  Scraping selesai dalam {elapsed:.1f} detik\n")


def scheduled_job(config: Config) -> None:
    """Wrapper to run the async scraper in the scheduler."""
    asyncio.run(run_scraper(config))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="LinkedIn Job Scraper Bot - Scrape lowongan kerja dari LinkedIn",
    )
    parser.add_argument(
        "--schedule",
        action="store_true",
        help="Jalankan scraper secara terjadwal (sesuai SCRAPE_INTERVAL_MINUTES)",
    )
    parser.add_argument(
        "--keywords",
        type=str,
        help="Override keywords (comma-separated), e.g. 'python,data analyst'",
    )
    parser.add_argument(
        "--location",
        type=str,
        help="Override location, e.g. 'Jakarta'",
    )
    args = parser.parse_args()

    print_banner()

    config = Config()

    # Override from CLI args
    if args.keywords:
        config.SEARCH_KEYWORDS = [kw.strip() for kw in args.keywords.split(",")]
    if args.location:
        config.SEARCH_LOCATION = args.location

    if args.schedule:
        # ── Scheduled Mode ──
        interval = config.SCRAPE_INTERVAL_MINUTES
        logger.info(f"⏰ Mode terjadwal: scraping setiap {interval} menit")
        logger.info("   Tekan Ctrl+C untuk berhenti\n")

        # Run immediately first
        scheduled_job(config)

        # Then schedule
        schedule.every(interval).minutes.do(scheduled_job, config)

        try:
            while True:
                schedule.run_pending()
                _time.sleep(1)
        except KeyboardInterrupt:
            logger.info("\n👋 Scraper dihentikan oleh user. Sampai jumpa!")
    else:
        # ── Single Run Mode ──
        asyncio.run(run_scraper(config))


if __name__ == "__main__":
    main()
