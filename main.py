import os
import asyncio
from time import sleep
from sys import argv
import requests
import bs4
from bs4 import BeautifulSoup
from telethon import TelegramClient, errors, connection
from telethon.tl.functions.messages import GetHistoryRequest, GetBotCallbackAnswerRequest

# API variables
api_id = 4779974  # add your api_id here
api_hash = "f4b4efb4068a0899d2448a146a844b21"  # add your api_hash here

c = requests.Session()
ua={"User-Agent": "Mozilla/5.0 (Linux; Android 5.1; A1603 Build/LMY47I; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/43.0.2357.121 Mobile Safari/537.36"}
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
    start = str(messages).find("url=")  # TODO change it
    link = str(messages)[start + 5:start + 36]
    if "'" in link:
        link = link[:-1]
    print(link)
    try:
        command = "curl --silent " + link + " > /dev/null"
        os.system(command)
    except:
        # we have some issue when get url!
        print("can't visit, invalid url!")
    sleep(1)


async def opening_link(username):
    """
    get message, find link and execute with open
    :param messages: get bot message as param
    :return: nothing
    """
    posts = await client(GetHistoryRequest(peer=username,limit=1,offset_date=None,offset_id=0,max_id=0,min_id=0,add_offset=0,hash=0))
    url = posts.messages[0].reply_markup.rows[0].buttons[0].url
    r = c.get(url, headers=ua, timeout=15, allow_redirects=True)
    soup = BeautifulSoup(r.content,"html.parser")
    for dat in soup.find_all('div',class_="container-fluid"):
        code = dat.get('data-code')
        timer = dat.get('data-timer')
        tokena = dat.get('data-token')
        print("waiting for " + timer + " seconds...")
        sleep(int(timer))
        r = c.post("https://dogeclick.com/reward",data={"code":code,"token":tokena}, headers=ua, timeout=15, allow_redirects=True)
        print("site, visited!!!")


async def get_balance(username):
    """
    get username, send balance command, get and filter message, print balance
    :param username: bot username
    :return: nothing just print balance
    """
    balance = "/balance"
    await client.send_message(username, balance)
    sleep(1.5)
    messages = await client.get_messages(username, limit=1)
    messages_list = str(messages[0])[8:-1].split(", ")  # TODO change it
    print(str(messages_list[9])[9:-1])


async def main():
    # logout and delete session file
    global waiting_time
    if len(argv) == 2:
        if argv[1] == "logout":
            print("logging out...")
            await client.log_out()
            exit(0)

    # getting waiting time
    if 2 <= len(argv) <= 3:
        if argv[len(argv) - 1] == "-ul":
            try:
                waiting_time = int(input("you activate unlimited mode, please enter waiting time(minutes):\n")) * 60
            except:
                print("undefined input, set 15 minutes by default.")
                waiting_time = 900

    # print user name
    me = await client.get_me()
    print("logged in as: " + str(me.first_name))

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
                    if ("10 seconds..." in str(messages[0])) or ("You earned" in str(messages[0])):
                        print("site visited!")
                    else:
                        # try to handle some unexpected messages
                        if "to /visit!" in str(messages[0]):
                            print("site, visited!")
                        elif "Sorry," in str(messages[0]):
                            print("Site, visited!")
                        else:
                            await opening_link(username)
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
