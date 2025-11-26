from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from helper.helper_func import encode, get_message_id
from config import LOGGER

async def get_db_channels_info(client):
    """Get formatted database channels information with links"""
    db_channels = getattr(client, 'db_channels', {})
    primary_db = getattr(client, 'primary_db_channel', client.db)
    
    if not db_channels:
        # If no additional DB channels, show primary only
        try:
            primary_chat = await client.get_chat(primary_db)
            if hasattr(primary_chat, 'invite_link') and primary_chat.invite_link:
                return f"<blockquote>✦ ᴘʀɪᴍᴀʀʏ ᴅʙ ᴄʜᴀɴɴᴇʟ: <a href='{primary_chat.invite_link}'>{primary_chat.title}</a></blockquote>"
            else:
                return f"<blockquote>✦ ᴘʀɪᴍᴀʀʏ ᴅʙ ᴄʜᴀɴɴᴇʟ: {primary_chat.title} (`{primary_db}`)</blockquote>"
        except:
            return f"<blockquote>✦ ᴘʀɪᴍᴀʀʏ ᴅʙ ᴄʜᴀɴɴᴇʟ: `{primary_db}`</blockquote>"
    
    # Format all DB channels with links
    channels_info = ["<blockquote>✦ ᴀᴠᴀɪʟᴀʙʟᴇ ᴅᴀᴛᴀʙᴀsᴇ ᴄʜᴀɴɴᴇʟs:</blockquote>"]
    for channel_id_str, channel_data in db_channels.items():
        channel_name = channel_data.get('name', 'ᴜɴᴋɴᴏᴡɴ')
        is_primary_text = "✦ ᴘʀɪᴍᴀʀʏ" if channel_data.get('is_primary', False) else "• sᴇᴄᴏɴᴅᴀʀʏ"
        
        try:
            chat = await client.get_chat(int(channel_id_str))
            if hasattr(chat, 'invite_link') and chat.invite_link:
                channels_info.append(f"{is_primary_text}: <a href='{chat.invite_link}'>{channel_name}</a>")
            else:
                channels_info.append(f"{is_primary_text}: {channel_name} (`{channel_id_str}`)")
        except:
            channels_info.append(f"{is_primary_text}: {channel_name} (`{channel_id_str}`)")
    
    return "\n".join(channels_info)

@Client.on_message(filters.private & filters.command('batch'))
async def batch(client: Client, message: Message):
    if message.from_user.id not in client.admins:
        return await message.reply(client.reply_text)
    
    # Get all database channels with links
    db_channels_info = await get_db_channels_info(client)
    
    batch_image_mode = getattr(client, 'batch_image_mode', True)
    custom_image_url = None
    
    if batch_image_mode:
        try:
            image_choice = await client.ask(
                text="**Do you want to use a custom verification image for this batch?**\n\nSend: YES or NO",
                chat_id=message.from_user.id,
                filters=filters.text,
                timeout=60
            )
            
            if image_choice.text.upper() in ['YES', 'Y']:
                image_msg = await client.ask(
                    text="**Send the verification image URL:**",
                    chat_id=message.from_user.id,
                    filters=filters.text,
                    timeout=60
                )
                custom_image_url = image_msg.text.strip()
        except:
            pass
    
    while True:
        try:
            first_message = await client.ask(
                text=f"""<blockquote>ꜰᴏʀᴡᴀʀᴅ ᴛʜᴇ ꜰɪʀsᴛ ᴍᴇssᴀɢᴇ ꜰʀᴏᴍ ᴅʙ ᴄʜᴀɴɴᴇʟ (ᴡɪᴛʜ ǫᴜᴏᴛᴇs)..</blockquote>
{db_channels_info}

<blockquote>ᴏʀ sᴇɴᴅ ᴛʜᴇ ᴅʙ ᴄʜᴀɴɴᴇʟ ᴘᴏsᴛ ʟɪɴᴋ</blockquote>""",
                chat_id=message.from_user.id,
                filters=(filters.forwarded | (filters.text & ~filters.forwarded)),
                timeout=60
            )
        except:
            return
        f_msg_id, source_channel_id = await get_message_id(client, first_message)
        if f_msg_id:
            break
        else:
            await first_message.reply("<blockquote>✗ ᴇʀʀᴏʀ</blockquote>\n\nᴛʜɪs ꜰᴏʀᴡᴀʀᴅᴇᴅ ᴘᴏsᴛ ɪs ɴᴏᴛ ꜰʀᴏᴍ ᴍʏ ᴅʙ ᴄʜᴀɴɴᴇʟ ᴏʀ ᴛʜɪs ʟɪɴᴋ ɪs ᴛᴀᴋᴇɴ ꜰʀᴏᴍ ᴅʙ ᴄʜᴀɴɴᴇʟ", quote = True)
            continue

    while True:
        try:
            second_message = await client.ask(
                text=f"""<blockquote>ꜰᴏʀᴡᴀʀᴅ ᴛʜᴇ ʟᴀsᴛ ᴍᴇssᴀɢᴇ ꜰʀᴏᴍ ᴅʙ ᴄʜᴀɴɴᴇʟ (ᴡɪᴛʜ ǫᴜᴏᴛᴇs)..</blockquote>
{db_channels_info}

<blockquote>ᴏʀ sᴇɴᴅ ᴛʜᴇ ᴅʙ ᴄʜᴀɴɴᴇʟ ᴘᴏsᴛ ʟɪɴᴋ</blockquote>""",
                chat_id=message.from_user.id,
                filters=(filters.forwarded | (filters.text & ~filters.forwarded)),
                timeout=60
            )
        except:
            return
        s_msg_id, _ = await get_message_id(client, second_message)  # We only need msg_id for second message
        if s_msg_id:
            break
        else:
            await second_message.reply("<blockquote>✗ ᴇʀʀᴏʀ</blockquote>\n\nᴛʜɪs ꜰᴏʀᴡᴀʀᴅᴇᴅ ᴘᴏsᴛ ɪs ɴᴏᴛ ꜰʀᴏᴍ ᴍʏ ᴅʙ ᴄʜᴀɴɴᴇʟ ᴏʀ ᴛʜɪs ʟɪɴᴋ ɪs ᴛᴀᴋᴇɴ ꜰʀᴏᴍ ᴅʙ ᴄʜᴀɴɴᴇʟ", quote = True)
            continue

    # Use the source channel ID for encoding instead of default primary channel
    client.LOGGER(__name__, client.name).info(f"Generating batch link with source channel: {source_channel_id}, first_msg: {f_msg_id}, last_msg: {s_msg_id}")
    string = f"get-{f_msg_id * abs(source_channel_id)}-{s_msg_id * abs(source_channel_id)}"
    base64_string = await encode(string)
    link = f"https://t.me/{client.username}?start={base64_string}"
    
    if custom_image_url:
        await client.mongodb.store_batch_verification_image(base64_string, custom_image_url)
    
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔁 sʜᴀʀᴇ ᴜʀʟ", url=f'https://telegram.me/share/url?url={link}')]])
    await second_message.reply_text(f"<blockquote>✓ ʜᴇʀᴇ ɪs ʏᴏᴜʀ ʙᴀᴛᴄʜ ʟɪɴᴋ</blockquote>\n\n<code>{link}</code>", quote=True, reply_markup=reply_markup)

#===============================================================#

@Client.on_message(filters.private & filters.command('genlink'))
async def link_generator(client: Client, message: Message):
    if message.from_user.id not in client.admins:
        return await message.reply(client.reply_text)
    
    # Get all database channels with links
    db_channels_info = await get_db_channels_info(client)
    
    batch_image_mode = getattr(client, 'batch_image_mode', True)
    custom_image_url = None
    
    if batch_image_mode:
        try:
            image_choice = await client.ask(
                text="**Do you want to use a custom verification image for this file?**\n\nSend: YES or NO",
                chat_id=message.from_user.id,
                filters=filters.text,
                timeout=60
            )
            
            if image_choice.text.upper() in ['YES', 'Y']:
                image_msg = await client.ask(
                    text="**Send the verification image URL:**",
                    chat_id=message.from_user.id,
                    filters=filters.text,
                    timeout=60
                )
                custom_image_url = image_msg.text.strip()
        except:
            pass
    
    while True:
        try:
            channel_message = await client.ask(
                text=f"""<blockquote>ꜰᴏʀᴡᴀʀᴅ ᴍᴇssᴀɢᴇ ꜰʀᴏᴍ ᴛʜᴇ ᴅʙ ᴄʜᴀɴɴᴇʟ (ᴡɪᴛʜ ǫᴜᴏᴛᴇs)..</blockquote>

{db_channels_info}

<blockquote>ᴏʀ sᴇɴᴅ ᴛʜᴇ ᴅʙ ᴄʜᴀɴɴᴇʟ ᴘᴏsᴛ ʟɪɴᴋ</blockquote>""",
                chat_id=message.from_user.id,
                filters=(filters.forwarded | (filters.text & ~filters.forwarded)),
                timeout=60
            )
        except:
            return
        msg_id, source_channel_id = await get_message_id(client, channel_message)
        if msg_id:
            break
        else:
            await channel_message.reply("<blockquote>✗ ᴇʀʀᴏʀ</blockquote>\n\nᴛʜɪs ꜰᴏʀᴡᴀʀᴅᴇᴅ ᴘᴏsᴛ ɪs ɴᴏᴛ ꜰʀᴏᴍ ᴍʏ ᴅʙ ᴄʜᴀɴɴᴇʟ ᴏʀ ᴛʜɪs ʟɪɴᴋ ɪs ɴᴏᴛ ᴛᴀᴋᴇɴ ꜰʀᴏᴍ ᴅʙ ᴄʜᴀɴɴᴇʟ", quote = True)
            continue

    base64_string = await encode(f"get-{msg_id * abs(source_channel_id)}")
    link = f"https://t.me/{client.username}?start={base64_string}"
    
    if custom_image_url:
        await client.mongodb.store_file_verification_image(base64_string, custom_image_url)
    
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔁 sʜᴀʀᴇ ᴜʀʟ", url=f'https://telegram.me/share/url?url={link}')]])
    await channel_message.reply_text(f"<blockquote>✓ ʜᴇʀᴇ ɪs ʏᴏᴜʀ ʟɪɴᴋ</blockquote>\n\n<code>{link}</code>", quote=True, reply_markup=reply_markup)

#===============================================================#

@Client.on_message(filters.private & filters.command("nbatch"))
async def nbatch(client: Client, message: Message):
    if message.from_user.id not in client.admins:
        return await message.reply(client.reply_text)
    
    args = message.text.split()
    if len(args) < 2 or not args[1].isdigit():
        await message.reply("<blockquote>✗ ɪɴᴠᴀʟɪᴅ ꜰᴏʀᴍᴀᴛ!</blockquote> ᴜsᴇ: /nbatch {number}")
        return
    
    batch_size = int(args[1])
    
    # Get all database channels with links
    db_channels_info = await get_db_channels_info(client)
    
    while True:
        try:
            first_message = await client.ask(
                text=f"""<blockquote>🚀 sᴇɴᴅ ᴅʙ ᴄʜᴀɴɴᴇʟ ꜰɪʀsᴛ ᴍᴇssᴀɢᴇ ʟɪɴᴋ (ᴡɪᴛʜ ǫᴜᴏᴛᴇs)...</blockquote>

{db_channels_info}""",
                chat_id=message.from_user.id,
                filters=(filters.text & ~filters.forwarded),
                timeout=60
            )
        except:
            return
    
        f_msg_id, source_channel_id = await get_message_id(client, first_message)
        if f_msg_id:
            break
        else:
            await first_message.reply("<blockquote>😫 ɪɴᴠᴀʟɪᴅ!</blockquote> sᴇɴᴅ ᴄᴏʀʀᴇᴄᴛ ᴅʙ ᴄʜᴀɴɴᴇʟ ᴍᴇssᴀɢᴇ ʟɪɴᴋ.", quote=True)
            continue
    
    s_msg_id = f_msg_id + batch_size - 1  # Adding batch_size to first message ID
    
    string = f"get-{f_msg_id * abs(source_channel_id)}-{s_msg_id * abs(source_channel_id)}"
    base64_string = await encode(string)
    link = f"https://t.me/{client.username}?start={base64_string}"
    
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("📫 ʏᴏᴜʀ ʙᴀᴛᴄʜ ᴜʀʟ", url=f'https://telegram.me/share/url?url={link}')]
    ])
    
    await first_message.reply_text(f"<blockquote>✓ ʜᴇʀᴇ ɪs ʏᴏᴜʀ ʙᴀᴛᴄʜ ʟɪɴᴋ</blockquote>\n\n<code>{link}</code>", quote=True, reply_markup=reply_markup)
