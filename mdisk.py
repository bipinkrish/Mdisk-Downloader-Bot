import requests
import json
import os
import subprocess
import threading
import shutil

# setting
currentFile = __file__
realPath = os.path.realpath(currentFile)
dirPath = os.path.dirname(realPath)
dirName = os.path.basename(dirPath)
ytdlp = dirPath + "/binaries/yt-dlp"
aria2c = dirPath + "/binaries/aria2c"
ffmpeg = dirPath + "/ffmpeg/ffmpeg"

# changing permission
os.system(f"chmod 777 {ytdlp} {aria2c} {ffmpeg} ffmpeg/ffprobe ffmpeg/qt-faststart")

# header for request
header = {
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Referer': 'https://mdisk.me/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36'
    	 }

# actual function
def mdow(link,message):

    #setting
    os.mkdir(str(message.id))
    input_video = dirPath + f'/{message.id}/vid.mp4'
    input_audio = dirPath + f'/{message.id}' 

    #input
    inp = link 
    fxl = inp.split("/")
    cid = fxl[-1]

    # resp capturing
    URL = f'https://diskuploader.entertainvideo.com/v1/file/cdnurl?param={cid}'
    resp = requests.get(url=URL, headers=header).json()['source']
    result = subprocess.run([ytdlp, '--no-warning', '-k', '--user-agent','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36', '--allow-unplayable-formats', '-F', resp], capture_output=True, text=True)
    with open(f"{message.id}.txt","w") as temp:
        temp.write(result.stdout)
    os.system(f"sed -i 1,6d {message.id}.txt")

    # getting ids
    with open(f"{message.id}.txt", 'r') as file1:
        Lines = file1.readlines()
    
    os.remove(f"{message.id}.txt")
    audids = []
    audname = []
    i = 1
    vid_format = str(0)

    for line in Lines:
        line = line.strip()
        if "audio" in line:
            audids.append(line[0])
            if "[" in line and "]" in line:
                audname.append(line.split("[")[1].split("]")[0])
                i = i + 1
            else:
                audname.append(f"Track - {i}")
                i = i + 1
        if "video" in line:
            vid_format = line[0]
       
    # threding audio download   
    audi = threading.Thread(target=lambda:downaud(input_audio,audids,resp),daemon=True)
    audi.start()    

    # video download
    subprocess.run([ytdlp, '--no-warning', '-k', '-f', vid_format, resp, '-o', input_video, '--user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
                   '--allow-unplayable-formats', '--external-downloader', aria2c, '--external-downloader-args', '-x 16 -s 16 -k 1M'])
    
    print("Video Downloaded")
    # renaming
    output = requests.get(url=URL, headers=header).json()['filename']
    output = output.replace(".mkv", "").replace(".mp4", "")
    
    # merge
    audi.join()
    cmd = f'{ffmpeg} -i "{input_video}" '

    len = 0
    for ele in audids:
        out_audio = input_audio + f'/aud-{ele}.m4a'
        cmd = cmd + f'-i "{out_audio}" '
        len = len + 1
    
    cmd = cmd + "-map 0 "
    i = 1
    while(i<=len):
        cmd = cmd + f"-map {i} "
        i = i + 1

    i = 1
    for ele in audname:
        cmd = cmd + f'-metadata:s:a:{i} language="{ele}" '

    tcmd = cmd    
    cmd = cmd + f'-c copy "{output}.mkv"'
    print(cmd)
    subprocess.call(cmd, shell=True)                        
    print('Muxing Done')

    # cleaning
    if os.path.exists(output+'.mkv'):
        print('Cleaning Leftovers...')
        shutil.rmtree(str(message.id))
        foutput = f"{output}.mkv"
        return foutput

    else:
        print("Trying with Changes")
        ffoutput = f" {output}.mkv"
        cmd = f'{tcmd} -c copy "{ffoutput}"'
        subprocess.call(cmd, shell=True)
        print('Muxing Done')
        
        if os.path.exists(output+'.mkv'):
            print('Cleaning Leftovers...')
            
            shutil.rmtree(str(message.id))
            return ffoutput
    
# threding audio download      
def downaud(input_audio,audids,resp):
    for ele in audids:
        out_audio = input_audio + f'/aud-{ele}.m4a'
        subprocess.run([ytdlp, '--no-warning', '-k', '-f', ele, resp, '-o', out_audio, '--user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
                   '--allow-unplayable-formats', '--external-downloader', aria2c, '--external-downloader-args', '-x 16 -s 16 -k 1M'])
