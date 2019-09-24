#!/usr/bin/python

import subprocess
import os
from time import sleep
from time import time

'''
sp56 = 170
startx = 112
starty = 1326
'''
#image end
sp56 = 170
startx = 112
starty = 1326
#touch end
spx = 640
spy = 320
startxP = 460
startyP = 2452

def adbdevices():
	return [dev.split('\t')[0] for dev in subprocess.check_output(['adb', 'devices']).decode('utf-8').splitlines() if dev.endswith('\tdevice')]
	
def touchscreen_devices(serial=None):
	return [dev.splitlines()[0].split()[-1] for dev in adbshell('getevent -il', serial).split('add device ') if dev.find('ABS_MT_POSITION_X') > -1]
	
def genswipe(devicename, swipelist, serial=None):
	devicename = "/dev/input/event2"
	pixellist = [[(swipelist[0][1])*spx+startxP,(swipelist[0][0])*spy+startyP]]*10+[[(x[1])*spx+startxP,(x[0])*spy+startyP] for x in swipelist]
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
	
def exeswipe(swipe):

	cmds = ['#!/bin/sh','echo Running - signature function']
	print(adbdevices())
	serial = adbdevices()[0]
	if not serial:
		exit(0)
	devicename = touchscreen_devices(serial)[0]
	cmds += genswipe(devicename, swipe, serial)

	open('to_push.scr','w').write('\n'.join(cmds))
	subprocess.call("adb push to_push.scr /data/local/tmp/to_push.scr", shell=True)
	subprocess.call("adb shell chmod 0777 /data/local/tmp/to_push.scr", shell=True)
	subprocess.call("adb shell sh /data/local/tmp/to_push.scr", shell=True)
	subprocess.call("echo run", shell=True)
	
def adbshell(command, serial=None): # legacy code I really need to remove dependency on this
	args = ['adb']
	if serial is not None:
		args.append('-s')
		args.append(serial)
	args.append('shell')
	args.append(command)
	return os.linesep.join(subprocess.check_output(args).decode('utf-8').split('\r\n')[0:-1])
