#!aoensuhatnsoeh

from time import sleep
from time import time
import oneBoardSolve
import numpy as np
import unicodedata
import pytesseract
import subprocess
import cv2


refPt = []
cropping = False
confirm = False
mode = 'full'
movetime = 9


def printMenu():
	print ""
	print "0: Autorun through everything based on preset conditions"
	print "# > 0: solve # of boards (until end)"
	print "select: select cropped image"
	print "input: manually input all the orbs (in case of clouds, blinds, etc)"
	print "confirm: toggle whether the solver asks for confirmation of board"
	print "config: configure what the solver does"
	print "mode: sets the orb grouping mode"
	print "movetime: set the time your team has to move orbs"
	print "issues: prints known problems that I'm too lazy to solve"
	
def printIssues():
	print ""
	print "Known issues:"
	print "------------------------------------------------------------"
	print "Doesn't work on 7x6 or 5x4 boards,"
	print "Gets stuck if team fails dungeon"
	print "Doesn't check for sufficient stamina"
	print "Exits if achievement box (rank or such) pops up"
	print "Exits if monster box fills up"
	print "Occasionally gets confused on selling monsters screen"
	print "Mortal poison can't be identified yet"
	print "Blinds, clouds, tape, etc, are not recognized"
	print "------------------------------------------------------------"
	print ""
	
def changeMode():
	global mode
	print ""
	print "Available Modes"
	print "------------------------------------------------------------"
	print "1. Full solve"
	print "2. Lock to 7 combos"
	print "3. Max combos"
	print "4. Max combos with setup"
	print "5. Fastest solve"
	print "6. Fastest solve with setup"
	mode = ''
	while not mode:
		a = raw_input("Choose Mode: ")
		if a == "1":
			mode = 'full'
		elif a == "2":
			mode = '7'
		elif a == "3":
			mode = 'max'
		elif a == "4":
			mode = 'max_setup'
		elif a == "5":
			mode = 'fast'
		elif a == "6":
			mode = 'fast_setup'
		else:
			print "that is not a valid mode"
	print "Setting to Mode " + mode
	return
	
def setMovetime():
	global movetime
	while True:
		try:
			movetime = float(raw_input("Enter amount of time you have to solve: "))
			if movetime > 100:
				movetime = 100
			if movetime < 4:
				movetime = 4
			break
		except ValueError:
			print "That is not a number"
	print "Time set for {} seconds".format(movetime)

def click_and_crop(event, x, y, flags, param):
	# grab references to the global variables
	global refPt, cropping, img
 
	# if the left mouse button was clicked, record the starting
	# (x, y) coordinates and indicate that cropping is being
	# performed
	if event == cv2.EVENT_LBUTTONDOWN:
		refPt = [(x, y)]
		cropping = True
 
	# check to see if the left mouse button was released
	elif event == cv2.EVENT_LBUTTONUP:
		# record the ending (x, y) coordinates and indicate that
		# the cropping operation is finished
		refPt.append((x, y))
		cropping = False
 
		# draw a rectangle around the region of interest
		cv2.rectangle(img, refPt[0], refPt[1], (0, 255, 0), 2)
		cv2.imshow("image", img)
		
def refineBounds():
	global img
	img = getScreenshot()
	clone = img.copy()
	cv2.namedWindow("image", cv2.WINDOW_NORMAL)
	cv2.setMouseCallback("image", click_and_crop)
	cv2.resize(img, (540, 960))
	
	while True:
		# display the image and wait for a keypress
		cv2.imshow("image", img)
		key = cv2.waitKey(1) & 0xFF
	 
		# if the 'r' key is pressed, reset the cropping region
		if key == ord("r"):
			image = clone.copy()
	 
		# if the 'c' key is pressed, break from the loop
		elif key == ord("c"):
			break
	 
	# if there are two reference points, then crop the region of interest
	# from the image and display it
	if len(refPt) == 2:
		roi = clone[refPt[0][1]:refPt[1][1], refPt[0][0]:refPt[1][0]]
		cv2.imshow("ROI", roi)
		cv2.waitKey(0)
		print refPt[0][1],":",refPt[1][1],",", refPt[0][0],":",refPt[1][0]
	cv2.destroyAllWindows()
'''
	x1,x2,y1,y2 = 0,1080,0,1920 #should really get data from image, not just 1920 by 1080
	while(True):
		cv2.imshow('image',img[y1:y2,x1:x2])
		cv2.waitKey(0)
		a = raw_input("Choose side to refine using l,r,u,d\n")
		if a == "u":
			y1 = int(raw_input("Top side new bound:\n"))
		elif a == "l":
			x1 = int(raw_input("Left side new bound:\n"))
		elif a == "d":
			y2 = int(raw_input("Bottom side new bound:\n"))
		elif a == "r":
			x2 = int(raw_input("Right side new bound:\n"))
		elif a == "exit": 
			break
		cv2.destroyAllWindows()
		'''

def tap(x, y, duration=80):
	subprocess.call('adb shell input touchscreen swipe {} {} {} {} {}'.format(str(x),str(y),str(x),str(y),str(duration)),shell=True)
	sleep(1)
def swipe(x1, y1, x2, y2, duration=300):
	subprocess.call('adb shell input touchscreen swipe {} {} {} {} {}'.format(str(x1),str(y1),str(x2),str(y2),str(duration)),shell=True)
	
def tapOnImage(img, button, occurence = 0):
	loc = np.where(cv2.matchTemplate(img,cv2.imread('assets/{}'.format(button),0),cv2.TM_CCOEFF_NORMED) > 0.96)
	if len(loc[0]) > 0:
		tap(loc[1][occurence],loc[0][occurence])
		print loc[1][occurence],loc[0][occurence]
		return True
	return False
	


def getScreenshot():
	subprocess.call('adb shell screencap /sdcard/screencap.rgba',shell=True) # take and pull screenshot
	subprocess.call('adb pull /sdcard/screencap.rgba',shell=True) # stored in same folder as this file
	subprocess.call('magick convert -size 1080x1920 -depth 8 screencap.rgba screencap.png',shell=True) #converts from rgba to png
	img = cv2.imread('screencap.png',0)
	return img
def inputBoard():
	print "Input orbs from the top left across"
	print "Red: 1, blue: 2, green: 3, yellow: 4, purple: 5, pink: 6, jammer: 7, poison: 8, mortal poison*: 9"
	b = np.zeros((oneBoardSolve.boardHeight,oneBoardSolve.boardWidth), dtype=int)
	input = ""
	i = 0
	while i < oneBoardSolve.boardHeight*oneBoardSolve.boardWidth:
		print b
		input += raw_input("orb > ")
		while i < len(input):
			y = int(i/6)
			x = i % 6
			try:
				b[y,x] = int(input[i])
				if b[y,x] > 9 or b[y,x] <= 0:
					print "That is not a valid orb number"
					raise Exception()
				i += 1
			except ValueError:
				print "That is not a valid number"
				input = input[:i]
			except Exception:
				input = input[:i]
				
		"""
	for y in xrange(oneBoardSolve.boardHeight):
		for x in xrange(oneBoardSolve.boardWidth):
			while True:
				try:
					b[y,x] = int(raw_input("> "))
					break
				except ValueError:
					print "That is not an integer"
					"""
	img = getScreenshot()
	while(True):
		try:
			print 'a'
			a = oneBoardSolve.solveBoard(img,mode,movetime,confirm,b)
			if a:
				sleep(15)
			break
		except (KeyboardInterrupt):
			print "Keyboard Interrupt"
			return
		#except:
		#	pass

def checkHome(img):
	others = cv2.imread('assets/others.png',0)
	if np.amax(cv2.matchTemplate(img[1760:,920:],others,cv2.TM_CCOEFF_NORMED)) > 0.98:
		return True
	return False	
def checkDungeon(img):
	menu = cv2.imread('assets/Menu.png',0)
	if np.amax(cv2.matchTemplate(img[75:110, 930:],menu,cv2.TM_CCOEFF_NORMED)) > 0.94:
		return True
	coin = cv2.imread('assets/Coin.png',0)
	if np.amax(cv2.matchTemplate(img[70:150, 15:85],coin,cv2.TM_CCOEFF_NORMED)) > 0.94:
		return True
	return False	
def checkSell(img):
	others = cv2.imread('assets/MonstersAcquired.png',0)
	if np.amax(cv2.matchTemplate(img,others,cv2.TM_CCOEFF_NORMED)) > 0.99:
		return True
	return False
	
def checkStamina(img): #unused
	text = pytesseract.image_to_string(img[243:290,500:664])
	a = str(text).split("/")
	return int(a[0])	
def getTab(img): #unused
	tab = img[350:430,10:680]
	cv2.imshow('image',tab)
	cv2.waitKey(0)
	cv2.destroyAllWindows()
	raw_text = pytesseract.image_to_string(tab)
	print len(raw_text)
	convert_text = unicodedata.normalize('NFKD', raw_text).encode('ascii','ignore')
	print convert_text
	
def goToDungeonSection(name):
	tap(90,1830)
	tap(90,1830)
	sleep(1)
	img = getScreenshot()
	tapOnImage(img,'DungeonsScreen/{}.png'.format(name))
def goToDungeon(dungeonName):
	if dungeonName == 'newest':
		swipe(1040, 1600, 1040, 400) # go to top of dungeons screen
		tap(540, 500)  # tap on top dungeon
	else:
		try:
			img = getScreenshot()
			if not tapOnImage(img, dungeonName + ".png"):
				print "I can't find the dungeon. The dungeon might not be on this page, scroll down to have it on screen and try again."
				exit()
		except (SystemExit):
			print "It doesn't look like I have a dungeon of that name, try saving an image of the dungeon tile. Use the refineBounds() function and drag over the region you want to select."
			exit()
def goToFloor(floorName):
	if floorName == 'newest':
		swipe(1040, 1600, 1040, 400) # go to top of dungeon level screen
		tap(540, 500)  # tap on top floor
	else:
		try:
			img = getScreenshot()
			if not tapOnImage(img, floorName + ".png"):
				print "I can't find the floor. The dungeon might not be on this page, scroll down to have it on screen and try again."
				exit()
		except (SystemExit):
			print "It doesn't look like I have a floor of that name, try saving an image of the dungeon tile. Use the refineBounds() function and drag over the region you want to select."
			exit()
			
	swipe(1040, 1600, 1040, 400) # go to top of helper screen
	tap(540, 500)  # tap on helper
	tap(540, 1100) # tap on ok
	tap(540, 1570) # tap on enter
		
def sellScreen(sellMonsters = "ask"): # sell, ask, or keep
	if sellMonsters == "sell":
		img = getScreenshot()
		if tapOnImage(img,"SellOne.png"): # if there's a 'sell monster' screen
			print "Selling all monsters"
			swipe(180,760,900,760,500) #sell two rows of monsters
			swipe(180,920,900,920,500)
			img = getScreenshot()
			tapOnImage(img,"SellTwo.png") # press the sell button to finalize sale
			tap(1070,1920/2, 200) # tap to exit monster screen
			tap(1070,1920/2, 200)
		else: # if there isn't a 'sell monster' screen
			print "No monsters to be sold"
	elif sellMonsters == 'ask':
		test = raw_input("You should sell them now, restart by pressing enter right after selling them")
	elif sellMonsters == 'keep':
		pass
	tap(1070,1920/2,200) #to exit sell screen
	tap(1070,1920/2,200) #in case of level up screen
	tap(585,1300) # tap to okay helper or decline friend, this declines the friend every time
		

def runBattles(rounds = 10000):
	for round in xrange(rounds):
		img = getScreenshot()
		if checkDungeon(img):
			if tapOnImage(img,"OKEnd.png"): #put in game over condition
				sleep(10)
				for i in xrange(20):
					sleep(1)
					img = getScreenshot()
					if checkSell(img):
						return True
					else:
						tap(1070,1920/2,200)
				break
			else:
				while(True):
					try:
						a = oneBoardSolve.solveBoard(img,mode,movetime,confirm)
						if a:
							if mode == 'fast' or mode == 'fast_setup':
								raw_input('waiting')
							else:
								sleep(15)
						break
					except (KeyboardInterrupt):
						print "Keyboard Interrupt"
						return
					except:
						pass
		else:
			print "This doesn't seem to be a dungeon"
			exit()
			
def run(section,dungeon,floor,sell):
	#refineBounds()
	while True:
		img = getScreenshot()
		if checkDungeon(img):
			runBattles()
			sleep(2)
		elif checkHome(img):
			goToDungeonSection(section)
			goToDungeon(dungeon)
			goToFloor(floor)
			sleep(10)
			if runBattles():
				sellScreen(sell)
		elif checkSell(img):
			sellScreen(sell)
		else:
			print "I don't know where I am"
			exit()
		
def main():
	global confirm
	print "Welcome to PadSolver, this utility solves boards from Puzzle and Dragons, and then automatically does the solve on your phone."
	printMenu()
	while True:
		text = raw_input(">")
		if text == "help" or text == "Help":
			printMenu()
		if text == "select":
			refineBounds()
		try:
			if int(text) > 0:
				runBattles(int(text))
		except ValueError:
			pass
		if text == "0":
			run("special","Persona","Mementos-Int","keep")
		if text == "issues":
			printIssues()
		if text == "mode":
			changeMode()
		if text == "movetime":
			setMovetime()
		if text == "confirm":
			confirm = not confirm
			if confirm:
				print "Solver will now ask for confirmation"
			elif not confirm:
				print "Solver will no longer ask for confirmation"
			sleep(0.5)
		if text == "input":
			inputBoard()

if __name__ == "__main__":
	main()
		