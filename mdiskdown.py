from pyrogram import Client
from pyrogram import filters
import os
import mdisk

bot_token = os.environ.get("TOKEN", "") 
api_hash = os.environ.get("HASH", "") 
api_id = os.environ.get("ID", "") 

app = Client("my_bot",api_id=api_id, api_hash=api_hash,bot_token=bot_token)

global mess,sta,linkk
sta = False

@app.on_message(filters.command(["start"]))
async def echo(client, message):
    await app.send_message(message.chat.id, 'Send me the mdisk link like this >> /mdisk link')

async def progress(current, total):
    global mess
    await app.send_message(mess.chat.id,f"{current * 100 / total:.1f}%")

async def down(v,a):
    global linkk, mess
    await app.send_message(mess.chat.id, 'downloading')
    file = mdisk.mdow(linkk,v,a)
    await app.send_message(mess.chat.id, 'uploading')
    await app.send_document(chat_id=623741973,document=file)#, progress=progress)
    os.remove(file)


@app.on_message(filters.command(["mdisk"]))
async def echo(client, message):
    global mess, sta, linkk
    link = message.text.split("mdisk ")[1]
    if "mdisk" in link:
        mess = message
        out = mdisk.req(link)
        await app.send_message(message.chat.id, out)
        await app.send_message(message.chat.id, 'send VideoID,AudioID like this >> 0,1')
        sta = True
        linkk = link
    else:
        await app.send_message(message.chat.id, 'send only mdisk link')
        await app.send_message(623741973,link)

@app.on_message()
async def echo(client, message):
    global sta
    if sta:
        ids = message.text.split(",")
        await down(ids[0],ids[1])
        sta = False

app.run()    