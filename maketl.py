import get_frames,os,subprocess,sys
from datetime import date, timedelta
from datetime import datetime
from shutil import copyfile
import logging,json,time
import logging.handlers
from pathlib import Path
from PIL import Image
import os.path


"""
        @Author: Tyler Conlon
        @Date: 11-6-2019
        @Links: https://github.com/smokedsalmonbagel/zoneminder-timelapse
"""

'''
usage:
python3 /full/path/to/maketl.py
'''
#set the camera ids you want to compile timelapses for
cams = ["2","3","4","5","6","7","8"]
#cams = ["7"]
#width in pixels of jpeg preview files
preview_size = 320
#location to put finished timelapse media
tl_destination = '/external/zoneminder/tl'
#path to timelapse log file
log_path = '/var/log/timelapse'

pathname = os.path.dirname(sys.argv[0])
mdt = round(os.path.getmtime(os.path.abspath(pathname)))

Path(log_path).mkdir(parents=True, exist_ok=True)

#logfile name:
log_file_name = os.path.join(log_path,'tl.log')
logging_level = logging.DEBUG
formatter = logging.Formatter('%(asctime)s, %(name)s, %(levelname)s, %(message)s')
handler = logging.handlers.TimedRotatingFileHandler(log_file_name, when='midnight', backupCount=365)
handler.suffix = "%Y-%m-%d"

handler.setFormatter(formatter)
logger = logging.getLogger('timelapse')
logger.addHandler(handler)
logger.setLevel(logging_level)
logger.info("--------------------------------------------")
logger.info("init. v: " +str(mdt))


tmpvideofile = os.path.join(pathname,"myvideo.mp4")
tmpsourcefile = os.path.join(pathname,"source.txt")
makeindexscript = os.path.join(pathname,"makeindex.php")


logger.info("start info:"+json.dumps(cams)+ ', '+tmpvideofile+', '+tmpsourcefile)

#function to get the web directory for a particular camera
def webdir(cam):
    return os.path.join(tl_destination,'c' + cam)
startm = time.time()
#name of folder in camera folder to store mp4 previews (jpeg thumbnails for  each timelapse) 
previewsdir = 'previews'
dtl = []

'''
if dates are give at the command line, script will make a tl for all cameras on just that/those date(s)  Example:
python3 /full/path/to/maketl.py 2022-06-05 2022-06-06
'''
if len(sys.argv) > 1:
    n=0;
    for arg in sys.argv:
        if n > 0:
            dtl.append(arg)
        n+=1
    logger.info("using cmd line dates "+json.dumps(dtl))
#if not date specified use yesterdays date:
if len(dtl) == 0:
    today = date.today()
    yesterday = today - timedelta(days = 1)
    dts = yesterday.strftime("%Y-%m-%d")
    dtl = [dts]
    logger.info("using yesterdays date "+json.dumps(dtl))
for dts in dtl:#iterate over date list
    logger.info("---- starting job for date "+dts+" ------")
    theday = datetime.strptime(dts, '%Y-%m-%d')
    for cam in cams:
        logger.info("---- cam "+cam+" ------")
        start = time.time()
        date_time = theday.strftime("%y_%m_%d_%H_%M")
        fn = date_time + '.mp4'
        webvideo = os.path.join(webdir(cam) , fn)
        if os.path.isfile(webvideo):
            logger.info(cam+":skipping video creation - already exists: "+webvideo)
        else:
            if os.path.exists(tmpvideofile):
                logger.info(cam+":removing last tmp video")
                os.remove(tmpvideofile)
            if os.path.exists(tmpsourcefile):
                logger.info(cam+":removing last source file")
                os.remove(tmpsourcefile)
            frames,previews = get_frames.get_images_by_date(cam,logger,dts)
            
            if frames is not None and len(frames) >= 0:
                f = None
                try:
                    f = open(tmpsourcefile,'w')
                except Exception as e:
                    logger.error(cam+":source file could not be opened: "+str(e))
                if f is not None:#framefile will be used by ffmpeg
                    for frame in frames:
                        f.write('file '+frame['file']+"\n")
                    f.close()
                start2 = time.time()
                logger.info(cam+":rendering video... ")
                #render the timelapse video from frames:
                cmd = ["ffmpeg","-f","concat","-safe","0","-i",tmpsourcefile,"-c:v","libx264","-vf","fps=28","-preset","slow","-crf","30","-pix_fmt","yuv420p",tmpvideofile]
                logger.info(cam+":"+' '.join(cmd))
                subprocess.call(cmd)
                logger.info(cam+":video render time: "+str(round(time.time()-start2,2)))
                
                date_stamp = theday.strftime("%y_%m_%d")
                Path(webdir(cam)).mkdir(parents=True, exist_ok=True)
                previewpath = os.path.join(webdir(cam),previewsdir,date_stamp)
                Path(previewpath).mkdir(parents=True, exist_ok=True)
                try:
                    copyfile(tmpvideofile, webvideo)#copy the rendered mp4 to the web location
                except Exception as e:
                    logger.error(cam+":could not copy file "+tmpvideofile+" to "+webvideo+' - '+str(e))
                    continue
                
                if previews is not None:
                    #logger.info(cam+":resizing/moving "+str(len(previews))+" previews")
                    for hr,preview in previews.items():
                        logger.info(cam+":preview: "+str(preview))
                        date_time = theday.strftime("%y_%m_%d")
                        fn = date_time + '_'+str(hr).zfill(2)+'_preview.jpg'
                        webpreview = os.path.join(previewpath , fn)
                        try: 
                            copyfile(preview, webpreview)#copy preview images
                        except Exception as e:
                            logger.error(cam+":could not copy file "+preview+" to "+webpreview +' - '+str(e))
                        
                        if os.path.isfile(webpreview):
                            basewidth = preview_size
                            img = Image.open(webpreview)
                            wpercent = (basewidth/float(img.size[0]))
                            hsize = int((float(img.size[1])*float(wpercent)))
                            try:
                                img = img.resize((basewidth,hsize), Image.ANTIALIAS)
                                img.save(webpreview)
                            except Exception as e:
                                logger.error(cam+":could not resize preview file "+webpreview +' - '+str(e))
                        else:
                            logger.error(cam+":preview frame missing: "+webpreview)
                            
                
            else:
                print("No frames")
                logger.info(cam+":no frames to process ")
            
            logger.info(cam+":total timelapse creation time: "+str(round(time.time()-start2,2)))
logger.info("building index...")
start = time.time()
cmd = ["php",makeindexscript]
subprocess.call(cmd)#call the php script which updates the index file.  The index json file speeds up page load times.  It is located in the root of the tl web dir.
logger.info("index built. time: "+str(round(time.time()-start,2)))
logger.info("run complete. time: "+str(round(time.time()-startm)))