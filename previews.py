from pathlib import Path
from PIL import Image
import os.path
import subprocess,os
from PIL import Image


"""
        @Author: Tyler Conlon
        @Date: 11-6-2019
        @Links: https://github.com/smokedsalmonbagel/zoneminder-timelapse
"""
'''
Creates preview images for timelapse videos if they are missing.

Normally maketl.py pulls event images and uses them as preview images but
if you have archived timelapse videos and no longer have the original event data
you are stuck with no preview images.  This script can be used to regenerate 
preview jpegs from the timelapse mp4 videos. Since we can't be sure what time of 
day a particular frame in a timelapse is from the script tries to pick the 
midpoint of the video for the thumbnail.  This works if timelapses go from midnight to midnight but might need to be adjusted in other cases.   

Run maketl.py again to regenerate the index file once preview.py completes.


'''

vidpath = '/external/zoneminder/tl'
basewidth = 320

for path in Path(vidpath).rglob('*.mp4'):
    vid = str(path.parent)+os.sep+str(path.name)
    
    parts = vid.split('/')
    parts = parts[1:]
    dt = parts[4].split('_')
    #print(parts,dt)
    previewpath = os.sep +parts[0]+os.sep +parts[1]+os.sep +parts[2]+os.sep +parts[3]+os.sep +'previews' +os.sep+ dt[0]+'_'+ dt[1]+'_'+ dt[2]
        #                        external       zoneminder       tl               cx                                      YY          MM           DD
    previewfn =  dt[0]+'_'+ dt[1]+'_'+ dt[2]+'_25_preview.jpg'
    print(vid)
    if os.path.isfile(previewpath+os.sep+previewfn):
        print("\tpreview exists - skipping")
    else:
        cmd = ["ffprobe","-v","error","-show_entries","format=duration","-of","default=noprint_wrappers=1:nokey=1",vid]
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err =  p.communicate()
        dur = float(out.decode("utf-8").strip())
        mid = int(round(dur /2)) 
        
        print("\tlen:"+str(dur))

        Path(previewpath).mkdir(parents=True, exist_ok=True)
        if os.path.exists('thumb.jpg'):
            os.remove('thumb.jpg')
        cmd = ['ffmpeg', '-ss', str(mid), '-i', vid, '-vframes', '1', '-q:v', '2', 'thumb.jpg']
        subprocess.call(cmd)
        if os.path.isfile('thumb.jpg'):
            print("\tcopy/resize "+'thumb.jpg', previewpath+os.sep+previewfn)
            img = Image.open('thumb.jpg')
            wpercent = (basewidth/float(img.size[0]))
            hsize = int((float(img.size[1])*float(wpercent)))
            img = img.resize((basewidth,hsize), Image.ANTIALIAS)
            img.save(previewpath+os.sep+previewfn) 
 