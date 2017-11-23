import pyautogui as pg
from time import sleep

while(True):
	x, y = pg.position()
	positionStr = 'X: ' + str(x) + ' Y: ' + str(y)
	print positionStr
	sleep(1)