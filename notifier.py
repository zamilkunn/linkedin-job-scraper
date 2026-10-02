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
        """Send a text message to all configured Telegram chats / channels."""
        if not self.is_configured:
            logger.warning("Telegram not configured. Skipping notification.")
            return False

        targets = self.config.telegram_chat_ids
        if not targets:
            return False

        all_ok = True
        bot = self._get_bot()

        for target in targets:
            try:
                await bot.send_message(
                    chat_id=target,
                    text=text,
                    parse_mode=ParseMode.MARKDOWN,
                    disable_web_page_preview=True,
                )
            except Exception as e:
                logger.warning(f"Markdown send failed for {target} ({e}), trying plain text...")
                try:
                    await bot.send_message(
                        chat_id=target,
                        text=text,
                        disable_web_page_preview=True,
                    )
                except Exception as e2:
                    logger.error(f"Failed to send Telegram message to {target}: {e2}")
                    all_ok = False

        return all_ok

    async def _send_to_target(self, target: str, text: str) -> bool:
        """Send a single message to a specific chat/channel."""
        bot = self._get_bot()
        try:
            await bot.send_message(
                chat_id=target,
                text=text,
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True,
            )
            return True
        except Exception as e:
            logger.warning(f"Markdown send failed for {target} ({e}), trying plain text...")
            try:
                await bot.send_message(
                    chat_id=target,
                    text=text,
                    disable_web_page_preview=True,
                )
                return True
            except Exception as e2:
                logger.error(f"Failed to send Telegram message to {target}: {e2}")
                return False

    async def notify_jobs(self, jobs: list[JobListing], batch_size: int = 5) -> int:
        """
        Send job listings as Telegram notifications.
        Private chats get 1-Click Sheets tracking; Public channels get clean links.
        """
        if not self.is_configured:
            logger.warning("Telegram not configured. Skipping notifications.")
            return 0

        targets = self.config.telegram_chat_ids
        if not targets:
            return 0

        if not jobs:
            await self.send_message("🔍 Scraping selesai. Tidak ada lowongan baru ditemukan.")
            return 1

        header = (
            f"🚀 *LinkedIn Job Scraper Report*\n"
            f"📅 {datetime.now().strftime('%d %B %Y, %H:%M')}\n"
            f"📊 Ditemukan *{len(jobs)}* lowongan baru!\n"
            f"{'─' * 30}"
        )
        footer = f"✅ Total: {len(jobs)} lowongan | Scraping berikutnya dalam {self.config.SCRAPE_INTERVAL_MINUTES} menit"

        total_sent = 0

        for target in targets:
            # Check if this target is a public channel/group (starts with @ or -100)
            is_channel = target.startswith("@") or target.startswith("-100")
            webhook_url = "" if is_channel else self.config.GOOGLE_SHEET_WEBHOOK_URL

            # Send Header
            if await self._send_to_target(target, header):
                total_sent += 1

            # Send Batches
            for i in range(0, len(jobs), batch_size):
                batch = jobs[i : i + batch_size]
                message_parts = []

                for idx, job in enumerate(batch, start=i + 1):
                    message_parts.append(f"*{idx}.* {job.summary(webhook_url)}")

                message = "\n\n".join(message_parts)
                if await self._send_to_target(target, message):
                    total_sent += 1

                # Delay between batches to prevent Telegram flood limits
                await asyncio.sleep(1.5)

            # Send Footer
            if await self._send_to_target(target, footer):
                total_sent += 1

        logger.info(f"📨 Sent {total_sent} messages across {len(targets)} targets for {len(jobs)} jobs")
        return total_sent

    async def notify_error(self, error: str) -> bool:
        """Send error notification."""
        message = f"⚠️ *Scraper Error*\n\n{error}"
        return await self.send_message(message)
