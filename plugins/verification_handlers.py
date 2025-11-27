import time
from pyrogram import Client, filters
from pyrogram.types import CallbackQuery

@Client.on_callback_query(filters.regex("^verify1_passed$"))
async def verify1_passed_handler(client: Client, query: CallbackQuery):
    """
    Handle verification1 completion.
    Save: verify1_expiry, verify2_start_time, last_verified_step=1
    Set proper state for verify1 completion with gap time
    """
    user_id = query.from_user.id
    current_time = int(time.time())
    
    # Get verification times from client settings
    verify_time_1 = getattr(client, 'verify_time_1', 60)
    gap_time = getattr(client, 'gap_time', 300)
    
    # Calculate expiry times
    verify1_expiry = current_time + verify_time_1
    verify2_start_time = current_time + gap_time
    
    # Save to database with proper state
    await client.mongodb.set_user_verify_status(
        user_id,
        verify1_expiry=verify1_expiry,
        verify2_start_time=verify2_start_time,
        verify2_expiry=None,
        last_verified_step=1
    )
    
    await query.answer("✅ Verification 1 Complete! Please wait for step 2.", show_alert=False)

#===============================================================#

@Client.on_callback_query(filters.regex("^verify2_passed$"))
async def verify2_passed_handler(client: Client, query: CallbackQuery):
    """
    Handle verification2 completion.
    Save: verify2_expiry = now + VERIFY_TIME_2, last_verified_step=2
    Set proper state for verify2 completion with full access
    """
    user_id = query.from_user.id
    current_time = int(time.time())
    
    # Get verification time 2 from client settings
    verify_time_2 = getattr(client, 'verify_time_2', 60)
    
    # Calculate expiry time for verify2
    verify2_expiry = current_time + verify_time_2
    
    # Save to database - verify2 completion grants full access
    await client.mongodb.set_user_verify_status(
        user_id,
        verify1_expiry=None,
        verify2_start_time=None,
        verify2_expiry=verify2_expiry,
        last_verified_step=2
    )
    
    await query.answer("✅ Verification 2 Complete! You can now access files.", show_alert=False)

#===============================================================#
