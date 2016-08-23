# coding=UTF-8
#CRON
########################################################################
#Imports
import os
import glob
import HIDS
import time
import chrono
import mailUtil
from progressbar import AnimatedMarker, Bar, BouncingBar, Counter, ETA, \
                        FileTransferSpeed, FormatLabel, Percentage, \
                        ProgressBar, ReverseBar, RotatingMarker, \
                        SimpleProgress, Timer
########################################################################
debug = True

def fastScan(path=os.getcwd()+"/wordpress/"):
	HIDS.bddConnect()
	t0 = chrono.start()
	status = "Failed"
	#Cette fonction renvoie le répertoire d'exectution du fichier du CRON
	files = HIDS.listdirectory(path)
	fileSize = len(files)
	storedHashData = HIDS.getLastMasterReleaseHash()
	hashArray = []
	iterator = 100/fileSize
	timeNow = chrono.getTime()
	widgets = ['Traitement: ', Percentage(), ' ', Bar(marker=RotatingMarker()),' ', ETA(), ' ']
	pbar = ProgressBar(widgets=widgets, maxval=fileSize).start()
	for i in range(fileSize) :
		ressourceName = files[i]
		data = HIDS.openFile(ressourceName)
		encodedData = HIDS.hashData(data)
		hashArray.append(encodedData)
		pbar.update(i+iterator)
	pbar.finish()
	duration = chrono.stop(t0)
	releaseHash = HIDS.hashData(''.join(hashArray))
	if(HIDS.compareHashToHash(releaseHash,storedHashData)):
			status = "Success"
	else:
		contacts = HIDS.getAdminMails()
		mailUtil.mailScanFailed(contacts)
	print("Status :"+status)
	HIDS.addNewScan(timeNow,'fast',fileSize,releaseHash,duration,status)
	if(status=='Failed'):
		print("Deep scan will start soon...")
		deepScan()

def deepScan(path=os.getcwd()+"/wordpress/"):
	HIDS.bddConnect()
	t0 = chrono.start()
	status = "Failed"
	#Cette fonction renvoie le répertoire d'exectution du fichier du CRON
	files = HIDS.listdirectory(path)
	fileSize = len(files)
	storedHashData = HIDS.getLastMasterReleaseHash()
	hashArray = []
	corruptedFiles = []
	iterator = 100/fileSize
	timeNow = chrono.getTime()
	widgets = ['Traitement: ', Percentage(), ' ', Bar(marker=RotatingMarker()),' ', ETA(), ' ']
	pbar = ProgressBar(widgets=widgets, maxval=fileSize).start()
	for i in range(fileSize) :
		ressourceName = files[i]
		data = HIDS.openFile(ressourceName)
		encodedData = HIDS.hashData(data)
		remoteData = HIDS.getHashByRessourceName(ressourceName)
		result = HIDS.compareHashToHash(encodedData,remoteData)
		if(result != True):
			data = '{ressourceName : '+ressourceName+' actual : '+encodedData+' expected : '+remoteData+' }'
			corruptedFiles.append(data)
		pbar.update(i+iterator)
	pbar.finish()
	releaseHash = HIDS.hashData(''.join(hashArray))
	duration = chrono.stop(t0)
	HIDS.addNewScan(timeNow,'deep',fileSize,releaseHash,duration,status)
	contacts = HIDS.getAdminMails()
	mailUtil.mailDeepScan(contacts,corruptedFiles)



