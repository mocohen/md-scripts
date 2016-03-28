import sys, getopt, os, errno, re, string
import numpy as np
import sqlite3

opts, args = getopt.getopt(sys.argv[1:], "i:j:o:p:m:r:")
for opt, arg in opts:
    if opt == '-i':
        inFile = arg
    elif opt == '-j':
        defectDescriptionFile = arg
    elif opt == '-o':
        dbFile = arg
    elif opt == '-p':
        prot = arg
    elif opt == '-m':
        membraneType = arg
    elif opt == '-r':
        runNumber = arg

# OPEN DB CONNECTION
conn = sqlite3.connect(dbFile)
c = conn.cursor()
# CREATE TABLES
c.execute('''CREATE TABLE IF NOT EXISTS DEFECT_CLUSTERS( 	Id INTEGER PRIMARY KEY AUTOINCREMENT,
											Defect_Frame_id INT, 
											timestep REAL, 
											X_pos REAL,
											X_min REAL,
											X_max REAL, 
											Y_pos REAL,
											Y_min REAL,
											Y_max REAL, 
											Size REAL,
                                            systemID INT)''')
c.execute('''CREATE TABLE IF NOT EXISTS DEFECT_MATCHES( 	Id INTEGER PRIMARY KEY AUTOINCREMENT, 
											Prev_id INT, 
											Curr_id INT)''')


if not inFile:
    raise('Usage: python track_defects.py -i inputFile -j defectDescriptionFile -o outputFile')
input = open(inFile, "r")

if not defectDescriptionFile:
    raise('Usage: python track_defects.py -i inputFile -j defectDescriptionFile -o outputFile')
defectInput = open(defectDescriptionFile, 'r')


c.execute('''SELECT key FROM Systems where membraneType=? and protein=?
                         and runNumber=?''', (membraneType,  prot, runNumber))


key = c.fetchone()[0]

			



print 'Beginning Tracking'
#allDefects = []
defects = {}
currentFrame = 0
currentTime = 0.0
frameIndex = -1

for line in defectInput:
    if re.match(r'Cluster', line):
        splitLine = line.split()
        # retreive all values
        clusterIndex = int(splitLine[1])
        x = float(splitLine[2])
        y = float(splitLine[3])
        size = float(splitLine[4])
        xmin = float(splitLine[5])
        xmax = float(splitLine[6])
        ymin = float(splitLine[7])
        ymax = float(splitLine[8])
        #print 'index %d size %f' % (clusterIndex, size)
        #allDefects.append([clusterIndex ,currentFrame, x, y, size])
        c.execute('INSERT INTO DEFECT_CLUSTERS (Defect_Frame_id, timestep, X_pos, Y_pos, X_min, X_max, Y_min, Y_max, Size, systemID) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', 
    		[clusterIndex , currentTime, x, y, xmin, xmax, ymin, ymax, size, key])
        # store defect in defects dictionary for later reference
        defects[(currentFrame, clusterIndex)] = c.lastrowid

    elif re.match(r'frame', line):	
        currentFrame = int(line.split()[1])
        currentTime = float(line.split()[3])
        #print 'frame', currentFrame
        frameIndex += 1


defectMatches = []

match_index = 0

frameNumber = 0
print 'Reading matching file...'
for line in input:
    if re.match(r'Match', line):
        splitLine = line.split()
        current = int(splitLine[1])
        previous = int(splitLine[2])
        prev = defects[(int(frameNumber) - 1, previous)]
        curr = defects[(int(frameNumber), current)]
        defectMatches.append([prev, curr]) 		
    elif re.match(r'frame', line):
        frameNumber = line.split()[1]



c.executemany('INSERT INTO DEFECT_MATCHES (Prev_id, Curr_id) VALUES(?, ?)', defectMatches)
print c.fetchone()
conn.commit()
conn.close()

