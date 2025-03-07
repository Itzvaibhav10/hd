from telethon import TelegramClient, events, Button
from telethon.tl.types import User
from telethon.errors import MessageDeleteForbiddenError
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

# Start command handler

# Start command handler
@Bad.on(events.NewMessage(pattern=r'/start'))
async def start_command(event):
    try:
        # Create buttons
        buttons = [
            [
                Button.url("👑 Owner", "https://t.me/Itz_mrunknown"),
                Button.url("👥 Group", "https://t.me/+xfCjPzSVgiBmZDM1")
            ],
            [Button.url("🛟 Support", "https://t.me/Itz_mrunknown")]
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
DELAY_BETWEEN_MESSAGES = 0.01

# Sudo system setup
OWNER_ID = 7331931794  # Replace with your Telegram ID
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
# Sudo system setup (keep this part near the top of your file)
def is_authorized(user_id):
    return user_id in SUDO_USERS

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
# ... existing code ...

# Spam command
@Bad.on(events.NewMessage(pattern=r'/spam'))
async def spam_command(event):
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
        if count > 100:  # Limit to prevent abuse
            count = 100
        message = parts[2]
        
        is_running = True
        chat_id = event.chat_id
        
        await event.delete()
        
        for _ in range(count):
            if not is_running:
                break
            try:
                await Bad.send_message(chat_id, message)
                await asyncio.sleep(0.1)  # Small delay between messages
            except Exception as e:
                await asyncio.sleep(1)
                continue
                
    except ValueError:
        await event.reply("Please provide a valid number!")
    except Exception as e:
        print(f"Error in spam command: {e}")
    finally:
        is_running = False

# ... existing code ...
# ... (rest of your commands remain the same) ...

# ... (rest of your commands) ...

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
# Gali spam command
# Gali spam command
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
                await Bad.send_message(chat_id, msg)
                await asyncio.sleep(0.1)
        except:
            await asyncio.sleep(1)
            continue

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

# Shayari spam command# Shayari Raid command
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

        await asyncio.sleep(0.5)
        try:
            await event.delete()
        except:
            pass

        while is_running:
            try:
                for shayari in shayari_messages:
                    if not is_running:
                        break
                    raid_text = f"{user_mention}\n{shayari}"
                    await Bad.send_message(chat_id, raid_text, parse_mode='md')
                    await asyncio.sleep(0.1)
            except Exception as e:
                await asyncio.sleep(1)
                continue

    except Exception as e:
        print(f"Error in shayari raid: {e}")
        is_running = False

# Bounded Shayari Raid command
@Bad.on(events.NewMessage(pattern=r'/bsraid'))
async def bounded_shayari_raid(event):
    if not is_authorized(event.sender_id):
        await send_unauthorized_message(event)
        return
    global is_running
    
    try:
        parts = event.raw_text.split()
        if len(parts) < 3:
            await event.reply("Use format: /bsraid <number> <username>")
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

        count = 0
        while is_running and count < number:
            try:
                shayari = shayari_messages[count % len(shayari_messages)]
                raid_text = f"{username}\n{shayari}"
                await Bad.send_message(chat_id, raid_text)
                count += 1
                await asyncio.sleep(0.1)
            except Exception as e:
                await asyncio.sleep(1)
                continue

    except ValueError:
        await event.reply("Please provide a valid number!")
    except Exception as e:
        print(f"Error in bounded shayari raid: {e}")
    finally:
        is_running = False
        
        
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

# Regular Raid command (continuous)
# Regular Raid command (continuous)
# Add this with your other message lists (near raid_messages and shayari_messages)
gali_messages = [
    "BACHE","VAIBHAV","TERA","PAPA","APNE","PAPA","SE","MAT","LADO","RAND","KI","AULAAD",
    "TUMHARI","AMMA","XHUD","JAAYEGI","CHHAKO","KE","SAATH","TUMHARI","AMMA","KA","SEX","VIDEO",
    "CHROME","PE","DALUNGA","TERI","AMMA","KI","KALI","CHUT","KA","KALA","PANI","TERI","MAA","KA",
    "KALA","BHOSDA","MAAR","MAAR","KE","FAD","DUNGA","JAO","APNI","MAA","CHUDAO",
]

# Regular Raid command (continuous)
# Regular Raid command (continuous)
@Bad.on(events.NewMessage(pattern=r'/raid'))
async def start_raid(event):
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

        await asyncio.sleep(0.5)
        try:
            await event.delete()
        except:
            pass

        while is_running:
            try:
                msg = random.choice(raid_messages)
                raid_text = f"{user_mention} {msg}"
                await Bad.send_message(chat_id, raid_text, parse_mode='md')
                await asyncio.sleep(0.1)
            except Exception as e:
                await asyncio.sleep(1)
                continue

    except Exception as e:
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

# Start the client
print("Starting...")
Bad.start()
print("Bot Started Successfully!")
Bad.run_until_disconnected()
