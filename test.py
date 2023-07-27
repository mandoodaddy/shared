import asyncio
import socket
import json
import discord
import time
from tap_titans.providers import providers
from tap_titans.models import models

TOKEN = 'MTEyMjkwNjc1MjU2NDg3MTE2OA.GEVCRg.5OUvksV7g0ba30jXBw24G29DulBtTRo1hVB3vU'
CHANNEL_ID = "968372146806063168"
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
channel = ""

# 소켓 서버의 호스트와 포트
HOST = '127.0.0.1'
PORT = 1234
def printdata(data):
    #f = open('raiddata.log', 'a')
    #f.write(data)
    #f.write('\n')
    #f.close()
    return

def start_client(msg):

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        while True:
            try:
                client.connect((HOST, PORT))
                print('Connected to {}:{}'.format(HOST, PORT))

                message = msg

                client.sendall(message.encode())
                response = client.recv(1024)
                #print('Server response:', response.decode())
                break
            except Exception as e:
                #print('Error occurred:', str(e))
                time.sleep(1)  # 1초 대기 후 재시도


# ----
# TOKEN should not be provided here, this is purely for an example
# At minimum provide through .env
# ----
AUTH_TOKEN = "c88595b8-168e-4fc8-a37c-e90052c2d41d"
PLAYER_TOKENS = ["08a9a652-d38b-4a57-b573-775693a66d4f"]

def jsondataformat(msg):
    msg = msg.replace("None", "'None'").replace("True", "'True'").replace("False", "'False'")
    msg = msg.replace("'", '"')
    return msg
# We have to subscribe after we connect
async def connected():
    print("Connected")

    r = providers.RaidRestAPI(AUTH_TOKEN)

    resp = await r.subscribe(PLAYER_TOKENS)
    if len(resp.refused) > 0:
        print("Failed to subscribe to clan with reason:", resp.refused[0].reason)
    else:
        print("Subscribed to clan:", resp.ok[0])


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
    message = jsondataformat(str(message))
    data = '{"clan_removed": %s}' % message
    printdata(str(data))
    print("Clan Removed", message)


async def raid_attack(message: models.RaidAttack):
    message = jsondataformat(str(message))
    data = '{"raid_attack": %s}' % message
    printdata(str(data))
    jsonObject = json.loads(message)
    data = ''
    if 'attack_log' in jsonObject:
        attack_log = jsonObject['attack_log']
        total_damage = 0
        for cards_damage in attack_log['cards_damage']:
            for damage_log in cards_damage['damage_log']:
                total_damage += int(damage_log['value'])
        if total_damage > 1000000:
            total_damage = "%.2fM" % (total_damage / 1000000)
        elif total_damage > 1000:
            total_damage = "%.2fk" % (total_damage / 1000)
        else:
            total_damage = "%d" % (total_damage)
        player = jsonObject['player']
        # print(str(damage_log))
        data = '{'
        data = data + ('"name" : "%s",' % player['name'])
        data = data + ('"raid_level" : %d,' % player['raid_level'])
        data = data + ('"attacks_remaining" : %d,' % player['attacks_remaining'])
        data = data + '"card_level":['
        index = 0
        for cardlevel in attack_log['cards_level']:
            if index == 0:
                data = data + '{"id" : "%s", "value": %d}' % (cardlevel['id'], cardlevel['value'])
            else:
                data = data + ',{"id" : "%s", "value": %d}' % (cardlevel['id'], cardlevel['value'])
            index = index + 1
        data = data + '],'
        data = data + '"damage" : "%s"' % total_damage
        data = data + '}'
        data = '{"attack_log": %s}' % data
    start_client(str(data))
    print("Raid Attack", data)


async def raid_start(message: models.RaidStart):
    message = jsondataformat(str(message))
    data = '{"raid_start": %s}' % message
    printdata(str(data))
    print("Raid Start", message)


async def clan_added_raid_start(message: models.RaidStart):
    message = jsondataformat(str(message))
    data = '{"clan_added_raid_start": %s}' % message
    printdata(str(data))
    print("Clan Added Raid Start", message)


async def raid_end(message: models.RaidEnd):
    message = jsondataformat(str(message))
    data = '{"raid_end": %s}' % message
    printdata(str(data))
    start_client(str(data))
    print("Raid End", message)


async def raid_retire(message: models.RaidRetire):
    message = jsondataformat(str(message))
    data = '{"raid_retire": %s}' % message
    printdata(str(data))
    print("Raid Retire", message)


async def raid_cycle_reset(message: models.RaidCycleReset):
    message = jsondataformat(str(message))
    data = '{"raid_cycle_reset": %s}' % message
    printdata(str(data))
    start_client(str(data))
    print("Raid Cycle Reset", message)

async def clan_added_cycle(message: models.RaidCycleReset):
    message = jsondataformat(str(message))
    data = '{"clan_added_cycle": %s}' % message
    printdata(str(data))
    print("Clan Added Cycle", message)

async def raid_target_changed(message: models.RaidTarget):
    message = jsondataformat(str(message))
    data = '{"raid_target_changed": %s}' % message
    printdata(str(data))
    start_client(str(data))
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


