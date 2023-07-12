import discord
import socket
import asyncio

# Discord 봇 토큰
TOKEN = 'MTEyMjkwNjc1MjU2NDg3MTE2OA.GqKKuD.EDGNNjOmp7OU26uuq_olEeV6m_ZCYVY1521rZc'
CHANNEL_ID = "968372146806063168"

HOST = '127.0.0.1'
PORT = 1234

# Discord 클라이언트 생성
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.content.startswith('!안녕'):
        await message.channel.send('안녕하세요')

    if message.author == client.user:
        return

    if message.content.startswith('!start_server'):
        await start_server(message.channel)

async def start_server(channel):
    try:
        server.bind((HOST, PORT))
        server.listen(1)
        await channel.send('Server started. Listening on {}:{}'.format(HOST, PORT))

        while True:
            conn, addr = server.accept()
            with conn:
                print('Connected by', addr)
                #await channel.send('Connected by {}'.format(addr))
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break
                    await channel.send('{}'.format(data.decode()))
                    conn.sendall('Message received'.encode())

    except Exception as e:
        await channel.send('Error occurred: {}'.format(str(e)))

client.run(TOKEN)
