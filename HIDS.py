# coding=UTF-8
#HIDS
########################################################################
#Imports
import pymongo
import os
import glob
import hashlib
import CRON
import chrono
import mailUtil
import time
#import progressbar
from progressbar import AnimatedMarker, Bar, BouncingBar, Counter, ETA, \
                        FileTransferSpeed, FormatLabel, Percentage, \
                        ProgressBar, ReverseBar, RotatingMarker, \
                        SimpleProgress, Timer

########################################################################
MONGODB_URI = 'mongodb://hids:hids@ds039291.mongolab.com:39291/tp_secu'
########################################################################
# Fonctions
debug = True

def initiateBDD():
	db = bddConnect()
	cleanBase()
	initiateSources()
	iniateWordpressBDD()


#Fonction pour se connecter à la BDD en local
def bddConnect(tries=3):
	from pymongo import MongoClient
	myDB = None
	try:
		client = MongoClient(MONGODB_URI)	
		myDB = client.tp_secu
	except pymongo.errors.ConnectionFailure:
		bddReconnect(tries)
	finally:
		return myDB

def bddReconnect(tries):
	print tries
	if(tries==0):
		print("Abandon")
		exit()
	print("Connection failed")
	time.sleep(10)
	print("Tentative de reconnexion")
	bddConnect()
	tries-=1
	return tries

#Se connecter à la base MySQL de wordpress
def sqlConnect():
	db = MySQLdb.connect("machine", "dbuser", "password", "dbname")

#Passer une requête afin de récuperer les données
def sqlRetrieveWorpressData():
	cursor = db.cursor()
	query = """SELECT post_title FROM i4_posts p 
	JOIN i4_term_relationships r ON r.object_id = p.ID 
	JOIN i4_term_taxonomy t ON r.term_taxonomy_id = t.term_taxonomy_id 
	JOIN i4_terms terms ON terms.term_id = t.term_id
	WHERE t.taxonomy ='category'
	AND terms.name = 'procedure'
	AND p.post_type = 'post';"""
	lines = cursor.execute(query)
	data = cursor.fetchall()
	db.close()


#ajoute une nouvelle ressource en base 
def addNewHashedRessource(collectionName,ressourceName,hashedDataToStore,database,dateHash):
	target = database[collectionName]
	format = {"ressourceName":ressourceName,"dateHash":dateHash,"hash":hashedDataToStore}
	posted = target.insert(format)


def addNewMasterRelease(releaseDate,releaseHash):
	format = {"releaseDate": releaseDate,"releaseHash":releaseHash}
	db = bddConnect()
	target = getAdminMails()
	posted = db.master.insert(format)
	try:
		mailUtil.mailNewMasterRealease(target)
	except socket_error as serr:
	    if serr.errno != errno.ECONNREFUSED:
	        # Not the error we are looking for, re-raise
	        raise serr
	    print("Connexion impossible au serveur de mail")

def addNewAdmin(adminName,mail,phone,status="valide"):
	format = {"adminName":adminName,"mail":mail,"phone":phone,"created":chrono.getTime(),"valide":status}
	db = bddConnect()
	target = db.adminDirectory
	posted = target.insert(format)

def addNewScan(scanDate,scanType,files,releaseHash,duration,status):
	format = {"scanDate":scanDate,"type":scanType,"files":files,"hash":releaseHash,"duration":duration,"status":status}
	db = bddConnect()
	target = db.scans
	posted = target.insert(format)

#Fonction qui va taper en base afin de récuperer la ressource en base via son nom de ressource 
def getRessourceByRessourceName(ressourceName):
	db = bddConnect()
	format = {"ressourceName": ressourceName}
	hashedRessource = db.hids_sources.find_one(format)
	return hashedRessource

#Fonction qui va taper en base afin de récuperer la ressource en base via son nom de ressource 
def getHashByRessourceName(ressourceName):
	db = bddConnect()
	format = {"ressourceName": ressourceName}
	hashedRessource = db.hids_sources.find_one(format)
	hashString = str(hashedRessource.get('hash'))
	return hashString

#Fonction qui récupère les mails des admins en base
def getAdminMails():
	db = bddConnect()
	mails=[]
	for admin in db.adminDirectory.find({"valide":"valide"},{'mail':True,'_id':False}):
		mailAddress = str(admin.get('mail'))
		mails.append(mailAddress)
	return mails
	
def getLastMasterReleaseHash():
	db = bddConnect()
	masterRelease = db.master.find({}).sort('_id',-1);
	masterHash = str(masterRelease[0].get('releaseHash'))
	return masterHash

#Fonction qui va taper en base afin de récuperer la ressource hashée en base via son Id
def getHashByRessourceId(ressourceId):
	db = bddConnect()
	format = {'_id' : ObjectId(ressourceId)}
	document = db.collection.find_one(format)
	return document

#Fonction basique de hash en sha1, testée 
def hashData(data):
	hash_object = hashlib.sha1(data)
	hex_dig = hash_object.hexdigest()
	return hex_dig

#compare une data à une hashedData
def compareToHash(data, hashedData):
    newDataHashed = hashData(data)
    return newDataHashed == hashedData

#renvoit un booleen suivant le resultat de l'operation
def compareHashToHash(hashedOne,hashedTwo):
 	return hashedOne == hashedTwo


#retourne la liste des fichiers de manière récursive dans un repertoire
def listdirectory(path):  
    fichiers=[]  
    for root, dirs, files in os.walk(path):  
        for i in files:  
            fichiers.append(os.path.join(root, i))  
    return fichiers

#ouvre un fichier afin de récupérer son contenu
def openFile(path):
	myFile = open(path,'r')
	data = myFile.read()
	return data

#vide les collections utilisées dans la base afin de faire un nouvel import
def cleanBase():
	if(debug):
		t0 = chrono.start()
	db = bddConnect()
	db.drop_collection('hids_sources')
	db.drop_collection('hids_wordpress')
	db.drop_collection('scans')
	db.drop_collection('master')
	#db.drop_collection('adminDirectory')
	if(debug):
		chrono.stop(t0)


#Fonction qui fait hydrate la BDD
def initiateSources(sourcePath=os.getcwd()+"/wordpress/"):
	
	if(debug):
		t0 = chrono.start()
	files = listdirectory(sourcePath)
	fileSize = len(files)
	iterator = 100/fileSize
	if(debug):
		print fileSize,"fichiers à traiter"
	hashArray = []
	database = bddConnect()
	database.drop_collection('hids_sources')
	hashDate = chrono.getTime()
	#initiate la barre
	widgets = ['Traitement: ', Percentage(), ' ', Bar(marker=RotatingMarker()),' ', ETA(), ' ']
	pbar = ProgressBar(widgets=widgets, maxval=fileSize).start()
	for i in range(fileSize) :
		data = openFile(files[i])
		encodedData = hashData(data)
		varFile = files[i]
		hashArray.append(encodedData)
		addNewHashedRessource("hids_sources",varFile,encodedData,database,hashDate)
		pbar.update(i+iterator)
	pbar.finish()
	releaseHash = hashData(''.join(hashArray))

	if(debug):
		print fileSize,"fichiers traités avec succès"
		chrono.stop(t0)
	return releaseHash

def initiateMasterRelease():
	releaseDate = chrono.getTime()
	releaseHash = initiateSources()
	addNewMasterRelease(releaseDate,releaseHash)


def iniateWordpressBDD():
	#se connecter à la base de donnée Wordpress
	#recuperer toutes les infos
	#inserer en base
	for x in xrange(1,10):
		ressourceName = ''
		encodedData = ''
		addNewHashedRessource("hids_worpress",ressourceName,encodedData)


