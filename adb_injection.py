#!/usr/bin/python

import subprocess
import os
from time import sleep
from time import time

sp56 = 176
startx = 98
starty = 1126

def adbshell(command, serial=None, adbpath='adb'):
	args = [adbpath]
	if serial is not None:
		args.append('-s')
		args.append(serial)
	args.append('shell')
	args.append(command)
	return os.linesep.join(subprocess.check_output(args).split('\r\n')[0:-1])

def adbdevices(adbpath='adb'):
	return [dev.split('\t')[0] for dev in subprocess.check_output([adbpath, 'devices']).splitlines() if dev.endswith('\tdevice')]

def touchscreen_devices(serial=None, adbpath='adb'):
	return [dev.splitlines()[0].split()[-1] for dev in adbshell('getevent -il', serial, adbpath).split('add device ') if dev.find('ABS_MT_POSITION_X') > -1]

def swipe(devicename, swipelist, serial=None, adbpath='adb'):
	pixellist = [[x[0]*sp56+startx,x[1]*sp56+starty] for x in swipelist]
	adbshell('S="sendevent {}";$S 1 330 1;'.format(devicename), serial, adbpath)
	for entry in pixellist:
		adbshell('S="sendevent {}";$S 3 53 {};$S 3 54 {};$S 0 0 0;'.format(devicename, entry[0], entry[1]), serial, adbpath)
	sleep(1)
	adbshell('S="sendevent {}";$S 3 57 -1;$S 1 330 0;$S 0 0 0;'.format(devicename), serial, adbpath)
	
def tap(devicename, x, y, serial=None, adbpath='adb'):
    adbshell('S="sendevent {}";$S 1 330 1;$S 3 53 {};$S 3 54 {};$S 3 48 5;$S 0 0 0;'.format(devicename, x, y), serial, adbpath)
    adbshell('S="sendevent {}";$S 3 57 -1;$S 1 330 0;$S 0 0 0;'.format(devicename), serial, adbpath)


serial = adbdevices()[0]
touchdev = touchscreen_devices(serial)[0]
swipe(touchdev, [[0,0],[1,0],[2,0],[3,0],[4,0],[4,1],[3,1],[2,1],[1,1],[0,1],[0,0],[1,0],[2,0],[3,0],[4,0],[4,1],[3,1],[2,1],[1,1],[0,1],[0,0],[1,0],[2,0],[3,0],[4,0],[4,1],[3,1],[2,1],[1,1],[0,1],[0,0],[1,0],[2,0],[3,0],[4,0],[4,1],[3,1],[2,1],[1,1],[0,1],[0,0],[1,0],[2,0],[3,0],[4,0],[4,1],[3,1],[2,1],[1,1],[0,1],[0,0],[1,0],[2,0],[3,0],[4,0],[4,1],[3,1],[2,1],[1,1],[0,1]], serial)

#ud -> 1214 & 1215. 1390 & 1391 spacing = 176, half spacing  = 88
#lr -> 185 & 186
#start = 98,1126, spacing = 176