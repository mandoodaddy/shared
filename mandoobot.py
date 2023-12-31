from discord.ext import tasks
import discord
import socket
import asyncio
import json
import pandas as pd
import configparser

# configparser 객체 생성
config = configparser.ConfigParser()

# config.ini 파일 읽기
config.read('config.ini')

player_rawdata = {'player' : ['HY', 'ShiJinBBing', 'ShinBBing', '가설', '고만두', '굿럭', '나우니스리', '다정', '두더지', '또가스', '마스터즈', '만두아빠', '멍총이', '미스터문', '백야', '비의', '비즈맨', '새벽', '샤이즌', '쉼찡', '스톰피스트', '스포디', '신속', '신우', '야르', '에펠탑꼭대기', '으엌', '이실', '임일병', '잘께요', '저녁', '조운', '진진', '찐콩', '초점없는눈', '치느', '킹물소', '택돌이', '탭하는아재', '테이커', '텍스트', '페이트', '풍경', '프리츠', '핑프', '하울', '하트', '하하', '헬보이']}
HYDF = pd.DataFrame(player_rawdata)
HYDF['Void'] = 0
HYDF['VM'] = 0
HYDF['Tactics'] = 0
HYDF['AttackCount'] = 0
HYDF['History'] = ""
target_turn = 6
default_attack_count = 294
remain_count = target_turn * default_attack_count
remain_titan_hp = 0
# Discord 봇 토큰
#TOKEN = config.get('tester', 'token')
TOKEN = config.get('Config', 'token')

CHANNEL_ID = "968372146806063168"

HOST = '127.0.0.1'
PORT = 1234

bStartServer = False

# Discord 클라이언트 생성
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def attackupdate(row):
    row['AttackCount'] = row['AttackCount'] + 6
    return row['AttackCount']

async def send_message_to_bot(message):
    channel = client.get_channel(int(CHANNEL_ID))
    await channel.send(message)

@client.event
async def on_ready():
    channel = client.get_channel(int(CHANNEL_ID))
    await channel.send('mandoobot이 시작되었습니다.')
    print('Logged in as {0.user}'.format(client))

@client.event
async def on_custom_event(message):
    # 이벤트로 전달된 메시지를 처리
    print(f'Received message: {message}')

@client.event
async def on_message(message):
    global target_turn
    global remain_count
    if message.author == client.user:
        return
    if message.content.startswith('.void'):
        Void = list(HYDF[HYDF['Void'] == 0]['player'])
        await message.channel.send("%s 남은타수 : %d" % (str(Void), len(Void)))

    if message.content.startswith('.vm'):
        VM = list(HYDF[HYDF['VM'] == 0]['player'])
        await message.channel.send("%s 남은타수 : %d" % (str(VM), len(VM)))

    if message.content.startswith('.tac'):
        TAC = list(HYDF[HYDF['Tactics'] == 0]['player'])
        await message.channel.send("%s 남은타수 : %d" % (str(TAC), len(TAC)))

    if message.content.startswith('.ak'):
        ATTACKCOUNTLIST = list(HYDF[HYDF['AttackCount'] > 0]['player'])
        ATTACKCOUNT = list(HYDF[HYDF['AttackCount'] > 0]['AttackCount'])
        await message.channel.send(
            "%s\n 남은 사람수 : %d, 남은타수 : %d" % (str(ATTACKCOUNTLIST), len(ATTACKCOUNTLIST), sum(ATTACKCOUNT)))

    if message.content.startswith('.info'):
        content = str(message.content)
        word = content.split(" ")
        if len(word) >= 2:
            name = word[1]
            row = HYDF[HYDF['player'] == name]
            history = row.iloc[0]['History'].split("|")
            log = "attack log"
            for data in history:
                log = log + "\n" + raidinfoparser(data)
            log = log + "\nEnd log"
            await message.channel.send(log)

    if 'manduappa' in str(message.author):
        if message.content.startswith('.ss'):
            global bStartServer
            if bStartServer:
                await message.channel.send('이미 서버가 시작중입니다.')
            else:
                bStartServer = True
                asyncio.create_task(start_server(message.channel))

        if message.content.startswith('.st'):
            content = str(message.content)
            word = content.split(" ")
            if len(word) >= 2:
                target_turn = int(word[1])
                remain_count = target_turn * default_attack_count
                average = remain_titan_hp / remain_count
                await message.channel.send('%d턴 목표 설정 남은 타수 %d로 설정 되었습니다.\n목표 딜이 변경되었습니다. 클리어 남은 평딜(%.1fM)' % (target_turn, remain_count, average/1000000))

        if message.content.startswith('.srt'):
            content = str(message.content)
            word = content.split(" ")
            if len(word) >= 2:
                remain_count = int(word[1])
                average = remain_titan_hp / remain_count
                await message.channel.send('남은 타수 %d로 설정 되었습니다\n목표 딜이 변경되었습니다. 클리어 남은 평딜(%.1fM)' % (remain_count, average/1000000))
def raidinfoparser(data):
    global remain_count
    jsonObject2 = json.loads(data)
    remainhp = jsonObject2['remainhp']
    attack_count = jsonObject2['attack_count']
    remain_attach_count = remain_count - attack_count
    average = remainhp / remain_attach_count
    data = "%s(%d) 남은타수 : %d, Damage: %s\n" % (
    jsonObject2['name'], jsonObject2['raid_level'], jsonObject2['attacks_remaining'], jsonObject2['damage'])
    for cardlevel in jsonObject2['card_level']:
        cardemoji = discord.utils.get(client.emojis, name=cardlevel['id'])
        data = data + "%s (%d), " % (str(cardemoji), cardlevel['value'])
    data = data + '%d턴 클리어 남은 평딜(%.1fM)' % (target_turn, average/1000000)
    return data

async def attack_log(data, channel):
    jsonObject = json.loads(data)
    row = HYDF[HYDF['player'] == jsonObject['name']]
    history = row.iloc[0]['History']
    if history == "":
        history = data
    else:
        history = "%s|%s" % (history, data)
    HYDF.loc[HYDF['player'] == jsonObject['name'], 'History'] = history
    HYDF.loc[HYDF['player'] == jsonObject['name'], 'AttackCount'] = jsonObject['attacks_remaining']
    for cardlevel in jsonObject['card_level']:
        if 'FinisherAttack' in cardlevel.values():
            HYDF.loc[HYDF['player'] == jsonObject['name'], 'VM'] = 1
        if 'CrushingVoid' in cardlevel.values():
            HYDF.loc[HYDF['player'] == jsonObject['name'], 'Void'] = 1
        if 'TeamTactics' in cardlevel.values():
            HYDF.loc[HYDF['player'] == jsonObject['name'], 'Tactics'] = 1
    data = raidinfoparser(data)
    await channel.send('{}'.format(data))

async def start_server(channel):
    global remain_count
    global remain_titan_hp
    server.bind((HOST, PORT))
    server.listen(1)
    await channel.send('Server started')
    while True:
        try:
            testch = client.get_channel(1134146247540887693)
            await testch.send('hello')
        except Exception as e:
            print('Error occurred: {}'.format(str(e)))

        try:
            server.settimeout(5.0)
            conn, addr = server.accept()
        except Exception as e:
            continue

        try:
            with conn:
                #print('Connected by', addr)
                #await channel.send('Connected')
                while True:
                    conn.settimeout(5.0)
                    data = conn.recv(1024)
                    if not data:
                        break
                    data = data.decode()
                    #print(data)
                    jsonObject = json.loads(data)
                    if 'attack_log' in jsonObject:
                        await attack_log(str(jsonObject['attack_log']).replace("'", '"'), channel)
                    elif 'raid_end' in jsonObject:
                        HYDF['Void'] = 0
                        HYDF['VM'] = 0
                        HYDF['Tactics'] = 0
                        HYDF['AttackCount'] = 6
                        HYDF['History'] = ""
                        await channel.send('raid가 종료되었습니다')
                    elif 'raid_cycle_reset' in jsonObject:
                        HYDF['Void'] = 0
                        HYDF['VM'] = 0
                        HYDF['Tactics'] = 0
                        HYDF['AttackCount'] = HYDF.apply(attackupdate, axis=1)
                        HYDF['History'] = ""
                        await channel.send('raid 턴이 reset 되었습니다')
                    elif 'clan_added_cycle' in jsonObject:
                        clan_added_cycle = jsonObject['clan_added_cycle']
                        remainhp = clan_added_cycle['remainhp']
                        remain_titan_hp = remainhp
                        average = remainhp / remain_count
                        await channel.send('raid가 추가 되었습니다. 남은 목표 평딜은 (%.1fM) 입니다.' % (average/1000000))
                    elif 'raid_target_changed' in jsonObject:
                        raid_target_changed = jsonObject['raid_target_changed']
                        remainhp = raid_target_changed['remainhp']
                        remain_titan_hp = remainhp
                        average = remainhp / remain_count
                        await channel.send('Target이 변경되었습니다. 남은 목표 평딜은 (%.1fM) 입니다.' % (average/1000000))
                    elif 'clan_added_raid_start' in jsonObject:
                        clan_added_raid_start = jsonObject['clan_added_raid_start']
                        remainhp = clan_added_raid_start['remainhp']
                        remain_titan_hp = remainhp
                        average = remainhp / remain_count
                        await channel.send('raid가 시작되었습니다. 남은 목표 평딜은 (%.1fM) 입니다.' % (average/1000000))

                    #elif 'raid_target_changed' in jsonObject:
                    #    await channel.send(str(jsonObject['raid_target_changed']))

                    conn.sendall('Message received'.encode())
        except Exception as e:
            print('Error occurred: {}'.format(str(e)))
            continue


client.run(TOKEN)
