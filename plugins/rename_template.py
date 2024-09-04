from pyrogram import Client, filters
from pyrogram.types import *
from helper.database import db
from pyromod.exceptions import ListenerTimeout


async def cancelled(message):
    if "/cancel" in message.text:
        await message.reply_text("**Process Cancelled.**")
        return True
    else:
        return False


@Client.on_message(
    filters.private & filters.command(["setrenameformats", "setrenameformat"])
)
async def setrenameformats(client: Client, message: Message):
    user_id = message.from_user.id
    try:
        askformat = await client.ask(
            chat_id=user_id,
            text="__**Send the rename format**__ **/cancel - cancel this process**",
            filters=filters.text,
            timeout=120,
        )
        if await cancelled(askformat):
            return
    except ListenerTimeout:
        await message.reply_text(
            "**You took too long..**\n\n⚠️ Restart by sending /SetRenameFormats"
        )
        return

    try:
        asktriggerr = await client.ask(
            chat_id=user_id,
            text="__**Send the trigger word**__ **/cancel - cancel this process**",
            filters=filters.text,
            timeout=120,
        )
        if await cancelled(asktriggerr):
            return
    except ListenerTimeout:
        await message.reply_text(
            "**You took too long..**\n\n⚠️ Restart by sending /SetRenameFormats"
        )
        return

    try:
        askchannel = await client.ask(
            chat_id=user_id,
            text="__**❪ SET TARGET CHAT ❫\n\n**Forward a message from Your target chat /cancel - cancel this process or /no to avoid adding channel**",
            timeout=120,
        )
        if await cancelled(askchannel):
            return

        if askchannel.text == "/no":
            askchannel = None
        else:
            askchannel = askchannel.forward_from_chat.id

    except ListenerTimeout:
        await message.reply_text(
            "**You took too long..**\n\n⚠️ Restart by sending /SetRenameFormats"
        )
        return

    check = await db.set_rename_template(
        user_id, askformat.text, asktriggerr.text, askchannel
    )

    if not check:
        return await message.reply_text(
            "⚠️ **Be cautious make sure your trigger word is unique otherwise it'll conflict with files if same trigger word found in different files**\n\nTry Again..."
        )

    await message.reply_text(
        "**Your Format and Trigger has been saved Saved Successfully ✅**\n\n**To see all the saved formats send /SeeFormats**"
    )


@Client.on_message(filters.private & filters.command(["seeformats", "seeformat"]))
async def getformats(client: Client, message: Message):
    user_id = message.from_user.id
    template = await db.get_rename_templates(user_id)

    if not template:
        return await message.reply_text("**You haven't saved any formats yet. 😑**")

    saved = ""
    
    for index, (key, value) in enumerate(template.items()):

        try:
            channelInfo = await client.get_chat(int(value[1]))
            title = channelInfo.title
        except:
            if not value[1]:
                title = "Not Set"
            else:
                title = f"Not Admin ({value[1]})"

        saved += "**Format {}:** `{}`\n**Trigger {}:** `{}`\n**Channel {}:** `{}`\n\n".format(
            index + 1, value[0], index + 1, key, index + 1, title
        )

    await message.reply_text(saved)


@Client.on_message(filters.private & filters.command(["delformats", "delformat"]))
async def delformats(client: Client, message: Message):
    user_id = message.from_user.id

    if len(message.command) == 1:
        await db.remove_rename_template(user_id)
        return await message.reply_text("**All Formats Deleted Successfully ✅**")

    else:
        await db.remove_rename_template(user_id, message.command[1])
        return await message.reply_text(
            f"**The Format Related To This `{message.command[1]}` Trigger Has Been Deleted Successfully ✅**"
        )
