import requests
import json
import os


def getuploadurl(TOKEN,type):
    reqUrl = f"https://botapi.tamtam.chat/uploads?type={type}&access_token={TOKEN}"
    headersList = {"Accept": "*/*"}
    payload = ""
    response = requests.request("POST", reqUrl, data=payload,  headers=headersList).json()
    return response["url"]


def curlupload(file,uploadurl):
    tempfile = f'{uploadurl.split("sig=")[1].split("&")[0]}.txt'
    req = f'curl -i -X POST -H "Content-Type: multipart/form-data" -F "data=@{file}" "{uploadurl}" > {tempfile}'
    os.system(req)
    with open(tempfile,"r") as file:
        info = file.readlines()
    os.remove(tempfile)    
    fileid = info[-1].split('"')[-2]
    return fileid


def sendfile(message,TOKEN,chatid,type,caption,fileid):
    reqUrl = f"https://botapi.tamtam.chat/messages?access_token={TOKEN}&user_id={chatid}"

    headersList = {
    "Accept": "*/*",
    "Content-Type": "application/json" 
    }

    payload = json.dumps({
                            "text": caption,
                            "link" : {'type': 'reply', 'mid': message.message.body.mid},
                            "attachments": [
                                {
                                    "type": type,
                                    "payload": { "token": fileid } }]})

    response = requests.request("POST", reqUrl, data=payload,  headers=headersList)
    while response.status_code != 200:
        response = requests.request("POST", reqUrl, data=payload,  headers=headersList)

    return response


def uploadfile(message,TOKEN,file,type,chatid,caption=""):
    uploadurl = getuploadurl(TOKEN,type)
    fileid = curlupload(file,uploadurl)
    resp = sendfile(message,TOKEN,chatid,type,caption,fileid)
    print(resp.text)
    return resp

