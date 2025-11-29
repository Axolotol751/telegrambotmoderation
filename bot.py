import logging
import os
import random
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ChatPermissions
from dotenv import load_dotenv

load_dotenv()
API_TOKEN = os.getenv("BOT_TOKEN")
if not API_TOKEN:
    raise ValueError("BOT_TOKEN не задан в .env")

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

warns = {}  # {user_id: warn_count}
MAX_WARNS = 5  # если хочешь лимит предупреждений

# --- Проверка: является ли пользователь админом чата ---
async def is_admin(message: types.Message) -> bool:
    chat = message.chat
    user = message.from_user
    member = await chat.get_member(user.id)
    return member.is_chat_admin() or member.is_chat_creator()

# --- Общие декораторы для команд /…@botusername и просто /… ---
def cmd_handler_names(cmd: str):
    return [cmd, f"{cmd}@{(await bot.get_me()).username}"]

@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    await message.reply("Бот активен! Команды для админов: /ban, /unban, /mute, /unmute, /warn, /unwarn, /warns. Есть и пасхалки 😊")

# --- BAN / UNBAN ---
@dp.message_handler(lambda m: m.text and (m.text.startswith("/ban") or m.text.startswith(f"/ban@{(await bot.get_me()).username}")))
async def cmd_ban(message: types.Message):
    if not await is_admin(message):
        return await message.reply("Ты не админ — нельзя банить.")
    if not message.reply_to_message:
        return await message.reply("Ответь на сообщение, кого баним.")
    user = message.reply_to_message.from_user
    await message.chat.kick(user.id)
    await message.reply(f"👢 Пользователь {user.full_name} забанен.")

@dp.message_handler(lambda m: m.text and (m.text.startswith("/unban") or m.text.startswith(f"/unban@{(await bot.get_me()).username}")))
async def cmd_unban(message: types.Message):
    if not await is_admin(message):
        return await message.reply("Ты не админ — нельзя разбанивать.")
    if not message.reply_to_message:
        return await message.reply("Ответь на сообщение, кого разбаниваем.")
    user = message.reply_to_message.from_user
    await message.chat.unban(user.id)
    await message.reply(f"✅ Пользователь {user.full_name} разбанен.")

# --- MUTE / UNMUTE ---
@dp.message_handler(lambda m: m.text and (m.text.startswith("/mute") or m.text.startswith(f"/mute@{(await bot.get_me()).username}")))
async def cmd_mute(message: types.Message):
    if not await is_admin(message):
        return await message.reply("Ты не админ — нельзя мутить.")
    if not message.reply_to_message:
        return await message.reply("Ответь на сообщение, кого мутим.")
    user = message.reply_to_message.from_user
    await message.chat.restrict(user.id, ChatPermissions(can_send_messages=False))
    await message.reply(f"🔇 Пользователь {user.full_name} замьючен.")

@dp.message_handler(lambda m: m.text and (m.text.startswith("/unmute") or m.text.startswith(f"/unmute@{(await bot.get_me()).username}")))
async def cmd_unmute(message: types.Message):
    if not await is_admin(message):
        return await message.reply("Ты не админ — нельзя размутить.")
    if not message.reply_to_message:
        return await message.reply("Ответь на сообщение, кого размутим.")
    user = message.reply_to_message.from_user
    await message.chat.restrict(user.id, ChatPermissions(can_send_messages=True))
    await message.reply(f"🔊 Пользователь {user.full_name} размьючен.")

# --- WARN / UNWARN / WARNS ---
@dp.message_handler(lambda m: m.text and (m.text.startswith("/warn") or m.text.startswith(f"/warn@{(await bot.get_me()).username}")))
async def cmd_warn(message: types.Message):
    if not await is_admin(message):
        return await message.reply("Ты не админ — нельзя выдавать варн.")
    if not message.reply_to_message:
        return await message.reply("Ответь на сообщение, кому варн.")
    user = message.reply_to_message.from_user
    uid = user.id
    warns[uid] = warns.get(uid, 0) + 1
    await message.reply(f"⚠️ {user.full_name} получил варн. Всего: {warns[uid]}")
    if warns[uid] >= MAX_WARNS:
        await message.chat.kick(uid)
        await message.reply(f"⚠️ {user.full_name} набрал {warns[uid]} варнов — бан!")

@dp.message_handler(lambda m: m.text and (m.text.startswith("/unwarn") or m.text.startswith(f"/unwarn@{(await bot.get_me()).username}")))
async def cmd_unwarn(message: types.Message):
    if not await is_admin(message):
        return await message.reply("Ты не админ — нельзя снимать варн.")
    if not message.reply_to_message:
        return await message.reply("Ответь на сообщение, кому снимаем варн.")
    user = message.reply_to_message.from_user
    uid = user.id
    warns[uid] = max(warns.get(uid, 0) - 1, 0)
    await message.reply(f"✅ У {user.full_name} варн снижен. Сейчас: {warns[uid]}")

@dp.message_handler(lambda m: m.text and (m.text.startswith("/warns") or m.text.startswith(f"/warns@{(await bot.get_me()).username}")))
async def cmd_warns(message: types.Message):
    if not message.reply_to_message:
        return await message.reply("Ответь на сообщение, чьи варны показать.")
    user = message.reply_to_message.from_user
    cnt = warns.get(user.id, 0)
    await message.reply(f"ℹ️ {user.full_name} — {cnt} варн(ов).")

# --- Пасхальные / fun команды ---
@dp.message_handler(commands=["hug"])
async def cmd_hug(message: types.Message):
    if not message.reply_to_message:
        return await message.reply("Ответь на сообщение человека, которого хочешь обнять 🤗")
    user = message.reply_to_message.from_user
    await message.reply(f"🤗 {message.from_user.full_name} обнял(а) {user.full_name}!")

@dp.message_handler(commands=["cake"])
async def cmd_cake(message: types.Message):
    await message.reply("🎂 С днём хорошего настроения! Примите торт 🍰")

@dp.message_handler(commands=["surprise"])
async def cmd_surprise(message: types.Message):
    texts = [
        "Улыбнись 😊",
        "Пусть сегодня случится что‑то хорошее!",
        "Не забудь сделать паузу и выпить воды 💧",
        "Поделись настроением с другом!",
    ]
    await message.reply(random.choice(texts))

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
