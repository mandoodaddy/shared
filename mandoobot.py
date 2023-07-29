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

player_rawdata = {'player' : ['HY', 'ShiJinBBing', 'ShinBBing', '가설', '고만두', '굿럭', '나우니스리', '다정', '다킁이', '두더지', '또가스', '마스터즈', '만두아빠', '미스터문', '백야', '비의', '비즈맨', '새벽', '샤이즌', '소이츠맨', '쉼찡', '스톰피스트', '스포디', '신속', '신우', '야르', '어택', '에펠탑꼭대기', '으엌', '이실', '임일병', '저녁', '조운', '진진', '찐콩', '초점없는눈', '치느', '킹물소', '택돌이', '탭하는아재', '테이커', '텍스트', '페이트', '풍경', '프리츠', '핑프', '하울', '하트', '하하', '헬보이']}
HYDF = pd.DataFrame(player_rawdata)
HYDF['Void'] = 0
HYDF['VM'] = 0
HYDF['Tactics'] = 0
HYDF['AttackCount'] = 0
HYDF['History'] = ""
target_turn = 6
remain_count = 1800
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

    if 'manduappa' in str(message.author):
        if message.content.startswith('!Void') or message.content.startswith('!void'):
            Void = list(HYDF[HYDF['Void'] == 0]['player'])
            await message.channel.send("%s 남은타수 : %d" % (str(Void), len(Void)))

        if message.content.startswith('!vm') or message.content.startswith('!VM'):
            VM = list(HYDF[HYDF['VM'] == 0]['player'])
            await message.channel.send("%s 남은타수 : %d" % (str(VM), len(VM)))

        if message.content.startswith('!tac'):
            TAC = list(HYDF[HYDF['Tactics'] == 0]['player'])
            await message.channel.send("%s 남은타수 : %d" % (str(TAC), len(TAC)))

        if message.content.startswith('!attack'):
            ATTACKCOUNTLIST = list(HYDF[HYDF['AttackCount'] > 0]['player'])
            ATTACKCOUNT = list(HYDF[HYDF['AttackCount'] > 0]['AttackCount'])
            await message.channel.send("%s\n 남은 사람수 : %d, 남은타수 : %d" % (str(ATTACKCOUNTLIST), len(ATTACKCOUNTLIST), sum(ATTACKCOUNT)))

        if message.content.startswith('!info'):
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

        if message.content.startswith('.안녕'):
            await message.channel.send('안녕하세요')

        if message.content.startswith('.start_server'):
            global bStartServer
            if bStartServer:
                await message.channel.send('이미 서버가 시작중입니다.')
            else:
                bStartServer = True
                asyncio.create_task(start_server(message.channel))

        if message.content.startswith('.setturn'):
            content = str(message.content)
            word = content.split(" ")
            if len(word) >= 2:
                target_turn = int(word[1])
                remain_count = target_turn * 300
                await message.channel.send('%d턴 목표 설정 남은 타수 %d로 설정 되었습니다' % (target_turn, remain_count))

        if message.content.startswith('.setremaincount'):
            content = str(message.content)
            word = content.split(" ")
            if len(word) >= 2:
                remain_count = int(word[1])
                await message.channel.send('남은 타수 %d로 설정 되었습니다' % (remain_count))
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
    data = data + '%d턴목표 평딜(%.1fM)' % (target_turn, average/1000000)
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
    server.bind((HOST, PORT))
    server.listen(1)
    await channel.send('Server started')
    while True:
        try:
            server.settimeout(5.0)
            conn, addr = server.accept()
            with conn:
                print('Connected by', addr)
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
                    elif 'raid_cycle_reset' in jsonObject:
                        HYDF['Void'] = 0
                        HYDF['VM'] = 0
                        HYDF['Tactics'] = 0
                        HYDF['AttackCount'] = HYDF.apply(attackupdate, axis=1)
                        HYDF['History'] = ""
                    #elif 'raid_target_changed' in jsonObject:
                    #    await channel.send(str(jsonObject['raid_target_changed']))

                    conn.sendall('Message received'.encode())
        except Exception as e:
            #print('Error occurred: {}'.format(str(e)))
            await channel.webhooks()
            continue


client.run(TOKEN)
