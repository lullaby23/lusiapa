import traceback
import asyncio # Lol! Weird Import!

from asyncio import QueueEmpty

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, Chat, CallbackQuery

from callsmusic import callsmusic, queues

from helpers.filters import command
from helpers.decorators import errors, authorized_users_only
from helpers.database import db, dcmdb, Database
from helpers.dbthings import handle_user_status, delcmd_is_on, delcmd_on, delcmd_off
from config import LOG_CHANNEL, BOT_OWNER, BOT_USERNAME
from . import que, admins as fuck


@Client.on_message()
async def _(bot: Client, cmd: Message):
    await handle_user_status(bot, cmd)

# Back Button
BACK_BUTTON = InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Kembali ⬅️", callback_data="cbback")]])

@Client.on_message(~filters.private)
async def delcmd(_, message: Message):
    if await delcmd_is_on(message.chat.id) and message.text.startswith("/") or message.text.startswith("!"):
        await message.delete()
    await message.continue_propagation()


@Client.on_message(filters.command(["reload", f"reload@{BOT_USERNAME}"]))
@authorized_users_only # Fuk Off Everyone! Admin Only Command!
async def update_admin(client, message):
    global fuck
    admins = await client.get_chat_members(message.chat.id, filter="administrators")
    new_ads = []
    for u in admins:
        new_ads.append(u.user.id)
    fuck[message.chat.id] = new_ads
    await message.reply_text("**Sukses update list admin ✅!**")


# Control Menu Of Player
@Client.on_message(command(["control", f"control@{BOT_USERNAME}", "p"]))
@errors
@authorized_users_only
async def controlset(_, message: Message):
    await message.reply_text(
        "**Sukses membuka menu musik!**",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "⏸ Berhenti ⏸", callback_data="cbpause"
                    ),
                    InlineKeyboardButton(
                        "▶️ Lanjut ▶️", callback_data="cbresume"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "⏩ Skip ⏩", callback_data="cbskip"
                    ),
                    InlineKeyboardButton(
                        "⏹ Stop ⏹", callback_data="cbend"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "🔇 Senyap 🔇", callback_data="cbmute"
                    ),
                    InlineKeyboardButton(
                        "🔈 Bunyikan 🔈", callback_data="cbunmute"
                    )
                ]
            ]
        )
    )



@Client.on_message(command(["pause", f"pause@{BOT_USERNAME}", "p"]))
@errors
@authorized_users_only
async def pause(_, message: Message):
    if callsmusic.pause(message.chat.id):
        await message.reply_text("⏸ Berhenti")
    else:
        await message.reply_text("❗️ Gak ada lagu yang dimulai")

@Client.on_message(command(["resume", f"resume@{BOT_USERNAME}", "r"]))
@errors
@authorized_users_only
async def resume(_, message: Message):
    if callsmusic.resume(message.chat.id):
        await message.reply_text("🎧 Lanjut")
    else:
        await message.reply_text("❗️ Gak ada yang lagu yang bisa diberhentikan")


@Client.on_message(command(["end", f"end@{BOT_USERNAME}", "e"]))
@errors
@authorized_users_only
async def stop(_, message: Message):
    if message.chat.id not in callsmusic.active_chats:
        await message.reply_text("❗️ Gak ada lagu yang dimulai")
    else:
        try:
            queues.clear(message.chat.id)
        except QueueEmpty:
            pass

        await callsmusic.stop(message.chat.id)
        await message.reply_text("✅ Menghapus playlist dan bot telah keluar dari voice chat!")


@Client.on_message(command(["skip", f"skip@{BOT_USERNAME}", "s"]))
@errors
@authorized_users_only
async def skip(_, message: Message):
    if message.chat.id not in callsmusic.active_chats:
        await message.reply_text("❗️ Gak ada lagu yang dimainin")
    else:
        queues.task_done(message.chat.id)

        if queues.is_empty(message.chat.id):
            await callsmusic.stop(message.chat.id)
        else:
            await callsmusic.set_stream(
                message.chat.id, queues.get(message.chat.id)["file"]
            )

        await message.reply_text("🗑 Skipped")


@Client.on_message(command(["mute", f"mute@{BOT_USERNAME}", "m"]))
@errors
@authorized_users_only
async def mute(_, message: Message):
    result = callsmusic.mute(message.chat.id)

    if result == 0:
        await message.reply_text("🔇 Berhenti")
    elif result == 1:
        await message.reply_text("🔇 Sudah Berhenti")
    elif result == 2:
        await message.reply_text("❗️ Bot belum masuk voice chat tot")


@Client.on_message(command(["unmute", f"unmute@{BOT_USERNAME}", "um"]))
@errors
@authorized_users_only
async def unmute(_, message: Message):
    result = callsmusic.unmute(message.chat.id)

    if result == 0:
        await message.reply_text("🔈 Senyap")
    elif result == 1:
        await message.reply_text("🔈 Sudah Senyap")
    elif result == 2:
        await message.reply_text("❗️ Bot belum masuk voice chat tot")


# Music Player Callbacks (Control by buttons feature)

@Client.on_callback_query(filters.regex("cbpause"))
async def cbpause(_, query: CallbackQuery):
    if callsmusic.pause(query.message.chat.id):
        await query.edit_message_text("⏸ Lagu diberhentikan", reply_markup=BACK_BUTTON)
    else:
        await query.edit_message_text("❗️ Gak ada lagu yang dimulai tolol!", reply_markup=BACK_BUTTON)

@Client.on_callback_query(filters.regex("cbresume"))
async def cbresume(_, query: CallbackQuery):
    if callsmusic.resume(query.message.chat.id):
        await query.edit_message_text("🎧 Dimulai", reply_markup=BACK_BUTTON)
    else:
        await query.edit_message_text("❗️ Gak ada yang di berhentikan tolol!", reply_markup=BACK_BUTTON)

@Client.on_callback_query(filters.regex("cbend"))
async def cbend(_, query: CallbackQuery):
    if query.message.chat.id not in callsmusic.active_chats:
        await query.edit_message_text("❗️ Gak ada lagu yang dimulai tolol", reply_markup=BACK_BUTTON)
    else:
        try:
            queues.clear(query.message.chat.id)
        except QueueEmpty:
            pass

        await callsmusic.stop(query.message.chat.id)
        await query.edit_message_text("✅ Menghapus playlist dan bot telah keluar dari voice chat!", reply_markup=BACK_BUTTON)

@Client.on_callback_query(filters.regex("cbskip"))
async def cbskip(_, query: CallbackQuery):
     if query.message.chat.id not in callsmusic.active_chats:
        await query.edit_message_text("❗️ Gak ada lagu yang dimulai tolol!", reply_markup=BACK_BUTTON)
     else:
        queues.task_done(query.message.chat.id)
        
        if queues.is_empty(query.message.chat.id):
            await callsmusic.stop(query.message.chat.id)
        else:
            await callsmusic.set_stream(
                query.message.chat.id, queues.get(query.message.chat.id)["file"]
            )

        await query.edit_message_text("🗑 Skipped", reply_markup=BACK_BUTTON)

@Client.on_callback_query(filters.regex("cbmute"))
async def cbmute(_, query: CallbackQuery):
    result = callsmusic.mute(query.message.chat.id)

    if result == 0:
        await query.edit_message_text("🔇 Berhenti", reply_markup=BACK_BUTTON)
    elif result == 1:
        await query.edit_message_text("🔇 Sudah Berhenti", reply_markup=BACK_BUTTON)
    elif result == 2:
        await query.edit_message_text("❗️ Bot belum masuk voice chat tot!.", reply_markup=BACK_BUTTON)

@Client.on_callback_query(filters.regex("cbunmute"))
async def cbunmute(_, query: CallbackQuery):
    result = callsmusic.unmute(query.message.chat.id)

    if result == 0:
        await query.edit_message_text("🔈 senyap", reply_markup=BACK_BUTTON)
    elif result == 1:
        await query.edit_message_text("🔈 Sudah Senyap", reply_markup=BACK_BUTTON)
    elif result == 2:
        await query.edit_message_text("❗️ Gak ada voice chat", reply_markup=BACK_BUTTON)


# Anti-Command Feature On/Off

@Client.on_message(filters.command(["delcmd", f"delcmd@{BOT_USERNAME}"]) & ~filters.private)
@authorized_users_only
async def delcmdc(_, message: Message):
    if len(message.command) != 2:
        await message.reply_text("Woi tolol bukan gitu cara gunain commandnya 😂! Baca dulu maknya **/help** ☺️")
        return
    status = message.text.split(None, 1)[1].strip()
    status = status.lower()
    chat_id = message.chat.id
    if status == "on":
        if await delcmd_is_on(message.chat.id):
            await message.reply_text("Woe! kamu sudah mengaktifkan layanan ini 😉")
            return
        else:
            await delcmd_on(chat_id)
            await message.reply_text(
                "Sukses mengatur hapus command di chat ini 😇"
            )
    elif status == "off":
        await delcmd_off(chat_id)
        await message.reply_text("Sukses mematikan hapus command di chat ini 😌")
    else:
        await message.reply_text(
            "Gw gak ngerti lu merintahin apa! Baca **/help** 🤔"
        )
