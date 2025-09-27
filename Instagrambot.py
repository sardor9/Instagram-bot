# Instagrambot.py
import os
import re
import asyncio
import logging
import json
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher
from aiogram.enums import ChatAction
from aiogram.filters import Command
from aiogram.types import Message, URLInputFile

from instagrapi import Client

# ========================
# .env o‘zgaruvchilar
# ========================
load_dotenv()
API_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
IG_USERNAME = os.getenv("IG_USERNAME")
IG_PASSWORD = os.getenv("IG_PASSWORD")

if not API_TOKEN:
    raise RuntimeError("Iltimos, TELEGRAM_BOT_TOKEN ni .env faylda belgilang.")
if not IG_USERNAME or not IG_PASSWORD:
    raise RuntimeError("Iltimos, IG_USERNAME va IG_PASSWORD ni .env faylda belgilang.")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

INSTAGRAM_URL_RE = re.compile(
    r"(https?://(?:www\.)?instagram\.com/(?:p|reel|tv)/[A-Za-z0-9_\-]+)",
    flags=re.IGNORECASE
)

# ========================
# Instagram login (session bilan)
# ========================
cl = Client()
SESSION_FILE = "session.json"

def login_instagram():
    """Session.json bor bo‘lsa yuklaydi, bo‘lmasa login qiladi."""
    if os.path.exists(SESSION_FILE):
        logging.info("♻️ Session fayl topildi, yuklanmoqda...")
        with open(SESSION_FILE) as f:
            settings = json.load(f)
        cl.set_settings(settings)
        try:
            cl.login(IG_USERNAME, IG_PASSWORD)
            return
        except Exception as e:
            logging.warning(f"Session bilan login bo‘lmadi: {e}. Yangi login qilinadi.")

    logging.info("🔑 Yangi login boshlanmoqda...")
    def challenge_code_handler(username, choice):
        print(f"📩 Kod {choice} orqali yuborildi")
        return input("6 xonali kodni kiriting: ")

    cl.challenge_code_handler = challenge_code_handler
    cl.login(IG_USERNAME, IG_PASSWORD)

    with open(SESSION_FILE, "w") as f:
        json.dump(cl.get_settings(), f)
    logging.info("✅ Session.json saqlandi!")

login_instagram()

# ========================
# Instagram media olish
# ========================
def fetch_instagram(url: str):
    """Instagrapi orqali media ma'lumotlarini olish."""
    try:
        media_pk = cl.media_pk_from_url(url)
        media = cl.media_info(media_pk)
    except Exception as e:
        return {"error": f"Instagramdan ma'lumot olishda xato: {e}"}

    data = {"caption": getattr(media, "caption_text", "") or ""}
    mtype = getattr(media, "media_type", None)

    if mtype == 1:  # photo
        data["image"] = getattr(media, "thumbnail_url", None)
    elif mtype == 2:  # video
        data["video"] = getattr(media, "video_url", None)
    elif mtype == 8:  # album
        album = []
        for r in getattr(media, "resources", []) or []:
            if getattr(r, "media_type", None) == 2:
                album.append(getattr(r, "video_url", None))
            else:
                album.append(getattr(r, "thumbnail_url", None))
        data["album"] = [x for x in album if x]

    return data

# ========================
# Handlers
# ========================
@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "👋 Salom!\n"
        "Menga Instagram post/reel linkini yuboring, men media va tavsifini qaytaraman.\n\n"
        "Misol: https://www.instagram.com/p/XXXXXXXXX/"
    )

@dp.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer("ℹ️ Instagram linkini yuboring (faqat public yoki siz kirgan akkauntdagi postlar).")

@dp.message()
async def handle_any_message(message: Message):
    text = message.text or message.caption or ""
    m = INSTAGRAM_URL_RE.search(text)
    if not m:
        await message.reply("❌ Iltimos, Instagram post/reel linkini yuboring.")
        return

    url = m.group(1)
    await bot.send_chat_action(message.chat.id, ChatAction.TYPING)

    result = await asyncio.to_thread(fetch_instagram, url)
    if "error" in result:
        await message.reply(f"⚠️ Xatolik: {result['error']}")
        return

    caption = result.get("caption", "")
    if len(caption) > 1000:
        caption = caption[:1000] + "…"

    # 🎥 Video
    if "video" in result and result["video"]:
        video_url = URLInputFile(str(result["video"]))
        try:
            await message.reply_video(video_url, caption=caption or None)
        except Exception as e:
            logging.exception("Video yuborishda xato")
            await message.reply(f"Video yuborilmadi: {e}\nURL: {result['video']}")
        return

    # 🖼 Rasm
    if "image" in result and result["image"]:
        image_url = URLInputFile(str(result["image"]))
        try:
            await message.reply_photo(image_url, caption=caption or None)
        except Exception as e:
            logging.exception("Rasm yuborishda xato")
            await message.reply(f"Rasm yuborilmadi: {e}\nURL: {result['image']}")
        return

    # 📚 Album
    if "album" in result and result["album"]:
        for media_url in result["album"]:
            if media_url.endswith(".mp4"):
                await message.reply_video(URLInputFile(str(media_url)), caption=caption or None)
            else:
                await message.reply_photo(URLInputFile(str(media_url)), caption=caption or None)
        return

    await message.reply("❌ Media topilmadi yoki post yopiq.")

# ========================
# Run bot
# ========================
async def main():
    logging.info("🤖 Bot ishga tushmoqda...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
