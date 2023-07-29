import asyncio
import socket
import json
import time
import copy
from tap_titans.providers import providers
from tap_titans.models import models

titan_hp_info = []
attack_count = 0
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


def update_info(titan_hp_info, raid_state):
    titan_index = raid_state['titan_index']
    parts = titan_hp_info[titan_index]['part']
    current = raid_state['current']
    current_hp = current['current_hp']
    current_parts = current['parts']
    titan_hp_info[titan_index]['total_hp'] = current_hp
    for i, current_part in enumerate(current_parts):
        titan_hp_info[titan_index]['part'][i]['total_hp'] = current_part['current_hp']
    return titan_hp_info

def remain_hp(titan_hp_info, raid_state):
    titan_index = raid_state['titan_index']
    sum = 0.0
    for i, titan in enumerate(titan_hp_info):
        if i < titan_index: continue
        total_hp = titan['total_hp']
        armor = 0.0
        for part in titan['part']:
            if part['state'] != '2':continue
            if 'Armor' in part['part_id']:
                armor += part['total_hp']
        total_hp += armor
        sum += total_hp
    return sum

def parser_log(message):
    jsonObject = json.loads(message)
    data = ''
    global attack_count
    global titan_hp_info
    if 'clan_added_raid_start' in jsonObject:
        titan_hp_info = []
        attack_count = 0
        clan_added_raid_start = jsonObject['clan_added_raid_start']
        raid = clan_added_raid_start['raid']
        titan_target = clan_added_raid_start['titan_target']
        spawn_sequence = raid['spawn_sequence']
        titans = raid['titans']

        titans_info = {}
        for target, titan in zip(titan_target, titans):
            state_list = [x for x in target['state'] for _ in range(2)]
            parts = titan['parts']
            name = titan['enemy_name']
            titan_info = {}
            titan_info['total_hp'] = titan['total_hp']
            part_list = []
            for part, state in zip(parts, state_list):
                part['state'] = state['state']
                part_list.append(part)
            titan_info['part'] = part_list
            titan_info['name'] = name
            titans_info[name] = titan_info
        titan_hp_info = []
        for titan in spawn_sequence:
            titan_hp_info.append(copy.deepcopy(titans_info[titan]))
    elif 'raid_attack' in jsonObject:
        attack_count += 1
        raid_attack = jsonObject['raid_attack']
        attack_log = raid_attack['attack_log']
        raid_state = raid_attack['raid_state']
        titan_hp_info = update_info(titan_hp_info, raid_state)
        remainhp = remain_hp(titan_hp_info, raid_state)

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
        player = raid_attack['player']
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
        data = data + '"damage" : "%s",' % total_damage
        data = data + '"attack_count" : %d,' % attack_count
        data = data + '"remainhp" : %d' % remainhp
        data = data + '}'
        data = '{"attack_log": %s}' % data
    elif 'clan_added_cycle' in jsonObject:
        titan_hp_info = []
        clan_added_cycle = jsonObject['clan_added_cycle']
        raid = clan_added_cycle['raid']
        titan_target = clan_added_cycle['titan_target']
        spawn_sequence = raid['spawn_sequence']
        titans = raid['titans']

        titans_info = {}
        for target, titan in zip(titan_target, titans):
            state_list = [x for x in target['state'] for _ in range(2)]
            parts = titan['parts']
            name = titan['enemy_name']
            titan_info = {}
            titan_info['total_hp'] = titan['total_hp']
            part_list = []
            for part, state in zip(parts, state_list):
                part['state'] = state['state']
                part_list.append(part)
            titan_info['part'] = part_list
            titan_info['name'] = name
            titans_info[name] = titan_info
        for titan in spawn_sequence:
            titan_hp_info.append(copy.deepcopy(titans_info[titan]))
    else:
        data = message
    return data
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
    start_client(str(parser_log(data)))
    print("Clan Removed", message)


async def raid_attack(message: models.RaidAttack):
    message = jsondataformat(str(message))
    data = '{"raid_attack": %s}' % message
    start_client(str(parser_log(data)))
    print("Raid Attack", data)


async def raid_start(message: models.RaidStart):
    message = jsondataformat(str(message))
    data = '{"raid_start": %s}' % message
    start_client(str(parser_log(data)))
    print("Raid Start", message)


async def clan_added_raid_start(message: models.RaidStart):
    message = jsondataformat(str(message))
    data = '{"clan_added_raid_start": %s}' % message
    start_client(str(parser_log(data)))
    print("Clan Added Raid Start", message)


async def raid_end(message: models.RaidEnd):
    message = jsondataformat(str(message))
    data = '{"raid_end": %s}' % message
    start_client(str(parser_log(data)))
    print("Raid End", message)


async def raid_retire(message: models.RaidRetire):
    message = jsondataformat(str(message))
    data = '{"raid_retire": %s}' % message
    start_client(str(parser_log(data)))
    print("Raid Retire", message)


async def raid_cycle_reset(message: models.RaidCycleReset):
    message = jsondataformat(str(message))
    data = '{"raid_cycle_reset": %s}' % message
    start_client(str(parser_log(data)))
    print("Raid Cycle Reset", message)

async def clan_added_cycle(message: models.RaidCycleReset):
    message = jsondataformat(str(message))
    data = '{"clan_added_cycle": %s}' % message
    start_client(str(parser_log(data)))
    print("Clan Added Cycle", message)

async def raid_target_changed(message: models.RaidTarget):
    message = jsondataformat(str(message))
    data = '{"raid_target_changed": %s}' % message
    start_client(str(parser_log(data)))
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


