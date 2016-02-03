import sys, getopt, os, errno, re, string
import numpy as np

from datetime import datetime, tzinfo
import sqlite3

opts, args = getopt.getopt(sys.argv[1:], "d:i:p:m:r:")
for opt, arg in opts:
    if opt == '-d':
    	dbFile = arg
    elif opt == '-i':
    	inFile = arg
    elif opt == '-p':
    	prot = arg
    elif opt == '-m':
    	membraneType = arg
    elif opt == '-r':
    	runNumber = arg

resNumOffset = 0

if 'alps' in prot:
	resNumOffset = 1

if 'M' in prot:
	resNumOffset = 1
if 'p2' in prot:
	resNumOffset = 27

dateStringFormat = "%Y-%m-%d %H:%M:%S.000"

existsdbFile = False
if os.path.isfile(dbFile):
	existsdbFile = True
	
conn= sqlite3.connect(dbFile)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS Systems 
			(key 				INTEGER PRIMARY KEY,
			membraneType 		TEXT,
			lipidType			TEXT,
			lipidComposition 	TEXT,
			protein				TEXT,
			runNumber			INTEGER)''')

c.execute('''CREATE TABLE IF NOT EXISTS ProteinPositions 
			(key 		INTEGER PRIMARY KEY,
			systemID   	INTEGER,
			timestep	real,
			distance 	real,
			resNum		INTEGER)''')

conn.commit()




dat = np.loadtxt(inFile, comments=('#', '@'))

numRes = ((len(dat[0]) - 1) / (2*3)) - 1

timeVals = np.zeros(len(dat))
resPosZ = np.zeros((numRes,len(dat)))


systemInfo = (membraneType, "POPC:DOPE:SAPI", "65:27:8", prot, runNumber)

c.execute('''INSERT INTO Systems (membraneType, lipidType, lipidComposition, protein, runNumber) 
				VALUES (?,?,?,?,?)''', systemInfo)

c.execute('''SELECT key FROM Systems where membraneType=? and protein=?
			 and runNumber=?''', (membraneType,  prot, runNumber))


key = c.fetchone()[0]

resPosDB = []

for i in range(len(dat)):
	#First get time at frame
	timeFrame = dat[i][0] / 1000.0
	timeVals[i] = timeFrame
	print timeFrame	
	first = False
	#check if first closer
	if(-1.0*dat[i][3] < dat[i][6]):
		first = True
	
	for j in range(numRes):
		index = 0
		sign = 1.0
		indexA = (j*6) + 9
		indexB = (j*6) + 12
		if -1.0*dat[i][indexA] < dat[i][indexB]:
			index = indexA
			sign = -1.0
		else:
			index = indexB
			sign = 1.0
		# switch to angs from gromacs units (nm)
		pos = 10*sign*dat[i][index]
		resPosZ[j][i] = pos
		resPosDB.append((key, timeFrame, pos, j+resNumOffset ))


c.executemany(''' INSERT INTO ProteinPositions (systemID, timestep, distance, resNum) VALUES (?,?,?,?)''',
					resPosDB)	
conn.commit()

conn.close()
exit()
