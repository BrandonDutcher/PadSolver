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


def printMenu():
	print ""
	print "# > 0: solve # of boards (until end)"
	print "0: solve until end of dungeon"
	print "select: select cropped image"
	print "config: configure what the solver does"
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
	print "------------------------------------------------------------"
	print ""

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
						if oneBoardSolve.solveBoard(img):
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
	print "Welcome to PadSolver, this utility solves boards from Puzzle and Dragons, and then automatically does the solve on your phone."
	while True:
		printMenu()
		text = raw_input(">")
		if text == "select":
			refineBounds()
		try:
			if int(text) > 0:
				runBattles(int(text))
		except ValueError:
			pass
		if text == "0":
			run("technical","newest","newest","sell")
		if text == "issues":
			printIssues()

if __name__ == "__main__":
	main()
		