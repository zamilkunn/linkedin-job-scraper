"""
Test Telegram Bot Connection
"""

import asyncio
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

from config import Config
from notifier import TelegramNotifier


async def main():
    config = Config()
    notifier = TelegramNotifier(config)

    print("=" * 50)
    print("🤖 Testing Telegram Notification...")
    print(f"Token: {'[TERISI]' if config.TELEGRAM_BOT_TOKEN else '[KOSONG]'}")
    print(f"Chat ID: {'[TERISI]' if config.TELEGRAM_CHAT_ID else '[KOSONG]'}")
    print("=" * 50)

    if not notifier.is_configured:
        print("❌ Token atau Chat ID masih kosong di file .env!")
        print("Silakan isi TELEGRAM_BOT_TOKEN dan TELEGRAM_CHAT_ID terlebih dahulu.")
        return

    print("Mengirim pesan tes ke Telegram...")
    success = await notifier.send_message(
        "🎉 *Halo Muhamad Cep Zamil!*\n\n"
        "Bot LinkedIn Scraper kamu sudah *berhasil terhubung* ke Telegram!\n"
        "Setiap kali scraper menemukan lowongan baru, notifikasinya akan langsung masuk ke sini 🚀"
    )

    if success:
        print("✅ BERHASIL! Cek aplikasi Telegram kamu, ada pesan masuk!")
    else:
        print("❌ Gagal mengirim pesan. Pastikan:")
        print("  1. Token & Chat ID sudah benar.")
        print("  2. Kamu sudah klik 'START' di bot Telegram kamu terlebih dahulu.")


if __name__ == "__main__":
    asyncio.run(main())
