#/bin/idkwhattoputhereshrug

from time import sleep
from time import time
import numpy as np
import subprocess
import itertools
import cv2
import os


sp56 = 177
startx = 96
starty = 1124
boardWidth = 6
boardHeight = 5

orbCount = [0,0,0,0,0,0,0,0,0,0,0]
orbTypeCount = 7 #how many types of orbs are programmed in
dirarray8 = [[0,1],[1,1],[1,0],[1,-1],[0,-1],[-1,-1],[-1,0],[-1,1]]
dirarray4 = [[0,1],[1,0],[0,-1],[-1,0]]
pathList = [[99,99],[99,89],[99,79]] # a list of all the places the picked-up orb has been
matchLocs = [[99,99,99,99,99]] # a list of all the locations of matches in the board
mixedUp = []
swipelist = []

#------------------------------------------------
# sending moves to phone
#------------------------------------------------



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

	
#------------------------------------------------
# getting board	
#------------------------------------------------

def getBoard():
	''' # for canny edge detection and contour mapping
	c_low = 100
	c_high = 180
	fire = cv2.Canny(cv2.imread('assets/fireorb.png',0),c_low,c_high)
	'''

	fire = cv2.imread('assets/fireorb.png',0)[10:-10,10:-10] #try not to include checkered background in image
	water = cv2.imread('assets/waterorb.png',0)[10:-10,10:-10]
	wood = cv2.imread('assets/woodorb.png',0)[10:-10,10:-10]
	light = cv2.imread('assets/lightorb.png',0)[10:-10,10:-10]
	dark = cv2.imread('assets/darkorb.png',0)[10:-10,10:-10]
	heart = cv2.imread('assets/heartorb.png',0)[10:-10,10:-10]
	imarray = [fire,water,wood,light,dark,heart]
	#jammer = 
	#poison = 
	#mortal poison = 
	#imgsize = len(fire) # for color averaging techniques
	''' # for color averaging techniques
	avgcolor = []
	for image in imarray:
		avgcolor.append(np.average(np.average(image,axis=0),axis=0))
	threshold = 0.9
	'''
	
	subprocess.call('adb shell screencap -p /sdcard/screencap.png',shell=True) # take and pull screenshot
	subprocess.call('adb pull /sdcard/screencap.png',shell=True) # stored in same folder as this file
	img = cv2.imread('screencap.png',0)
	#cv2.imshow('image',img)
	#cv2.waitKey(0)
	#cv2.destroyAllWindows()
	
	
	board = np.zeros([boardHeight,boardWidth],dtype = int)
	''' #blind template matching (fails on plusses)
	for cval,template in enumerate(imarray):
		res = cv2.matchTemplate(img,template,cv2.TM_CCOEFF_NORMED)
		loc = np.where(res > threshold)
		scaledloc = [[int((float(loc[0][i])-starty)/sp56+0.5),int((float(loc[1][i])-startx)/sp56+0.5)] for i in xrange(len(loc[0]))] # scales the values returned by 
np.where
		try: scaledloc = np.unique(scaledloc,axis=0) #check for duplicates - duplicates happen when threshold is low
		except: break
		for entry in scaledloc:
			if board[entry[0]][entry[1]] != 0:
				print "Error, orb recognized as multiple colors"
				exit(0)
			board[entry[0]][entry[1]] = cval+1
	'''
	""" #average color calculations (fails on bright fires and bright hearts)
	if 0 in board:    # made to be done after the template matching
		invloc = np.where(board == 0)
		boardloc = [[invloc[0][i],invloc[1][i]] for i in xrange(len(invloc[0]))]
		imgloc = [[invloc[0][i]*sp56+starty-imgsize/2,invloc[1][i]*sp56+startx-imgsize/2] for i in xrange(len(invloc[0]))]
		for i, entry in enumerate(imgloc):
			unkorb = img[entry[0]:entry[0]+imgsize,entry[1]:entry[1]+imgsize]
			cv2.imshow('image',unkorb)
			cv2.waitKey(0)
			cv2.destroyAllWindows()
			unkavg = np.average(np.average(unkorb,axis=0),axis=0)
			compavg = [np.dot(unkavg,x)/np.linalg.norm(unkavg)/np.linalg.norm(x) for x in avgcolor]
			board[boardloc[i][0],boardloc[i][1]] = compavg.index(max(compavg))+1
			print "orb at {} identified as {}".format([boardloc[i][0],boardloc[i][1]],board[boardloc[i][0],boardloc[i][1]])
			print ' '
			''' #smallest vector difference
			unkavg = np.average(np.average(unkorb,axis=0),axis=0)
			compavg = [np.linalg.norm(unkavg-x) for x in avgcolor]
			board[boardloc[i][0],boardloc[i][1]] = compavg.index(min(compavg))+1
			print "orb at {} identified as {}".format([boardloc[i][0],boardloc[i][1]],board[boardloc[i][0],boardloc[i][1]])
			print ' '
			'''
	"""
	''' #contor recognition (this sucks in general, idk probably because it just looks at the first contour, could be better)
	for y in xrange(boardHeight): #roll this back, make one of the images larger, and search for the edges inside the bigger one
		for x in xrange(boardWidth):
			imgy = y*sp56+starty-imgsize/2
			imgx = x*sp56+startx-imgsize/2
			unkorb = img[imgy:imgy+imgsize,imgx:imgx+imgsize]
			unkedge = cv2.Canny(unkorb,c_low,c_high) #contour recognition
			a,unkcontours,hierarchy = cv2.findContours(unkedge,2,1)
			compcontour = []
			for orb in imarray:
				a,orbcontours,hierarchy = cv2.findContours(orb,2,1)
				compcontour.append(cv2.matchShapes(unkcontours[0],orbcontours[0],1,0.0))
			board[y,x] = compcontour.index(min(compcontour))+1
			cv2.imshow('image',unkedge)
			cv2.waitKey(0)
			cv2.destroyAllWindows()
	'''
	for y in xrange(boardHeight): # windowed template matching (works very well)
		for x in xrange(boardWidth):
			imgy = y*sp56+starty-sp56/2
			imgx = x*sp56+startx-sp56/2
			unkorb = img[imgy:imgy+sp56,imgx:imgx+sp56]
			bestmatchlist = [np.amax(cv2.matchTemplate(orb,unkorb,cv2.TM_CCOEFF_NORMED)) for orb in imarray]
			board[y,x] = bestmatchlist.index(max(bestmatchlist))+1
			#print "orb at {} identified as {}".format([y,x],board[y][x])
			#print ' '
			#cv2.imshow('image',unkorb)
			#cv2.waitKey(0)
			#cv2.destroyAllWindows()
			
	for y in range(boardHeight):	
		for x in range(boardWidth):
			orbCount[board[y,x]] += 1
	print board
	return board

#------------------------------------------------
# solving board and generating moves
#-------------------------------------------------
def mv(y, x): # appends the move made to swipelist
	swipelist.append([y,x])
def tdistance(y1, x1, y2, x2): # calculates the number of moves it would take to transport an orb from one place to another (will probably need a path distance function eventually)
	return (max(abs(y1-y2),abs(x1-x2))*3)+min(abs(y1-y2),abs(x1-x2)) #this is transport distance with nothing in the way
def mdistance(y1,x1,y2,x2):
	return max(abs(y1-y2),abs(x1-x2))
def dearray(p): # splits an array into two values (for use in weird numpy situations with referencing array values)
	return p[0],p[1]
def exists(p): # makes sure that the location is within orb bounds
	if (p[0] < boardHeight and p[1] < boardWidth and p[1] >= 0 and p[0] >= 0):
		return True
	return False
	
def search(starty, startx, goal): #searches for the closest transport-distanced orb that matches the color desired
	global cury, curx, board, lockedBoard
	miny, minx = 50, 50
	shortest = 100
	for y in xrange(0,len(board)):
		for x in xrange(0,len(board[0])):
			if board[y, x] == goal and lockedBoard[y, x] == 0 and [y,x] != [cury,curx]:
				if tdistance(starty, startx, y, x) <= shortest:
					miny, minx = y, x
					shortest = tdistance(starty, startx, y, x)
	if miny == 50 and minx == 50:
		print "Error, no orbs of color", goal, "found"
		print board
		print lockedBoard
		print len(swipelist)
		exit(0)
	return miny, minx
					
def swap(y, x):
	global cury, curx, board, lockedBoard, pathList, mixedUp, swipelist
	if len(swipelist) > 300:
		print 'swipelist longer than 300 entries. Likely entered a loop somewhere, not going to execute'
		exit(0)
	if abs(cury-y > 1) or abs(curx-x > 1):
		print 'Error, moving too far in a swap'
		exit()
	
	if lockedBoard[y,x] == 1:
		lockedBoard[y,x] = 0
		mixedUp.append([y,x,board[y,x]])
	
	mv(y,x)
	pathList.append([y,x])
	
	tempval = board[y,x]
	board[y,x] = board[cury,curx]
	board[cury,curx] = tempval
	cury = y
	curx = x
	
def path(y, x, permission, orby, orbx):
	global cury, curx, board, lockedBoard, dirarray8, pathList
	
	while (y != cury or x != curx) and pathList[-3] != [cury,curx]:
		diry = min(1, max(-1, y-cury))
		dirx = min(1, max(-1, x-curx))
		direction = dirarray8.index([diry,dirx])
		curpos = np.array([cury,curx]) 
		
		if (lockedBoard[cury+diry,curx+dirx] == 0 or permission) and not np.array_equal([orby, orbx], curpos+dirarray8[(direction)]):
			swap(cury+diry, curx+dirx)
		elif exists(curpos+dirarray8[(direction+1)%8]) and not np.array_equal([orby, orbx], curpos+dirarray8[(direction+1)%8]) and (lockedBoard[dearray(curpos+dirarray8[(direction+1)%8])] == 0 or permission):
			# This paths it within the bounds of the board, not through locked orbs, and also not through the orb that is currently being transported (if given 'admin')
			swap(cury+dirarray8[(direction+1)%8][0],curx+dirarray8[(direction+1)%8][1])
		elif exists(curpos+dirarray8[(direction-1)%8]) and not np.array_equal([orby, orbx], curpos+dirarray8[(direction-1)%8]) and (lockedBoard[dearray(curpos+dirarray8[(direction-1)%8])] == 0 or permission):
			swap(cury+dirarray8[(direction-1)%8][0],curx+dirarray8[(direction-1)%8][1])
		elif exists(curpos+dirarray8[(direction+2)%8]) and not np.array_equal([orby, orbx], curpos+dirarray8[(direction+2)%8]) and (lockedBoard[dearray(curpos+dirarray8[(direction+2)%8])] == 0 or permission):
			swap(cury+dirarray8[(direction+2)%8][0],curx+dirarray8[(direction+2)%8][1])
		elif exists(curpos+dirarray8[(direction-2)%8]) and not np.array_equal([orby, orbx], curpos+dirarray8[(direction-2)%8]) and (lockedBoard[dearray(curpos+dirarray8[(direction-2)%8])] == 0 or permission):
			swap(cury+dirarray8[(direction-2)%8][0],curx+dirarray8[(direction-2)%8][1])
		else: 
			print "pathing failed"
			return False
	if pathList[-3] == [cury,curx]:
		return False
	return True

def transportOrb(orby, orbx, targety, targetx, permission, endState):
	global cury, curx, board, lockedBoard, dirarray8, pathList, mixedUp
	success = True
	
	
	while(orby != targety or orbx != targetx) and pathList[-3] != [cury,curx]:
		diry = min(1, max(-1, targety-orby))
		dirx = min(1, max(-1, targetx-orbx))
		direction = dirarray8.index([diry,dirx])
		orbpos = np.array([orby,orbx]) 
		if lockedBoard[orby+diry,orbx+dirx] == 0 or permission:
			success = path(orby+diry, orbx+dirx, permission, orby, orbx)
		elif exists(orbpos+dirarray8[(direction+1)%8]) and (lockedBoard[dearray(orbpos+dirarray8[(direction+1)%8])] == 0 or permission):
				# if the direction doesn't take you offboard and is not locked ( permission ignores that part )
			success = path(orby+dirarray8[(direction+1)%8][0], orbx+dirarray8[(direction+1)%8][1], permission, orby, orbx)
		elif exists(orbpos+dirarray8[(direction-1)%8]) and (lockedBoard[dearray(orbpos+dirarray8[(direction-1)%8])] == 0 or permission):
			success = path(orby+dirarray8[(direction-1)%8][0], orbx+dirarray8[(direction-1)%8][1], permission, orby, orbx)
		elif exists(orbpos+dirarray8[(direction+2)%8]) and (lockedBoard[dearray(orbpos+dirarray8[(direction+2)%8])] == 0 or permission):
			success = path(orby+dirarray8[(direction+2)%8][0], orbx+dirarray8[(direction+2)%8][1], permission, orby, orbx)
		elif exists(orbpos+dirarray8[(direction-2)%8]) and (lockedBoard[dearray(orbpos+dirarray8[(direction-2)%8])] == 0 or permission):
			success = path(orby+dirarray8[(direction-2)%8][0], orbx+dirarray8[(direction-2)%8][1], permission, orby, orbx)
		else: 
			success = False
		if success:
			tempy = cury
			tempx = curx
			swap(orby,orbx)
			orby = tempy
			orbx = tempx
		else:
			if permission:
				print "Transport REALLY failed this time"
				print board
				print ' '
				print lockedBoard
				print ' '
				print mixedUp
				exit()
			print 'sliding in', board[orby,orbx]
			pathList = [[99,99],[99,89],[99,79]]
			transportOrb(orby, orbx, targety, targetx, True, endState) 	#gives access to push orb through locked orbs
			lockedBoard[targety, targetx] = 1
			for entry in mixedUp[::-1]:							#repairs earlier orbs
				#print 'repairing at', entry[0], entry[1], 'with color', entry[2]
				#print mixedUp
				#print '--------'
				#print board
				#print ' '
				#print lockedBoard
				#print '--------'
				displacedy, displacedx = search(entry[0],entry[1],entry[2])
				transportOrb(displacedy, displacedx, entry[0], entry[1], False, endState)
			mixedUp = []
			return
			
	lockedBoard[targety, targetx] = endState

def transportStep(orby, orbx, targety, targetx, permission, endState):
	global cury, curx, board, lockedBoard, dirarray8, pathList, mixedUp
	success = True
	if orbx == targetx and orby == targety:
		lockedBoard[orby, orbx] = 1
		return
	
	diry = min(1, max(-1, targety-orby))
	dirx = min(1, max(-1, targetx-orbx))
	direction = dirarray8.index([diry,dirx])
	orbpos = np.array([orby,orbx]) 
	if lockedBoard[orby+diry,orbx+dirx] == 0 or permission:
		success = path(orby+diry, orbx+dirx, permission, orby, orbx)
	elif exists(orbpos+dirarray8[(direction+1)%8]) and (lockedBoard[dearray(orbpos+dirarray8[(direction+1)%8])] == 0 or permission):
			# if the direction doesn't take you offboard and is not locked ( permission ignores that part )
		success = path(orby+dirarray8[(direction+1)%8][0], orbx+dirarray8[(direction+1)%8][1], permission, orby, orbx)
	elif exists(orbpos+dirarray8[(direction-1)%8]) and (lockedBoard[dearray(orbpos+dirarray8[(direction-1)%8])] == 0 or permission):
		success = path(orby+dirarray8[(direction-1)%8][0], orbx+dirarray8[(direction-1)%8][1], permission, orby, orbx)
	elif exists(orbpos+dirarray8[(direction+2)%8]) and (lockedBoard[dearray(orbpos+dirarray8[(direction+2)%8])] == 0 or permission):
		success = path(orby+dirarray8[(direction+2)%8][0], orbx+dirarray8[(direction+2)%8][1], permission, orby, orbx)
	elif exists(orbpos+dirarray8[(direction-2)%8]) and (lockedBoard[dearray(orbpos+dirarray8[(direction-2)%8])] == 0 or permission):
		success = path(orby+dirarray8[(direction-2)%8][0], orbx+dirarray8[(direction-2)%8][1], permission, orby, orbx)
	else: 
		success = False
	if success:
		tempy = cury
		tempx = curx
		swap(orby,orbx)
		orby = tempy
		orbx = tempx
		lockedBoard[orby, orbx] = endState
		return
	else:
		if permission:
			print "Transport REALLY failed this time"
			print board
			print ' '
			print lockedBoard
			print ' '
			print mixedUp
			exit()
		print 'sliding in', board[orby,orbx]
		pathList = [[99,99],[99,89],[99,79]]
		transportOrb(orby, orbx, targety, targetx, True, endState) 	#gives access to push orb through locked orbs
		lockedBoard[targety, targetx] = 1
		for entry in mixedUp[::-1]:							#repairs earlier orbs
			#print 'repairing at', entry[0], entry[1], 'with color', entry[2]
			#print mixedUp
			#print '--------'
			#print board
			#print ' '
			#print lockedBoard
			#print '--------'
			displacedy, displacedx = search(entry[0],entry[1],entry[2])
			transportOrb(displacedy, displacedx, entry[0], entry[1], False, endState)
		mixedUp = []
		return

def getColorAdjLocked(y,x): #checks nearby immovable orbs for the colors they have
	global board, lockedBoard
	list = []
	if exists([y, x-1]) and lockedBoard[y, x-1] == 1:
		list.append(board[y,x-1])
	if exists([y, x+1]) and lockedBoard[y, x+1] == 1:
		list.append(board[y,x+1])
	if exists([y-1, x]) and lockedBoard[y-1, x] == 1:
		list.append(board[y-1,x])
	if exists([y+1, x]) and lockedBoard[y+1, x] == 1:
		list.append(board[y+1,x])
	return list
	
def getUnpreferred(starty, startx, dir, leng): # checks an entire combo area for surrounding immovable orbs' colors, so as to avoid those and prevent match crossing
	unpreferredOrbs = []
	for i in xrange(leng):
		list = getColorAdjLocked(starty+dir[0]*i, startx+dir[1]*i)
		for entry in list:
			if entry not in unpreferredOrbs:
				unpreferredOrbs.append(entry)
	return unpreferredOrbs
	
def findMatch(starty, startx, dir, leng, undesired):
	global board, lockedBoard, orbCount, carriedColor, allMatches
	# check to see if there are locked orbs in the way
	for i in xrange(leng):
		if not exists([starty+dir[0]*i,startx+dir[1]*i]):
			print "can't make a match here because OoB"
			print "with values", starty, startx, dir, leng
			return False
			
		if lockedBoard[starty+dir[0]*i, startx+dir[1]*i] == 1:
			print "can't make a match here because of locks"
			print "with values", starty, startx, dir, leng
			return False
	
	# check what colors would not create a new combo
	
	unpreferredOrbs = getUnpreferred(starty, startx, dir, leng)
	#print ' '
	#print unpreferredOrbs
	preferredOrbs = [x for x in xrange(1,len(orbCount)) if x not in unpreferredOrbs]
	
	# check if match is already made
	color = board[starty,startx]
	if color not in unpreferredOrbs:
		perfect = True
		for i in xrange(1,leng):
			if board[starty+dir[0]*i,startx+dir[1]*i] != color:
				perfect = False
				
		if perfect:
			print 'match already made'
			return color
	
	# find optimal color to match here
	allowedIndex = np.where(np.array([allMatches[x][1] for x in xrange(len(allMatches))]) == leng)
	print [allMatches[x][1] for x in xrange(len(allMatches))]
	print allowedIndex[0]
	colorDistanceList = np.zeros(10, dtype=np.int)
	if len(allowedIndex[0]) == 0:
		print 'no matches of size', leng, 'found'
		return False
		
	for index in allowedIndex[0]:
		color = allMatches[index][0]
		print allMatches[index]
		if color not in unpreferredOrbs:
			for i in xrange(leng):
				absy, absx = search(starty, startx, color)
				lockedBoard[absy,absx] = 2
				colorDistanceList[color] += tdistance(starty+dir[0]*i, startx+dir[1]*i, absy, absx)		
				
	oldColorDistanceList = [x for x in colorDistanceList]
	newColorDistanceList = [x for x in colorDistanceList if x != 0]
	print oldColorDistanceList
	
	# reset lockedBoard
	twos = np.where(lockedBoard == 2)
	for i in xrange(len(twos[0])):
		lockedBoard[ twos[0][i], twos[1][i] ] = 0
	
	# make sure there are orbs to match
	if not newColorDistanceList:
		print "No more Orb matches"
		return False
	
	color = oldColorDistanceList.index(min(newColorDistanceList))
	print 'matching', color
	return color
	
def getStepPriority(y,x):
	global lockedBoard, dirarray8, dirarray4
	if lockedBoard[y,x] == 1: return 0
	loc = np.array([y,x])
	prio8 = 0
	for dir in dirarray8:
		if exists(loc+dir) and lockedBoard[dearray(loc+dir)] == 0:
			prio8 += 1
	prio4 = 0
	for dir in dirarray4:
		if exists(loc+dir) and lockedBoard[dearray(loc+dir)] == 0:
			prio4 += 1
	#print y,x,prio4,prio8
	if prio8 >= 7: return 0
	elif prio8 == 6: return 0.5
	elif prio8 >= 4 and prio8 <= 5: return 1
	elif prio8 == 3 and prio4 >= 2: return 1
	elif prio8 == 3 and prio4 <= 1: return 5
	elif prio8 == 2: return 10
	elif prio8 == 1: return 50
	elif prio8 == 0:
		print "Orb captured!, you're really good at playing Go"
		print "y =", y, "x =", x
		print board
		print coloredBoard
		print lockedBoard
		return 1000
	else:
		print "idk screwed up in getStepPriority though"
		exit(0)
		
def getCost(locy,locx,priority):
	global board, cury, curx
	orby, orbx = search(locy,locx,coloredBoard[locy,locx])
	if locy == orby and locx == orbx:
		return 0
	return float(mdistance(cury, curx, orby + min(1, max(-1, locy-orby)), orbx + min(1, max(-1, locx-orbx)))+1)/priority
	
def step():
	global board, lockedBoard, coloredBoard, cury, curx
	costBoard = np.zeros_like(board, dtype=float)+100
	priorityBoard = np.zeros_like(board)
	
	for y in xrange(boardHeight):
		for x in xrange(boardWidth):
			priorityBoard[y,x] = getStepPriority(y,x)
			if priorityBoard[y,x] != 0 and coloredBoard[y,x] != board[cury,curx]:
				costBoard[y,x] = getCost(y, x, priorityBoard[y,x])
	
	loc = np.where(costBoard == np.amin(costBoard))
	#print loc
	locy = loc[0][0]
	locx = loc[1][0]
	print board
	print lockedBoard
	print coloredBoard
	print priorityBoard
	print costBoard
	orby, orbx = search(locy,locx, coloredBoard[locy,locx])
	print "moving",orby,orbx,"towards",locy,locx
	
	if mdistance(locy,locx,orby,orbx) <= 1:
		endState = 1
	else:
		endState = 0
		
	transportStep(orby, orbx, locy, locx, False, endState)
	
def makeMatch(starty, startx, dir, leng):
	global board, lockedBoard, orbCount, allMatches
	
	goalcolor = findMatch(starty, startx, dir, leng, [])
	if not goalcolor:
		return False
	print 'matching:', goalcolor
	print '----'
	print board
	print ' ' 
	print lockedBoard
	print '----'
	for i in range(leng):
		orby, orbx = search(starty+dir[0]*i,startx+dir[1]*i,goalcolor)
		transportOrb(orby,orbx,starty+dir[0]*i,startx+dir[1]*i, False,1)
	orbCount[goalcolor] -= leng
	if matchLocs[-1] != [starty, startx, dir, leng, goalcolor]:
		matchLocs.append([starty, startx, dir, leng, goalcolor])
	allMatches.remove([goalcolor,leng])
	return True

def selectStartOrb(): # tries to select an orb that won't be matched in the end
	global allMatches, trashOrbs
	mincolor = 0
	mindist = 99
	if trashOrbs:
		for entry in trashOrbs:
			y, x = search(0,0,entry[0])
			curdist = mdistance(0,0,y,x)
			if curdist < mindist:
				mincolor = entry[0]
				mindist = curdist
		return search(0,0,mincolor)
	else:
		for entry in allMatches:
			if entry[1] == 3:
				y, x = search(0,0,entry[0])
				curdist = mdistance(0,0,y,x)
				if curdist < mindist:
					mincolor = entry[0]
					mindist = curdist
		allMatches.remove([mincolor, 3])
		return search(0,0,mincolor)
	error #no matches of 3 found
	return 1,0
	
def getMatches(): # looks at the board and groups the orbs into their best potential combos
	global orbCount
	allMatches = []
	trashOrbs = []
	if len([x for x in orbCount if x != 0]):
		pass #do something for boards of fewer colors
	for color in xrange(len(orbCount)):
		while orbCount[color] != 0:
			quantity = orbCount[color]
			if quantity >= 3:
				allMatches.append([color,3+quantity%3])
				orbCount[color] -= 3+quantity%3
			elif quantity > 0:
				trashOrbs.append([color,1])
				orbCount[color] -= 1
	return allMatches + trashOrbs

def getClosestZero(starty, startx):
	global lockedBoard
	miny = 99
	minx = 99
	mindist = 99
	for y in xrange(len(lockedBoard)):
		for x in xrange(len(lockedBoard[0])):
			if lockedBoard[y, x] == 0:
				if mdistance(starty, startx, y, x) <= mindist:
					mindist = mdistance(starty, startx, y, x)
					miny, minx = y, x
	print 'closest zero to', starty, startx, 'at', miny, minx
	print lockedBoard
	return miny, minx

def getSnugness(y, x, size):
	coord = np.array([y,x])
	maximum = [0,0,0,0]
	if lockedBoard[y,x] != 0:
		return 0, [0,0]
	for i, dir in enumerate(dirarray4):
		for j in xrange(size):
			ndir = np.multiply(dir,j)
			if exists(coord+ndir) and lockedBoard[dearray(coord+ndir)] == 0:
				for dirsub in dirarray4:
					if not exists(coord+ndir+dirsub) or exists(coord+ndir+dirsub) and lockedBoard[dearray(coord+ndir+dirsub)] != 0:
						maximum[i] += 1
			else: 
				maximum[i] = 0
				break
	print maximum
	return max(maximum), dirarray4[maximum.index(max(maximum))]
	
def arrangeBoard(): # oh god this is hard
	global solvedBoard, arrLocs
	solvedBoard = np.zeros_like(board)
	priorityBoard = np.zeros_like(board)
	
	allMatches = getMatches()
	matchOrdering = [[],[],[],[]]
	for match in allMatches:
		if match[1] == 5: matchOrdering[0].append(match[1])
		elif match[1] == 4: matchOrdering[2].append(match[1])	# need to have the 4 first to match it first but the 1 has to come first in the filling in
		elif match[1] == 1: matchOrdering[1].append(match[1])
		elif match[1] == 3: matchOrdering[3].append(match[1])
		else: print "k, that didn't work here's the matches:", allMatches
	
	matchLengths = []
	for matchSet in matchOrdering: matchLengths += matchSet
	
	arrLocs = []
	mnum = 1
	setToNumber(0,0,[1,0],mnum,matchLengths[0])
	currentrem = matchLengths[0]%3
	mnum += 1
	setToNumber = setToNumber[1:]
	while matchLengths.size:
		pass

def setToNumber(y,x,dir,color,length): # sets on solvedBoard
	global solvedBoard, lockedBoard, arrLocs
	loc = np.array([y,x])
	if color == 0:
		for i in xrange(length):
			solvedBoard[dearray(loc+np.multiply(dir,i))] = 0
			lockedBoard[dearray(loc+np.multiply(dir,i))] = 0
		arrLocs = arrLocs[:-1]
		return False
	
	for i in xrange(length):
		if lockedBoard[dearray(loc+np.multiply(dir,i))] == 1:
			return False
	arrLocs.append([y,x,dir,color,length])
	for i in xrange(length):
		solvedBoard[dearray(loc+np.multiply(dir,i))] = color
		lockedBoard[dearray(loc+np.multiply(dir,i))] = 1
	return True
	
def arrangeBoardBrute():
	global solvedBoard, lockedBoard, arrLocs, allPerm
	solvedBoard = np.zeros_like(board)
	getMatches()
	allLengths = [x[1] for x in allMatches]
	allPerm = np.unique(list(itertools.permutations(allLengths)),axis=0) # this takes rather long, but will probably end up under 10000 after running
	#print allLengths
	arrLocs = []
	for perm in allPerm:#change this back
		#print perm
		if brute(0,0,1,perm):
			break
	print solvedBoard
	
def brute(y,x,mnum,perm):
	global arrLocs
	if not (0 in solvedBoard):
		print 'Board Organized'
		#print solvedBoard
		#print arrLocs
		return True
	if lockedBoard[y,x] == 0:
		if exists([y,x+perm[mnum-1]-1]):
			if setToNumber(y, x, [0,1], mnum, perm[mnum-1]):
				if brute( y+int((x+1)/boardWidth), (x+1)%boardWidth, mnum+1, perm):
					return True
				setToNumber(y, x, [0,1], 0, perm[mnum-1])
				print arrLocs
		
		if exists([y+perm[mnum-1]-1,x]):
			if setToNumber(y, x, [1,0], mnum, perm[mnum-1]):
				if brute( y+int((x+1)/boardWidth), (x+1)%boardWidth, mnum+1, perm):
					return True
				setToNumber(y, x, [1,0], 0, perm[mnum-1])
				print arrLocs
		
	else:
		if brute( y+int((x+1)/boardWidth), (x+1)%boardWidth, mnum, perm):
			return True
	return False
	
def assignColors():
	global coloredBoard, solvedBoard, allMatches
	coloredBoard = np.zeros_like(solvedBoard)
	for l in arrLocs:
		print l
	print allMatches
	maxi = np.amax(solvedBoard)
	for i in xrange(1,maxi+1):
		for match in allMatches:
			if match[1] == arrLocs[i-1][4]:
				coloredBoard[solvedBoard == i] = match[0]
				allMatches.remove(match)
				break
	print "Colors Assigned"
	print coloredBoard
	
def numberBoard():
	global lockedBoard
	lockedBoard = np.zeros_like(lockedBoard)
	i = 10
	for y in xrange(boardHeight):
		for x in xrange(boardWidth):
			orby, orbx = search(y,x,coloredBoard[y,x])
			board[orby,orbx] = i
			coloredBoard[y,x] = i
			i += 1
	print "Board Numbered"
	print board
	print coloredBoard

def solveBoard():
	global board, lockedBoard, curx, cury, trashOrbs, allMatches
	board = getBoard()
	lockedBoard = np.zeros_like(board, dtype=int)
	allMatches = getMatches()
	arrangeBoardBrute()
	assignColors()
	#cury, curx = -1, -1
	#numberBoard()
	cury, curx = 2, 2
	mv(cury,curx)
	pathList.append([cury,curx])
	lockedBoard = np.zeros_like(lockedBoard)
	while( not np.array_equal(board,coloredBoard)):
		step()
	print board
	print lockedBoard
	print coloredBoard
	print len(swipelist)
	exeswipe(swipelist)
	'''
	curx, cury = -1, -1
	curx, cury = selectStartOrb()
	mv(curx,cury)
	pathList.append([curx,cury])
	
	print board
	print lockedBoard
	exeswipe(swipelist)'''

solveBoard()
#do some ending thing if I can

