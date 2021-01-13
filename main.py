import os
import asyncio
from time import sleep
from telethon import TelegramClient, errors

# API variables
api_id = 01234 		     # add your api_id here
api_hash = "19f30c5a1c..."   # add your api_hash here

user_names = ["Zcash_click_bot", "Dogecoin_click_bot", "Litecoin_click_bot", "BCH_clickbot", "BitcoinClick_bot"]
message = "/visit"

# Client Object
client = TelegramClient("session_C4C", api_id, api_hash)
client.start()

# Then we need a loop to work with
loop = asyncio.get_event_loop()


async def main():
    i = 0
    while i < 15:
        i += 1
        print(user_names)
        if len(user_names) <= 0:
            print("all ads finished, try again later...")
            exit(0)
        for username in user_names:
            try:
                await client.send_message(username, message)
                print("sending message to {}".format(username))
                sleep(1)
                messages = await client.get_messages(username, limit=1)
                if "Sorry," not in str(messages[0]):
                    start = str(messages).find("url=")
                    link = str(messages)[start + 5:start + 36]
                    print(link)
                    command = "curl --silent " + link + " > /dev/null"
                    os.system(command)
                    sleep(1)
                    messages = await client.get_messages(username, limit=1)
                    if "stay" not in str(messages[0]) or "earned" not in str(messages[0]):
                        print("skipping task...")
                        await messages[0].click(1, 1)
                else:
                    print("no more ads in {}, removing bot from list.".format(username))
                    user_names.remove(username)

            except errors.FloodWaitError as e:
                print('Have to sleep', e.seconds, 'seconds')
                print("this limit is set by telegram!\n Nobody knows the exact limits for all requests since they "
                      "depend on a lot of factors.\n don't worry about it.")
                sleep(e.seconds)
        print("wait 9 seconds...")
        sleep(9)
    exit(0)


# Then, we need to run the loop with a task
loop.run_until_complete(main())
