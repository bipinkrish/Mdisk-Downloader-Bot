import ttbotapi
import os
import threading
import mdisk
import split
from split import TG_SPLIT_SIZE
import upload
import extras

# bot
TOKEN = os.environ.get("TOKEN", "") 
app = ttbotapi.Bot(access_token=TOKEN)


# start command
@app.update_handler(chat_type='dialog', bot_command=['/start'])
def send_welcome(message):
    app.send_message(text='**Send link like this >> _/mdisk link_**', user_id=message.message.sender.user_id, formatter="markdown", chat_id=None,link={'type': 'reply', 'mid': message.message.body.mid})


# help command
@app.update_handler(chat_type='dialog', bot_command=['/help'])
def send_help(message):
    helpmessage = """_**/start** - basic usage
**/help** - this message
**/mdisk mdisklink** - usage
**/change** - change upload mode ( default mode is Document )_"""
    app.send_message(text=helpmessage, user_id=message.message.sender.user_id, formatter="markdown", chat_id=None,link={'type': 'reply', 'mid': message.message.body.mid})


# download and upload
def down(message,link):

    # checking link and download with progress thread
    msg = app.send_message(text='_Downloading_', user_id=message.message.sender.user_id, formatter="markdown", chat_id=None,link={'type': 'reply', 'mid': message.message.body.mid})
    size = mdisk.getsize(link)
    if size == 0:
        app.send_message(text="_Invalid Link_", user_id=message.message.sender.user_id, formatter="markdown", chat_id=None,link={'type': 'reply', 'mid': message.message.body.mid})  
        return

    # checking link and download and merge
    file,check,filename = mdisk.mdow(link,message)
    if file == None:
        app.send_message(text="_Invalid Link_", user_id=message.message.sender.user_id, formatter="markdown", chat_id=None,link={'type': 'reply', 'mid': message.message.body.mid})  
        return

    # checking size
    size = split.get_path_size(file)
    if(size > TG_SPLIT_SIZE):
        app.send_message(text="_Splitting_", user_id=message.message.sender.user_id, formatter="markdown", chat_id=None,link={'type': 'reply', 'mid': message.message.body.mid})  
        flist = split.split_file(file,size,file,".", TG_SPLIT_SIZE)
        os.remove(file) 
    else:
        flist = [file]
    app.send_message(text="_Uploading_", user_id=message.message.sender.user_id, formatter="markdown", chat_id=None,link={'type': 'reply', 'mid': message.message.body.mid})  
    i = 1

    # uploading
    for ele in flist:

        # checking file existence
        if not os.path.exists(ele):
            app.send_message(text='_Error in Merging File_"', user_id=message.message.sender.user_id, formatter="markdown", chat_id=None,link={'type': 'reply', 'mid': message.message.body.mid})
            return
            
        # check if it's multi part
        if len(flist) == 1:
            partt = ""
        else:
            partt = f"_part {i}_\n"
            i = i + 1

        info = extras.getdata(str(message.message.sender.user_id))
        if info == 'V':
            type = "video"
        else:
            type = "file"

        # actual uplaod    
        upload.uploadfile(message,TOKEN,ele,type,message.message.sender.user_id,f"{partt}{filename}")

        # deleting uploaded file
        os.remove(ele)
        
    # checking if restriction is removed    
    if check == 0:
        rmmsg = "Can't remove the **restriction**, you have to use **MX player** to play this **video**\n\nThis happens because either the_ **file** length is **too small** or **video** doesn't have separate **audio layer**"
        app.send_message(text=rmmsg, user_id=message.message.sender.user_id, formatter="markdown", chat_id=None,link={'type': 'reply', 'mid': message.message.body.mid})


# change mode
@app.update_handler(chat_type='dialog', bot_command=['/change'])
def change(message):
    info = extras.getdata(str(message.message.sender.user_id))
    extras.swap(str(message.message.sender.user_id))
    if info == "V":
        app.send_message(text="**Mode** changed from **Video** format to **Document** format", user_id=message.message.sender.user_id, formatter="markdown", chat_id=None,link={'type': 'reply', 'mid': message.message.body.mid})
    else:
        app.send_message(text='**Mode** changed from **Document** format to **Video** format', user_id=message.message.sender.user_id, formatter="markdown", chat_id=None,link={'type': 'reply', 'mid': message.message.body.mid})


# mdisk command
@app.update_handler(func=lambda update: update.message.body.text)
def mdiskdown(message):
    try:
        link = message.message.body.text
        if "/mdisk " in link:
            link = link.split("/mdisk ")[1]
        if "https://mdisk.me" in link:
            d = threading.Thread(target=lambda:down(message,link),daemon=True)
            d.start()
            return 
    except:
        pass

    sndmsg = '_Send only MDisk Link with command followed by the link_'
    app.send_message(text=sndmsg, user_id=message.message.sender.user_id, formatter="markdown", chat_id=None,link={'type': 'reply', 'mid': message.message.body.mid})


# infinty polling
app.polling()
