import requests
import json
import os
import subprocess

#setting
currentFile = __file__
realPath = os.path.realpath(currentFile)
dirPath = os.path.dirname(realPath)
dirName = os.path.basename(dirPath)
ytdlp = dirPath + "/binaries/yt-dlp"
aria2c = dirPath + "/binaries/aria2c"
mkvmerge = dirPath + "/binaries/mkvmerge"
ffmpeg = dirPath + "/ffmpeg/ffmpeg"

os.system(f"chmod 777 {ytdlp} {aria2c} {mkvmerge} {ffmpeg} ffmpeg/ffprobe ffmpeg/qt-faststart")

def req(link):
    inp = link #input('Enter the Link: ')
    fxl = inp.split("/")
    cid = fxl[-1]

    URL = f'https://diskuploader.entertainvideo.com/v1/file/cdnurl?param={cid}'

    header = {
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Referer': 'https://mdisk.me/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36'
    }

    print("Requesting to Server")


    #requesting
    resp = requests.get(url=URL, headers=header).json()['source']
    result = subprocess.run([ytdlp, '--no-warning', '-k', '--user-agent','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36', '--allow-unplayable-formats', '-F', resp], capture_output=True, text=True)
    outtext = result.stdout
    #print(outtext)

    #printingrequiredonly
    outtext = outtext.split("-")
    temp = outtext[0]
    temp = temp.split("\n")
    temp =  temp[-2]
    outtext = outtext[-1]
    outtext = f"{temp}\n{outtext}"
    print (outtext)
    return outtext


def mdow(link,v,a,message):

    #setting
    os.system(f"mkdir {message.id}")
    input_video = dirPath + f'/{message.id}/vid.mp4'
    input_audio = dirPath + f'/{message.id}/aud.m4a'

    #input
    inp = link #input('Enter the Link: ')
    fxl = inp.split("/")
    cid = fxl[-1]

    URL = f'https://diskuploader.entertainvideo.com/v1/file/cdnurl?param={cid}'

    header = {
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Referer': 'https://mdisk.me/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36'
    }

    print("Requesting to Server")


    #requesting
    resp = requests.get(url=URL, headers=header).json()['source']

    #choosing
    vid_format = v
    aud_format = a 

    #downloading
    #video
    if not os.path.exists(input_video):
        subprocess.run([ytdlp, '--no-warning', '-k', '-f', vid_format, resp, '-o', input_video, '--user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
                   '--allow-unplayable-formats', '--external-downloader', aria2c, '--external-downloader-args', '-x 16 -s 16 -k 1M'])
    else:
        pass
    
    #audio
    if not os.path.exists(input_audio):
        subprocess.run([ytdlp, '--no-warning', '-k', '-f', aud_format, resp, '-o', input_audio, '--user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
                   '--allow-unplayable-formats', '--external-downloader', aria2c, '--external-downloader-args', '-x 16 -s 16 -k 1M'])
    else:
        pass

    #renaming
    output = requests.get(url=URL, headers=header).json()['filename']
    output = output.replace(".mkv", "").replace(".mp4", "")

   
    #mkvmerge not used
    #mkvmerge_command = [mkvmerge, '--appimage-extract-and-run', '--output', output + '.mkv', '--language', '0:und', '--default-track', '0:yes', '--compression', '0:none', input_video,'--language', '0:en', '--default-track', '0:yes', '--compression', '0:none', input_audio]
    #subprocess.run(mkvmerge_command)
    
    #merge
    cmd = f'{ffmpeg} -i {input_video} -i {input_audio} -c copy "{output}.mkv"'
    subprocess.call(cmd, shell=True)                        
    print('Muxing Done')

    #cleaning
    if os.path.exists(output+'.mkv'):
        print('Cleaning Leftovers...')
        os.remove(input_audio)
        os.remove(input_video)
        print('Done!')
        foutput = f"{output}.mkv"
        os.system(f'rmdir {message.id}')
        return foutput

    else:
        print("Trying with Changes")
        ffoutput = f" {output}.mkv"
        
        #mkvmerge not used
        #mkvmerge_command = f'{mkvmerge} --appimage-extract-and-run --output "{ffoutput}" --language 0:und --default-track 0:yes --compression 0:none {input_video} --language 0:en --default-track 0:yes --compression 0:none {input_audio}'
        #os.system(mkvmerge_command)
        
        cmd = f'{ffmpeg} -i {input_video} -i {input_audio} -c copy "{ffoutput}"'
        subprocess.call(cmd, shell=True)
        print('Muxing Done')
        
        if os.path.exists(output+'.mkv'):
            print('Cleaning Leftovers...')
            os.remove(input_audio)
            os.remove(input_video)
            print('Done!')
            os.system(f'rmdir {message.id}')
            return ffoutput
        
