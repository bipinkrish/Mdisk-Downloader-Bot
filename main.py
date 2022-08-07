import os
import threading
import subprocess
import time

from pyrogram import Client
from pyrogram import filters

import mdisk
import split
from split import TG_SPLIT_SIZE


bot_token = os.environ.get("TOKEN", "") 
api_hash = os.environ.get("HASH", "") 
api_id = os.environ.get("ID", "")
app = Client("my_bot",api_id=api_id, api_hash=api_hash,bot_token=bot_token)


@app.on_message(filters.command(["start"]))
def echo(client, message):
    app.send_message(message.chat.id, 'Send link like this >> /mdisk link')


def status(folder,message):
    length = len(folder)
    
    # wait for the folder to create
    while True:
        if os.path.exists(folder + "/vid.mp4.part-Frag0"):
            break
    
    while os.path.exists(folder + "/" ):
        result = subprocess.run(["du", "-hs", f"{folder}/"], capture_output=True, text=True)
        size = result.stdout[:-(length+2)]
        try:
            app.edit_message_text(message.chat.id, message.id, f"Downloaded : {size}")
            time.sleep(10)
        except:
            time.sleep(5)


def upstatus(statusfile,message):

    while True:
        if os.path.exists(statusfile):
            break
        
    txt = "0%"    
    while os.path.exists(statusfile):
        with open(statusfile,"r") as upread:
            txt = upread.read()
        try:
            app.edit_message_text(message.chat.id, message.id, f"Uploaded : {txt}")
            time.sleep(10)
        except:
            time.sleep(5)


def progress(current, total, message):
    with open(f'{message.id}upstatus.txt',"w") as fileup:
        fileup.write(f"{current * 100 / total:.1f}%")


def down(message,link):
    msg = app.send_message(message.chat.id, 'Downloading...', reply_to_message_id=message.id)
    sta = threading.Thread(target=lambda:status(str(message.id),msg),daemon=True)
    sta.start()

    file = mdisk.mdow(link,message)
    size = split.get_path_size(file)

    upsta = threading.Thread(target=lambda:upstatus(f'{message.id}upstatus.txt',msg),daemon=True)
    upsta.start()

    if(size > TG_SPLIT_SIZE):
        app.edit_message_text(message.chat.id, msg.id, "Splitting...")
        flist = split.split_file(file,size,file,".", TG_SPLIT_SIZE)
        os.remove(file)
        app.edit_message_text(message.chat.id, msg.id, "Uploading...")
        i = 1
        for ele in flist:
            app.send_document(message.chat.id,document=ele,caption=f"part {i}", reply_to_message_id=message.id, progress=progress, progress_args=[message])
            i = i + 1
            os.remove(ele)
    else:
        app.edit_message_text(message.chat.id, msg.id, "Uploading...")
        try:
            app.send_document(message.chat.id,document=file, reply_to_message_id=message.id, progress=progress, progress_args=[message])
        except:
            app.send_message(message.chat.id,"Error in Merging File")
        os.remove(file)

    os.remove(f'{message.id}upstatus.txt')
    app.delete_messages(message.chat.id,message_ids=[msg.id])


@app.on_message(filters.command(["mdisk"]))
def echo(client, message):
    try:
        link = message.text.split("mdisk ")[1]
        if "mdisk" in link:
            d = threading.Thread(target=lambda:down(message,link),daemon=True)
            d.start()
    except:
        app.send_message(message.chat.id, 'send only mdisk link with command followed by link')

app.run()    
