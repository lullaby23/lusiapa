# A Plugin From Daisyxmusic (Telegram bot project)
# Copyright (C) 2021  Inukaasith

from callsmusic.callsmusic import client as USER
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors import UserAlreadyParticipant
from helpers.decorators import errors, authorized_users_only

@Client.on_message(filters.group & filters.command(["joingrp"]))
@authorized_users_only
@errors
async def addchannel(client, message):
    chid = message.chat.id
    try:
        invitelink = await client.export_chat_invite_link(chid)
    except:
        await message.reply_text(
            "<b>tf? Jadiin gw admin dulu tolol!</b> 😄",
        )
        return

    try:
        user = await USER.get_me()
    except:
        user.first_name =  "TG - VC Music Bot" # F this

    try:
        await USER.join_chat(invitelink)
        await USER.send_message(message.chat.id,"Ok! Saya sudah masuk sesuai request mu, jangan spam lagi anjeng! 😂")
    except UserAlreadyParticipant:
        await message.reply_text(
            "<b>Gw sudah ada di group cok!</b> Jangan kaya <b>Bocil</b> 😒",
        )
        pass
    except Exception as e:
        print(e)
        await message.reply_text(
            f"Shit! <b>❌ Flood Wait Error ❌ \n Sorry! user {user.first_name} Maaf gw gk bisa masuk chat karena banyak yang merintah gw! Jangan sampe gw di ban dari group lu tot. ✅"
            "\n\nOr you can manually add @{(await USER.get_me()).username} to your Group!</b> 😉",
        )
        return
    await message.reply_text(
            "<b>Bot Telah bergabung</b> 😊",
        )

# Remove Bot and Streamer Account From the group
@Client.on_message(filters.group & filters.command(["leavegrp"]))
@authorized_users_only
async def botleavegrp(client, message):
    await message.chat.leave()

@USER.on_message(filters.group & filters.command(["leavegrp"]))
async def strmleavegrp(USER, message):
    try:
        await USER.leave_chat(message.chat.id)
    except:
        await message.reply_text(
            f"<b>Oops! Gw gk bisa keluar dari voice chat banyak yang merintah gw sih 🤔"
            "\n\nAtau kamubisa keluarin gwsecara manual @{(await USER.get_me()).username} 🤗</b>",
        )
        return
