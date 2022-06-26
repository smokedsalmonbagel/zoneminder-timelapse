import sys,os,time,datetime
from pathlib import Path
from datetime import date, timedelta

"""
        @Author: Tyler Conlon
        @Date: 11-6-2019
        @Links: https://github.com/smokedsalmonbagel/zoneminder-timelapse
"""

#path to where zoneminder stores events.  This dir should contain directories with camera numbers 1,2,3 etc
event_path = '/external'

'''
function gets images from zoneminder events.  returns list of image data which will be used in the timelapse  
Generally the assumption is these are for cameras in record mode
but you could also you modect mode cameras, of course the timelapse would jump around within the motion events only

example args:
cam = 2
logger = name of logger object instance 
dts = datetime string if you want to specify a certain day to do timelapse (assumption is 24 hour timelapses)
interval = number of seconds between timelapse frames
'''

def get_images_by_date(cam,logger,dts=None,interval = 60):
    if dts is None:
        today = date.today()
        yesterday = today - timedelta(days = 1)
        dts = yesterday.strftime("%Y-%m-%d")
    
    
    imgpath = os.path.join(event_path , cam, dts)
    
    logger.info(cam+":path = "+imgpath)
    
    if os.path.isdir(imgpath):
        print("Using cam: "+cam+" date: "+dts)
        fl = []#storage of all the files
        n=0
        start = time.time()
        for path in Path(imgpath).rglob('*capture.jpg'):#step through jpegs in event folder
            img = {}
            img['file'] = os.path.join(str(path.parent),str(path.name))
            stat = os.stat(img['file'])
            img['mtime'] = stat.st_mtime
            #img['dts'] = datetime.datetime.utcfromtimestamp(img['mtime']).strftime('%Y-%m-%d %H:%M:%S')
            fl.append(img)
            if n % 10000 == 0:#print the status every so often
                print("\t",n)
            n+=1
  
        fl = sorted(fl, key=lambda k: k['mtime'])#sort by file modified time 
        print("\tTotal files: ",len(fl))
        logger.info(cam+":total files: "+str(len(fl)))
        logger.info(cam+":file search time: "+str(round(time.time()-start,2)))
        frames = [] #storage of frames per the interval

        

        last = 0 #time of last selected frame
        n=0 #file counter
        start = time.time()
        previewmap = {}
        '''
        Here we look at the creation datetime (mtime) of each jpeg which was gathered in the loop above
        
        '''
        for img in fl:
            if n == 0 or (img['mtime'] - last >= interval):
                frames.append(img)
                last = img['mtime']
                hr = datetime.datetime.utcfromtimestamp(img['mtime']).hour
                if hr not in previewmap.keys():#if we dont already have a preview image for this particular hour, store it in previewmap
                    previewmap[hr] = img['file']
            n+=1

        print("\tFiltered frames: ",len(frames))
        logger.info(cam+":total filtered frames: "+str(len(frames)))
        logger.info(cam+":frame filter time: "+str(round(time.time()-start,2)))
        return frames,previewmap
    else:
        print("Path not found "+imgpath)
        logger.error(cam+":Path not found "+imgpath)
        return None,None




