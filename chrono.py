# coding=UTF-8
import time
def start():
	start = time.time()
	return start;

def stop(startTime):
	stopTime = time.time()
	result = stopTime - startTime
	return chronoCalc(result)
	
def getTime():
	return time.strftime("%d/%m/%Y %H:%M:%S")

def chronoCalc(timer):
	strTimer = str(timer)
	timer = int(timer)
	hours = timer/3600
	minsLeft=timer%3600
	mins = minsLeft/60
	secsLeft=minsLeft%60
	#récupère les millièmes de secondes
	milliSec = strTimer.split('.')[1][0:3]
	varTime = "Temps execution :",hours,"h",mins,"min",secsLeft,"secondes",milliSec,"ms"
	return varTime
