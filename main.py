# (c) @RoyalKrrishna
import os
from os import link
from telethon import Button
from configs import Config
from pyrogram import Client, idle
import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession
from plugins.tgraph import *
from helpers import *
from telethon import TelegramClient, events
import urllib.parse
from telethon.errors import UserNotParticipantError
from telethon.tl.functions.channels import GetParticipantRequest
import re

# Create Telegram Client for the main bot
tbot = TelegramClient('mdisktelethonbot', Config.API_ID, Config.API_HASH).start(bot_token=Config.BOT_TOKEN)

# Create Telegram Client for the inline search bot
client = TelegramClient(StringSession(Config.USER_SESSION_STRING), Config.API_ID, Config.API_HASH)

# Generate a unique session string for each instance of the bot
# You can use any string as the session name, such as 'bot_instance_1', 'bot_instance_2', etc.
SESSION_NAME = 'bot_instance_1'

# Check if the session file exists
if os.path.exists(f'{SESSION_NAME}.session'):
    # If it exists, load the existing session
    session = StringSession(filename=f'{SESSION_NAME}.session')
else:
    # If it doesn't exist, create a new session
    session = StringSession()

# Create a new instance of the TelegramClient with the unique session file
client = TelegramClient(session, Config.API_ID, Config.API_HASH)

# Start the Client and connect
client.start(bot_token=Config.BOT_TOKEN)

# Run the Client until it's disconnected
client.run_until_disconnected()

async def get_user_join(id):
    if Config.FORCE_SUB == "False":
        return True

    ok = True
    try:
        await tbot(GetParticipantRequest(channel=int(Config.UPDATES_CHANNEL), participant=id))
        ok = True
    except UserNotParticipantError:
        ok = False
    return ok

# Event handler for incoming messages
@tbot.on(events.NewMessage(incoming=True))
async def message_handler(event):
    try:
        if event.message.post:
            return

        # Ignore messages starting with "/"
        if event.text.startswith("/"):
            return

        print("\n")
        print("Message Received: " + event.text)

        # Force Subscription
        if not await get_user_join(event.sender_id):
            haha = await event.reply(f'''**Hey! {event.sender.first_name} 😃**

**You Have To Join Our Update Channel To Use Me ✅**

**Click Bellow Button To Join Now.👇🏻**''', buttons=Button.url('🍿Updates Channel🍿', f'https://t.me/{Config.UPDATES_CHANNEL_USERNAME}'))
            await asyncio.sleep(Config.AUTO_DELETE_TIME)
            return await haha.delete()

        args = event.text
        args = await validate_q(args)

        print("Search Query: {args}".format(args=args))
        print("\n")

        if not args:
            return

        txt = await event.reply('**Searching For "{}" 🔍**'.format(event.text))

        search = []
        if event.is_group or event.is_channel:
            group_info = await db.get_group(str(event.chat_id).replace("-100", ""))

            if group_info["has_access"] and group_info["db_channel"] and await db.is_group_verified(str(event.chat_id).replace("-100", "")):
                CHANNEL_ID = group_info["db_channel"]
            else:
                CHANNEL_ID = Config.CHANNEL_ID
        else:
            CHANNEL_ID = Config.CHANNEL_ID

        async for i in AsyncIter(re.sub("__|\*", "", args).split()):
            if len(i) > 2:
                search_msg = client.iter_messages(CHANNEL_ID, limit=5, search=i)
                search.append(search_msg)

        username = Config.UPDATES_CHANNEL_USERNAME
        answer = f'**Join** [@{username}](https://telegram.me/{username}) \n\n'

        c = 0

        async for msg_list in AsyncIter(search):
            async for msg in msg_list:
                c += 1
                f_text = re.sub("__|\*", "", msg.text)

                f_text = await link_to_hyperlink(f_text)
                answer += f'\n\n\n✅ PAGE {c}:\n\n━━━━━━━━━\n\n' + '' + f_text.split("\n", 1)[0] + '' + '\n\n' + '' + f_text.split("\n", 2)[
                    -1] + "\n\n"
                
        finalsearch = []
        async for msg in AsyncIter(search):
            finalsearch.append(msg)

        if c <= 0:
            answer = f'''**No Results Found For {event.text}**

**Type Only Movie Name 💬**
**Check Spelling On** [Google](http://www.google.com/search?q={event.text.replace(' ', '%20')}%20Movie) 🔍
    '''

            newbutton = [Button.url('Click To Check Spelling ✅',
                                    f'http://www.google.com/search?q={event.text.replace(" ", "%20")}%20Movie')], [
                            Button.url('Click To Check Release Date 📅',
                                    f'http://www.google.com/search?q={event.text.replace(" ", "%20")}%20Movie%20Release%20Date')]
            await txt.delete()
            result = await event.reply(answer, buttons=newbutton, link_preview=False)
            await asyncio.sleep(Config.AUTO_DELETE_TIME)
            await event.delete()
            return await result.delete()
        else:
            pass

        answer += f"\n\n**Uploaded By @{Config.UPDATES_CHANNEL_USERNAME}**"
        answer = await replace_username(answer)
        html_content = await markdown_to_html(answer)
        html_content = await make_bold(html_content)
        
        tgraph_result = await telegraph_handler(
            html=html_content,
            title=event.text,
            author=Config.BOT_USERNAME
        )
        message = f'**Click Here 👇 For "{event.text}" All Links Are Fixed**\n\n[🍿🎬 {str(event.text).upper()}\n🍿🎬 {str("Click me for results").upper()}]({tgraph_result})'

        await txt.delete()
        result = await event.reply(message, link_preview=False)
        await asyncio.sleep(Config.AUTO_DELETE_TIME)
        # await event.delete()
        return await result.delete()

    except Exception as e:
        print(e)
        await txt.delete()
        result = await event.reply("Some error occurred while searching for movie")
        await asyncio.sleep(Config.AUTO_DELETE_TIME)
        await event.delete() 
        return await result.delete()

async def escape_url(str):
    escape_url = urllib.parse.quote(str)
    return escape_url

# Bot Client for Inline Search
Bot = Client(
    session_name=Config.BOT_SESSION_NAME,
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    bot_token=Config.BOT_TOKEN,
    plugins=dict(root="plugins")
)

print()
print("-------------------- Initializing Telegram Bot --------------------")
# Start Clients
Bot.start()

print("------------------------------------------------------------------")
print()
print(f"""
 _____________________________________________   
|                                             |  
|          Deployed Successfully              |  
|              Join @{Config.UPDATES_CHANNEL_USERNAME}                 |
|_____________________________________________|
    """)

# User.start
# User.start()
with tbot, client:
    tbot.run_until_disconnected()
    client.run_until_disconnected()

# Loop Clients till Disconnects
idle()

# After Disconnects,
# Stop Clients
print()
print("------------------------ Stopped Services ------------------------")
Bot.stop()
# User.stop()


async def main():
    # Bot Client for Inline Search
    Bot = Client(
        session_name=Config.BOT_SESSION_NAME,
        api_id=Config.API_ID,
        api_hash=Config.API_HASH,
        bot_token=Config.BOT_TOKEN,
        plugins=dict(root="plugins")
    )

    print()
    print("-------------------- Initializing Telegram Bot --------------------")
    # Start Clients
    Bot.start()

    print("------------------------------------------------------------------")
    print()
    print(f"""
     _____________________________________________   
    |                                             |  
    |          Deployed Successfully              |  
    |              Join @dtg_tv                   |
    |_____________________________________________|
        """)

    # User.start()
    await tbot.start()
    await client.start()

    # Loop Clients till Disconnects
    await idle()

    # After Disconnects,
    # Stop Clients
    print()
    print("------------------------ Stopped Services ------------------------")
    await Bot.stop()
    await tbot.stop()
    await client.stop()

# Run the main function
if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())

