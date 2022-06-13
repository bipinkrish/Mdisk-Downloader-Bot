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

os.system(f"mkdir Downloads")
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
    os.mkdir(dirPath + f'/Downloads/{message.id}')
    os.system(f'mkdir {dirPath}/Downloads/{message.id}')
    input_video = dirPath + f'/Downloads/{message.id}/vid.mp4'
    input_audio = dirPath + f'/Downloads/{message.id}/aud.m4a'

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
    #result = subprocess.run([ytdlp, '--no-warning', '-k', '--user-agent','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36', '--allow-unplayable-formats', '-F', resp], capture_output=True, text=True)
    #outtext = result.stdout
    #print(outtext)

    #printingrequiredonly
    #outtext = outtext.split("-")
    #temp = outtext[0]
    #temp = temp.split("\n")
    #temp =  temp[-2]
    #outtext = outtext[-1]
    #outtext = temp + outtext
    #print (outtext)


    #choosing
    vid_format = v #input('Enter Video Format ID: ')
    aud_format = a #input('Enter Audio Format ID: ')


    #downloading
    #video
    if not os.path.exists(input_video):
        subprocess.run([ytdlp, '--no-warning', '-k', '-f', vid_format, resp, '-o', f'/Downloads/{message.id}/vid.mp4', '--user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36','--allow-unplayable-formats', '--external-downloader', aria2c, '--external-downloader-args', '-x 16 -s 16 -k 1M'])
    else:
        pass

    #audio
    if not os.path.exists(input_audio):
        subprocess.run([ytdlp, '--no-warning', '-k', '-f', aud_format, resp, '-o', f'/Downloads/{message.id}/aud.m4a', '--user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36','--allow-unplayable-formats', '--external-downloader', aria2c, '--external-downloader-args', '-x 16 -s 16 -k 1M'])
    else:
        pass

    #renaming
    output = requests.get(url=URL, headers=header).json()['filename']
    output = output.replace(".mkv", "").replace(".mp4", "")
    output = f'Downlods/{message.id}/{output}'

    #merge
    #mkvmerge_command = [mkvmerge, '--output', output + '.mkv', '--language', '0:und', '--default-track', '0:yes', '--compression', '0:none', input_video,'--language', '0:en', '--default-track', '0:yes', '--compression', '0:none', input_audio]
    #subprocess.run(mkvmerge_command)

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
        return foutput

    else:
        print("Trying with Changes")
        ffoutput = f" {output}.mkv"
        #mkvmerge_command = f'{mkvmerge} --output "{ffoutput}" --language 0:und --default-track 0:yes --compression 0:none {input_video} --language 0:en --default-track 0:yes --compression 0:none {input_audio}'
        #os.system(mkvmerge_command)
        cmd = f'{ffmpeg} -i {input_video} -i {input_audio} -c copy "{ffoutput}"'
        subprocess.call(cmd, shell=True)
        print('Muxing Done')
        
        if os.path.exists(output+'.mkv'):
            print('Cleaning Leftovers...')
            os.remove(input_audio)
            os.remove(input_video)
            print('Done!')
            return ffoutput
        
