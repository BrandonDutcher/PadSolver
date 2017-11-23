#/bin/idkwhattoputhereshrug

from time import sleep
from time import time
import numpy as np
import subprocess
import cv2
import os


sp56 = 177
startx = 96
starty = 1124
boardWidth = 6
boardHeight = 5

orbCount = [0,0,0,0,0,0,0,0,0,0,0]
orbTypeCount = 7 #how many types of orbs are programmed in
dirarray8 = [[1,0],[1,1],[0,1],[-1,1],[-1,0],[-1,-1],[0,-1],[1,-1]]
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

	return board

#------------------------------------------------
# solving board and generating moves
#-------------------------------------------------
def mv(x, y): # appends the move made to swipelist
	swipelist.append([x,y])
def tdistance(x1, y1, x2, y2): # calculates the number of moves it would take to transport an orb from one place to another (will probably need a path distance function eventually)
	return (max(abs(x1-x2),abs(y1-y2))*3)+min(abs(x1-x2),abs(y1-y2)) #this is transport distance with nothing in the way
def mdistance(x1,y1,x2,y2):
	return max(abs(x1-x2),abs(y1-y2))
def dearray(p): # splits an array into two values (for use in weird numpy situations with referencing array values)
	return p[1],p[0]
def exists(p): # makes sure that the location is within orb bounds
	if (p[1] < boardHeight and p[0] < boardWidth and p[1] >= 0 and p[0] >= 0):
		return True
	return False
	
def search(startx, starty, goal): #searches for the closest transport-distanced orb that matches the color desired
	global curx, cury, board, lockedBoard
	minx, miny = 50, 50
	shortest = 100
	for y in xrange(0,len(board)):
		for x in xrange(0,len(board[0])):
			if board[y, x] == goal and lockedBoard[y, x] == 0 and [x,y] != [curx,cury]:
				if tdistance(startx, starty, x, y) <= shortest:
					minx, miny = x, y
	if minx == 50 and miny == 50:
		print "Error, no orbs of color", goal, "found"
		print board
		print lockedBoard
		error
	return minx, miny
					
def swap(x, y):
	global curx, cury, board, lockedBoard, pathList, mixedUp, swipelist
	if len(swipelist) > 300:
		print 'swipelist longer than 300 entries. Likely entered a loop somewhere, not going to execute'
	if abs(curx-x > 1) or abs(cury-y > 1):
		print 'Error, moving too far in a swap'
		exit()
	
	if lockedBoard[y][x] == 1:
		lockedBoard[y][x] = 0
		mixedUp.append([x,y,board[y][x]])
	
	mv(x,y)
	pathList.append([x,y])
	
	tempval = board[y][x]
	board[y][x] = board[cury][curx]
	board[cury][curx] = tempval
	curx = x
	cury = y
	
def path(x, y, permission, orbx, orby):
	global curx, cury, board, lockedBoard, dirarray8, pathList
	
	while (x != curx or y != cury) and pathList[-3] != [curx,cury]:
		dirx = min(1, max(-1, x-curx))
		diry = min(1, max(-1, y-cury))
		direction = dirarray8.index([dirx,diry])
		curpos = np.array([curx,cury]) 
		
		if (lockedBoard[cury+diry][curx+dirx] == 0 or permission) and not np.array_equal([orbx, orby], curpos+dirarray8[(direction)]):
			swap(curx+dirx, cury+diry)
		elif exists(curpos+dirarray8[(direction+1)%8]) and not np.array_equal([orbx, orby], curpos+dirarray8[(direction+1)%8]) and 
(lockedBoard[dearray(curpos+dirarray8[(direction+1)%8])] == 0 or permission):
			# This paths it within the bounds of the board, not through locked orbs, and also not through the orb that is currently being transported (if given 'admin')
			swap(curx+dirarray8[(direction+1)%8][0],cury+dirarray8[(direction+1)%8][1])
		elif exists(curpos+dirarray8[(direction-1)%8]) and not np.array_equal([orbx, orby], curpos+dirarray8[(direction-1)%8]) and 
(lockedBoard[dearray(curpos+dirarray8[(direction-1)%8])] == 0 or permission):
			swap(curx+dirarray8[(direction-1)%8][0],cury+dirarray8[(direction-1)%8][1])
		elif exists(curpos+dirarray8[(direction+2)%8]) and not np.array_equal([orbx, orby], curpos+dirarray8[(direction+2)%8]) and 
(lockedBoard[dearray(curpos+dirarray8[(direction+2)%8])] == 0 or permission):
			swap(curx+dirarray8[(direction+2)%8][0],cury+dirarray8[(direction+2)%8][1])
		elif exists(curpos+dirarray8[(direction-2)%8]) and not np.array_equal([orbx, orby], curpos+dirarray8[(direction-2)%8]) and 
(lockedBoard[dearray(curpos+dirarray8[(direction-2)%8])] == 0 or permission):
			swap(curx+dirarray8[(direction-2)%8][0],cury+dirarray8[(direction-2)%8][1])
		else: 
			print "pathing failed"
			return False
	if pathList[-3] == [curx,cury]:
		return False
	return True

def transportOrb(orbx, orby, targetx, targety, permission):
	global curx, cury, board, lockedBoard, dirarray8, pathList, mixedUp
	success = True
	
	
	while(orbx != targetx or orby != targety) and pathList[-3] != [curx,cury]:
		dirx = min(1, max(-1, targetx-orbx))
		diry = min(1, max(-1, targety-orby))
		direction = dirarray8.index([dirx,diry])
		orbpos = np.array([orbx,orby]) 
		if lockedBoard[orby+diry][orbx+dirx] == 0 or permission:
			success = path(orbx+dirx, orby+diry, permission, orbx, orby)
		elif exists(orbpos+dirarray8[(direction+1)%8]) and (lockedBoard[dearray(orbpos+dirarray8[(direction+1)%8])] == 0 or permission):
				# if the direction doesn't take you offboard and is not locked ( permission ignores that part )
			success = path(orbx+dirarray8[(direction+1)%8][0], orby+dirarray8[(direction+1)%8][1], permission, orbx, orby)
		elif exists(orbpos+dirarray8[(direction-1)%8]) and (lockedBoard[dearray(orbpos+dirarray8[(direction-1)%8])] == 0 or permission):
			success = path(orbx+dirarray8[(direction-1)%8][0], orby+dirarray8[(direction-1)%8][1], permission, orbx, orby)
		elif exists(orbpos+dirarray8[(direction+2)%8]) and (lockedBoard[dearray(orbpos+dirarray8[(direction+2)%8])] == 0 or permission):
			success = path(orbx+dirarray8[(direction+2)%8][0], orby+dirarray8[(direction+2)%8][1], permission, orbx, orby)
		elif exists(orbpos+dirarray8[(direction-2)%8]) and (lockedBoard[dearray(
		orbpos+dirarray8[(direction-2)%8])] == 0 or permission):
			success = path(orbx+dirarray8[(direction-2)%8][0], orby+dirarray8[(direction-2)%8][1], permission, orbx, orby)
		else: 
			success = False
		if success:
			tempx = curx
			tempy = cury
			swap(orbx,orby)
			orbx = tempx
			orby = tempy
		else:
			if permission:
				print "Transport REALLY failed this time"
				print board
				print ' '
				print lockedBoard
				print ' '
				print mixedUp
				pg.mouseUp()
				exit()
			print 'sliding in', board[orby][orbx]
			pathList = [[99,99],[99,89],[99,79]]
			transportOrb(orbx, orby, targetx, targety, True) 	#gives access to push orb through locked orbs
			lockedBoard[targety, targetx] = 1
			for entry in mixedUp[::-1]:							#repairs earlier orbs
				#print 'repairing at', entry[0], entry[1], 'with color', entry[2]
				#print mixedUp
				#print '--------'
				#print board
				#print ' '
				#print lockedBoard
				#print '--------'
				displacedx, displacedy = search(entry[0],entry[1],entry[2])
				transportOrb(displacedx, displacedy, entry[0], entry[1], False)
			mixedUp = []
			return
			
	lockedBoard[targety, targetx] = 1

def getColorAdjLocked(x,y): #checks nearby immovable orbs for the colors they have
	global board, lockedBoard
	list = []
	if exists([x-1,y]) and lockedBoard[y, x-1] == 1:
		list.append(board[y][x-1])
	if exists([x+1,y]) and lockedBoard[y, x+1] == 1:
		list.append(board[y][x+1])
	if exists([x,y-1]) and lockedBoard[y-1, x] == 1:
		list.append(board[y-1][x])
	if exists([x,y+1]) and lockedBoard[y+1, x] == 1:
		list.append(board[y+1][x])
	return list
	
def getUnpreferred(startx, starty, dir, leng): # checks an entire combo area for surrounding immovable orbs' colors, so as to avoid those and prevent match crossing
	unpreferredOrbs = []
	for i in xrange(leng):
		list = getColorAdjLocked(startx+dir[0]*i, starty+dir[1]*i)
		for entry in list:
			if entry not in unpreferredOrbs:
				unpreferredOrbs.append(entry)
	return unpreferredOrbs
	
def findMatch(startx, starty, dir, leng, undesired):
	global board, lockedBoard, orbCount, carriedColor, allMatches
	# check to see if there are locked orbs in the way
	for i in xrange(leng):
		if not exists([startx+dir[0]*i,starty+dir[1]*i]):
			print "can't make a match here because OoB"
			print "with values", startx, starty, dir, leng
			return False
		if lockedBoard[starty+dir[1]*i, startx+dir[0]*i] == 1:
			print "can't make a match here because of locks"
			print "with values", startx, starty, dir, leng
			return False
	
	# check what colors would not create a new combo
	
	unpreferredOrbs = getUnpreferred(startx, starty, dir, leng)
	#print ' '
	#print unpreferredOrbs
	preferredOrbs = [x for x in xrange(1,len(orbCount)) if x not in unpreferredOrbs]
	
	# check if match is already made
	color = board[starty][startx]
	if color not in unpreferredOrbs:
		perfect = True
		for i in xrange(1,leng):
			if board[starty+dir[1]*i][startx+dir[0]*i] != color:
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
				absx, absy = search(startx, starty, color)
				lockedBoard[absy][absx] = 2
				colorDistanceList[color] += tdistance(startx+dir[0]*i, starty+dir[1]*i, absx, absy)			
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
			
def makeMatch(startx, starty, dir, leng):
	global board, lockedBoard, orbCount, allMatches
	
	goalcolor = findMatch(startx, starty, dir, leng, [])
	if not goalcolor:
		return False
	print 'matching:', goalcolor
	print '----'
	print board
	print ' ' 
	print lockedBoard
	print '----'
	for i in range(leng):
		orbx, orby = search(startx+dir[0]*i,starty+dir[1]*i,goalcolor)
		transportOrb(orbx,orby,startx+dir[0]*i,starty+dir[1]*i, False)
	orbCount[goalcolor] -= leng
	if matchLocs[-1] != [startx, starty, dir, leng, goalcolor]:
		matchLocs.append([startx, starty, dir, leng, goalcolor])
	allMatches.remove([goalcolor,leng])
	return True

def selectStartOrb(): # tries to select an orb that won't be matched in the end
	global allMatches, trashOrbs
	mincolor = 0
	mindist = 99
	if trashOrbs:
		for entry in trashOrbs:
			x, y = search(0,0,entry[0])
			curdist = mdistance(0,0,x,y)
			if curdist < mindist:
				mincolor = entry[0]
				mindist = curdist
		return search(0,0,mincolor)
	else:
		for entry in allMatches:
			if entry[1] == 3:
				x, y = search(0,0,entry[0])
				curdist = mdistance(0,0,x,y)
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
				trashOrbs.append([color,quantity])
				orbCount[color] -= quantity
	return allMatches, trashOrbs

def getClosestZero(startx, starty):
	global lockedBoard
	minx = 99
	miny = 99
	mindist = 99
	for y in xrange(len(lockedBoard)):
		for x in xrange(len(lockedBoard[0])):
			if lockedBoard[y, x] == 0:
				if mdistance(startx, starty, x, y) <= mindist:
					mindist = mdistance(startx, starty, x, y)
					minx, miny = x, y
	print 'closest zero to', startx, starty, 'at', minx, miny
	print lockedBoard
	return minx, miny


board = getBoard()
lockedBoard = np.zeros_like(board, dtype=int)

allMatches, trashOrbs = getMatches()
# organize allmatches by length
print allMatches
print trashOrbs
print [allMatches[x][1] for x in xrange(len(allMatches))]

curx, cury = -1, -1
curx, cury = selectStartOrb()
mv(curx,cury)
pathList.append([curx,cury])

while 5 in [allMatches[x][1] for x in xrange(len(allMatches))]:
	#x, y = getClosestZero(5,0)
	#makeMatch(x,y,[0,1],5)
	x, y = getClosestZero(0,0)
	makeMatch(x,y,[1,0],5)
print 'fives finished'

while 4 in [allMatches[x][1] for x in xrange(len(allMatches))]:
	x, y = getClosestZero(0,0)
	makeMatch(x,y,[1,0],4)
	x, y = getClosestZero(len(board[0])-1,0)
	makeMatch(x,y,[0,1],4)
print 'fours finished'

for i in range(4,-1,-1):
	makeMatch(5,4,[-1,0],3)
	makeMatch(0,4,[1,0],3)

makeMatch(0,0,[0,1],3) #solve this part better using some location optizing code
makeMatch(1,0,[0,1],3)
makeMatch(2,0,[0,1],3)
makeMatch(3,0,[0,1],3)
makeMatch(4,0,[0,1],3)

makeMatch(0,1,[0,1],3)
makeMatch(1,1,[0,1],3)
makeMatch(2,1,[0,1],3)
makeMatch(3,1,[0,1],3)
makeMatch(4,1,[0,1],3)

makeMatch(0,2,[0,1],3)
makeMatch(1,2,[0,1],3)
makeMatch(2,2,[0,1],3)
makeMatch(3,2,[0,1],3)
makeMatch(4,2,[0,1],3)


#do some ending thing if I can


print board
print lockedBoard
exeswipe(swipelist)