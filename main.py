from pyrogram import Client
from pyrogram import filters
import os
import threading
import mdisk
import split
import subprocess
import time

bot_token = os.environ.get("TOKEN", "") 
api_hash = os.environ.get("HASH", "") 
api_id = os.environ.get("ID", "")

app = Client("my_bot",api_id=api_id, api_hash=api_hash,bot_token=bot_token)
TG_SPLIT_SIZE = 2097151000

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
        
    app.edit_message_text(message.chat.id, message.id, "Uploading..")
    

def down(message,link):
    msg = app.send_message(message.chat.id, 'Downloading...', reply_to_message_id=message.id)
    sta = threading.Thread(target=lambda:status(str(message.id),msg),daemon=True)
    sta.start()

    file = mdisk.mdow(link,message)
    size = split.get_path_size(file)

    if(size > 2097151000):
        app.edit_message_text(message.chat.id, msg.id, "Splitting...")
        flist = split.split_file(file,size,file,".", TG_SPLIT_SIZE)
        os.remove(file)
        app.edit_message_text(message.chat.id, msg.id, "Uploading...")
        i = 1
        for ele in flist:
            app.send_document(message.chat.id,document=ele,caption=f"part {i}", reply_to_message_id=message.id)#, progress=progress)
            i = i + 1
            os.remove(ele)
    else:
        app.edit_message_text(message.chat.id, msg.id, "Uploading...")
        try:
            app.send_document(message.chat.id,document=file, reply_to_message_id=message.id)#, progress=progress)
        except:
            app.send_message(message.chat.id,"Error in Merging File")
        os.remove(file)

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
