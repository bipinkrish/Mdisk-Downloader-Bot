import os
import threading
import subprocess
import time
import json

import pyrogram
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ForceReply, BotCommand

from mdisk import iswin, getinfo, mdow, merge
import mediainfo
from split import TG_SPLIT_SIZE, split_file, get_path_size, ss, temp_channel, isPremmium

# conifg
with open('config.json', 'r') as f: CONFIGDATA = json.load(f)

# app
TOKEN = os.environ.get("TOKEN") or CONFIGDATA.get("TOKEN", "")
HASH = os.environ.get("HASH") or CONFIGDATA.get("HASH", "")
ID = os.environ.get("ID") or CONFIGDATA.get("ID", "")
app = Client("my_bot", api_id=ID, api_hash=HASH, bot_token=TOKEN)

# preiumum
if isPremmium: acc = Client("myacc", api_id=ID, api_hash=HASH, session_string=ss)

# optionals
AUTH = os.environ.get("AUTH") or CONFIGDATA.get("AUTH", "")
AUTHUSERS = AUTH.split()
BAN = os.environ.get("BAN") or CONFIGDATA.get("BAN", "")
BANNEDUSERS = BAN.split()

# control
OWNER = os.environ.get("OWNER") or CONFIGDATA.get("OWNER", "")
OWNERS = OWNER.split()
TARGET = os.environ.get("TARGET") or CONFIGDATA.get("TARGET", "")
LINK = os.environ.get("LINK") or CONFIGDATA.get("LINK", "")


# setting commands
cmds = ["start","help","mdisk","thumb","remove","show","change"]
descs = ["Basic Usage","Help Message","Usage","Reply to a Image of size less than 200KB to set it as Thumbnail","Remove Thumbnail","Show Thumbnail","Change Upload Mode"]
with app: app.set_bot_commands(BotCommand(cmds[i].lower(),descs[i]) for i in range(len(cmds)))


# formats data
datalist = {}
def adddata(id,mod): datalist[id] = mod
def getdata(id): return datalist.get(id,"D")
def swap(id):
    temp = getdata(id)
    if temp == "V": adddata(id,"D")
    else: adddata(id,"V")
    return getdata(id)


# msgs data
msgsdata = {}
def store(message,info,link): msgsdata[str(message.id)] = [message,info,link]
def get(id): return msgsdata.get(str(id), [None,None,None])


# locks
locks = {}
def setlock(uid,mid): locks[str(uid)] = mid
def getlock(uid): return locks.get(str(uid), None)


# progress tracker
prev = {}
prevtime = {}

# Create a progress bar
def progress_bar(progress):
    bar_length = 12
    filled_length = int(progress / (100/bar_length))
    bar = '█' * filled_length + '░' * (bar_length - filled_length)
    return f"[{bar}] {progress:.2f}%"

# format msgs
def getformatmsg(filename,status,procs,size,firsttime=False):
    if firsttime:
        previous_progress = 0
        previous_time = time.time()
    else:
        previous_progress = prev[filename]
        previous_time = prevtime[filename]

    progress = procs / size * 100
    speed = (progress - previous_progress) / (time.time() - previous_time) * 12.4
    prev[filename] = progress
    prevtime[filename] = time.time()

    return f"**{filename}**\n\n\
┌ Status: **{status}**\n\
├ {progress_bar(progress)}\n\
├ Processed: **{procs/1048000:.2f} MB**\n\
├ Total Size: **{size/1048000:.2f} MB**\n\
└ Speed: **{speed:.2f} MB/s**"


# check for user access
def checkuser(message):
    if isowner(message): return True
    user_id = str(message.from_user.id)
    if AUTHUSERS and user_id not in AUTHUSERS: return False
    if user_id in BANNEDUSERS: return False
    return True


# check for owner
def isowner(message):
    if str(message.from_user.id) in OWNERS: return True
    return False


# download status
def status(folder,message,fsize,filename):

    # wait for the folder to create
    while True:
        if os.path.exists(folder + "/vid.mp4.part-Frag0") or os.path.exists(folder + "/vid.mp4.part"):
            break
    
    time.sleep(3)
    while os.path.exists(folder + "/" ):
        if "Status: Merging" in app.get_messages(message.chat.id, message.id).text: return

        if iswin == "0":
            result = subprocess.run(["du", "-hsb", f"{folder}/"], capture_output=True, text=True)
            size = float(str(result.stdout).split()[0])
        else:
            os.system(f"dir /a/s {folder} > tempS-{message.id}.txt")
            size = float(open(f"tempS-{message.id}.txt","r").readlines()[-2].split()[2].replace(",",""))

        try:
            app.edit_message_text(message.chat.id, message.id, getformatmsg(filename,"Downloading",size,fsize))
            time.sleep(10)
        except:
            time.sleep(5)

    if iswin != "0": os.remove(f"tempS-{message.id}.txt")


# upload status
def upstatus(statusfile,message,filename):
    while True:
        if os.path.exists(statusfile):
            break

    time.sleep(3)      
    while os.path.exists(statusfile):
        with open(statusfile,"r") as upread:
            txt = upread.read().split()
        try:
            app.edit_message_text(message.chat.id, message.id, getformatmsg(filename,"Uploading",float(txt[0]),float(txt[1])))
            time.sleep(10)
        except:
            time.sleep(5)


# progress writter
def progress(current, total, message):
    with open(f'{message.id}upstatus.txt',"w") as fileup:
        fileup.write(f'{current} {total}')


# format printter
def formatprint(id,link="",edit=False,call=None, emsg=None):
    
    message,alldata,link = get(id)
    if message is None:
        app.edit_message_text(call.message.chat.id,call.message.id,"__Expired__")
        return
    m, s = divmod(alldata['duration'], 60)
    h, m = divmod(m, 60)
    format = "Document" if getdata(str(message.from_user.id)) == "D" else "Media/Stream"
    thumb,thum = ("Exists","Remove Thumbnail") if os.path.exists(f'{message.from_user.id}-thumb.jpg') else ("Not Exists","Set Thumbnail")
    text = f'__Filename:__ `{alldata["filename"]}`\n__Link:__ {link}\n\
__Size:__ **{alldata["size"]//1048000} MB**\n__Duration:__ **{h}h{m}m{s}s**\n\
__Resolution:__ **{alldata["width"]}x{alldata["height"]}**\n\
__Format:__ **{format}**\n__Thumbnail:__ **{thumb}**'
    keybord = InlineKeyboardMarkup(
            [   
                [
                    InlineKeyboardButton("Rename", callback_data=f'rename {message.id}'),
                    InlineKeyboardButton("Change Format", callback_data=f'change {message.id}')
                ],
                [ 
                    InlineKeyboardButton(thum, callback_data=f'thumb {message.id}'),
                    InlineKeyboardButton("Download", callback_data=f'down {message.id}') 
                ]
            ])

    if not edit:
        app.send_message(message.chat.id, text, reply_to_message_id=message.id, reply_markup=keybord)
    else:
        if call:
            app.edit_message_text(call.message.chat.id,call.message.id, text, reply_markup=keybord)
        else:
            app.edit_message_text(emsg.chat.id, emsg.reply_to_message.reply_to_message_id, text, reply_markup=keybord)

# handler
def handlereq(message,link):
    alldata = getinfo(link)

    if alldata.get("size", 0) == 0 or alldata.get("source", None) is None:
        app.send_message(message.chat.id,f"__Invalid Link : {link}__", reply_to_message_id=message.id)
        return

    store(message,alldata,link)
    formatprint(message.id,link)


# hanldle rename
def handlereanme(msg,id):
    setlock(msg.from_user.id,None)
    message,alldata,link = get(id)
    alldata['filename'] = msg.text
    store(message,alldata,link)
    formatprint(id,"",True,None,msg)
    app.delete_messages(msg.chat.id,[msg.id,msg.reply_to_message.id])


# handle thumb
def handlethumb(msg,id):
    setlock(msg.from_user.id,None)
    formatprint(id,"",True,None,msg)
    app.delete_messages(msg.chat.id,[msg.id,msg.reply_to_message.id])


# check for memeber present
def ismemberpresent(id):
    if TARGET == "" or LINK == "": return True
    try:
        app.get_chat_member(TARGET,id)
        return True
    except: return False
    

# start command
@app.on_message(filters.command(["start"]))
def echo(client: pyrogram.client.Client, message: pyrogram.types.messages_and_media.message.Message):

    if not checkuser(message):
        app.send_message(message.chat.id, '__You are either not **Authorized** or **Banned**__', reply_to_message_id=message.id,reply_markup=InlineKeyboardMarkup([[ InlineKeyboardButton("📦 Source Code", url="https://github.com/bipinkrish/Mdisk-Downloader-Bot")]]))
        return
    
    app.send_message(message.chat.id, f'__Hi {message.from_user.mention}, I am Mdisk Video Downloader, you can watch Downloaded Videos without MX Player.\n\nSend me a link to Start... or click /help to check usage__',reply_to_message_id=message.id,
    reply_markup=InlineKeyboardMarkup([[ InlineKeyboardButton("📦 Source Code", url="https://github.com/bipinkrish/Mdisk-Downloader-Bot")]]))


# help command
@app.on_message(filters.command(["help"]))
def help(client: pyrogram.client.Client, message: pyrogram.types.messages_and_media.message.Message):
    
    if not checkuser(message):
        app.send_message(message.chat.id, '__You are either not **Authorized** or **Banned**__',reply_to_message_id=message.id)
        return
    
    helpmessage = """__**/start** - basic usage
**/help** - 
**/mdisk mdisklink** - usage
**/thumb** - reply to a image document of size less than 200KB to set it as Thumbnail ( you can also send image as a photo to set it as Thumbnail automatically )
**/remove** - remove Thumbnail
**/show** - show Thumbnail
**/change** - change upload mode ( default mode is Document )__"""
    app.send_message(message.chat.id, helpmessage, reply_to_message_id=message.id)


# auth command
@app.on_message(filters.command(["auth","unauth"]))
def auth(client: pyrogram.client.Client, message: pyrogram.types.messages_and_media.message.Message):

    if not isowner(message):
        app.send_message(message.chat.id, '__You are not a Owner__', reply_to_message_id=message.id)
        return

    try: userid = str(message.reply_to_message.forward_from.id)
    except:
        try: userid = message.text.split("auth ")[1]
        except:
            app.send_message(message.chat.id, '__Invalid Format, use like this\n/auth 123456 or just reply command to a forwarded message of a user__',reply_to_message_id=message.id)
            return

    if "unauth" in message.text and userid in AUTHUSERS: AUTHUSERS.remove(userid)
    elif "unauth" not in message.text and userid not in AUTHUSERS: AUTHUSERS.append(userid)

    CONFIGDATA["AUTH"] = " ".join(AUTHUSERS)
    with open("config.json",'w') as f: json.dump(CONFIGDATA,f)

    if "unauth" in message.text: app.send_message(message.chat.id, f'__UnAuth Sucessful for **{userid}**\nuse /members to see the updated list__',reply_to_message_id=message.id)      
    else: app.send_message(message.chat.id, f'__Auth Sucessful for **{userid}**\nuse /members to see the updated list__',reply_to_message_id=message.id)        


# ban command
@app.on_message(filters.command(["ban","unban"]))
def ban(client: pyrogram.client.Client, message: pyrogram.types.messages_and_media.message.Message):

    if not isowner(message):
        app.send_message(message.chat.id, '__You are not a Owner__', reply_to_message_id=message.id)
        return

    try: userid = str(message.reply_to_message.forward_from.id)
    except:
        try: userid = message.text.split("ban ")[1]
        except:
            app.send_message(message.chat.id, '__Invalid Format, use like this\n/ban 123456 or just reply command to a forwarded message of a user__',reply_to_message_id=message.id)
            return

    if "unban" in message.text and userid in BANNEDUSERS: BANNEDUSERS.remove(userid)
    elif "unban" not in message.text and userid not in BANNEDUSERS: BANNEDUSERS.append(userid)

    CONFIGDATA["BAN"] = " ".join(BANNEDUSERS)
    with open("config.json",'w') as f: json.dump(CONFIGDATA,f)

    if "unban" in message.text: app.send_message(message.chat.id, f'__UnBan Sucessful for **{userid}**\nuse /members to see the updated list__',reply_to_message_id=message.id)      
    else: app.send_message(message.chat.id, f'__Ban Sucessful for **{userid}**\nuse /members to see the updated list__',reply_to_message_id=message.id)


# members command
@app.on_message(filters.command(["members"]))
def members(client: pyrogram.client.Client, message: pyrogram.types.messages_and_media.message.Message):
    
    if not isowner(message):
        app.send_message(message.chat.id, '__You are not a Owner__', reply_to_message_id=message.id)
        return

    owners = app.get_users(OWNERS)
    auths = app.get_users(AUTHUSERS)
    bans = app.get_users(BANNEDUSERS)

    app.send_message(message.chat.id,
    '**--OWNERS--**\n\n__' + (''.join([f"@{x.username} - `{x.id}`\n" for x in owners]) if len(owners)!= 0 else "__No Owners__") + "__\n" + 
    '**--AUTH USERS--**\n\n__' + (''.join([f"@{x.username} - `{x.id}`\n" for x in auths]) if len(auths)!= 0 else "__No Auth Users__") + "__\n" + 
    '**--BANNED USERS--**\n\n__' + (''.join([f"@{x.username} - `{x.id}`\n" for x in bans]) if len(bans)!= 0 else "__No Banned Users__") + "__",
    reply_to_message_id=message.id)


# callback
@app.on_callback_query()
def handle(client: pyrogram.client.Client, call: pyrogram.types.CallbackQuery):

    if call.from_user.id != call.message.reply_to_message.from_user.id: return

    if not ismemberpresent(call.from_user.id):
        app.send_message(call.message.chat.id, '__You are not a member of our Chat\nJoin and Retry__',reply_to_message_id=call.message.id,
        reply_markup=InlineKeyboardMarkup([[ InlineKeyboardButton("Join", url=LINK)]]))
        return

    data = call.data.split()[0]

    if  data == "down":
        downld = threading.Thread(target=lambda:startdown(call),daemon=True)
        downld.start()
    
    elif data == "change":
        swap(str(call.from_user.id))
        formatprint(call.data.split()[-1],"",True,call)

    elif data == "rename":
        id = int(call.data.split()[-1])
        if get(id)[0] is None: app.edit_message_text(call.message.chat.id,call.message.id,"__Expired__")
        else:
            setlock(call.from_user.id,id)
            app.send_message(call.message.chat.id, f"**{call.from_user.mention}** send me new Filename", reply_to_message_id=call.message.id, reply_markup=ForceReply(selective=True, placeholder="Filename..."))

    elif data == "thumb":
        if os.path.exists(f'{call.from_user.id}-thumb.jpg'):
            os.remove(f'{call.from_user.id}-thumb.jpg')
            formatprint(call.data.split()[-1],"",True,call)
        else:
            id = int(call.data.split()[-1])
            if get(id)[0] is None: app.edit_message_text(call.message.chat.id,call.message.id,"__Expired__")
            else:
                setlock(call.from_user.id,id)
                app.send_message(call.message.chat.id, f"**{call.from_user.mention}** send a Image", reply_to_message_id=call.message.id, reply_markup=ForceReply(selective=True, placeholder="Image..."))


# start process
def startdown(call):

    msg = call.message
    message,alldata,link = get(call.data.split()[-1])

    if message is None:
        app.edit_message_text(msg.chat.id, msg.id,"__Expired__")
        return

    # checking link and download with progress thread
    app.edit_message_text(msg.chat.id, msg.id, getformatmsg(alldata['filename'],"Downloading",0,alldata['size'],True))
    sta = threading.Thread(target=lambda:status(str(message.id),msg,alldata['size'],alldata['filename']),daemon=True)
    sta.start()

    # checking link and download
    file,check,filename = mdow(alldata,message)

    if file == None:
        app.edit_message_text(msg.chat.id, msg.id,f"__Invalid Link : {link}__")
        return

    # checking if its a link returned
    if check == -1:
        app.edit_message_text(msg.chat.id, msg.id,f"__Can't Download File but here is the Download Link : {alldata['download']} \n\n {alldata['source']}__")
        os.rmdir(str(message.id))
        return

    # merginig
    app.edit_message_text(message.chat.id, msg.id, getformatmsg(filename,"Merging",0,alldata['size'],True))
    file,check,filename = merge(message,file,check,filename)

    # checking size
    size = get_path_size(file)
    if(size > TG_SPLIT_SIZE):
        app.edit_message_text(message.chat.id, msg.id, getformatmsg(filename,"Spliting",0,alldata['size'],True))
        flist = split_file(file,size,file,".", TG_SPLIT_SIZE)
        os.remove(file) 
    else: flist = [file]

    app.edit_message_text(message.chat.id, msg.id, getformatmsg(filename,"Uploading",0,alldata['size'],True))
    i = 1

    # checking thumbline
    if not os.path.exists(f'{message.from_user.id}-thumb.jpg'): thumbfile = None
    else: thumbfile = f'{message.from_user.id}-thumb.jpg'

    # upload thread
    upsta = threading.Thread(target=lambda:upstatus(f'{message.id}upstatus.txt',msg,alldata['filename']),daemon=True)
    upsta.start()
    info = getdata(str(message.from_user.id))

    # uploading
    for ele in flist:

        # checking file existence
        if not os.path.exists(ele):
            app.send_message(message.chat.id,"__Error in Merging File__",reply_to_message_id=message.id)
            return
            
        # check if it's multi part
        if len(flist) == 1:
            partt = ""
        else:
            partt = f"__**part {i}**__\n"
            i = i + 1

        # actuall upload
        if info == "V":
            thumb,duration,width,height = mediainfo.allinfo(ele,thumbfile)
            if not isPremmium : app.send_video(message.chat.id, video=ele, caption=f"{partt}**{filename}**", thumb=thumb, duration=duration, height=height, width=width, reply_to_message_id=message.id, progress=progress, progress_args=[message])
            else:
                with acc: tmsg = acc.send_video(temp_channel, video=ele, caption=f"{partt}**{filename}**", thumb=thumb, duration=duration, height=height, width=width, progress=progress, progress_args=[message])
                app.copy_message(message.chat.id, temp_channel, tmsg.id, reply_to_message_id=message.id)
            if "-thumb.jpg" not in thumb: os.remove(thumb)
        else:
            if not isPremmium : app.send_document(message.chat.id, document=ele, caption=f"{partt}**{filename}**", thumb=thumbfile, force_document=True, reply_to_message_id=message.id, progress=progress, progress_args=[message])
            else:
                with acc: tmsg = acc.send_document(temp_channel, document=ele, thumb=thumbfile, caption=f"{partt}**{filename}**", force_document=True, progress=progress, progress_args=[message])
                app.copy_message(message.chat.id, temp_channel, tmsg.id, reply_to_message_id=message.id)
       
        # deleting uploaded file
        os.remove(ele)
        
    # checking if restriction is removed    
    if check == 0:
        app.send_message(message.chat.id,"__Can't remove the **restriction**, you have to use **MX player** to play this **video**\n\nThis happens because either the **file** length is **too small** or **video** doesn't have separate **audio layer**__",reply_to_message_id=message.id)
    if os.path.exists(f'{message.id}upstatus.txt'):
        os.remove(f'{message.id}upstatus.txt')
    app.delete_messages(message.chat.id,message_ids=[msg.id])


# mdisk command
@app.on_message(filters.command(["mdisk"]))
def mdiskdown(client: pyrogram.client.Client, message: pyrogram.types.messages_and_media.message.Message):
    if not checkuser(message):
        app.send_message(message.chat.id, '__You are either not **Authorized** or **Banned**__',reply_to_message_id=message.id)
        return

    if not ismemberpresent(message.from_user.id):
        app.send_message(message.chat.id, '__You are not a member of our Chat\nJoin and Retry__',reply_to_message_id=message.id,
        reply_markup=InlineKeyboardMarkup([[ InlineKeyboardButton("Join", url=LINK)]]))
        return

    try: link = message.reply_to_message.text
    except:
        try: link = message.text.split("mdisk ")[1]
        except:
            app.send_message(message.chat.id, '__Invalid Format, use like this\n/mdisk https://mdisk.me/xxxxx\nor just send a link without command__',reply_to_message_id=message.id)
            return

    if "https://mdisk.me/" in link: handlereq(message,link)
    else: app.send_message(message.chat.id, '__Send only MDisk Link with command followed by the link__',reply_to_message_id=message.id)


# thumb command
@app.on_message(filters.command(["thumb"]))
def thumb(client: pyrogram.client.Client, message: pyrogram.types.messages_and_media.message.Message):
    
    if not checkuser(message):
        app.send_message(message.chat.id, '__You are either not **Authorized** or **Banned**__',reply_to_message_id=message.id)
        return

    try:
        if int(message.reply_to_message.document.file_size) > 200000:
            app.send_message(message.chat.id, '__Thumbline size allowed is < 200 KB__',reply_to_message_id=message.id)
            return

        msg = app.get_messages(message.chat.id, int(message.reply_to_message.id))
        file = app.download_media(msg)
        os.rename(file,f'{message.from_user.id}-thumb.jpg')
        app.send_message(message.chat.id, '__Thumbnail is Set__',reply_to_message_id=message.id)

    except:
        app.send_message(message.chat.id, '__reply /thumb to a image document of size less than 200KB__',reply_to_message_id=message.id)


# show thumb command
@app.on_message(filters.command(["show"]))
def showthumb(client: pyrogram.client.Client, message: pyrogram.types.messages_and_media.message.Message):
    
    if not checkuser(message):
        app.send_message(message.chat.id, '__You are either not **Authorized** or **Banned**__',reply_to_message_id=message.id)
        return
    
    if os.path.exists(f'{message.from_user.id}-thumb.jpg'):
        app.send_photo(message.chat.id,photo=f'{message.from_user.id}-thumb.jpg',reply_to_message_id=message.id)
    else:
        app.send_message(message.chat.id, '__Thumbnail is not Set__',reply_to_message_id=message.id)


# remove thumbline command
@app.on_message(filters.command(["remove"]))
def removethumb(client: pyrogram.client.Client, message: pyrogram.types.messages_and_media.message.Message):
    
    if not checkuser(message):
        app.send_message(message.chat.id, '__You are either not **Authorized** or **Banned**__',reply_to_message_id=message.id)
        return
    
    if os.path.exists(f'{message.from_user.id}-thumb.jpg'):
        os.remove(f'{message.from_user.id}-thumb.jpg')
        app.send_message(message.chat.id, '__Thumbnail is Removed__',reply_to_message_id=message.id)
    else:
        app.send_message(message.chat.id, '__Thumbnail is not Set__',reply_to_message_id=message.id)


# thumbline
@app.on_message(filters.photo)
def ptumb(client: pyrogram.client.Client, message: pyrogram.types.messages_and_media.message.Message):
    
    if not checkuser(message):
        app.send_message(message.chat.id, '__You are either not **Authorized** or **Banned**__',reply_to_message_id=message.id)
        return
    
    file = app.download_media(message)
    os.rename(file,f'{message.from_user.id}-thumb.jpg')

    id = getlock(message.from_user.id)
    if id: handlethumb(message,id)
    else: app.send_message(message.chat.id, '__Thumbnail is Set__',reply_to_message_id=message.id)
    

# change mode
@app.on_message(filters.command(["change"]))
def change(client: pyrogram.client.Client, message: pyrogram.types.messages_and_media.message.Message):
    
    if not checkuser(message):
        app.send_message(message.chat.id, '__You are either not **Authorized** or **Banned**__',reply_to_message_id=message.id)
        return
    
    info = getdata(str(message.from_user.id))
    swap(str(message.from_user.id))
    if info == "V":
        app.send_message(message.chat.id, '__Mode changed from **Video** format to **Document** format__',reply_to_message_id=message.id)
    else:
        app.send_message(message.chat.id, '__Mode changed from **Document** format to **Video** format__',reply_to_message_id=message.id)
    

# mdisk link in text
@app.on_message(filters.text)
def mdisktext(client: pyrogram.client.Client, message: pyrogram.types.messages_and_media.message.Message):
    
    if isPremmium and message.chat.id == temp_channel: return

    if not checkuser(message):
        app.send_message(message.chat.id, '__You are either not **Authorized** or **Banned**__',reply_to_message_id=message.id)
        return

    if not ismemberpresent(message.from_user.id):
        app.send_message(message.chat.id, '__You are not a member of our Chat\nJoin and Retry__',reply_to_message_id=message.id,
        reply_markup=InlineKeyboardMarkup([[ InlineKeyboardButton("Join", url=LINK)]]))
        return

    if message.text[0] == "/":
        app.send_message(message.chat.id, '__see /help__',reply_to_message_id=message.id)
        return

    id = getlock(message.from_user.id)
    if id:
        handlereanme(message,id)
        return

    if "https://mdisk.me/" in message.text:
        links = message.text.split("\n")
        handlereq(message,links[0])
    else:
        app.send_message(message.chat.id, '__Send only MDisk Link__',reply_to_message_id=message.id)


# polling
app.run()
