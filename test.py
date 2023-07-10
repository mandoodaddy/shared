import asyncio
import socket
import json
from tap_titans.providers import providers
from tap_titans.models import models


# 소켓 서버의 호스트와 포트
HOST = '127.0.0.1'
PORT = 1234
def printdata(data):
    f = open('raiddata.log', 'a')
    f.write(data)
    f.write("\n")
    f.close()
    return

def start_client(msg):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        try:
            client.connect((HOST, PORT))
            print('Connected to {}:{}'.format(HOST, PORT))

            message = msg

            client.sendall(message.encode())
            response = client.recv(1024)
            print('Server response:', response.decode())

        except Exception as e:
            print('Error occurred:', str(e))

# ----
# TOKEN should not be provided here, this is purely for an example
# At minimum provide through .env
# ----
AUTH_TOKEN = "c88595b8-168e-4fc8-a37c-e90052c2d41d"
PLAYER_TOKENS = ["08a9a652-d38b-4a57-b573-775693a66d4f"]


# We have to subscribe after we connect
async def connected():
    print("Connected")

    r = providers.RaidRestAPI(AUTH_TOKEN)

    resp = await r.subscribe(PLAYER_TOKENS)
    if len(resp.refused) > 0:
        print("Failed to subscribe to clan with reason:", resp.refused[0].reason)
    else:
        print("Subscribed to clan:", resp.ok[0].clan_code)


# Here is an example of every event type with its corresponding object
# Each message has a param called message. This is a python object that can be navigated through dot notation
# View the corresponding object in the models directory
async def disconnected():
    print("Disconnected")


async def error(message: models.Message):
    printdata(str(message))
    print("Error", message)


async def connection_error(message: models.Message):
    printdata(str(message))
    print("Connection Error", message)


async def clan_removed(message: models.ClanRemoved):
    printdata(str(message))
    print("Clan Removed", message)


async def raid_attack(message: models.RaidAttack):
    printdata(str(message))
    js1 = str(message).replace("None", "'None'")
    js1 = js1.replace("'", '"')
    jsonObject = json.loads(js1)
    data = str(jsonObject.get('player').get('name')+'('+str(jsonObject.get('player').get('raid_level'))+') 남은타수:'+str(jsonObject.get('player').get('attacks_remaining')))
    data = data + '\n' + str('카드 : ' + jsonObject.get('attack_log').get('cards_level')[0].get('id') + '('+str(jsonObject.get('attack_log').get('cards_level')[0].get('value'))+'),' + jsonObject.get('attack_log').get('cards_level')[1].get('id') + '('+str(jsonObject.get('attack_log').get('cards_level')[1].get('value'))+'),' + jsonObject.get('attack_log').get('cards_level')[2].get('id') + '('+str(jsonObject.get('attack_log').get('cards_level')[2].get('value'))+'),')
    start_client(str(data))
    print("Raid Attack", data)


async def raid_start(message: models.RaidStart):
    printdata(str(message))
    print("Raid Start", message)


async def clan_added_raid_start(message: models.RaidStart):
    printdata(str(message))
    print("Clan Added Raid Start", message)


async def raid_end(message: models.RaidEnd):
    printdata(str(message))
    print("Raid End", message)


async def raid_retire(message: models.RaidRetire):
    printdata(str(message))
    print("Raid Retire", message)


async def raid_cycle_reset(message: models.RaidCycleReset):
    printdata(str(message))
    print("Raid Cycle Reset", message)


async def clan_added_cycle(message: models.RaidCycleReset):
    printdata(str(message))
    print("Clan Added Cycle", message)


async def raid_target_changed(message: models.RaidTarget):
    printdata(str(message))
    print("Raid Target Changed", message)


wsc = providers.WebsocketClient(
    connected=connected,
    disconnected=disconnected,
    error=error,
    connection_error=connection_error,
    clan_removed=clan_removed,
    raid_attack=raid_attack,
    raid_start=raid_start,
    clan_added_raid_start=clan_added_raid_start,
    raid_end=raid_end,
    raid_retire=raid_retire,
    raid_cycle_reset=raid_cycle_reset,
    clan_added_cycle=clan_added_cycle,
    raid_target_changed=raid_target_changed,
    setting_validate_arguments=False,
)


asyncio.run(wsc.connect(AUTH_TOKEN))
