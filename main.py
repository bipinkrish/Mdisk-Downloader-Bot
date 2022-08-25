import os
import threading
import subprocess
import time

import pyrogram
from pyrogram import Client
from pyrogram import filters

import mdisk
import split
from split import TG_SPLIT_SIZE


# app
bot_token = os.environ.get("TOKEN", "") 
api_hash = os.environ.get("HASH", "") 
api_id = os.environ.get("ID", "")
app = Client("my_bot",api_id=api_id, api_hash=api_hash,bot_token=bot_token)


# start command
@app.on_message(filters.command(["start"]))
def echo(client: pyrogram.client.Client, message: pyrogram.types.messages_and_media.message.Message):
    app.send_message(message.chat.id, '**Send link like this >> __/mdisk link__**',reply_to_message_id=message.id)


# download status
def status(folder,message):

    length = len(folder)
    # wait for the folder to create
    while True:
        if os.path.exists(folder + "/vid.mp4.part-Frag0") or os.path.exists(folder + "/vid.mp4.part"):
            break
    
    time.sleep(3)
    while os.path.exists(folder + "/" ):
        result = subprocess.run(["du", "-hs", f"{folder}/"], capture_output=True, text=True)
        size = result.stdout[:-(length+2)]
        try:
            app.edit_message_text(message.chat.id, message.id, f"__Downloaded__ : **{size}**")
            time.sleep(10)
        except:
            time.sleep(5)


# upload status
def upstatus(statusfile,message):

    while True:
        if os.path.exists(statusfile):
            break

    time.sleep(3)      
    while os.path.exists(statusfile):
        with open(statusfile,"r") as upread:
            txt = upread.read()
        try:
            app.edit_message_text(message.chat.id, message.id, f"__Uploaded__ : **{txt}**")
            time.sleep(10)
        except:
            time.sleep(5)


# progress writter
def progress(current, total, message):
    with open(f'{message.id}upstatus.txt',"w") as fileup:
        fileup.write(f"{current * 100 / total:.1f}%")


# download and upload
def down(message,link):

    msg = app.send_message(message.chat.id, '__Downloading__', reply_to_message_id=message.id)
    sta = threading.Thread(target=lambda:status(str(message.id),msg),daemon=True)
    sta.start()

    file,check = mdisk.mdow(link,message)

    if file == None:
        app.edit_message_text(message.chat.id, msg.id,"__**Invalid Link**__")
        return

    size = split.get_path_size(file)

    upsta = threading.Thread(target=lambda:upstatus(f'{message.id}upstatus.txt',msg),daemon=True)
    upsta.start()

    if(size > TG_SPLIT_SIZE):

        app.edit_message_text(message.chat.id, msg.id, "__Splitting__")
        flist = split.split_file(file,size,file,".", TG_SPLIT_SIZE)
        os.remove(file)
        app.edit_message_text(message.chat.id, msg.id, "__Uploading__")
        i = 1

        for ele in flist:
            if not os.path.exists(f'{message.from_user.id}-thumb.jpg'):
                app.send_document(message.chat.id,document=ele,caption=f"__**part {i}**__", reply_to_message_id=message.id, progress=progress, progress_args=[message])
            else:
                app.send_document(message.chat.id,document=ele,caption=f"__**part {i}**__", thumb=f'{message.from_user.id}-thumb.jpg', reply_to_message_id=message.id, progress=progress, progress_args=[message])
            i = i + 1
            os.remove(ele)
    
    else:
        app.edit_message_text(message.chat.id, msg.id, "__Uploading __")
        if os.path.exists(file):
            if not os.path.exists(f'{message.from_user.id}-thumb.jpg'):
                app.send_document(message.chat.id,document=file, reply_to_message_id=message.id, progress=progress, progress_args=[message])
            else:
                app.send_document(message.chat.id,document=file, thumb=f'{message.from_user.id}-thumb.jpg', reply_to_message_id=message.id, progress=progress, progress_args=[message])  
            os.remove(file)
        else:
            app.send_message(message.chat.id,"**Error in Merging File**",reply_to_message_id=message.id)
        
    if check == 0:
        app.send_message(message.chat.id,"__Can't remove the **restriction**, you have to use **MX player** to play this **video**\n\nThis happens because either the **file** length is **too small** or **video** doesn't have separate **audio layer**__",reply_to_message_id=message.id)
    os.remove(f'{message.id}upstatus.txt')
    app.delete_messages(message.chat.id,message_ids=[msg.id])


# mdisk command
@app.on_message(filters.command(["mdisk"]))
def mdiskdown(client: pyrogram.client.Client, message: pyrogram.types.messages_and_media.message.Message):
    
    try:
        link = message.text.split("mdisk ")[1]
        if "mdisk" in link:
            d = threading.Thread(target=lambda:down(message,link),daemon=True)
            d.start()
    except:
        app.send_message(message.chat.id, '**Send only __MDisk Link__ with command followed by the link**',reply_to_message_id=message.id)


# thumb command
@app.on_message(filters.command(["thumb"]))
def thumb(client: pyrogram.client.Client, message: pyrogram.types.messages_and_media.message.Message):
    
    try:
        if int(message.reply_to_message.document.file_size) > 200000:
            app.send_message(message.chat.id, '**Thumbline size allowed is < 200 KB**',reply_to_message_id=message.id)
            return

        msg = app.get_messages(message.chat.id, int(message.reply_to_message.id))
        file = app.download_media(msg)
        os.rename(file,f'{message.from_user.id}-thumb.jpg')
        app.send_message(message.chat.id, '**Thumbnail is Set**',reply_to_message_id=message.id)

    except:
        app.send_message(message.chat.id, '**reply __/thumb__ to a image document of size less than 200KB**',reply_to_message_id=message.id)


# show thumb command
@app.on_message(filters.command(["show"]))
def showthumb(client: pyrogram.client.Client, message: pyrogram.types.messages_and_media.message.Message):
    if os.path.exists(f'{message.from_user.id}-thumb.jpg'):
        app.send_photo(message.chat.id,photo=f'{message.from_user.id}-thumb.jpg',reply_to_message_id=message.id)
    else:
        app.send_message(message.chat.id, '**Thumbnail is not Set**',reply_to_message_id=message.id)


# remove thumbline command
@app.on_message(filters.command(["remove"]))
def removethumb(client: pyrogram.client.Client, message: pyrogram.types.messages_and_media.message.Message):
    if os.path.exists(f'{message.from_user.id}-thumb.jpg'):
        os.remove(f'{message.from_user.id}-thumb.jpg')
        app.send_message(message.chat.id, '**Thumbnail is Removed**',reply_to_message_id=message.id)
    else:
        app.send_message(message.chat.id, '**Thumbnail is not Set**',reply_to_message_id=message.id)


# thumbline
@app.on_message(filters.photo)
def ptumb(client: pyrogram.client.Client, message: pyrogram.types.messages_and_media.message.Message):
    file = app.download_media(message)
    os.rename(file,f'{message.from_user.id}-thumb.jpg')
    app.send_message(message.chat.id, '**Thumbnail is Set**',reply_to_message_id=message.id)
    

# polling
app.run()    
