import requests
import random
import string
from config import SHORT_URL, SHORT_API, MESSAGES
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputMediaPhoto
from pyrogram.errors.pyromod import ListenerTimeout
from helper.helper_func import force_sub

# ✅ In-memory cache
shortened_urls_cache = {}

def generate_random_alphanumeric():
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(8))

def get_short(url, client):

    # Check if shortner is enabled
    shortner_enabled = getattr(client, 'shortner_enabled', True)
    if not shortner_enabled:
        return url  # Return original URL if shortner is disabled

    # Step 2: Check cache
    if url in shortened_urls_cache:
        return shortened_urls_cache[url]

    try:
        alias = generate_random_alphanumeric()
        # Use dynamic shortner settings from client if available
        short_url = getattr(client, 'short_url', SHORT_URL)
        short_api = getattr(client, 'short_api', SHORT_API)
        
        api_url = f"https://{short_url}/api?api={short_api}&url={url}&alias={alias}"
        response = requests.get(api_url)
        rjson = response.json()

        if rjson.get("status") == "success" and response.status_code == 200:
            short_url = rjson.get("shortenedUrl", url)
            shortened_urls_cache[url] = short_url
            return short_url
    except Exception as e:
        print(f"[Shortener Error] {e}")

    return url  # fallback

#===============================================================#

@Client.on_message(filters.command('shortner') & filters.private)
async def shortner_command(client: Client, message: Message):
    await shortner_panel(client, message)

#===============================================================#

async def shortner_panel(client, query_or_message):
    shortner1_domain = getattr(client, 'shortner1_domain', SHORT_URL)
    shortner1_api = getattr(client, 'shortner1_api', SHORT_API)
    verify_time_1 = getattr(client, 'verify_time_1', 60)
    verify1_mode = getattr(client, 'verify1_mode', True)
    
    shortner2_domain = getattr(client, 'shortner2_domain', '')
    shortner2_api = getattr(client, 'shortner2_api', '')
    verify_time_2 = getattr(client, 'verify_time_2', 60)
    verify2_mode = getattr(client, 'verify2_mode', False)
    
    gap_time = getattr(client, 'gap_time', 300)
    default_verification_image = getattr(client, 'default_verification_image', '')
    per_file_image_mode = getattr(client, 'per_file_image_mode', True)
    batch_image_mode = getattr(client, 'batch_image_mode', True)
    
    verify1_text = "✓ ᴏɴ" if verify1_mode else "✗ ᴏғғ"
    verify2_text = "✓ ᴏɴ" if verify2_mode else "✗ ᴏғғ"
    per_file_text = "✓ ᴏɴ" if per_file_image_mode else "✗ ᴏғғ"
    batch_text = "✓ ᴏɴ" if batch_image_mode else "✗ ᴏғғ"
    
    default_img_status = "✓ sᴇᴛ" if default_verification_image else "✗ ɴᴏᴛ sᴇᴛ"
    
    msg = f"""<blockquote>✦ 𝗗𝗨𝗔𝗟 𝗩𝗘𝗥𝗜𝗙𝗜𝗖𝗔𝗧𝗜𝗢𝗡 & 𝗦𝗛𝗢𝗥𝗧𝗘𝗡𝗘𝗥 𝗦𝗘𝗧𝗧𝗜𝗡𝗚𝗦</blockquote>

**ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ 1:**
• sᴛᴀᴛᴜs: {verify1_text}
• ᴛɪᴍᴇ: `{verify_time_1}s`
• ᴅᴏᴍᴀɪɴ: `{shortner1_domain[:15]}...`

**ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ 2:**
• sᴛᴀᴛᴜs: {verify2_text}
• ᴛɪᴍᴇ: `{verify_time_2}s`
• ᴅᴏᴍᴀɪɴ: `{shortner2_domain if shortner2_domain else 'ɴᴏᴛ sᴇᴛ'}`

**ɢᴀᴘ ᴛɪᴍᴇ:** `{gap_time}s`

**ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ ɪᴍᴀɢᴇs:**
• ᴅᴇғᴀᴜʟᴛ ɪᴍᴀɢᴇ: {default_img_status}
• ᴘᴇʀ-ғɪʟᴇ ɪᴍᴀɢᴇ: {per_file_text}
• ʙᴀᴛᴄʜ ɪᴍᴀɢᴇ: {batch_text}"""
    
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton('• ᴠᴇʀɪғ 1 sᴇᴛᴛɪɴɢs •', 'verify1_settings'), InlineKeyboardButton('• ᴠᴇʀɪғ 2 sᴇᴛᴛɪɴɢs •', 'verify2_settings')],
        [InlineKeyboardButton('• ɢᴀᴘ ᴛɪᴍᴇ •', 'set_gap_time'), InlineKeyboardButton('• ɪᴍᴀɢᴇ sᴇᴛᴛɪɴɢs •', 'image_settings')],
        [InlineKeyboardButton('• ʀᴇsᴇᴛ ᴀʟʟ •', 'reset_shortner')],
        [InlineKeyboardButton('◂ ʙᴀᴄᴋ ᴛᴏ ꜱᴇᴛᴛɪɴɢꜱ', 'settings')] if hasattr(query_or_message, 'message') else []
    ])
    
    image_url = MESSAGES.get("SHORT", "https://telegra.ph/file/8aaf4df8c138c6685dcee-05d3b183d4978ec347.jpg")
    
    if hasattr(query_or_message, 'message'):
        await query_or_message.message.edit_media(
            media=InputMediaPhoto(media=image_url, caption=msg),
            reply_markup=reply_markup
        )
    else:
        await query_or_message.reply_photo(photo=image_url, caption=msg, reply_markup=reply_markup)


#===============================================================#

@Client.on_callback_query(filters.regex("^shortner$"))
async def shortner_callback(client, query):
    if not query.from_user.id in client.admins:
        return await query.answer('❌ ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ!', show_alert=True)
    await query.answer()
    await shortner_panel(client, query)

#===============================================================#
@Client.on_callback_query(filters.regex("^verify1_settings$"))
async def verify1_settings(client: Client, query: CallbackQuery):
    if not query.from_user.id in client.admins:
        return await query.answer('❌ ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ!', show_alert=True)
    
    await query.answer()
    
    shortner1_domain = getattr(client, 'shortner1_domain', SHORT_URL)
    shortner1_api = getattr(client, 'shortner1_api', SHORT_API)
    verify_time_1 = getattr(client, 'verify_time_1', 60)
    verify1_mode = getattr(client, 'verify1_mode', True)
    
    verify1_text = "✓ ᴇɴᴀʙʟᴇᴅ" if verify1_mode else "✗ ᴅɪsᴀʙʟᴇᴅ"
    toggle_text = "✗ ᴏғғ" if verify1_mode else "✓ ᴏɴ"
    
    msg = f"""<blockquote>✦ ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ 1 sᴇᴛᴛɪɴɢs</blockquote>
• **sᴛᴀᴛᴜs:** {verify1_text}
• **ᴛɪᴍᴇ:** `{verify_time_1}s`
• **ᴅᴏᴍᴀɪɴ:** `{shortner1_domain}`
• **ᴀᴘɪ:** `{shortner1_api[:20]}...` {'✓' if shortner1_api else '✗'}"""
    
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton(f'• {toggle_text} ᴠᴇʀɪғ 1 •', 'toggle_verify1'), InlineKeyboardButton('• sᴇᴛ ᴛɪᴍᴇ •', 'set_time1')],
        [InlineKeyboardButton('• sᴇᴛ ᴀᴘɪ/ᴅᴏᴍᴀɪɴ •', 'set_api1')],
        [InlineKeyboardButton('‹ ʙᴀᴄᴋ', 'shortner')]
    ])
    
    await query.message.edit_text(msg, reply_markup=reply_markup)

#===============================================================#
@Client.on_callback_query(filters.regex("^verify2_settings$"))
async def verify2_settings(client: Client, query: CallbackQuery):
    if not query.from_user.id in client.admins:
        return await query.answer('❌ ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ!', show_alert=True)
    
    await query.answer()
    
    shortner2_domain = getattr(client, 'shortner2_domain', '')
    shortner2_api = getattr(client, 'shortner2_api', '')
    verify_time_2 = getattr(client, 'verify_time_2', 60)
    verify2_mode = getattr(client, 'verify2_mode', False)
    
    verify2_text = "✓ ᴇɴᴀʙʟᴇᴅ" if verify2_mode else "✗ ᴅɪsᴀʙʟᴇᴅ"
    toggle_text = "✗ ᴏғғ" if verify2_mode else "✓ ᴏɴ"
    
    msg = f"""<blockquote>✦ ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ 2 sᴇᴛᴛɪɴɢs</blockquote>
• **sᴛᴀᴛᴜs:** {verify2_text}
• **ᴛɪᴍᴇ:** `{verify_time_2}s`
• **ᴅᴏᴍᴀɪɴ:** `{shortner2_domain if shortner2_domain else 'ɴᴏᴛ sᴇᴛ'}`
• **ᴀᴘɪ:** `{shortner2_api[:20]}...` {'✓' if shortner2_api else '✗'}"""
    
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton(f'• {toggle_text} ᴠᴇʀɪғ 2 •', 'toggle_verify2'), InlineKeyboardButton('• sᴇᴛ ᴛɪᴍᴇ •', 'set_time2')],
        [InlineKeyboardButton('• sᴇᴛ ᴀᴘɪ/ᴅᴏᴍᴀɪɴ •', 'set_api2')],
        [InlineKeyboardButton('‹ ʙᴀᴄᴋ', 'shortner')]
    ])
    
    await query.message.edit_text(msg, reply_markup=reply_markup)

#===============================================================#
@Client.on_callback_query(filters.regex("^image_settings$"))
async def image_settings(client: Client, query: CallbackQuery):
    if not query.from_user.id in client.admins:
        return await query.answer('❌ ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ!', show_alert=True)
    
    await query.answer()
    
    default_verification_image = getattr(client, 'default_verification_image', '')
    per_file_image_mode = getattr(client, 'per_file_image_mode', True)
    batch_image_mode = getattr(client, 'batch_image_mode', True)
    
    per_file_text = "✓ ᴏɴ" if per_file_image_mode else "✗ ᴏғғ"
    batch_text = "✓ ᴏɴ" if batch_image_mode else "✗ ᴏғғ"
    default_img_status = "✓ sᴇᴛ" if default_verification_image else "✗ ɴᴏᴛ sᴇᴛ"
    
    msg = f"""<blockquote>✦ ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ ɪᴍᴀɢᴇ sᴇᴛᴛɪɴɢs</blockquote>

• **ᴅᴇғᴀᴜʟᴛ ɪᴍᴀɢᴇ:** {default_img_status}
• **ᴘᴇʀ-ғɪʟᴇ ɪᴍᴀɢᴇ:** {per_file_text}
• **ʙᴀᴛᴄʜ ɪᴍᴀɢᴇ:** {batch_text}"""
    
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton('• sᴇᴛ ᴅᴇғᴀᴜʟᴛ ɪᴍᴀɢᴇ •', 'set_default_image')],
        [InlineKeyboardButton(f'• {per_file_text} ᴘᴇʀ-ғɪʟᴇ •', 'toggle_per_file_image')],
        [InlineKeyboardButton(f'• {batch_text} ʙᴀᴛᴄʜ •', 'toggle_batch_image')],
        [InlineKeyboardButton('• ʀᴇsᴇᴛ ᴅᴇғᴀᴜʟᴛ •', 'reset_default_image')],
        [InlineKeyboardButton('‹ ʙᴀᴄᴋ', 'shortner')]
    ])
    
    await query.message.edit_text(msg, reply_markup=reply_markup)

#===============================================================#
@Client.on_callback_query(filters.regex("^toggle_verify1$"))
async def toggle_verify1(client: Client, query: CallbackQuery):
    if not query.from_user.id in client.admins:
        return await query.answer('❌ ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ!', show_alert=True)
    
    await query.answer()
    
    current_status = getattr(client, 'verify1_mode', True)
    new_status = not current_status
    client.verify1_mode = new_status
    
    await client.mongodb.update_shortner_setting('verify1_mode', new_status)
    
    status_text = "ᴇɴᴀʙʟᴇᴅ" if new_status else "ᴅɪsᴀʙʟᴇᴅ"
    await query.answer(f"✓ ᴠᴇʀɪғ 1 {status_text}!")
    
    await verify1_settings(client, query)

#===============================================================#
@Client.on_callback_query(filters.regex("^toggle_verify2$"))
async def toggle_verify2(client: Client, query: CallbackQuery):
    if not query.from_user.id in client.admins:
        return await query.answer('❌ ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ!', show_alert=True)
    
    await query.answer()
    
    current_status = getattr(client, 'verify2_mode', False)
    new_status = not current_status
    client.verify2_mode = new_status
    
    await client.mongodb.update_shortner_setting('verify2_mode', new_status)
    
    status_text = "ᴇɴᴀʙʟᴇᴅ" if new_status else "ᴅɪsᴀʙʟᴇᴅ"
    await query.answer(f"✓ ᴠᴇʀɪғ 2 {status_text}!")
    
    await verify2_settings(client, query)

#===============================================================#
@Client.on_callback_query(filters.regex("^set_time1$"))
async def set_time1(client: Client, query: CallbackQuery):
    if not query.from_user.id in client.admins:
        return await query.answer('❌ ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ!', show_alert=True)
    
    await query.answer()
    
    current_time = getattr(client, 'verify_time_1', 60)
    msg = f"""**sᴇᴛ ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ 1 ᴛɪᴍᴇ:**

**ᴄᴜʀʀᴇɴᴛ ᴛɪᴍᴇ:** `{current_time}` sᴇᴄᴏɴᴅs

__sᴇɴᴅ ᴀ ɴᴜᴍʙᴇʀ (ɪɴ sᴇᴄᴏɴᴅs) ɪɴ ᴛʜᴇ ɴᴇxᴛ 60 sᴇᴄᴏɴᴅs!__"""
    
    await query.message.edit_text(msg)
    try:
        res = await client.listen(user_id=query.from_user.id, filters=filters.text, timeout=60)
        if res.text.isdigit():
            new_time = int(res.text)
            if 10 <= new_time <= 3600:
                client.verify_time_1 = new_time
                await client.mongodb.update_shortner_setting('verify_time_1', new_time)
                await query.message.edit_text(f"**✓ ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ 1 ᴛɪᴍᴇ sᴇᴛ ᴛᴏ:** `{new_time}s`", 
                                            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'verify1_settings')]]))
            else:
                await query.message.edit_text("**✗ ᴠᴀʟᴜᴇ ᴍᴜsᴛ ʙᴇ ʙᴇᴛᴡᴇᴇɴ 10 ᴀɴᴅ 3600 sᴇᴄᴏɴᴅs!**", 
                                            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'verify1_settings')]]))
        else:
            await query.message.edit_text("**✗ ᴘʟᴇᴀsᴇ sᴇɴᴅ ᴀ ᴠᴀʟɪᴅ ɴᴜᴍʙᴇʀ!**", 
                                        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'verify1_settings')]]))
    except ListenerTimeout:
        await query.message.edit_text("**⏰ ᴛɪᴍᴇᴏᴜᴛ!**", 
                                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'verify1_settings')]]))

#===============================================================#
@Client.on_callback_query(filters.regex("^set_time2$"))
async def set_time2(client: Client, query: CallbackQuery):
    if not query.from_user.id in client.admins:
        return await query.answer('❌ ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ!', show_alert=True)
    
    await query.answer()
    
    current_time = getattr(client, 'verify_time_2', 60)
    msg = f"""**sᴇᴛ ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ 2 ᴛɪᴍᴇ:**

**ᴄᴜʀʀᴇɴᴛ ᴛɪᴍᴇ:** `{current_time}` sᴇᴄᴏɴᴅs

__sᴇɴᴅ ᴀ ɴᴜᴍʙᴇʀ (ɪɴ sᴇᴄᴏɴᴅs) ɪɴ ᴛʜᴇ ɴᴇxᴛ 60 sᴇᴄᴏɴᴅs!__"""
    
    await query.message.edit_text(msg)
    try:
        res = await client.listen(user_id=query.from_user.id, filters=filters.text, timeout=60)
        if res.text.isdigit():
            new_time = int(res.text)
            if 10 <= new_time <= 3600:
                client.verify_time_2 = new_time
                await client.mongodb.update_shortner_setting('verify_time_2', new_time)
                await query.message.edit_text(f"**✓ ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ 2 ᴛɪᴍᴇ sᴇᴛ ᴛᴏ:** `{new_time}s`", 
                                            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'verify2_settings')]]))
            else:
                await query.message.edit_text("**✗ ᴠᴀʟᴜᴇ ᴍᴜsᴛ ʙᴇ ʙᴇᴛᴡᴇᴇɴ 10 ᴀɴᴅ 3600 sᴇᴄᴏɴᴅs!**", 
                                            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'verify2_settings')]]))
        else:
            await query.message.edit_text("**✗ ᴘʟᴇᴀsᴇ sᴇɴᴅ ᴀ ᴠᴀʟɪᴅ ɴᴜᴍʙᴇʀ!**", 
                                        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'verify2_settings')]]))
    except ListenerTimeout:
        await query.message.edit_text("**⏰ ᴛɪᴍᴇᴏᴜᴛ!**", 
                                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'verify2_settings')]]))

#===============================================================#
@Client.on_callback_query(filters.regex("^set_gap_time$"))
async def set_gap_time(client: Client, query: CallbackQuery):
    if not query.from_user.id in client.admins:
        return await query.answer('❌ ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ!', show_alert=True)
    
    await query.answer()
    
    current_gap = getattr(client, 'gap_time', 300)
    msg = f"""**sᴇᴛ ɢᴀᴘ ᴛɪᴍᴇ (ᴘᴀsᴛɪᴍᴇ):**

**ᴄᴜʀʀᴇɴᴛ ɢᴀᴘ:** `{current_gap}` sᴇᴄᴏɴᴅs

__ᴛɪᴍᴇ ʙᴇᴛᴡᴇᴇɴ ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ 1 → ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ 2__
__sᴇɴᴅ ᴀ ɴᴜᴍʙᴇʀ (ɪɴ sᴇᴄᴏɴᴅs) ɪɴ ᴛʜᴇ ɴᴇxᴛ 60 sᴇᴄᴏɴᴅs!__"""
    
    await query.message.edit_text(msg)
    try:
        res = await client.listen(user_id=query.from_user.id, filters=filters.text, timeout=60)
        if res.text.isdigit():
            new_gap = int(res.text)
            if 0 <= new_gap <= 3600:
                client.gap_time = new_gap
                await client.mongodb.update_shortner_setting('gap_time', new_gap)
                await query.message.edit_text(f"**✓ ɢᴀᴘ ᴛɪᴍᴇ sᴇᴛ ᴛᴏ:** `{new_gap}s`", 
                                            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'shortner')]]))
            else:
                await query.message.edit_text("**✗ ᴠᴀʟᴜᴇ ᴍᴜsᴛ ʙᴇ ʙᴇᴛᴡᴇᴇɴ 0 ᴀɴᴅ 3600 sᴇᴄᴏɴᴅs!**", 
                                            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'shortner')]]))
        else:
            await query.message.edit_text("**✗ ᴘʟᴇᴀsᴇ sᴇɴᴅ ᴀ ᴠᴀʟɪᴅ ɴᴜᴍʙᴇʀ!**", 
                                        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'shortner')]]))
    except ListenerTimeout:
        await query.message.edit_text("**⏰ ᴛɪᴍᴇᴏᴜᴛ!**", 
                                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'shortner')]]))

#===============================================================#
@Client.on_callback_query(filters.regex("^set_default_image$"))
async def set_default_image(client: Client, query: CallbackQuery):
    if not query.from_user.id in client.admins:
        return await query.answer('❌ ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ!', show_alert=True)
    
    await query.answer()
    
    msg = """**sᴇɴᴅ ᴀ ᴄʜᴀɪɴ ʟɪɴᴋ ᴏꜱ ᴛᴇʟᴇɢʀᴀᴘʜ ʟɪɴᴋ (ɪᴍᴀɢᴇ) ɪɴ ᴛʜᴇ ɴᴇxᴛ 60 sᴇᴄᴏɴᴅs!**

__ᴛʜɪs ɪᴍᴀɢᴇ ᴡɪʟʟ ʙᴇ sʜᴏᴡɴ ᴀs ᴛʜᴇ ᴅᴇғᴀᴜʟᴛ ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ ɪᴍᴀɢᴇ.__"""
    
    await query.message.edit_text(msg)
    try:
        res = await client.listen(user_id=query.from_user.id, filters=filters.text, timeout=60)
        image_url = res.text.strip()
        
        if image_url.startswith('http'):
            client.default_verification_image = image_url
            await client.mongodb.update_shortner_setting('default_verification_image', image_url)
            await query.message.edit_text(f"**✓ ᴅᴇғᴀᴜʟᴛ ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ ɪᴍᴀɢᴇ sᴇᴛ!**", 
                                        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'image_settings')]]))
        else:
            await query.message.edit_text("**✗ ᴘʟᴇᴀsᴇ sᴇɴᴅ ᴀ ᴠᴀʟɪᴅ ʟɪɴᴋ!**", 
                                        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'image_settings')]]))
    except ListenerTimeout:
        await query.message.edit_text("**⏰ ᴛɪᴍᴇᴏᴜᴛ!**", 
                                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'image_settings')]]))

#===============================================================#
@Client.on_callback_query(filters.regex("^toggle_per_file_image$"))
async def toggle_per_file_image(client: Client, query: CallbackQuery):
    if not query.from_user.id in client.admins:
        return await query.answer('❌ ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ!', show_alert=True)
    
    await query.answer()
    
    current_status = getattr(client, 'per_file_image_mode', True)
    new_status = not current_status
    client.per_file_image_mode = new_status
    
    await client.mongodb.update_shortner_setting('per_file_image_mode', new_status)
    
    status_text = "ᴇɴᴀʙʟᴇᴅ" if new_status else "ᴅɪsᴀʙʟᴇᴅ"
    await query.answer(f"✓ ᴘᴇʀ-ғɪʟᴇ ɪᴍᴀɢᴇ ᴍᴏᴅᴇ {status_text}!")
    
    await image_settings(client, query)

#===============================================================#
@Client.on_callback_query(filters.regex("^toggle_batch_image$"))
async def toggle_batch_image(client: Client, query: CallbackQuery):
    if not query.from_user.id in client.admins:
        return await query.answer('❌ ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ!', show_alert=True)
    
    await query.answer()
    
    current_status = getattr(client, 'batch_image_mode', True)
    new_status = not current_status
    client.batch_image_mode = new_status
    
    await client.mongodb.update_shortner_setting('batch_image_mode', new_status)
    
    status_text = "ᴇɴᴀʙʟᴇᴅ" if new_status else "ᴅɪsᴀʙʟᴇᴅ"
    await query.answer(f"✓ ʙᴀᴛᴄʜ ɪᴍᴀɢᴇ ᴍᴏᴅᴇ {status_text}!")
    
    await image_settings(client, query)

#===============================================================#
@Client.on_callback_query(filters.regex("^reset_default_image$"))
async def reset_default_image(client: Client, query: CallbackQuery):
    if not query.from_user.id in client.admins:
        return await query.answer('❌ ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ!', show_alert=True)
    
    await query.answer()
    
    client.default_verification_image = ''
    await client.mongodb.update_shortner_setting('default_verification_image', '')
    
    await query.message.edit_text("**✓ ᴅᴇғᴀᴜʟᴛ ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ ɪᴍᴀɢᴇ ʀᴇsᴇᴛ!**", 
                                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'image_settings')]]))

#===============================================================#
@Client.on_callback_query(filters.regex("^reset_shortner$"))
async def reset_shortner(client: Client, query: CallbackQuery):
    if not query.from_user.id in client.admins:
        return await query.answer('❌ ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ!', show_alert=True)
    
    await query.answer()
    
    # Reset all settings to defaults
    client.shortner1_domain = SHORT_URL
    client.shortner1_api = SHORT_API
    client.verify_time_1 = 60
    client.verify1_mode = True
    
    client.shortner2_domain = ''
    client.shortner2_api = ''
    client.verify_time_2 = 60
    client.verify2_mode = False
    
    client.gap_time = 300
    client.default_verification_image = ''
    client.per_file_image_mode = True
    client.batch_image_mode = True
    
    # Update database
    await client.mongodb.set_shortner_settings({
        'shortner1_domain': SHORT_URL,
        'shortner1_api': SHORT_API,
        'verify_time_1': 60,
        'verify1_mode': True,
        'shortner2_domain': '',
        'shortner2_api': '',
        'verify_time_2': 60,
        'verify2_mode': False,
        'gap_time': 300,
        'default_verification_image': '',
        'per_file_image_mode': True,
        'batch_image_mode': True
    })
    
    await query.message.edit_text("**✓ ᴀʟʟ sʜᴏʀᴛɴᴇʀ sᴇᴛᴛɪɴɢs ʜᴀᴠᴇ ʙᴇᴇɴ ʀᴇsᴇᴛ!**", 
                                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'shortner')]]))

#===============================================================#
@Client.on_callback_query(filters.regex("^set_api1$"))
async def set_api1(client: Client, query: CallbackQuery):
    if not query.from_user.id in client.admins:
        return await query.answer('❌ ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ!', show_alert=True)
    
    await query.answer()
    
    current_domain = getattr(client, 'shortner1_domain', SHORT_URL)
    msg = f"""**sᴇᴛ ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ 1 ᴅᴏᴍᴀɪɴ & ᴀᴘɪ:**

**ᴄᴜʀʀᴇɴᴛ ᴅᴏᴍᴀɪɴ:** `{current_domain}`

__sᴇɴᴅ ɪɴ ᴛʜɪs ꜰᴏʀᴍᴀᴛ ɪɴ ᴛʜᴇ ɴᴇxᴛ 60 sᴇᴄᴏɴᴅs:__
**ᴅᴏᴍᴀɪɴ ᴀᴘɪ_ᴋᴇʏ**
**ᴇxᴀᴍᴘʟᴇ:** `inshorturl.com 9435894656863495834957348`"""
    
    await query.message.edit_text(msg)
    try:
        res = await client.listen(user_id=query.from_user.id, filters=filters.text, timeout=60)
        response_text = res.text.strip()
        
        parts = response_text.split(None, 1)
        if len(parts) >= 2:
            new_domain = parts[0].replace('https://', '').replace('http://', '').replace('/', '')
            new_api = parts[1]
            
            if new_domain and '.' in new_domain and new_api and len(new_api) > 10:
                client.shortner1_domain = new_domain
                client.shortner1_api = new_api
                
                await client.mongodb.update_shortner_setting('shortner1_domain', new_domain)
                await client.mongodb.update_shortner_setting('shortner1_api', new_api)
                
                await query.message.edit_text(f"**✓ ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ 1 ᴅᴏᴍᴀɪɴ & ᴀᴘɪ ᴜᴘᴅᴀᴛᴇᴅ!**", 
                                            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'verify1_settings')]]))
            else:
                await query.message.edit_text("**✗ ɪɴᴠᴀʟɪᴅ ғᴏʀᴍᴀᴛ! ᴄʜᴇᴄᴋ ᴅᴏᴍᴀɪɴ ᴀɴᴅ ᴀᴘɪ ᴋᴇʏ.**", 
                                            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'verify1_settings')]]))
        else:
            await query.message.edit_text("**✗ ɪɴᴠᴀʟɪᴅ ғᴏʀᴍᴀᴛ!**", 
                                        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'verify1_settings')]]))
    except ListenerTimeout:
        await query.message.edit_text("**⏰ ᴛɪᴍᴇᴏᴜᴛ!**", 
                                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'verify1_settings')]]))

#===============================================================#
@Client.on_callback_query(filters.regex("^set_api2$"))
async def set_api2(client: Client, query: CallbackQuery):
    if not query.from_user.id in client.admins:
        return await query.answer('❌ ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ!', show_alert=True)
    
    await query.answer()
    
    current_domain = getattr(client, 'shortner2_domain', '')
    msg = f"""**sᴇᴛ ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ 2 ᴅᴏᴍᴀɪɴ & ᴀᴘɪ:**

**ᴄᴜʀʀᴇɴᴛ ᴅᴏᴍᴀɪɴ:** `{current_domain if current_domain else 'ɴᴏᴛ sᴇᴛ'}`

__sᴇɴᴅ ɪɴ ᴛʜɪs ꜰᴏʀᴍᴀᴛ ɪɴ ᴛʜᴇ ɴᴇxᴛ 60 sᴇᴄᴏɴᴅs:__
**ᴅᴏᴍᴀɪɴ ᴀᴘɪ_ᴋᴇʏ**
**ᴇxᴀᴍᴘʟᴇ:** `inshorturl.com 9435894656863495834957348`"""
    
    await query.message.edit_text(msg)
    try:
        res = await client.listen(user_id=query.from_user.id, filters=filters.text, timeout=60)
        response_text = res.text.strip()
        
        parts = response_text.split(None, 1)
        if len(parts) >= 2:
            new_domain = parts[0].replace('https://', '').replace('http://', '').replace('/', '')
            new_api = parts[1]
            
            if new_domain and '.' in new_domain and new_api and len(new_api) > 10:
                client.shortner2_domain = new_domain
                client.shortner2_api = new_api
                
                await client.mongodb.update_shortner_setting('shortner2_domain', new_domain)
                await client.mongodb.update_shortner_setting('shortner2_api', new_api)
                
                await query.message.edit_text(f"**✓ ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ 2 ᴅᴏᴍᴀɪɴ & ᴀᴘɪ ᴜᴘᴅᴀᴛᴇᴅ!**", 
                                            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'verify2_settings')]]))
            else:
                await query.message.edit_text("**✗ ɪɴᴠᴀʟɪᴅ ғᴏʀᴍᴀᴛ! ᴄʜᴇᴄᴋ ᴅᴏᴍᴀɪɴ ᴀɴᴅ ᴀᴘɪ ᴋᴇʏ.**", 
                                            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'verify2_settings')]]))
        else:
            await query.message.edit_text("**✗ ɪɴᴠᴀʟɪᴅ ғᴏʀᴍᴀᴛ!**", 
                                        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'verify2_settings')]]))
    except ListenerTimeout:
        await query.message.edit_text("**⏰ ᴛɪᴍᴇᴏᴜᴛ!**", 
                                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('◂ ʙᴀᴄᴋ', 'verify2_settings')]]))
