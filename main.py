from pyrogram import Client
from pyrogram import filters
import os
import threading
import mdisk
import split

bot_token = os.environ.get("TOKEN", "") 
api_hash = os.environ.get("HASH", "") 
api_id = os.environ.get("ID", "") 

app = Client("my_bot",api_id=api_id, api_hash=api_hash,bot_token=bot_token)

TG_SPLIT_SIZE = 2097151000

@app.on_message(filters.command(["start"]))
def echo(client, message):
    app.send_message(message.chat.id, 'Send link like this >> /mdisk link')

'''async def progress(current, total):
    await app.send_message(message.chat.id,f"{current * 100 / total:.1f}%")'''

def down(v,a,message,link):
    app.send_message(message.chat.id, 'downloading')
    file = mdisk.mdow(link,v,a,message)
    size = split.get_path_size(file)
    if(size > 2097151000):
        app.send_message(message.chat.id, 'spliting')
        flist = split.split_file(file,size,file,".", TG_SPLIT_SIZE)
        os.remove(file)
        app.send_message(message.chat.id, 'uploading')
        i = 1
        for ele in flist:
            app.send_document(message.chat.id,document=ele,caption=f"part {i}")#, progress=progress)
            i = i + 1
            os.remove(ele)
    else:
        app.send_message(message.chat.id, 'uploading')
        app.send_document(message.chat.id,document=file)#, progress=progress)
        os.remove(file)


@app.on_message(filters.command(["mdisk"]))
def echo(client, message):
    try:
        link = message.text.split("mdisk ")[1]
        if "mdisk" in link:
            out = mdisk.req(link)
            app.send_message(message.chat.id, out)
            app.send_message(message.chat.id, 'send VideoID,AudioID like this >> 0,1')
            with open(f"{message.chat.id}.txt","w") as ci:
                ci.write(link)
    except:
        app.send_message(message.chat.id, 'send only mdisk link with command followed by link')

@app.on_message(filters.text)
def echo(client, message):
    if os.path.exists(f"{message.chat.id}.txt"):
        with open(f"{message.chat.id}.txt","r") as li:
            link = li.read()
        link = link.split("\n")[0] 
        os.remove(f"{message.chat.id}.txt")
        ids = message.text.split(",")
        d = threading.Thread(target=lambda:down(ids[0],ids[1],message,link),daemon=True)
        d.start()
        #await down(ids[0],ids[1],message,link)
    else:
        app.send_message(message.chat.id, "first send me link /mdisk")

app.run()    
