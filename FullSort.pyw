
# to find most efficient combo board, iterate through all permutations of where to place each same-sized match
	# when the board is laid out, look at the total number of blobs with size >= 6 as well as their size (tree search)
	# if better than the current stored board, save it and its data
	# if the board is optimal (no blobs larger than 5), exit and make the board

# start combo in place that requires the least movement
	# make a variable ending routine

# lay out board before execution?

# move farthest orb towards first? or maybe group them?
	# allow moving through combos to hasten that combo
	
# change distance function based on the type of move

# figure out what to do on a board with few colors
	# check if the most plentiful orb has more than 15



import pyautogui as pg
from time import sleep
from time import time
import numpy

pg.PAUSE = .05
pg.FAILSAFE = True
doMovement = False


start = [720,635]
sp56 = 95.5
plusstart = [746, 655]
boardWidth = 6
boardHeight = 5
totalMoves = 0

fireval = (255,116,75)
waterval = (36,50,106)
woodval = (85,234,100)
lightval = (251,248,138)
darkval = (30,10,85)
heartval = (214,31,125)
plusval = (254,251,0)
jammerval = (63,101,125)

orbCount = [0,0,0,0,0,0,0,0,0,0,0]
orbTypeCount = 7 #how many types of orbs are programmed in
board = numpy.zeros((boardHeight,boardWidth), dtype=numpy.int)
lockedBoard = numpy.zeros((boardHeight,boardWidth), dtype=numpy.int)
dirarray8 = [[1,0],[1,1],[0,1],[-1,1],[-1,0],[-1,-1],[0,-1],[1,-1]]
pathList = [[99,99],[99,89],[99,79]] # a list of all the places the picked-up orb has been
matchLocs = [[99,99,99,99,99]] # a list of all the locations of matches in the board
mixedUp = []



def pos(x, y):
	return [start[0]+x*sp56,start[1]+y*sp56]
def plusPos(x, y):
	return [plusstart[0]+x*sp56,plusstart[1]+y*sp56]
def mv(x, y):
	if doMovement:
		pg.moveTo(pos(x,y))
def distance(x1, y1, x2, y2):
	return (max(abs(x1-x2),abs(y1-y2))*3)+min(abs(x1-x2),abs(y1-y2))
def dearray(p):
	return p[1],p[0]
	
	
def exists(p): #makes sure that the location is within orb bounds
	if (p[1] < boardHeight and p[0] < boardWidth and p[1] >= 0 and p[0] >= 0):
		return True
	return False
	
def tolerence(identity, test, tol): #checks whether the color is within tolerence
	for i in xrange(3):
		if (identity[i]-tol > test[i] or test[i] > identity[i]+tol):
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
	#poison
	#mortal poison
	#bomb?
	#cloud?
	#darkened orb?
	#lights out board?
	
def getBoard():
	'''
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
		
	'''
	
	board = numpy.random.randint(6, size=(boardHeight, boardWidth))
	board = board+1
	for y in range(boardHeight):
		for x in range(boardWidth):
			orbCount[board[y,x]] += 1
	
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
		error
	return minx, miny
					
def swap(x, y):
	global curx, cury, board, lockedBoard, pathList, mixedUp, beginTime, doMovement, totalMoves
	totalMoves += 1
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
		elif exists(curpos+dirarray8[(direction+1)%8]) and not numpy.array_equal([orbx, orby], curpos+dirarray8[(direction+1)%8]) and (lockedBoard[dearray(curpos+dirarray8[(direction+1)%8])] == 0 or permission):
			# This paths it within the bounds of the board, not through locked orbs, and also not through the orb that is currently being transported (if given 'admin')
			swap(curx+dirarray8[(direction+1)%8][0],cury+dirarray8[(direction+1)%8][1])
		elif exists(curpos+dirarray8[(direction-1)%8]) and not numpy.array_equal([orbx, orby], curpos+dirarray8[(direction-1)%8]) and (lockedBoard[dearray(curpos+dirarray8[(direction-1)%8])] == 0 or permission):
			swap(curx+dirarray8[(direction-1)%8][0],cury+dirarray8[(direction-1)%8][1])
		elif exists(curpos+dirarray8[(direction+2)%8]) and not numpy.array_equal([orbx, orby], curpos+dirarray8[(direction+2)%8]) and (lockedBoard[dearray(curpos+dirarray8[(direction+2)%8])] == 0 or permission):
			swap(curx+dirarray8[(direction+2)%8][0],cury+dirarray8[(direction+2)%8][1])
		elif exists(curpos+dirarray8[(direction-2)%8]) and not numpy.array_equal([orbx, orby], curpos+dirarray8[(direction-2)%8]) and (lockedBoard[dearray(curpos+dirarray8[(direction-2)%8])] == 0 or permission):
			swap(curx+dirarray8[(direction-2)%8][0],cury+dirarray8[(direction-2)%8][1])
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
	global curx, cury, board, lockedBoard, dirarray8, pathList, mixedUp
	success = True
	
	
	while(orbx != targetx or orby != targety) and pathList[-3] != [curx,cury]:
		dirx = min(1, max(-1, targetx-orbx))
		diry = min(1, max(-1, targety-orby))
		direction = dirarray8.index([dirx,diry])
		orbpos = numpy.array([orbx,orby]) 
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
	
def getUnpreferred(startx, starty, dir, leng):
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
	allowedIndex = numpy.where(numpy.array([allMatches[x][1] for x in xrange(len(allMatches))]) == leng)
	print [allMatches[x][1] for x in xrange(len(allMatches))]
	print allowedIndex[0]
	colorDistanceList = numpy.zeros(10, dtype=numpy.int)
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

def selectStartOrb():
	global allMatches, trashOrbs
	mincolor = 0
	mindist = 99
	if trashOrbs:
		for entry in trashOrbs:
			x, y = search(0,0,entry[0])
			curdist = distance(0,0,x,y)
			if curdist < mindist:
				mincolor = entry[0]
				mindist = curdist
		return search(0,0,mincolor)
	else:
		for entry in allMatches:
			if entry[1] == 3:
				x, y = search(0,0,entry[0])
				curdist = distance(0,0,x,y)
				if curdist < mindist:
					mincolor = entry[0]
					mindist = curdist
		allMatches.remove([mincolor, 3])
		return search(0,0,mincolor)
	error #no matches of 3 found
	return 1,0
	
def getMatches():
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
				if distance(startx, starty, x, y) <= mindist:
					mindist = distance(startx, starty, x, y)
					minx, miny = x, y
	print 'closest zero to', startx, starty, 'at', minx, miny
	print lockedBoard
	return minx, miny
	

board = getBoard()

allMatches, trashOrbs = getMatches()
# organize allmatches by length
print allMatches
print trashOrbs
print [allMatches[x][1] for x in xrange(len(allMatches))]

curx, cury = -1, -1
curx, cury = selectStartOrb()
mv(curx,cury)
pathList.append([curx,cury])

if doMovement:
	pg.mouseDown()


carriedColor = board[cury][curx]
print 'picked up', carriedColor


sleep(.2)
beginTime = time()

#put fives in horizontal in upper left
#put fours alternating upper right going down and upper left going right
#use the size of the zeros in the left column to determine placement of threes vertically or horizonatally along the bottom

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
print "Total Moves:", totalMoves

if doMovement:
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