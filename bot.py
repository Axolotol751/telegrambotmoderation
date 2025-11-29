import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ChatPermissions

API_TOKEN = "8371048146:AAFzCWlxb5mkouEoIQDn24LP-ZPqKQiYvgs"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

warns = {}  # словарь для варнов


@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.reply("Бот работает! Можешь использовать команды /ban /mute /warn /warns")


@dp.message_handler(commands=["ban"])
async def ban(message: types.Message):
    if not message.reply_to_message:
        return await message.reply("Ответьте на сообщение пользователя.")

    user_id = message.reply_to_message.from_user.id
    await message.chat.kick(user_id)
    await message.reply("Пользователь забанен.")


@dp.message_handler(commands=["mute"])
async def mute(message: types.Message):
    if not message.reply_to_message:
        return await message.reply("Ответьте на сообщение пользователя.")

    user_id = message.reply_to_message.from_user.id
    permissions = ChatPermissions(can_send_messages=False)

    await message.chat.restrict(user_id, permissions=permissions)
    await message.reply("Пользователь замьючен.")


@dp.message_handler(commands=["warn"])
async def warn(message: types.Message):
    if not message.reply_to_message:
        return await message.reply("Ответьте на сообщение пользователя.")

    user_id = message.reply_to_message.from_user.id
    warns[user_id] = warns.get(user_id, 0) + 1

    await message.reply(f"Варн выдан. Всего: {warns[user_id]}")


@dp.message_handler(commands=["warns"])
async def get_warns(message: types.Message):
    if not message.reply_to_message:
        return await message.reply("Ответьте на сообщение пользователя.")

    user_id = message.reply_to_message.from_user.id
    count = warns.get(user_id, 0)

    await message.reply(f"У пользователя {count} предупреждений.")


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
