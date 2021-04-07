import logging
from control import *
import time,datetime
from Constants import *

source_defs = [
	(DPP2607_Write_SystemReset,(),"",""),
	(time.sleep,(1,),"",""),
	(DPP2607_Write_VideoSourceSelection,(SourceSel.EXTERNAL_VIDEO_PARALLEL_I_F_,),"",""),
	(DPP2607_Write_VideoPixelFormat,(RGB888_24_BIT,),"",""),
	(DPP2607_Write_VideoResolution,(Resolution.NHD_LANDSCAPE,),"",""),
	(Mplayer,("nhd_test.mp4",),"play video","Does the video play on the screen? (Pass/Fail/Stop)"),
]

Test_name = 'Video Play Test'
#Filepath_n,

# setup the Test name
datalog = DataLog(LogDir, Test_name)

# general setup
logging.getLogger().setLevel(logging.ERROR)
DPP2607_Open()
DPP2607_SetSlaveAddr(SlaveAddr)
DPP2607_SetIODebug(IODebug)

print "Make sure the display port is set. For example export DISPLAY=:0 \n"
time.sleep(4)

try:
    callTable(Test_name,datalog,source_defs);
        
except Exception:
    print "Test failed Exception"
    datalogConstants(datalog)
    datalog.add_col('Test name', Test_name)
    datalog.add_col('End Time',' '+str(datetime.datetime.now()))
    datalog.add_col('Result', "Test Fail EXCEPTION")        
    datalog.add_col('P/F Result', "Fail")
    datalog.log()

finally:
    # cleanup
    DPP2607_Close()
    datalog.close()