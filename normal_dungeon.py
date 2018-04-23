#!aoensuhatnsoeh

from time import sleep
from time import time
import FastPhoneSort
import numpy as np
import unicodedata
import pytesseract
import subprocess
import cv2


def tap(x, y, duration=50):
	subprocess.call('adb shell input touchscreen swipe {} {} {} {} {}'.format(str(x),str(y),str(x),str(y),str(duration)),shell=True)
def swipe(x1, y1, x2, y2, duration=300):
	subprocess.call('adb shell input touchscreen swipe {} {} {} {} {}'.format(str(x1),str(y1),str(x2),str(y2),str(duration)),shell=True)
	
def tapOnImage(img, button, occurence):
	loc = np.where(cv2.matchTemplate(img,cv2.imread('assets/{}'.format(button),0),cv2.TM_CCOEFF_NORMED) > 0.98)
	if len(loc[0]) > 0:
		tap(loc[1][occurence],loc[0][occurence])
		print loc[1][occurence],loc[0][occurence]
		return True
	return False
	
def refineBounds(img):
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
		
def checkDungeon(img):
	menu = cv2.imread('assets/Menu.png',0)
	if np.amax(cv2.matchTemplate(img[75:110,930:],menu,cv2.TM_CCOEFF_NORMED)) > 0.96:
		return True
		
def checkStamina(img):
	text = pytesseract.image_to_string(img[243:290,500:664])
	a = str(text).split("/")
	return int(a[0])
	
def getTab(img):
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
	tapOnImage(img,'DungeonsScreen/{}.png'.format(name),0)
	
def goToDungeon(name):
	if name == 'newest':
		swipe(1040, 1600, 1040, 400)
		tap(540, 500)
		sleep(1)
		img = getScreenshot()
		tapOnImage(img,"battles.png",0)
		tap(540, 500)
		sleep(1)
		tap(540, 1100)
		sleep(1)
		tap(540, 1570)
		
def runBattles():
	while(True):
		img = getScreenshot()
		if tapOnImage(img,"OKEnd.png",0): #put in game over condition
			sleep(10)
			for i in xrange(20):
				tap(1070,1920/2, 200)
			tap(585,1300)
			sleep(2)
			break
		else:
			while(True):
				try:
					if FastPhoneSort.solveBoard(img):
						sleep(12)
						break
				except (KeyboardInterrupt):
					exit()
				except:
					pass
def main():
	for i in xrange(20):
		img = getScreenshot()
		#refineBounds(img)
		if checkDungeon(img):
			runBattles()
			sleep(2)
		elif checkHome(img):
			goToDungeonSection('normal')
			goToDungeon('newest')
			sleep(10)
			runBattles()
		
if __name__ == "__main__":
	main()
		