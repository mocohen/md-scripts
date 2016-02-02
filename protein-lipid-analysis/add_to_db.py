import sys, getopt, os, errno, re, string
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

c.execute('''CREATE TABLE IF NOT EXISTS proteinPositions 
			(key 		INTEGER PRIMARY KEY,
			systemID   	INTEGER,
			timestep	real,
			distance 	real,
			resNum		real)''')

conn.commit()




dat = np.loadtxt(inFile, comments=('#', '@'))

numRes = ((len(dat[0]) - 1) / (2*3)) - 1

timeVals = np.zeros(len(dat))
resPosZ = np.zeros((numRes,len(dat)))


systemInfo = (membraneType, "POPC:DOPE:SAPI", "65:27:8", prot, runNumber)

c.execute('INSERT INTO Systems (membraneType, lipidType, lipidComposition, protein, runNumber) VALUES (?,?,?,?,?)', systemInfo)

c.execute('SELECT key FROM Systems where membraneType=? and protein=? and runNumber=?', (membraneType,  prot, runNumber))

print c.fetchone()

exit()

c.executemany('INSERT INTO Users (name, machine, date, usage) VALUES (?,?,?,?)', userInfo)

for i in range(len(dat)):
	#First get time at frame
	timeVals[i] = dat[i][0] / 1000.0
	
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
		resPosZ[j][i] = 10*sign*dat[i][index]
# 		if j == 0 and i % 1000 == 0:
# 	


for line in input:
	#print line
	
	# Check if beginning of a machine
	if 'Resource' in line:
		currentMachine = -1
		
		# loop through list of machines to find current machine
		i = 0
		for machine in machines:
			if machine in line:
				currentMachine = i
				isFirst = True
			i += 1
	
	# All User information contains SU in line
	if currentMachine >= 0 and 'SU' in line:
		split = line.strip().split()
		
		# 0      1      2      3   4          5   6          7
		# lName, fName, Alloc, SU, Remaining, SU, userUsage, SU
		
		
		#Check to make sure current year's allocation
		if split[2] == initial[currentMachine]:
			userInfo.append(( "%s %s" % (split[1], split[0]), machines[currentMachine], dateString, int(split[6])))
			
			if isFirst == True:
				isFirst = False
				totalRemaining += int(split[4])
				machineInfo.append((machines[currentMachine], dateString, int(split[4])))

machineInfo.append((machines[5], dateString, totalRemaining))
#print machineInfo

c.executemany('INSERT INTO Machines (machine, date, remainingSU) VALUES (?,?,?)', machineInfo)
c.executemany('INSERT INTO Users (name, machine, date, usage) VALUES (?,?,?,?)', userInfo)