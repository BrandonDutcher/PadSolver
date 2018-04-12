#!/usr/bin/python

import subprocess
import os
from time import sleep
from time import time


sp56 = 177
startx = 96
starty = 1124

def adbdevices():
	return [dev.split('\t')[0] for dev in subprocess.check_output(['adb', 'devices']).splitlines() if dev.endswith('\tdevice')]
	
def touchscreen_devices(serial=None):
	return [dev.splitlines()[0].split()[-1] for dev in adbshell('getevent -il', serial).split('add device ') if dev.find('ABS_MT_POSITION_X') > -1]
	
def genswipe(devicename, swipelist, serial=None):
	pixellist = [[x[1]*sp56+startx,x[0]*sp56+starty] for x in swipelist]

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
	return os.linesep.join(subprocess.check_output(args).split('\r\n')[0:-1])