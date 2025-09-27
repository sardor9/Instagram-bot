# 📸 Instagram Downloader Bot (Telegram)

Bu loyiha **Telegram bot** bo‘lib, unga Instagram `post/reel/tv` linkini yuborsangiz — media (foto/video) va post tavsifini qaytaradi.  
Bot **[aiogram](https://docs.aiogram.dev/)** va **[instagrapi](https://github.com/adw0rd/instagrapi)** kutubxonalaridan foydalanadi.

---

## ⚙️ O‘rnatish

### 1. Klonlash
```bash
git clone https://github.com/<username>/instagram-downloader-bot.git
cd instagram-downloader-bot
```
**### 2. Virtual environment yaratish**
``` bash
python -m venv venv
source venv/bin/activate   # Linux/MacOS
venv\Scripts\activate      # Windows
```
**### 3. Kutubxonalarni o‘rnatish**
``` bash
pip install -r requirements.txt
```
**### 4. .env fayl yaratish**
``` ini
TELEGRAM_BOT_TOKEN=telegram_bot_tokeningiz
IG_USERNAME=instagram_username
IG_PASSWORD=instagram_password
```
**###▶️ Ishga tushirish**
``` bash
python Instagrambot.py```
