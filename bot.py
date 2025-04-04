from telethon import TelegramClient, events, Button
from telethon.tl.types import User, Channel, Chat
from telethon.errors import MessageDeleteForbiddenError, UserNotParticipantError
import asyncio
import random
import json
import os
from datetime import datetime
import time

# Initialize client
api_id = 29488492
api_hash = '58b6e5ad1d7eec6c21e97c0706bbd687'
Bad = TelegramClient('session_name', api_id, api_hash)

# Force Subscribe Configuration
FORCE_SUB_CHANNEL = -2632256651  # Your group ID with -100 prefix
FORCE_SUB_CHANNEL_LINK = "https://t.me/+caX0bGW4ivBmZjI1"  # Your group invite link

async def force_sub(event):
    try:
        # Try to check user's permissions in the channel
        try:
            await Bad.get_permissions(FORCE_SUB_CHANNEL, event.sender_id)
            return True
        except UserNotParticipantError:
            # User is not a member
            try:
                # Create buttons
                buttons = [
                    [Button.url("🔔 Join Group", FORCE_SUB_CHANNEL_LINK)],
                    [Button.inline("🔄 Check Again", "check_sub")]
                ]
                
                # Send message with buttons
                await event.reply(
                    f"""
**⚠️ Access Denied!**

You need to join our group to use this bot.

**Steps:**
1. Click the button below to join our group
2. Come back and click "Check Again"
3. Start using the bot!

**Group:** {FORCE_SUB_CHANNEL_LINK}
""",
                    buttons=buttons
                )
                return False
            except Exception as e:
                log_error(e, "force_sub - send message")
                return True  # Allow access if we can't send the message
        except Exception as e:
            log_error(e, "force_sub - get_permissions")
            return True  # Allow access if we can't check
    except Exception as e:
        log_error(e, "force_sub check")
        return True  # Allow access if there's any error

# Callback handler for check sub button
@Bad.on(events.CallbackQuery(pattern="check_sub"))
async def check_sub_callback(event):
    try:
        # Check if user is now a member using get_permissions
        try:
            await Bad.get_permissions(FORCE_SUB_CHANNEL, event.sender_id)
            # User is a member, send success message
            await event.answer("✅ You are now a member! You can use the bot.", alert=True)
            await event.edit(
                """
**✅ Access Granted!**

You are now a member of our group.
You can now use all bot features!

**Enjoy!** 🎉
"""
            )
        except UserNotParticipantError:
            # User is still not a member
            await event.answer("❌ You haven't joined the group yet!", alert=True)
        except Exception as e:
            log_error(e, "check_sub_callback - get_permissions")
            await event.answer("❌ An error occurred. Please try again.", alert=True)
    except Exception as e:
        log_error(e, "check_sub_callback")
        await event.answer("❌ An error occurred. Please try again.", alert=True)

# Start command handler
@Bad.on(events.NewMessage(pattern=r'/start'))
async def start_command(event):
    try:
        # Check force sub first
        if not await force_sub(event):
            return
            
        # Create buttons
        buttons = [
            [
                Button.url("👑 Owner", "https://t.me/Itz_mrunknownn"),
                Button.url("👥 Group", "https://t.me/+caX0bGW4ivBmZjI1")
            ],
            [Button.url("🛟 Support", "https://t.me/Itz_mrunknownn")]
        ]

        # Welcome message
        welcome_msg = """
**🤖 Welcome to Bad Bot!**

I am a powerful Telegram bot with various features including:
• Spam Commands
• Raid Commands
• Admin Management
• And much more!

**👨‍💻 Click the buttons below to get started!**
"""
        
        # Send message with buttons
        await event.reply(welcome_msg, buttons=buttons)
        
    except Exception as e:
        print(f"Error in start command: {e}")
        await event.reply("An error occurred while processing your request.")

# Global variables
is_running = False
DELAY_BETWEEN_MESSAGES = 0.001  # Fast delay
MAX_RETRIES = 3  # Maximum number of retries for failed messages
ERROR_DELAY = 0.1  # Delay after errors
RATE_LIMIT = 0.05  # Rate limit between messages
MAX_MESSAGES_PER_MINUTE = 30  # Maximum messages per minute

# Sudo system setup
OWNER_ID = 7563987769  # Replace with your Telegram ID
SUDO_USERS_FILE = "sudo_users.json"

# Initialize sudo users
if os.path.exists(SUDO_USERS_FILE):
    with open(SUDO_USERS_FILE, 'r') as f:
        SUDO_USERS = set(json.load(f))
else:
    SUDO_USERS = {OWNER_ID}
    with open(SUDO_USERS_FILE, 'w') as f:
        json.dump(list(SUDO_USERS), f)

def is_authorized(user_id):
    return user_id in SUDO_USERS

def save_sudo_users():
    with open(SUDO_USERS_FILE, 'w') as f:
        json.dump(list(SUDO_USERS), f)

# Sudo management commands
@Bad.on(events.NewMessage(pattern=r'/addsudo'))
async def add_sudo(event):
    if event.sender_id != OWNER_ID:
        await event.reply("❌ Only the owner can add sudo users!")
        return
    
    try:
        if event.reply_to_msg_id:
            reply_msg = await event.get_reply_message()
            user = await reply_msg.get_sender()
            user_id = user.id
            name = user.first_name
        else:
            parts = event.raw_text.split()
            if len(parts) != 2:
                await event.reply("❌ Please reply to a user or provide user ID!")
                return
            try:
                user_id = int(parts[1])
                user = await Bad.get_entity(user_id)
                name = user.first_name
            except ValueError:
                await event.reply("❌ Invalid user ID!")
                return

        if user_id in SUDO_USERS:
            await event.reply(f"❌ {name} is already a sudo user!")
            return

        SUDO_USERS.add(user_id)
        save_sudo_users()
        await event.reply(f"✅ Added {name} (`{user_id}`) as sudo user!")

    except Exception as e:
        print(f"Error in addsudo: {e}")
        await event.reply("❌ Error adding sudo user!")

@Bad.on(events.NewMessage(pattern=r'/delsudo'))
async def del_sudo(event):
    if event.sender_id != OWNER_ID:
        await event.reply("❌ Only the owner can remove sudo users!")
        return
    
    try:
        if event.reply_to_msg_id:
            reply_msg = await event.get_reply_message()
            user = await reply_msg.get_sender()
            user_id = user.id
            name = user.first_name
        else:
            parts = event.raw_text.split()
            if len(parts) != 2:
                await event.reply("❌ Please reply to a user or provide user ID!")
                return
            try:
                user_id = int(parts[1])
                user = await Bad.get_entity(user_id)
                name = user.first_name
            except ValueError:
                await event.reply("❌ Invalid user ID!")
                return

        if user_id == OWNER_ID:
            await event.reply("❌ Cannot remove the owner!")
            return

        if user_id not in SUDO_USERS:
            await event.reply(f"❌ {name} is not a sudo user!")
            return

        SUDO_USERS.remove(user_id)
        save_sudo_users()
        await event.reply(f"✅ Removed {name} (`{user_id}`) from sudo users!")

    except Exception as e:
        print(f"Error in delsudo: {e}")
        await event.reply("❌ Error removing sudo user!")

@Bad.on(events.NewMessage(pattern=r'/sudolist'))
async def sudo_list(event):
    if event.sender_id not in SUDO_USERS:
        return
    
    try:
        if len(SUDO_USERS) == 0:
            await event.reply("❌ No sudo users found!")
            return

        sudo_list = "**🛡️ Sudo Users List:**\n\n"
        for user_id in SUDO_USERS:
            try:
                user = await Bad.get_entity(user_id)
                sudo_list += f"• {user.first_name} (`{user_id}`)\n"
            except:
                sudo_list += f"• Unknown User (`{user_id}`)\n"

        await event.reply(sudo_list)

    except Exception as e:
        print(f"Error in sudolist: {e}")
        await event.reply("❌ Error getting sudo list!")

async def send_unauthorized_message(event):
    await event.reply("""
**⚠️ Access Denied!**

You are not authorized to use this command.
To get authorization, contact the bot owner.

**Owner:** @Itz_mrunknown
""")

# Ping command
@Bad.on(events.NewMessage(pattern=r'/ping'))
async def ping(event):
    if not is_authorized(event.sender_id):
        return
        
    try:
        start = time.time()
        
        # Get start time
        start_time = datetime.now()
        
        # Send initial message
        message = await event.reply("**Pong!**")
        
        # Get end time
        end_time = datetime.now()
        
        # Calculate ping time
        ping_time = (end_time - start_time).microseconds / 1000
        
        # Edit message with ping time
        await message.edit(f"""
**🏓 Pong!**
⚡ **Speed:** `{ping_time:.2f}ms`
🤖 **Uptime:** Online
""")

    except Exception as e:
        print(f"Error in ping command: {e}")
        await event.reply("**Error checking ping!**")

# Add rate limiting
class RateLimiter:
    def __init__(self):
        self.messages = []
        self.lock = asyncio.Lock()

    async def acquire(self):
        async with self.lock:
            now = time.time()
            # Remove messages older than 1 minute
            self.messages = [t for t in self.messages if now - t < 60]
            
            if len(self.messages) >= MAX_MESSAGES_PER_MINUTE:
                # Wait until we can send more messages
                wait_time = 60 - (now - self.messages[0])
                if wait_time > 0:
                    await asyncio.sleep(wait_time)
            
            self.messages.append(now)
            await asyncio.sleep(RATE_LIMIT)

rate_limiter = RateLimiter()

# Add error logging function
def log_error(error, command_name):
    print(f"\n❌ Error in {command_name}:")
    print(f"Error details: {str(error)}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# Add safe message sending function
async def safe_send_message(chat_id, message, **kwargs):
    for retry in range(MAX_RETRIES):
        try:
            await rate_limiter.acquire()
            await Bad.send_message(chat_id, message, **kwargs)
            return True
        except Exception as e:
            if retry == MAX_RETRIES - 1:
                log_error(e, "safe_send_message")
            await asyncio.sleep(ERROR_DELAY)
    return False

# Spam command
@Bad.on(events.NewMessage(pattern=r'/spam'))
async def spam_command(event):
    if not await force_sub(event):
        return
        
    if not is_authorized(event.sender_id):
        await send_unauthorized_message(event)
        return
    global is_running
    
    try:
        parts = event.raw_text.split(maxsplit=2)
        if len(parts) < 3:
            await event.reply("Usage: /spam <count> <message>")
            return
            
        count = int(parts[1])
        if count > 100:
            count = 100
        message = parts[2]
        
        is_running = True
        chat_id = event.chat_id
        
        try:
            await event.delete()
        except Exception as e:
            log_error(e, "spam_command_delete")
        
        for _ in range(count):
            if not is_running:
                break
            if not await safe_send_message(chat_id, message):
                break
                
    except ValueError:
        await event.reply("Please provide a valid number!")
    except Exception as e:
        log_error(e, "spam_command")
    finally:
        is_running = False

# Single stop command for all features
@Bad.on(events.NewMessage(pattern=r'/stop'))
async def stop_all(event):
    if not is_authorized(event.sender_id):
        await send_unauthorized_message(event)
        return
    global is_running
    is_running = False
    
    await event.reply("**⚠️ All running commands have been stopped!**")

# Purge command
@Bad.on(events.NewMessage(pattern=r'/purge'))
async def purge_messages(event):
    if not is_authorized(event.sender_id):
        return
        
    try:
        if not event.reply_to_msg_id:
            await event.reply("Reply to a message to start purging from.")
            return

        messages = []
        message_count = 0
        
        chat = await event.get_input_chat()
        from_message = event.reply_to_msg_id
        
        async for message in Bad.iter_messages(chat, min_id=from_message-1):
            messages.append(message)
            message_count += 1
            if len(messages) == 100:
                await Bad.delete_messages(chat, messages)
                messages = []

        if len(messages) > 0:
            await Bad.delete_messages(chat, messages)
        
        
        await asyncio.sleep(2)
        
        
    except MessageDeleteForbiddenError:
        msg = await event.reply("Cannot delete messages here. Make sure I have proper admin rights.")
        await asyncio.sleep(2)
        await msg.delete()
    except Exception as e:
        print(f"Error in purge: {e}")

# Gali spam command
@Bad.on(events.NewMessage(pattern=r'/gali2'))
async def start_spam(event):
    if not is_authorized(event.sender_id):
        await send_unauthorized_message(event)
        return
    global is_running
    is_running = True
    chat_id = event.chat_id
    
    gali_messages = [
       "BACHE","VAIBHAV","TERA","PAPA","APNE","PAPA","SE","MAT","LADO","RAND","KI","AULAAD",
       "TUMHARI","AMMA","XHUD","JAAYEGI","CHHAKO","KE","SAATH","TUMHARI","AMMA","KA","SEX","VIDEO",
       "CHROME","PE","DALUNGA","TERI","AMMA","KI","KALI","CHUT","KA","KALA","PANI","TERI","MAA","KA",
       "KALA","BHOSDA","MAAR","MAAR","KE","FAD","DUNGA","JAO","APNI","MAA","CHUDAO",
    ]
    
    try:
        await event.delete()
    except Exception as e:
        log_error(e, "gali2_command_delete")
    
    while is_running:
        for msg in gali_messages:
            if not is_running:
                break
            if not await safe_send_message(chat_id, msg):
                break

# BGali2 command (Reply version)
@Bad.on(events.NewMessage(pattern=r'/bgali2'))
async def bounded_gali(event):
    if not is_authorized(event.sender_id):
        await send_unauthorized_message(event)
        return
    global is_running
    
    try:
        if not event.reply_to_msg_id:
            return

        reply_msg = await event.get_reply_message()
        is_running = True
        chat_id = event.chat_id

        gali_messages = [
           "BACHE","UNKNOWN","TERA","PAPA","APNE","PAPA","SE","MAT","LADO","RAND","KI","AULAAD",
           "TUMHARI","AMMA","XHUD","JAAYEGI","CHHAKO","KE","SAATH","TUMHARI","AMMA","KA","SEX","VIDEO",
           "CHROME","PE","DALUNGA","TERI","AMMA","KI","KALI","CHUT","KA","KALA","PANI","TERI","MAA","KA",
           "KALA","BHOSDA","MAAR","MAAR","KE","FAD","DUNGA","JAO","APNI","MAA","CHUDAO",
        ]

        await asyncio.sleep(0.5)
        try:
            await event.delete()
        except:
            pass

        while is_running:
            try:
                for msg in gali_messages:
                    if not is_running:
                        break
                    await Bad.send_message(chat_id, msg, reply_to=reply_msg.id)
                    await asyncio.sleep(0.1)
            except Exception as e:
                await asyncio.sleep(1)
                continue

    except Exception as e:
        is_running = False

# Shayari messages list
shayari_messages = [
    "Tere ishq me is tarah mai neelam ho jau,\nTu mujhe chahe to main tere naam ho jau ❤️",
    "Tumhe dekhkar mehsoos hota hai,\nKi khuda ne tumhe mere liye banaya hai 💝",
    "Mohabbat karne wale kam na honge,\nMagar tum sa koi aur na hoga 💖",
    "Dil ke raste bahut door tak jate hai,\nChalo mil kar dekhein kaha tak jate hai 💗",
    "Tum mere liye chaand ho ya sitare ho,\nMere dil ke liye tum hi sahaare ho 💓",
    "Tere pyaar mein main kho jaaun yun,\nJaise subah ki kirn mein shabnam kho jaaye 🌹",
    "Har dhadkan mein tu hai, har saans mein tu hai,\nMeri zindagi ka har lamha tera hai 💞",
    "Teri aankhon ke dariya ka utarna bhi zaroori tha\nMere pyaar ko doobna bhi zaroori tha 💕",
    "Tumhare ishq mein hum kitna tadpe ye bata na sake\nMagar tumhare liye kitna roye ye chupa na sake 💝",
    "Tum mere kareeb ho ya door ho\nMere dil mein hamesha hazoor ho 💖",
    "Koi toh wajah hogi ki khuda ne hume banaya\nKisi ke liye toh humara dil dhadkaya 💗",
    "Tere khayalon mein kho jata hoon\nTeri yaad mein bas jata hoon 💓",
    "Mohabbat ki raah mein rukawat bahut hai\nPhir bhi tere liye chahat bahut hai 🌹",
    "Teri har ada pe main fida hoon\nTeri har khushi ke liye main zinda hoon 💞",
    "Tumhe paa kar khushi hui\nTumhe kho kar majboori hui 💕",
    "Tere ishq ne mujhe badal diya\nMeri zindagi ka har rang badal diya 💝",
    "Tum mere dil ki dhadkan ho\nMeri zindagi ki dharkan ho 💖",
    "Koi itna bhi khoobsurat kaise ho sakta hai\nKoi itna bhi masoom kaise ho sakta hai 💗",
    "Tere bina jeena mushkil hai\nTere bina har pal mushkil hai 💓",
    "Mohabbat mein junoon sa ho gaya hai\nHar lamha tere liye deewana ho gaya hai 🌹"
]

# Add group chat optimization variables
GROUP_CHAT_DELAY = 0.005  # Very small delay for group chats
GROUP_CHAT_BATCH_SIZE = 3  # Smaller batch size for group chats
GROUP_CHAT_MAX_RETRIES = 3  # Fewer retries for group chats

# Raid messages list
raid_messages = [
    "SUN SUN SUAR KE PILLE JHANTO KE SOUDAGAR APNI MUMMY KI NUDES BHEJ",
    "YA DU TERE GAAND ME TAPAA TAP",
    "Apni gaand mein muthi daal",
    "Apni lund choos",
    "ABE TERI BEHEN KO CHODU RANDIKE BACHHE TEREKO CHAKKO SE PILWAVUNGA RANDIKE BACHHE 🤣🤣",
    "TERI BEHEN KOTO CHOD CHODKE PURA FAAD DIA CHUTH ABB TERI GF KO BHEJ 😆💦🤤",
    "2 RUPAY KI PEPSI TERI MUMMY SABSE SEXY 💋💦",
    "CHAL TERE BAAP KO BHEJ TERA BASKA NHI HE PAPA SE LADEGA TU",
    "AAJA TERI JINDEGI SAWAR DU TERI MAA KI CHUT MAZE MAI MAAR DU",
    "HAHAHAHA BACHHE TERI MAAAKO CHOD DIA NANGA KARKE",
    "TERI BEHEN KO CHOD CHODKE VIDEO BANAKE XNXX.COM PE NEELAM KARDUNGA KUTTE KE PILLE 💦💋",
    "GALI GALI NE SHOR HE TERI MAA RANDI CHOR HE 💋💋💦",
    "TERI MAA KAA BHOSDA",
    "BEHEN K LUND",
    "BACHHE TERI MAA KI CHUTT",
    "SHARAM KAR TERI BEHEN KA BHOSDA KITNA GAALIA SUNWAYEGA APNI MAAA BEHEN KE UPER",
    "TERI BEHEN KI CHUTH ME BOMB DALKE UDA DUNGA MAAKE LAWDE",
    "Gaand mein bambu DEDUNGAAAAAA",
    "TERI MAAA RANDI HAI",
    "Jhaant ke pissu",
    "RYAN TERA BAAP !!",
    "Gote kitne bhi bade ho, lund ke niche hi rehte hai",
    "ALE ALE MELA BCHAAAA",
    "TERI BHEN KA BHOSRA FAARUUU",
    "CHAL BETA TUJHE MAAF KIA 🤣 ABB APNI GF KO BHEJ",
    "SPEED LAAA TERI BEHEN CHODU RANDIKE PILLE 💋💦🤣",
    "TERI MAAA KO HORLICKS PILAUNGA MADARCHOD",
    "TERI BEHEN KI CHUTH ME MUTHKE FARAR HOJAVUNGA HUI HUI HUI",
    "KIDSSSSSSSSSSSS",
    "SPEED PKDDD",
    "TERI BEHEN LETI MERI LUND BADE MASTI SE TERI BEHEN KO MENE CHOD DALA BOHOT SASTE SE"
]

# Chat hang messages list
hang_messages = [
    "⚡️", "⚡️", "⚡️", "⚡️", "⚡️", "⚡️", "⚡️", "⚡️", "⚡️", "⚡️",
    "⚡️", "⚡️", "⚡️", "⚡️", "⚡️", "⚡️", "⚡️", "⚡️", "⚡️", "⚡️",
    "⚡️", "⚡️", "⚡️", "⚡️", "⚡️", "⚡️", "⚡️", "⚡️", "⚡️", "⚡️",
    "⚡️", "⚡️", "⚡️", "⚡️", "⚡️", "⚡️", "⚡️", "⚡️", "⚡️", "⚡️",
    "⚡️", "⚡️", "⚡️", "⚡️", "⚡️", "⚡️", "⚡️", "⚡️", "⚡️", "⚡️",
    "⚡️", "⚡️", "⚡️", "⚡️", "⚡️", "⚡️", "⚡️", "⚡️", "⚡️", "⚡️",
    "⚡️", "⚡️", "⚡️", "⚡️", "⚡️", "⚡️", "⚡️", "⚡️", "⚡️", "⚡️",
    "⚡️", "⚡️", "⚡️", "⚡️", "⚡️", "⚡️", "⚡️", "⚡️", "⚡️", "⚡️",
    "⚡️", "⚡️", "⚡️", "⚡️", "⚡️", "⚡️", "⚡️", "⚡️", "⚡️", "⚡️",
    "⚡️", "⚡️", "⚡️", "⚡️", "⚡️", "⚡️", "⚡️", "⚡️", "⚡️", "⚡️"
]

# Optimize the raid command for faster execution in group chats
@Bad.on(events.NewMessage(pattern=r'/raid'))
async def start_raid(event):
    if not await force_sub(event):
        return
        
    if not is_authorized(event.sender_id):
        await send_unauthorized_message(event)
        return
    global is_running
    
    try:
        if not event.reply_to_msg_id:
            await event.reply("Reply to a user to start raiding!")
            return

        reply_msg = await event.get_reply_message()
        target_user = await reply_msg.get_sender()
        
        if not target_user:
            return

        is_running = True
        chat_id = event.chat_id
        
        if isinstance(target_user, User):
            if target_user.username:
                user_mention = f"@{target_user.username}"
            else:
                user_mention = f"[{target_user.first_name}](tg://user?id={target_user.id})"
        else:
            user_mention = f"[User](tg://user?id={target_user.id})"

        try:
            await event.delete()
        except Exception as e:
            log_error(e, "raid_command_delete")

        # Rapid raid with minimal delays optimized for group chats
        while is_running:
            try:
                # Send multiple raid messages in quick succession
                for _ in range(GROUP_CHAT_BATCH_SIZE):  # Smaller batch size for groups
                    if not is_running:
                        break
                    msg = random.choice(raid_messages)
                    raid_text = f"{user_mention} {msg}"
                    await Bad.send_message(chat_id, raid_text, parse_mode='md')
                
                # Minimal delay between batches
                await asyncio.sleep(GROUP_CHAT_DELAY)
                
            except Exception as e:
                if "FLOOD_WAIT" in str(e):
                    # Extract wait time from error message if possible
                    try:
                        wait_time = int(str(e).split("seconds")[0].split()[-1])
                        await asyncio.sleep(wait_time + 0.2)  # Shorter wait time
                    except:
                        await asyncio.sleep(1)  # Shorter default wait time
                elif "CHAT_WRITE_FORBIDDEN" in str(e):
                    await event.respond("❌ Cannot send messages to this chat!")
                    is_running = False
                    break
                else:
                    log_error(e, "raid_command")
                    await asyncio.sleep(0.2)  # Very short delay before retrying

    except Exception as e:
        log_error(e, "raid_command")
        is_running = False

# Optimize the shayari raid command for faster execution in group chats
@Bad.on(events.NewMessage(pattern=r'/sraid'))
async def shayari_raid(event):
    if not is_authorized(event.sender_id):
        await send_unauthorized_message(event)
        return
    global is_running
    
    try:
        if not event.reply_to_msg_id:
            await event.reply("Reply to a user to start shayari raid!")
            return

        reply_msg = await event.get_reply_message()
        target_user = await reply_msg.get_sender()
        
        if not target_user:
            return

        is_running = True
        chat_id = event.chat_id
        
        if isinstance(target_user, User):
            if target_user.username:
                user_mention = f"@{target_user.username}"
            else:
                user_mention = f"[{target_user.first_name}](tg://user?id={target_user.id})"
        else:
            user_mention = f"[User](tg://user?id={target_user.id})"

        try:
            await event.delete()
        except Exception as e:
            log_error(e, "sraid_command_delete")

        # Rapid shayari raid with minimal delays optimized for group chats
        while is_running:
            try:
                # Send multiple shayari messages in quick succession
                for _ in range(GROUP_CHAT_BATCH_SIZE):  # Smaller batch size for groups
                    if not is_running:
                        break
                    shayari = random.choice(shayari_messages)
                    raid_text = f"{user_mention}\n{shayari}"
                    await Bad.send_message(chat_id, raid_text, parse_mode='md')
                
                # Minimal delay between batches
                await asyncio.sleep(GROUP_CHAT_DELAY)
                
            except Exception as e:
                if "FLOOD_WAIT" in str(e):
                    # Extract wait time from error message if possible
                    try:
                        wait_time = int(str(e).split("seconds")[0].split()[-1])
                        await asyncio.sleep(wait_time + 0.2)  # Shorter wait time
                    except:
                        await asyncio.sleep(1)  # Shorter default wait time
                elif "CHAT_WRITE_FORBIDDEN" in str(e):
                    await event.respond("❌ Cannot send messages to this chat!")
                    is_running = False
                    break
                else:
                    log_error(e, "sraid_command")
                    await asyncio.sleep(0.2)  # Very short delay before retrying

    except Exception as e:
        log_error(e, "sraid_command")
        is_running = False

# Shayari spam command
@Bad.on(events.NewMessage(pattern=r'/shayari'))
async def shayari_spam(event):
    if not is_authorized(event.sender_id):
        await send_unauthorized_message(event)
        return
    global is_running
    is_running = True
    chat_id = event.chat_id
    
    try:
        parts = event.raw_text.split()
        if len(parts) < 2:
            await event.reply("Please specify the number of shayaris to send!")
            return
            
        number = int(parts[1])
        if number > 100:  # Added limit
            number = 100
        await asyncio.sleep(0.5)
        try:
            await event.delete()
        except:
            pass
        
        for _ in range(number):
            if not is_running:
                break
            try:
                shayari = random.choice(shayari_messages)
                await Bad.send_message(chat_id, shayari)
                await asyncio.sleep(0.1)
            except Exception as e:
                await asyncio.sleep(1)
                continue
                
    except ValueError:
        await event.reply("Please provide a valid number!")
    except Exception as e:
        print(f"Error in shayari command: {e}")

# Bounded Raid command
@Bad.on(events.NewMessage(pattern=r'/braid'))
async def bounded_raid(event):
    if not is_authorized(event.sender_id):
        await send_unauthorized_message(event)
        return
    global is_running
    
    try:
        parts = event.raw_text.split()
        if len(parts) < 3:
            await event.reply("Use format: /braid <number> <username>")
            return
            
        number = int(parts[1])
        if number > 100:  # Added limit
            number = 100
        username = parts[2]
        
        if not username.startswith("@"):
            username = "@" + username

        is_running = True
        chat_id = event.chat_id

        await asyncio.sleep(0.5)
        try:
            await event.delete()
        except:
            pass

        for _ in range(number):
            if not is_running:
                break
            try:
                msg = random.choice(raid_messages)
                raid_text = f"{username} {msg}"
                await Bad.send_message(chat_id, raid_text)
                await asyncio.sleep(0.1)
            except Exception as e:
                await asyncio.sleep(1)
                continue

    except ValueError:
        await event.reply("Please provide a valid number!")
    except Exception as e:
        print(f"Error in bounded raid: {e}")
    finally:
        is_running = False

@Bad.on(events.NewMessage(pattern=r'/help'))
async def help_command(event):
    if not is_authorized(event.sender_id):
        await send_unauthorized_message(event)
        return
        
    try:
        help_text = """
**🤖 Bad Bot Commands Manual**

**🛡️ Admin Commands:**
• `/addsudo` - Add a sudo user (Owner only)
• `/delsudo` - Remove a sudo user (Owner only)
• `/sudolist` - List all sudo users

**⚡ Basic Commands:**
• `/start` - Start the bot
• `/ping` - Check bot's response time
• `/help` - Show this help message
• `/stop` - Stop any running command

**🔥 Spam Commands:**
• `/spam <count> <message>` - Spam a message
• `/shayari <count>` - Spam random shayaris
• `/gali2` - Start continuous gali spam
• `/bgali2` - Reply to start bounded gali spam

**⚔️ Raid Commands:**
• `/raid` - Reply to user to start continuous raid
• `/braid <count> <username>` - Bounded raid on user
• `/sraid` - Reply to start shayari raid
• `/bsraid <count> <username>` - Bounded shayari raid

**🧹 Moderation:**
• `/purge` - Reply to message to purge from there

**Note:** 
• Max limit for spam/raid commands is 100
• Only authorized users can use these commands
• Use commands responsibly

**👨‍�� Owner:** @Itz_mrunknownn
"""
        await event.reply(help_text)
        
    except Exception as e:
        print(f"Error in help command: {e}")
        await event.reply("An error occurred while showing help!")

# Modify the chat hang command for better performance in group chats
@Bad.on(events.NewMessage(pattern=r'/hang'))
async def chat_hang(event):
    if not is_authorized(event.sender_id):
        await send_unauthorized_message(event)
        return
    global is_running
    
    try:
        if not event.reply_to_msg_id:
            await event.reply("Reply to a message to start hanging the chat!")
            return

        reply_msg = await event.get_reply_message()
        chat_id = event.chat_id
        
        is_running = True
        message_count = 0
        max_messages = 1000  # Reduced to prevent overload
        
        try:
            await event.delete()
        except Exception as e:
            log_error(e, "hang_command_delete")
            
        # Send initial message
        await event.respond("🚀 Starting chat hang...")
        
        # Rapid message sending with minimal delays optimized for group chats
        while is_running and message_count < max_messages:
            try:
                # Send multiple messages in quick succession
                for _ in range(GROUP_CHAT_BATCH_SIZE):  # Smaller batch size for groups
                    if not is_running or message_count >= max_messages:
                        break
                    msg = random.choice(hang_messages)
                    await Bad.send_message(chat_id, msg)
                    message_count += 1
                
                # Minimal delay between batches
                await asyncio.sleep(GROUP_CHAT_DELAY)
                
            except Exception as e:
                if "FLOOD_WAIT" in str(e):
                    # Extract wait time from error message if possible
                    try:
                        wait_time = int(str(e).split("seconds")[0].split()[-1])
                        await asyncio.sleep(wait_time + 0.2)  # Shorter wait time
                    except:
                        await asyncio.sleep(1)  # Shorter default wait time
                elif "CHAT_WRITE_FORBIDDEN" in str(e):
                    await event.respond("❌ Cannot send messages to this chat!")
                    is_running = False
                    break
                else:
                    log_error(e, "chat_hang")
                    await asyncio.sleep(0.2)  # Very short delay before retrying
                    
        if message_count >= max_messages:
            await event.respond(f"✅ Chat hang completed! Sent {message_count} messages.")
        elif not is_running:
            await event.respond(f"🛑 Chat hang stopped! Sent {message_count} messages.")
            
    except Exception as e:
        log_error(e, "chat_hang")
        is_running = False
        await event.respond("❌ An error occurred while hanging the chat!")

# Start the client
print("Starting...")
Bad.start()
print("Bot Started Successfully!")
Bad.run_until_disconnected()

