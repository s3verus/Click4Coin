import os
import asyncio
from time import sleep
from sys import argv
import requests
import bs4
from telethon import TelegramClient, errors, connection

# API variables
api_id = 12345  # add your api_id here
api_hash = "19f30c5a1c..."  # add your api_hash here

user_names = ["Zcash_click_bot", "Dogecoin_click_bot", "Litecoin_click_bot", "BCH_clickbot", "BitcoinClick_bot"]
temp_list = ["Zcash_click_bot", "Dogecoin_click_bot", "Litecoin_click_bot", "BCH_clickbot", "BitcoinClick_bot"]
message = "/visit"

# Client Object
if 2 <= len(argv) <= 3:
    if argv[1] == "-mt":
        f = open("mtproxy.txt", "r")
        proxy = (f.readline()).split(", ")
        proxy[1] = int(proxy[1])
        if proxy[2][-1] == "\n":
            proxy[2] = proxy[2][:-1]
        proxy = tuple(proxy)
        f.close()
        client = TelegramClient(
            'session_C4C', api_id, api_hash,
            connection=connection.ConnectionTcpMTProxyRandomizedIntermediate,
            proxy=proxy
        )
        client.start()
    elif argv[1] == "-p":  # TODO add other kind of proxy
        pass
    else:
        client = TelegramClient("session_C4C", api_id, api_hash)
        client.start()
else:
    client = TelegramClient("session_C4C", api_id, api_hash)
    client.start()

# Then we need a loop to work with
loop = asyncio.get_event_loop()


async def visiting_link(messages):
    """
    get message, find link and execute with curl
    :param messages: get bot message as param
    :return: nothing, just print url
    """
    start = str(messages).find("url=")
    link = str(messages)[start + 5:start + 36]
    if "'" in link:
        link = link[:-1]
    print(link)
    command = "curl --silent " + link + " > /dev/null"
    os.system(command)
    sleep(1)


async def opening_link(messages):
    """
    get message, find link and execute with open
    :param messages: get bot message as param
    :return: nothing
    """
    # getting url
    start = str(messages).find("url=")
    link = str(messages)[start + 5:start + 36]
    if "'" in link:
        link = link[:-1]
    # getting time for waiting in site
    response = requests.get(link)
    soup = bs4.BeautifulSoup(response.text, 'html.parser')
    all_div = soup.findAll('div')
    n = str(all_div[0])[76:79]
    if n[-1] == '"':
        n = n[:-1]
    if n[0] == '"':
        n = n[1:]
    try:
        n = int(n)
    except:
        n = 20
    print("opening task and waiting {} seconds...".format(n))
    # opening browser
    command = "xdg-open " + link
    os.system(command)
    sleep(n)


async def get_balance(username):
    """
    get username, send balance command, get and filter message, print balance
    :param username: bot username
    :return: nothing just print balance
    """
    balance = "/balance"
    await client.send_message(username, balance)
    sleep(1)
    messages = await client.get_messages(username, limit=1)
    messages_list = str(messages[0])[8:-1].split(", ")
    print(str(messages_list[9])[9:-1])


async def compare_2last_links(username):
    """
    get 5 last messages in chat for checking urls
    if find same url skip the ads
    :param username: get bot username as input
    :return: bool value,
    """
    messages = await client.get_messages(username, limit=5)
    start1 = str(messages[0]).find("url=")
    link1 = str(messages[0])[start1 + 5:start1 + 36]
    start2 = str(messages[4]).find("url=")
    link2 = str(messages[4])[start2 + 5:start2 + 36]
    if link1 == link2:
        print("can't open, skipping task...")
        await messages[0].click(1, 1)
        return True
    else:
        return False


async def main():
    # logout and delete session file
    global waiting_time
    if len(argv) == 2:
        if argv[1] == "logout":
            print("logging out...")
            await client.log_out()
            exit(0)

    # get permission from user to open some sites
    visit = input("some sites should open in browser, wanna accept our reject?(accept/reject)\n").lower()
    if visit == "accept":
        allow = True
    elif visit == "reject":
        allow = False
    else:
        print("undefined input, reject by default.")
        allow = False

    # getting waiting time
    if 2 <= len(argv) <= 3:
        if argv[len(argv) - 1] == "-ul":
            try:
                waiting_time = int(input("you activate unlimited mode, please enter waiting time(minutes):\n")) * 60
            except:
                print("undefined input, set 15 minutes by default.")
                waiting_time = 900

    while True:
        if len(user_names) <= 0:
            # active unlimited mode
            if 2 <= len(argv) <= 3:
                if argv[len(argv) - 1] == "-ul":
                    user_names.extend(temp_list)
                    print("unlimited mode is activated, sleeping for {} minutes...".format(waiting_time / 60))
                    print("")
                    sleep(waiting_time)
                else:
                    print("all ads finished, try again later...")
                    exit(0)
            else:
                print("all ads finished, try again later...")
                exit(0)

        for username in user_names:
            try:
                await client.send_message(username, message)
                print("sending message to {}".format(username))
                sleep(1)
                messages = await client.get_messages(username, limit=1)
                if "Sorry," not in str(messages[0]):
                    await visiting_link(messages)
                    messages = await client.get_messages(username, limit=1)
                    if "10 seconds..." not in str(messages[0]):
                        if allow:
                            if not await compare_2last_links(username):
                                await opening_link(messages)
                        else:
                            print("skipping task...")
                            await messages[0].click(1, 1)
                    else:
                        print("site visited!")
                else:
                    print("no more ads in {}, removing bot from list.".format(username))
                    await get_balance(username)
                    user_names.remove(username)

            except errors.FloodWaitError as e:
                print('Have to sleep', e.seconds, 'seconds')
                print("this limit is set by telegram!\n Nobody knows the exact limits for all requests since they "
                      "depend on a lot of factors.\n don't worry about it.")
                sleep(e.seconds)
        print("waiting 10 seconds...")
        sleep(10)


# Then, we need to run the loop with a task
loop.run_until_complete(main())
