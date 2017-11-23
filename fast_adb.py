
import subprocess
import os
from time import sleep
from time import time

sp56 = 176
startx = 98
starty = 1126

adbpath = 'adb'

cmds = ['#!/bin/sh','echo Running - signature function']

def adbdevices():
	return [dev.split('\t')[0] for dev in subprocess.check_output([adbpath, 'devices']).splitlines() if dev.endswith('\tdevice')]

def touchscreen_devices(serial=None):
	return [dev.splitlines()[0].split()[-1] for dev in adbshell('getevent -il', serial, adbpath).split('add device ') if dev.find('ABS_MT_POSITION_X') > -1]

def genswipe(devicename, swipelist, serial=None):
	pixellist = [[x[0]*sp56+startx,x[1]*sp56+starty] for x in swipelist]
	
	retval = []
	retval.append('sendevent ' + devicename + ' 1 330 1')
	
	for entry in pixellist:
		retval.append('sendevent {} 3 53 {}'.format(devicename, str(entry[0])))
		retval.append('sendevent {} 3 54 {}'.format(devicename, str(entry[1])))
		retval.append('sendevent {} 0 0 0'.format(devicename))
		
	retval.append('sendevent {} 3 57 -1'.format(devicename))
	retval.append('sendevent {} 1 330 0'.format(devicename))
	retval.append('sendevent {} 0 0 0'.format(devicename))
	return retval

############################## legacy code I really need to remove dependency on this
def adbshell(command, serial=None, adbpath='adb'):
	args = [adbpath]
	if serial is not None:
		args.append('-s')
		args.append(serial)
	args.append('shell')
	args.append(command)
	return os.linesep.join(subprocess.check_output(args).split('\r\n')[0:-1])
##############################

serial = adbdevices()[0]
if not serial:
	exit(0)
devicename = touchscreen_devices(serial)[0]
cmds += genswipe(devicename, [[0,0],[1,0],[2,0],[3,0],[4,0],[4,1],[3,1],[2,1],[1,1],[0,1],[0,0],[1,0],[2,0],[3,0],[4,0],[4,1],[3,1],[2,1],[1,1],[0,1],[0,0],[1,0],[2,0],[3,0],[4,0],[4,1],[3,1],[2,1],[1,1],[0,1],[0,0],[1,0],[2,0],[3,0],[4,0],[4,1],[3,1],[2,1],[1,1],[0,1],[0,0],[1,0],[2,0],[3,0],[4,0],[4,1],[3,1],[2,1],[1,1],[0,1],[0,0],[1,0],[2,0],[3,0],[4,0],[4,1],[3,1],[2,1],[1,1],[0,1],[0,0],[1,0],[2,0],[3,0],[4,0],[4,1],[3,1],[2,1],[1,1],[0,1],[0,0],[1,0],[2,0],[3,0],[4,0],[4,1],[3,1],[2,1],[1,1],[0,1],[0,0],[1,0],[2,0],[3,0],[4,0],[4,1],[3,1],[2,1],[1,1],[0,1]], serial)
#print '\n'.join(cmds)
open('to_push.scr','w').write('\n'.join(cmds))
subprocess.call("adb push to_push.scr /data/local/tmp/to_push.scr", shell=True)
subprocess.call("adb shell chmod 0777 /data/local/tmp/to_push.scr", shell=True)
subprocess.call("adb shell sh /data/local/tmp/to_push.scr", shell=True)
subprocess.call("echo run", shell=True)



#ud -> 1214 & 1215. 1390 & 1391 spacing = 176, half spacing  = 88
#lr -> 185 & 186
#start = 98,1126, spacing = 176