from pyrogram import Client, filters
from config import Txt
from helper.database import db

@Client.on_message(filters.private & filters.command("autorename"))
async def auto_rename_command(client, message):
    user_id = message.from_user.id

    # Checking if the user has use command properly or not
    if len(message.command) == 1:
        format_template = await db.get_format_template(user_id)
        return await message.reply_text(Txt.FILE_NAME_TXT.format(format_template=format_template if format_template else "Not Set Yet"),  reply_to_message_id = message.id)
    
    # Extract the format from the command
    format_template = message.text.split("/autorename", 1)[1].strip()

    # Save the format template to the database
    await db.set_format_template(user_id, format_template)

    await message.reply_text("**Auto Rename Format Updated Successfully! ✅**", reply_to_message_id = message.id)