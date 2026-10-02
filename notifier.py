"""
LinkedIn Job Scraper - Telegram Notifier Module
Sends job listing notifications to a Telegram chat.
"""

import logging
from datetime import datetime

from telegram import Bot
from telegram.constants import ParseMode

from config import Config
from scraper import JobListing

logger = logging.getLogger(__name__)


class TelegramNotifier:
    """Sends job notifications via Telegram Bot."""

    def __init__(self, config: Config | None = None):
        self.config = config or Config()
        self._bot: Bot | None = None

    @property
    def is_configured(self) -> bool:
        """Check if Telegram credentials are provided."""
        return bool(self.config.TELEGRAM_BOT_TOKEN and self.config.TELEGRAM_CHAT_ID)

    def _get_bot(self) -> Bot:
        """Get or create Telegram Bot instance."""
        if self._bot is None:
            self._bot = Bot(token=self.config.TELEGRAM_BOT_TOKEN)
        return self._bot

    async def send_message(self, text: str) -> bool:
        """Send a text message to the configured Telegram chat."""
        if not self.is_configured:
            logger.warning("Telegram not configured. Skipping notification.")
            return False

        try:
            bot = self._get_bot()
            await bot.send_message(
                chat_id=self.config.TELEGRAM_CHAT_ID,
                text=text,
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True,
            )
            return True
        except Exception as e:
            logger.warning(f"Markdown send failed ({e}), trying plain text...")
            try:
                bot = self._get_bot()
                await bot.send_message(
                    chat_id=self.config.TELEGRAM_CHAT_ID,
                    text=text,
                    disable_web_page_preview=True,
                )
                return True
            except Exception as e2:
                logger.error(f"Failed to send Telegram message: {e2}")
                return False

    async def notify_jobs(self, jobs: list[JobListing], batch_size: int = 5) -> int:
        """
        Send job listings as Telegram notifications.
        Groups jobs into batches to avoid flooding.
        Returns the number of messages sent successfully.
        """
        if not self.is_configured:
            logger.warning("Telegram not configured. Skipping notifications.")
            return 0

        if not jobs:
            await self.send_message("🔍 Scraping selesai. Tidak ada lowongan baru ditemukan.")
            return 1

        # Send header
        header = (
            f"🚀 *LinkedIn Job Scraper Report*\n"
            f"📅 {datetime.now().strftime('%d %B %Y, %H:%M')}\n"
            f"📊 Ditemukan *{len(jobs)}* lowongan baru!\n"
            f"{'─' * 30}"
        )
        sent_count = 0
        if await self.send_message(header):
            sent_count += 1

        # Send jobs in batches
        for i in range(0, len(jobs), batch_size):
            batch = jobs[i : i + batch_size]
            message_parts = []

            for idx, job in enumerate(batch, start=i + 1):
                message_parts.append(f"*{idx}.* {job.summary()}")

            message = "\n\n".join(message_parts)
            if await self.send_message(message):
                sent_count += 1

        # Send footer
        footer = f"✅ Total: {len(jobs)} lowongan | Scraping berikutnya dalam {self.config.SCRAPE_INTERVAL_MINUTES} menit"
        if await self.send_message(footer):
            sent_count += 1

        logger.info(f"📨 Sent {sent_count} Telegram messages for {len(jobs)} jobs")
        return sent_count

    async def notify_error(self, error: str) -> bool:
        """Send error notification."""
        message = f"⚠️ *Scraper Error*\n\n{error}"
        return await self.send_message(message)
