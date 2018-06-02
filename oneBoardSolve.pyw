#/bin/idkwhattoputhereshrug

# requires Windows, Android adb, ImageMagick, OpenCV, an Android Phone with STDHD screen and USB Debugging turned on
# requires Tesseract/pytesseract for macro stuff


from time import sleep
from time import time
import adb_injection #script that sends list of positions to the phone
import numpy as np
import subprocess
import itertools
import random
import cv2
import os


#instead of going through the reorganization every time, instead try permutations of colors that can be changed


sp56 = adb_injection.sp56
startx = adb_injection.startx
starty = adb_injection.starty
boardWidth = 6
boardHeight = 5
top,bottom,left,right = 0,boardHeight-1,0,boardWidth-1

curx, cury = -1, -1
orbCount = [0,0,0,0,0,0,0,0,0,0,0]
orbTypeCount = 7 #how many types of orbs are programmed in
dirarray8 = [[0,1],[1,1],[1,0],[1,-1],[0,-1],[-1,-1],[-1,0],[-1,1]]
dirarray4 = [[0,1],[1,0],[0,-1],[-1,0]]
pathList = [[99,99],[99,89],[99,79]] # a list of all the places the picked-up orb has been
matchLocs = [[99,99,99,99,99]] # a list of all the locations of matches in the board
mixedUp = []
swipelist = []

#------------------------------------------------
# getting board
#------------------------------------------------

def getBoard(img = []):
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
	jammer = cv2.imread('assets/jammerorb.png',0)[10:-10,10:-10]
	poison = cv2.imread('assets/poisonorb.png',0)[10:-10,10:-10]
	imarray = [fire,water,wood,light,dark,heart,jammer,poison]
	#mortal poison =
	
	if not len(img):
		print "no image passed"
		subprocess.call('adb shell screencap /sdcard/screencap.rgba',shell=True) # take and pull screenshot
		subprocess.call('adb pull /sdcard/screencap.rgba',shell=True) # stored in same folder as this file
		subprocess.call('magick convert -size 1080x1920 -depth 8 screencap.rgba screencap.png',shell=True) #converts from rgba to png
		img = cv2.imread('screencap.png',0)
	#cv2.imshow('image',img)
	#cv2.waitKey(0)
	#cv2.destroyAllWindows()


	board = np.zeros([boardHeight,boardWidth],dtype = int)
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
	#board = np.array([[5,6,3,6,3,1],[6,4,4,5,4,3],[4,5,4,1,6,5],[5,2,2,3,3,2],[3,2,2,1,1,2]])
	for y in range(boardHeight):
		for x in range(boardWidth):
			orbCount[board[y,x]] += 1
	print board
	return board

#------------------------------------------------
# getting information from original board
#------------------------------------------------

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
		print coloredBoard
		print len(shortpath), "was the best though"
		print cury, curx
		exit(0)
	return miny, minx
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

	

#------------------------------------------------
# manipulating the original board
#------------------------------------------------

def swap(y, x):
	global cury, curx, board, lockedBoard, pathList, mixedUp, swipelist
	if len(swipelist) > 300:
		print 'swipelist longer than 300 entries. Likely entered a loop somewhere, not going to execute'
		print len(shortpath), "was best though"
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
		elif exists(curpos+dirarray8[(direction+1)%8]) and (not np.array_equal([orby, orbx], curpos+dirarray8[(direction+1)%8])) and (lockedBoard[dearray(curpos+dirarray8[(direction+1)%8])] == 0 or permission):
			# This paths it within the bounds of the board, not through locked orbs, and also not through the orb that is currently being transported (if given 'admin')
			swap(cury+dirarray8[(direction+1)%8][0],curx+dirarray8[(direction+1)%8][1])
		elif exists(curpos+dirarray8[(direction-1)%8]) and (not np.array_equal([orby, orbx], curpos+dirarray8[(direction-1)%8])) and (lockedBoard[dearray(curpos+dirarray8[(direction-1)%8])] == 0 or permission):
			swap(cury+dirarray8[(direction-1)%8][0],curx+dirarray8[(direction-1)%8][1])
		elif exists(curpos+dirarray8[(direction+2)%8]) and (not np.array_equal([orby, orbx], curpos+dirarray8[(direction+2)%8])) and (lockedBoard[dearray(curpos+dirarray8[(direction+2)%8])] == 0 or permission):
			swap(cury+dirarray8[(direction+2)%8][0],curx+dirarray8[(direction+2)%8][1])
		elif exists(curpos+dirarray8[(direction-2)%8]) and (not np.array_equal([orby, orbx], curpos+dirarray8[(direction-2)%8])) and (lockedBoard[dearray(curpos+dirarray8[(direction-2)%8])] == 0 or permission):
			swap(cury+dirarray8[(direction-2)%8][0],curx+dirarray8[(direction-2)%8][1])
		else:
			#print "pathing failed"
			return False
	if pathList[-3] == [cury,curx]:
		return False
	return True
def transportOrb(orby, orbx, targety, targetx, permission, endState):
	global board, lockedBoard, pathList, mixedUp
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
			if len(swipelist) > len(shortpath):
				return
			print 'sliding in', board[orby,orbx]
			pathList = [[99,99],[99,89],[99,79]]
			transportOrb(orby, orbx, targety, targetx, True, endState) 	#gives access to push orb through locked
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
	global board, lockedBoard, pathList, mixedUp
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
		#print 'sliding in', board[orby,orbx]
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
			transportOrb(displacedy, displacedx, entry[0], entry[1], False, 1)
		mixedUp = []
		return

	
#------------------------------------------------
# some helper functions for randomness that I might benefit from later
#------------------------------------------------	

class unique_element:
    def __init__(self,value,occurrences):
        self.value = value
        self.occurrences = occurrences
def perm_unique(elements):
    eset=set(elements)
    listunique = [unique_element(i,elements.count(i)) for i in eset]
    u=len(elements)
    return perm_unique_helper(listunique,[0]*u,u-1)
def perm_unique_helper(listunique,result_list,d):
    if d < 0:
        yield tuple(result_list)
    else:
        for i in listunique:
            if i.occurrences > 0:
                result_list[d]=i.value
                i.occurrences-=1
                for g in  perm_unique_helper(listunique,result_list,d-1):
                    yield g
                i.occurrences+=1

#------------------------------------------------
# manipulating the solved board
#------------------------------------------------

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
def brute(y,x,mnum,perm):
	global arrLocs
	if not (0 in solvedBoard):
		#print 'Board Organized'
		#print solvedBoard
		#print arrLocs
		return True
	if not exists([y,x]):
		print solvedBoard
	if lockedBoard[y,x] == 0:
		if exists([y,x+perm[mnum-1]-1]):
			if setToNumber(y, x, [0,1], mnum, perm[mnum-1]):
				if brute( y+int((x+1)/boardWidth), (x+1)%boardWidth, mnum+1, perm):
					return True
				setToNumber(y, x, [0,1], 0, perm[mnum-1])
				#print arrLocs

		if exists([y+perm[mnum-1]-1,x]):
			if setToNumber(y, x, [1,0], mnum, perm[mnum-1]):
				if brute( y+int((x+1)/boardWidth), (x+1)%boardWidth, mnum+1, perm):
					return True
				setToNumber(y, x, [1,0], 0, perm[mnum-1])
				#print arrLocs

	else:
		if brute( y+int((x+1)/boardWidth), (x+1)%boardWidth, mnum, perm):
			return True
	return False
def step(): #moves the board one step closer to the solved board
	global board, lockedBoard, coloredBoard, cury, curx
	if len(swipelist) > len(shortpath):
		return False
	costBoard = np.zeros_like(board, dtype=float)+100
	priorityBoard = np.zeros_like(board)

	for y in xrange(boardHeight):
		for x in xrange(boardWidth):
			priorityBoard[y,x] = getStepPriority(y,x)
			if priorityBoard[y,x] != 0 and (coloredBoard[y,x] != board[cury,curx] or np.sum(lockedBoard[coloredBoard == board[cury,curx]] == 0) > 1):
				costBoard[y,x] = getCost(y, x, priorityBoard[y,x])

	loc = np.where(costBoard == np.amin(costBoard))
	#print loc
	locy = loc[0][0]
	locx = loc[1][0]
	orby, orbx = search(locy,locx, coloredBoard[locy,locx])
	if False:
		print board
		print lockedBoard
		print coloredBoard
		print priorityBoard
		print costBoard
		print top,bottom,left,right
		print "moving",orby,orbx,"towards",locy,locx

	if mdistance(locy,locx,orby,orbx) <= 1:
		endState = 1
	else:
		endState = 0

	transportStep(orby, orbx, locy, locx, False, endState)
	return True
def arrangeBoardRandom():
	global solvedBoard, lockedBoard, coloredBoard, arrLocs, board, left, right, top, bottom, shortpath, curx, cury
	getMatches()
	shortpath = xrange(300)
	minapprox = 300
	starttime = time()
	for i in xrange(3000):
		timeouttime = 10*float(len(shortpath)-60)/100
		if time()-starttime > timeouttime: # stops if the solution is good enough or if it hasn't found a better solution in the last second
			break
		match = random.sample(allMatches,len(allMatches))
		colors = [x[0] for x in match]
		lengths = [x[1] for x in match]
		solvedBoard = np.zeros_like(board)
		lockedBoard = np.zeros_like(board)
		arrLocs = []
		if brute(0,0,1,lengths): #tries to make a board from all of the matches via brute force
			#print 'a'*1000

			maxi = np.amax(solvedBoard)
			coloredBoard = np.zeros_like(solvedBoard)
			for i in xrange(maxi): coloredBoard[solvedBoard == i+1] = colors[i]

			tempboard = np.copy(board)
			curx, cury = -1, -1
			lockedBoard = np.zeros_like(board)
			approxLen = getApproxLength(coloredBoard)
			board = np.copy(tempboard)
			if approxLen < minapprox+5:

				top,bottom,left,right = 0,boardHeight-1,0,boardWidth-1
				swipelist = getMoves()
				if len(swipelist) < len(shortpath): #could add more checks like max combo
					shortpath = swipelist
					minapprox = approxLen
					starttime = time()
					print len(swipelist)#, approxLen
				board = np.copy(tempboard)

	return shortpath

	
#------------------------------------------------
# getting information from the solved board
#------------------------------------------------

def getApproxLength(sBoard):
	cost = 0
	for y in xrange(boardHeight):
		for x in xrange(boardWidth):
   			orby, orbx = search(y,x,sBoard[y,x])
			cost += mdistance(y,x,orby,orbx)
			board[orby,orbx] = 0
	return cost
def getStepPriority(y,x): # limits the solving to the edge of the unsolved area, so it decreases in a rectangle
	global top, bottom, left, right
	if lockedBoard[y,x] == 1: return 0
	if not 0 in lockedBoard[top,:]: top = top+1
	if not 0 in lockedBoard[bottom,:]: bottom = bottom-1
	if not 0 in lockedBoard[:,left]: left = left+1
	if not 0 in lockedBoard[:,right]: right = right-1
	if top>0:
		if 0 in lockedBoard[0:top,:]:
			print "HERE (top)"
			print lockedBoard
			exit(0)
	if bottom<boardHeight-1:
		if 0 in lockedBoard[bottom+1:boardHeight,:]:
			print "HERE (bottom)"
			print lockedBoard
			exit(0)
	if top>0:
		if 0 in lockedBoard[:,0:left]:
			print "HERE (left)"
			print lockedBoard
			exit(0)
	if top>0:
		if 0 in lockedBoard[:,right+1:boardWidth]:
			print "HERE (right)"
			print lockedBoard
			exit(0)
	if bottom-top < right-left and (x == left or x == right): return 2
	if right-left < bottom-top and (y == top or y == bottom): return 2
	if y == top or y == bottom or x == left or x == right: return 1
	else: return 0

	'''
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
		'''
def getCost(locy,locx,priority): # gets the distance the finger would need to travel to fill an unlocked edge slot
	global board, cury, curx
	orby, orbx = search(locy,locx,coloredBoard[locy,locx])
	if locy == orby and locx == orbx:
		return 0
	return float(mdistance(cury, curx, orby + min(1, max(-1, locy-orby)), orbx + min(1, max(-1, locx-orbx)))+1)/priority


def getMoves():
	global swipelist, lockedBoard, curx, cury
	swipelist = []
	cury, curx = 2, 2 #maybe pick one of the most common color?
	mv(cury,curx)
	pathList.append([cury,curx])
	lockedBoard = np.zeros_like(lockedBoard)
	while( not np.array_equal(board,coloredBoard)):
		if not step():
			return xrange(300)
	return swipelist

def solveBoard(img = []):
	global board, lockedBoard, trashOrbs, allMatches
	board = getBoard(img)
	starttime = time()
	lockedBoard = np.zeros_like(board, dtype=int)
	allMatches = getMatches()
	moves = arrangeBoardRandom()
	#cury, curx = -1, -1
	#numberBoard()
	#print board
	#print lockedBoard
	print coloredBoard
	print len(moves)
	print "time to execute =", time() - starttime
	adb_injection.exeswipe(moves)
	return True
	
if __name__ == '__main__':
    solveBoard()

