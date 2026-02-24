import requests
import telebot
import os
import time
import hashlib
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# ========== SOZLAMALAR ==========
TOKEN = "BOT_TOKEN"  # @BotFather dan oling
ADMIN_ID = ADMIN_ID  # O'z ID ingiz
# ================================

bot = telebot.TeleBot(TOKEN)

# KANAL REKLAMA
CHANNEL = "@qakhorov_dev"
AUTHOR = "@cyber_qakhorov"

# Vaqtinchalik ma'lumotlar uchun dict
temp_data = {}

def generate_short_id(text, max_length=30):
    """Uzun textni qisqartirish"""
    return hashlib.md5(text.encode()).hexdigest()[:max_length]

def format_file_size(bytes):
    """Fayl hajmini formatlash"""
    if bytes == 0:
        return "0 B"
    
    sizes = ['B', 'KB', 'MB', 'GB', 'TB']
    i = 0
    while bytes >= 1024 and i < len(sizes)-1:
        bytes /= 1024.0
        i += 1
    return f"{bytes:.1f} {sizes[i]}"

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        text=f'''🎥 VIDEO DOWNLOADER BOT

🔍 Menga video link yuboring:
• YouTube
• Instagram

⚡️ Tez yuklab olish
📥 Barcha sifatlar

📱 {CHANNEL}
👨‍💻 {AUTHOR}'''
    )

@bot.message_handler(commands=['search'])
def search(message):
    msg = bot.send_message(
        message.chat.id,
        text="🔍 Qidiruv so'zini kiriting:"
    )
    bot.register_next_step_handler(msg, search_videos)

def search_videos(message):
    keyword = message.text.strip()
    
    if len(keyword) < 3:
        bot.send_message(message.chat.id, text="❌ Kamida 3 ta harf")
        return
    
    msg = bot.send_message(message.chat.id, text="⏳ Qidirilmoqda...")
    
    try:
        search_url = "https://vidssave.com/api/proxy"
        headers = {'content-type': 'application/json', 'user-agent': 'Mozilla/5.0'}
        payload = {
            "url": "/media/hot_list", 
            "data": {"hot_type": "ytb", "keyword": keyword}
        }
        
        resp = requests.post(search_url, headers=headers, json=payload, timeout=20)
        data = resp.json()
        items = data.get('data', {}).get('items', [])
        
        if not items:
            bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=msg.message_id,
                text="❌ Hech narsa topilmadi"
            )
            return
        
        markup = InlineKeyboardMarkup()
        for i, item in enumerate(items[:10]):
            title = item.get('title', 'No title')[:30]  # Qisqartirildi
            video_url = item.get('url', '')
            video_id = generate_short_id(video_url, 15)
            
            # URL ni vaqtinchalik saqlash
            temp_data[f"url_{video_id}"] = video_url
            
            markup.add(InlineKeyboardButton(
                text=f"{i+1}. {title}",
                callback_data=f"url|{video_id}"  # Qisqa ID
            ))
        
        bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=msg.message_id,
            text=f"📋 {len(items[:10])} ta video topildi. Birini tanlang:",
            reply_markup=markup
        )
        
    except Exception as e:
        bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=msg.message_id,
            text=f"❌ Xatolik: {str(e)[:50]}"
        )

@bot.message_handler(content_types=['text'])
def handle_video(message):
    url = message.text.strip()
    
    if not url.startswith(('http://', 'https://')):
        bot.send_message(
            message.chat.id,
            text="❌ Iltimos, to'liq URL yuboring\nMasalan: https://youtube.com/..."
        )
        return
    
    msg = bot.send_message(
        message.chat.id,
        text="⏳ Video ma'lumotlari olinmoqda..."
    )
    
    try:
        api_url = "https://api.vidssave.com/api/contentsite_api/media/parse"
        headers = {
            'authority': 'api.vidssave.com',
            'content-type': 'application/x-www-form-urlencoded',
            'user-agent': 'Mozilla/5.0'
        }
        data = {
            'auth': '20250901majwlqo',
            'domain': 'api-ak.vidssave.com',
            'origin': 'source',
            'link': url
        }
        
        response = requests.post(api_url, headers=headers, data=data, timeout=20)
        result = response.json()
        
        video_data = result.get('data', {})
        title = video_data.get('title', 'video')
        resources = video_data.get('resources', [])
        
        if not resources:
            bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=msg.message_id,
                text="❌ Yuklab olish mumkin emas"
            )
            return
        
        # === YAXSHILANGAN TUGMALAR QISMI ===
        markup = InlineKeyboardMarkup(row_width=2)
        buttons = []
        quality_list = []
        
        # Barcha sifatlarni yig'ish va saralash
        for i, res in enumerate(resources):
            download_url = res.get('download_url')
            if download_url and isinstance(download_url, str) and len(download_url) > 10:
                quality = res.get('quality', 'N/A')
                fmt = res.get('format', 'mp4')
                media_type = res.get('type', 'video').upper()
                filesize = res.get('filesize', 0)
                
                if download_url.startswith('//'):
                    download_url = 'https:' + download_url
                
                # Sifatni raqamga aylantirish (saralash uchun)
                quality_num = 0
                if '2160' in quality or '4k' in quality.lower():
                    quality_num = 2160
                elif '1440' in quality or '2k' in quality.lower():
                    quality_num = 1440
                elif '1080' in quality:
                    quality_num = 1080
                elif '720' in quality:
                    quality_num = 720
                elif '480' in quality:
                    quality_num = 480
                elif '360' in quality:
                    quality_num = 360
                elif '240' in quality:
                    quality_num = 240
                elif '144' in quality:
                    quality_num = 144
                elif 'AUDIO' in media_type:
                    quality_num = 0
                
                quality_list.append({
                    'index': i,
                    'quality_num': quality_num,
                    'quality_text': quality,
                    'fmt': fmt,
                    'download_url': download_url,
                    'filesize': filesize,
                    'media_type': media_type
                })
        
        # Sifat bo'yicha saralash (kattadan kichikga)
        quality_list.sort(key=lambda x: x['quality_num'], reverse=True)
        
        # Tugmalarni yaratish
        for i, q in enumerate(quality_list[:10]):  # Eng yaxshi 10 ta sifat
            download_url = q['download_url']
            quality = q['quality_text']
            fmt = q['fmt']
            media_type = q['media_type']
            filesize = q['filesize']
            quality_num = q['quality_num']
            
            dl_id = generate_short_id(f"{download_url}_{i}", 10)
            
            # Ma'lumotlarni saqlash
            temp_data[f"dl_{dl_id}"] = {
                'url': download_url,
                'title': title,
                'quality': quality,
                'fmt': fmt,
                'filesize': filesize
            }
            
            # Sifatga qarab emoji va rang
            if quality_num >= 2160:
                emoji = "🔥 4K"
            elif quality_num >= 1440:
                emoji = "✨ 2K"
            elif quality_num >= 1080:
                emoji = "🔴 1080p"
            elif quality_num >= 720:
                emoji = "🟠 720p"
            elif quality_num >= 480:
                emoji = "🟡 480p"
            elif quality_num >= 360:
                emoji = "🟢 360p"
            elif quality_num >= 240:
                emoji = "🔵 240p"
            elif quality_num >= 144:
                emoji = "⚪️ 144p"
            elif 'AUDIO' in media_type:
                emoji = "🎵 AUDIO"
            else:
                emoji = f"📹 {quality[:3]}"
            
            # Fayl hajmini qo'shish
            size_text = f" ({format_file_size(filesize)})" if filesize else ""
            button_text = f"{emoji}{size_text}"
            
            buttons.append(InlineKeyboardButton(
                text=button_text,
                callback_data=f"dl|{dl_id}"
            ))
        
        # Buttonlarni 2 ustun qilib joylash
        for i in range(0, len(buttons), 2):
            row = buttons[i:i+2]
            markup.add(*row)
        
        # Kanal buttoni
        markup.add(InlineKeyboardButton(
            text=f"📱 {CHANNEL}",
            url=f"https://t.me/{CHANNEL.replace('@', '')}"
        ))
        
        # Sarlavhani qisqartirish
        short_title = title[:50] + "..." if len(title) > 50 else title
        
        bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=msg.message_id,
            text=f'''📹 **{short_title}**

📥 **Yuklab olish sifatini tanlang:**''',
            reply_markup=markup,
            parse_mode='Markdown'
        )
        # === YAXSHILANGAN TUGMALAR QISMI TUGADI ===
        
    except Exception as e:
        bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=msg.message_id,
            text=f"❌ Xatolik: {str(e)[:100]}"
        )

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    try:
        data = call.data.split('|')
        
        if data[0] == 'url':
            # Search dan tanlangan video
            video_id = data[1]
            video_url = temp_data.get(f"url_{video_id}")
            
            if not video_url:
                bot.answer_callback_query(call.id, "⏰ Vaqt o'tdi, qaytadan urinib ko'ring")
                return
            
            bot.delete_message(call.message.chat.id, call.message.message_id)
            
            # Video ni qayta ishlash
            msg = bot.send_message(call.message.chat.id, text="⏳ Yuklanmoqda...")
            
            api_url = "https://api.vidssave.com/api/contentsite_api/media/parse"
            headers = {
                'authority': 'api.vidssave.com',
                'content-type': 'application/x-www-form-urlencoded',
                'user-agent': 'Mozilla/5.0'
            }
            post_data = {
                'auth': '20250901majwlqo',
                'domain': 'api-ak.vidssave.com',
                'origin': 'source',
                'link': video_url
            }
            
            response = requests.post(api_url, headers=headers, data=post_data, timeout=20)
            result = response.json()
            
            video_data = result.get('data', {})
            title = video_data.get('title', 'video')
            resources = video_data.get('resources', [])
            
            # === YAXSHILANGAN TUGMALAR (SEARCH UCHUN) ===
            markup = InlineKeyboardMarkup(row_width=2)
            buttons = []
            quality_list = []
            
            for i, res in enumerate(resources):
                download_url = res.get('download_url')
                if download_url:
                    if download_url.startswith('//'):
                        download_url = 'https:' + download_url
                    
                    quality = res.get('quality', 'N/A')
                    fmt = res.get('format', 'mp4')
                    filesize = res.get('filesize', 0)
                    
                    quality_num = 0
                    if '2160' in quality or '4k' in quality.lower():
                        quality_num = 2160
                    elif '1440' in quality or '2k' in quality.lower():
                        quality_num = 1440
                    elif '1080' in quality:
                        quality_num = 1080
                    elif '720' in quality:
                        quality_num = 720
                    elif '480' in quality:
                        quality_num = 480
                    elif '360' in quality:
                        quality_num = 360
                    
                    quality_list.append({
                        'download_url': download_url,
                        'quality': quality,
                        'quality_num': quality_num,
                        'fmt': fmt,
                        'filesize': filesize
                    })
            
            quality_list.sort(key=lambda x: x['quality_num'], reverse=True)
            
            for i, q in enumerate(quality_list[:8]):
                download_url = q['download_url']
                quality = q['quality']
                fmt = q['fmt']
                filesize = q['filesize']
                quality_num = q['quality_num']
                
                dl_id = generate_short_id(f"{download_url}_{i}", 10)
                temp_data[f"dl_{dl_id}"] = {
                    'url': download_url,
                    'title': title,
                    'quality': quality,
                    'fmt': fmt,
                    'filesize': filesize
                }
                
                if quality_num >= 2160:
                    emoji = "🔥 4K"
                elif quality_num >= 1440:
                    emoji = "✨ 2K"
                elif quality_num >= 1080:
                    emoji = "🔴 1080p"
                elif quality_num >= 720:
                    emoji = "🟠 720p"
                elif quality_num >= 480:
                    emoji = "🟡 480p"
                elif quality_num >= 360:
                    emoji = "🟢 360p"
                else:
                    emoji = f"📹 {quality[:3]}"
                
                size_text = f" ({format_file_size(filesize)})" if filesize else ""
                button_text = f"{emoji}{size_text}"
                
                buttons.append(InlineKeyboardButton(
                    text=button_text,
                    callback_data=f"dl|{dl_id}"
                ))
            
            for i in range(0, len(buttons), 2):
                row = buttons[i:i+2]
                markup.add(*row)
            
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=msg.message_id,
                text=f'''📹 **{title[:50]}...**

📥 **Yuklab olish sifatini tanlang:**''',
                reply_markup=markup,
                parse_mode='Markdown'
            )
            # === YAXSHILANGAN TUGMALAR TUGADI ===
        
        elif data[0] == 'dl':
            dl_id = data[1]
            dl_info = temp_data.get(f"dl_{dl_id}")
            
            if not dl_info:
                bot.answer_callback_query(call.id, "⏰ Yuklab olish linki eskirgan")
                return
            
            download_url = dl_info['url']
            title = dl_info['title']
            quality = dl_info['quality']
            fmt = dl_info['fmt']
            filesize = dl_info.get('filesize', 0)
            
            # Fayl nomi
            filename = f"{title[:30]}_{quality}.{fmt}"
            clean_filename = "".join([c for c in filename if c.isalnum() or c in (' ._-')]).strip()
            
            size_text = f" ({format_file_size(filesize)})" if filesize else ""
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=f"⏳ **{quality}{size_text}** yuklanmoqda...\nBu bir necha soniya davom etishi mumkin",
                parse_mode='Markdown'
            )
            
            # Faylni yuklab olish
            response = requests.get(download_url, stream=True, timeout=60)
            
            if response.status_code == 200:
                with open(clean_filename, 'wb') as f:
                    total_size = int(response.headers.get('content-length', 0))
                    downloaded = 0
                    
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if total_size > 0:
                            percent = (downloaded / total_size) * 100
                            if int(percent) % 20 == 0:  # Har 20% da yangilash
                                try:
                                    bot.edit_message_text(
                                        chat_id=call.message.chat.id,
                                        message_id=call.message.message_id,
                                        text=f"⏳ **Yuklanmoqda:** {percent:.0f}%",
                                        parse_mode='Markdown'
                                    )
                                except:
                                    pass
                
                # Faylni yuborish
                with open(clean_filename, 'rb') as f:
                    if fmt == 'mp3' or 'audio' in fmt.lower():
                        bot.send_audio(
                            chat_id=call.message.chat.id,
                            audio=f,
                            caption=f"🎵 **{title[:50]}**\n\n📥 {CHANNEL} orqali yuklab olindi",
                            timeout=120
                        )
                    else:
                        bot.send_video(
                            chat_id=call.message.chat.id,
                            video=f,
                            caption=f"📹 **{title[:50]}**\n\n📥 {CHANNEL} orqali yuklab olindi",
                            timeout=180,
                            supports_streaming=True
                        )
                
                # Faylni o'chirish
                os.remove(clean_filename)
                
                # Ma'lumotni o'chirish
                if f"dl_{dl_id}" in temp_data:
                    del temp_data[f"dl_{dl_id}"]
                
                bot.delete_message(call.message.chat.id, call.message.message_id)
                
                # Reklama
                bot.send_message(
                    call.message.chat.id,
                    text=f"📱 {CHANNEL} | 👨‍💻 {AUTHOR}"
                )
            else:
                bot.send_message(
                    call.message.chat.id,
                    text="❌ Yuklab olishda xatolik"
                )
                
    except Exception as e:
        bot.send_message(
            call.message.chat.id,
            text=f"❌ Xatolik: {str(e)[:100]}"
        )

# Vaqti-vaqti bilan eskirgan ma'lumotlarni tozalash
def clean_temp_data():
    while True:
        time.sleep(300)  # 5 daqiqa
        temp_data.clear()
        print("🧹 Temp data cleaned")

import threading
cleaner = threading.Thread(target=clean_temp_data, daemon=True)
cleaner.start()

print("✅ BOT ISHGA TUSHDI")
print(f"📱 {CHANNEL}")
print(f"👨‍💻 {AUTHOR}")
bot.polling(none_stop=True)    