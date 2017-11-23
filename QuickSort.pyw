
# start combo in place that requires the least movement
	# make a variable ending routine
# full board clear?
# lay out board before execution?
# determine combo placement automatically
	# descending size
# move farthest orb towards first? or maybe group them?



import pyautogui as pg
from time import sleep
from time import time
import numpy

pg.PAUSE = .05
pg.FAILSAFE = True


start = [720,635]
sp56 = 95.5
plusstart = [746, 655]

fireval = (255,116,75)
waterval = (36,50,106)
woodval = (85,234,100)
lightval = (251,248,138)
darkval = (30,10,85)
heartval = (214,31,125)
plusval = (254,251,0)
jammerval = (63,101,125)

orbCount = [0,0,0,0,0,0,0,0,0,0,0]
board = numpy.zeros((5,6), dtype=numpy.int)
lockedBoard = numpy.zeros((5,6), dtype=numpy.int)
dirarray8 = [[1,0],[1,1],[0,1],[-1,1],[-1,0],[-1,-1],[0,-1],[1,-1],[1,0],[1,1]]
pathList = [[99,99],[99,89],[99,79]]
matchLocs = [[99,99,99,99,99]]
mixedUp = []



def pos(x, y):
	return [start[0]+x*sp56,start[1]+y*sp56]
def plusPos(x, y):
	return [plusstart[0]+x*sp56,plusstart[1]+y*sp56]
def mv(x, y):
	pg.moveTo(pos(x,y))
def distance(x1, y1, x2, y2):
	return (max(abs(x1-x2),abs(y1-y2))*3)+min(abs(x1-x2),abs(y1-y2))
def dearray(p):
	return p[1],p[0]
	
	
def exists(p):
	if (p[1] < 5 and p[0] < 6 and p[1] >= 0 and p[0] >= 0):
		return True
	return False
	
def tolerence(identity, test, dev):
	for i in xrange(3):
		if (identity[i]-dev > test[i] or test[i] > identity[i]+dev):
			return False
	return True
	
def getOrbColor(x, y, color):
	global board, orbCount
	if tolerence(fireval,color,20):
		board[y][x] = 1
		orbCount[1] += 1
	elif tolerence(waterval,color,15):
		board[y][x] = 2
		orbCount[2] += 1
	elif tolerence(woodval,color,30):
		board[y][x] = 3
		orbCount[3] += 1
	elif tolerence(lightval,color,10):
		board[y][x] = 4
		orbCount[4] += 1
	elif tolerence(darkval,color,30):
		board[y][x] = 5
		orbCount[5] += 1
	elif tolerence(heartval,color,10):
		board[y][x] = 6
		orbCount[6] += 1
	elif tolerence(jammerval,color,20):
		board[y][x] = 7
		orbCount[7] += 1
	
def getBoard():
	global orbCount
	
	im = pg.screenshot()										# initial color checking
	for y in xrange(5):
		for x in xrange(6):
			p = pos(x,y)
			getOrbColor(x, y, im.getpixel((p[0],p[1])))
	checks = numpy.where(board == 0)
	
	for i in xrange(len(checks[0])): 							# checking if 0's are plus orbs
		p = plusPos(checks[1][i],checks[0][i])
		if not tolerence(plusval, im.getpixel((p[0],p[1])), 20):
			mv(checks[1][i],checks[0][i])
			print im.getpixel((p[0],p[1]))
			print "Recognition error"
			print board	
			exit()
			
	startTime = time()
	while 0 in board: 											# resolving plus orbs
		if time() > startTime + 10:
			print "Plus Recognition error"
			print board
			exit()
		checks = numpy.where(board == 0)
		im = pg.screenshot()
		for i in xrange(len(checks[0])):
			p = pos(checks[1][i], checks[0][i])
			getOrbColor(checks[1][i], checks[0][i], im.getpixel((p[0],p[1])))
		
	print board
	return board

	
def search(startx, starty, goal):
	global curx, cury, board, lockedBoard
	minx, miny = 50, 50
	for y in xrange(0,len(board)):
		for x in xrange(0,len(board[0])):
			if board[y, x] == goal and lockedBoard[y, x] == 0 and [x,y] != [curx,cury]:
				if distance(startx, starty, minx, miny) >= distance(startx, starty, x, y):
					minx, miny = x, y
	if minx == 50 and miny == 50:
		print "Error, no orbs of color", goal, "found"
		print board
		print lockedBoard
	return minx, miny
					
def swap(x, y):
	global curx, cury, board, lockedBoard, pathList, mixedUp, beginTime
	
	if time() > beginTime + 12:
		pg.mouseUp()
		print 'timeout error'
		print board
		print ' ' 
		print lockedBoard
	
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
		curpos = numpy.array([curx,cury]) 
		
		if (lockedBoard[cury+diry][curx+dirx] == 0 or permission) and not numpy.array_equal([orbx, orby], curpos+dirarray8[(direction)]):
			swap(curx+dirx, cury+diry)
		elif exists(curpos+dirarray8[(direction+1)]) and not numpy.array_equal([orbx, orby], curpos+dirarray8[(direction+1)]) and (lockedBoard[dearray(curpos+dirarray8[(direction+1)])] == 0 or permission):
			# This paths it within the bounds of the board, not through locked orbs, and also not through the orb that is currently being transported (if given 'admin')
			swap(curx+dirarray8[(direction+1)][0],cury+dirarray8[(direction+1)][1])
		elif exists(curpos+dirarray8[(direction-1)]) and not numpy.array_equal([orbx, orby], curpos+dirarray8[(direction-1)]) and (lockedBoard[dearray(curpos+dirarray8[(direction-1)])] == 0 or permission):
			swap(curx+dirarray8[(direction-1)][0],cury+dirarray8[(direction-1)][1])
		elif exists(curpos+dirarray8[(direction+2)]) and not numpy.array_equal([orbx, orby], curpos+dirarray8[(direction+2)]) and (lockedBoard[dearray(curpos+dirarray8[(direction+2)])] == 0 or permission):
			swap(curx+dirarray8[(direction+2)][0],cury+dirarray8[(direction+2)][1])
		elif exists(curpos+dirarray8[(direction-2)]) and not numpy.array_equal([orbx, orby], curpos+dirarray8[(direction-2)]) and (lockedBoard[dearray(curpos+dirarray8[(direction-2)])] == 0 or permission):
			swap(curx+dirarray8[(direction-2)][0],cury+dirarray8[(direction-2)][1])
		else: 
			print "pathing failed"
			return False
	if pathList[-3] == [curx,cury]:
		return False
	return True

def getColorAdjLocked(x,y):
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
	
def transportOrb(orbx, orby, targetx, targety, permission):
	global curx, cury, board, lockedBoard, dirarray8, pathList, orbCount, mixedUp
	success = True
	
	#print board
	#print ' '
	#print lockedBoard
	#print 'v    v    v    v'
	
	while(orbx != targetx or orby != targety) and pathList[-3] != [curx,cury]:
		dirx = min(1, max(-1, targetx-orbx))
		diry = min(1, max(-1, targety-orby))
		direction = dirarray8.index([dirx,diry])
		orbpos = numpy.array([orbx,orby]) #critical difference between path and transport
		if lockedBoard[orby+diry][orbx+dirx] == 0 or permission:
			success = path(orbx+dirx, orby+diry, permission, orbx, orby)
		elif exists(orbpos+dirarray8[(direction+1)]) and (lockedBoard[dearray(orbpos+dirarray8[(direction+1)])] == 0 or permission):
			success = path(orbx+dirarray8[(direction+1)][0], orby+dirarray8[(direction+1)][1], permission, orbx, orby)
		elif exists(orbpos+dirarray8[(direction-1)]) and (lockedBoard[dearray(orbpos+dirarray8[(direction-1)])] == 0 or permission):
			success = path(orbx+dirarray8[(direction-1)][0], orby+dirarray8[(direction-1)][1], permission, orbx, orby)
		elif exists(orbpos+dirarray8[(direction+2)]) and (lockedBoard[dearray(orbpos+dirarray8[(direction+2)])] == 0 or permission):
			success = path(orbx+dirarray8[(direction+2)][0], orby+dirarray8[(direction+2)][1], permission, orbx, orby)
		elif exists(orbpos+dirarray8[(direction-2)]) and (lockedBoard[dearray(orbpos+dirarray8[(direction-2)])] == 0 or permission):
			success = path(orbx+dirarray8[(direction-2)][0], orby+dirarray8[(direction-2)][1], permission, orbx, orby)
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
			#print 'start higher level transport'
			transportOrb(orbx, orby, targetx, targety, True) 	#gives access to push orb through locked orbs
			lockedBoard[targety, targetx] = 1
			#print 'end higher level transport'
			#match = matchLocs[-1]								#but only once the orb has gone as far as possible
			#for i in xrange(match[3]):
			#	lockedBoard[match[1]+match[2][1]*i][match[0]+match[2][0]*i] = 0
			#orbCount[match[4]] += match[3]
			#print 'begin repairing match'
			#print board
			#print lockedBoard
			#print 'AAAAAAAA'
			for entry in mixedUp[::-1]:							#repairs earlier orbs
				print 'repairing at', entry[0], entry[1], 'with color', entry[2]
				print mixedUp
				print '--------'
				print board
				print ' '
				print lockedBoard
				print '--------'
				displacedx, displacedy = search(entry[0],entry[1],entry[2])
				transportOrb(displacedx, displacedy, entry[0], entry[1], False)
			mixedUp = []
			return
			#print 'end repairing match v'
			#print board
			#print lockedBoard
			#print 'AAAAAAA'
			
	lockedBoard[targety, targetx] = 1
	#print board
	#print ' '
	#print lockedBoard
	#print '----------------'
	
def getUnpreferred(startx, starty, dir, leng):
	unpreferredOrbs = []
	for i in xrange(leng):
		list = getColorAdjLocked(startx+dir[0]*i, starty+dir[1]*i)
		for entry in list:
			if entry not in unpreferredOrbs:
				unpreferredOrbs.append(entry)
	return unpreferredOrbs
	
def findMatch(startx, starty, dir, leng, undesired):
	global board, lockedBoard, orbCount, carriedColor
	
	# check to see if there are locked orbs in the way
	for i in xrange(leng):
		if lockedBoard[starty+dir[1]*i][startx+dir[0]*i] == 1:
			print "can't make a match here because of locks"
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
	colorDistanceList = numpy.zeros(10, dtype=numpy.int)
	for color in preferredOrbs:
		if orbCount[color] >= leng:
			for i in xrange(leng):
				absx, absy = search(startx, starty, color)
				lockedBoard[absy][absx] = 2
				colorDistanceList[color] += distance(startx+dir[0]*i, starty+dir[1]*i, absx, absy)
	oldColorDistanceList = [x for x in colorDistanceList]
	newColorDistanceList = [x for x in colorDistanceList if x != 0]
	print oldColorDistanceList
	
	# reset lockedBoard
	twos = numpy.where(lockedBoard == 2)
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
	global board, lockedBoard, orbCount
	
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
	#print 'after match v'
	#print board
	#print ' '
	#print lockedBoard
	#print 'after match A'
	if matchLocs[-1] != [startx, starty, dir, leng, goalcolor]:
		matchLocs.append([startx, starty, dir, leng, goalcolor])
	return True

def selectStartOrb():
	global board, orbCount
	for i in xrange(1,6):
		for y in xrange(-i,i+1):
			for x in xrange(-i,i+1):
				if exists([x,y]):
					if orbCount[board[y][x]]%3 != 0 and [x,y] != [0,0]:
						return x,y
	return 1,0
	

board = getBoard()

curx, cury = selectStartOrb()
mv(curx,cury)
pathList.append([curx,cury])
pg.mouseDown()

carriedColor = board[cury][curx]
print 'picked up', carriedColor
orbCount[carriedColor] -= 1

sleep(.2)
beginTime = time()
makeMatch(0,0,[1,0],3)
makeMatch(0,1,[1,0],3)
makeMatch(0,2,[1,0],3)
makeMatch(0,3,[1,0],3)
makeMatch(0,4,[1,0],3)

makeMatch(3,0,[1,0],3)
makeMatch(3,1,[1,0],3)
makeMatch(3,2,[1,0],3)

for color in xrange(len(orbCount)):
	if orbCount[color] >= 3:
		x,y = search(3,3,color)
		transportOrb(x,y, 3,4, False)
		x,y = search(5,3,color)
		transportOrb(x,y, 5,4, False)
		x,y = search(4,3,color)
		transportOrb(x,y, 4,4, False)


print board
print lockedBoard

sleep(.1)
pg.mouseUp()

'''
x, y = pos(0,0)
print pg.pixel(x, y)
x, y = pos(0,0)
print pg.pixel(x, y)
x, y = pos(0,0)
print pg.pixel(x, y)

while(True):
	x, y = pg.position()
	positionStr = 'X: ' + str(x) + ' Y: ' + str(y)
	print positionStr
	sleep(1)
'''