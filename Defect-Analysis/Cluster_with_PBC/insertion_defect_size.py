import sys, getopt, os, errno, re, string
import Queue
from datetime import datetime, tzinfo
#import matplotlib.pyplot as plt
#import matplotlib.dates as mdates
import numpy as np

opts, args = getopt.getopt(sys.argv[1:], "c:d:r:o:")
for opt, arg in opts:
    if opt == '-c':
        clusterFile = arg
    elif opt == '-d':
        distanceDir = arg
    elif opt == '-r':
        residueNumb = int(arg)
    elif opt == '-o':
        outFile = arg
        
#ind 0 - time
#ind 1-6: protein pos
#we will average top and bottom x + y distances

#residue 1 - ind 7,8 10,11
#residue 2 - ind 13
residueIndex = residueNumb + 1

threshold = 7.5

def isWithin(point, theMin, theMax, center, pbc):
    shift = np.round((center - point) / pbc)
    if shift != 0:
        point += pbc
    if theMax + threshold > point and theMin - threshold < point:
        return True
    else:
        return False

def rect1Distance(point, theMin, theMax, center, pbc):
    shift = np.round((center - point) / pbc)
    if shift != 0:
        point += pbc
    return np.amax((theMin - point, 0, point - theMax))    

def rect2Distance(resX, resY, x, y, size, xmin, xmax, ymin, ymax, pbcX, pbcY):
    dx = rect1Distance(resX, xmin, xmax, x, pbcX)
    dy = rect1Distance(resY, ymin, ymax, y, pbcY)
    return np.sqrt(np.square(dx) + np.square(dy))


xData = np.loadtxt(distanceDir + '.x.dat', comments=('@', '#'), usecols=(residueIndex,))
yData = np.loadtxt(distanceDir + '.y.dat', comments=('@', '#'), usecols=(residueIndex,))
resPos = np.zeros((len(xData), 2))

residueIndex = 0
i = 0
for row in range(len(xData)):
    # don't forget to convert to angs
    resPos[i][0] = 1.0*(xData[row])
    resPos[i][1] = 1.0*(yData[row])
    i += 1

distanceData = []

currentFrame = 0
currentTime = 0.0
frameIndex = -1

resX = 0.0
resY = 0.0
pbcX = 0.0
pbcY = 0.0

defectSizes = np.zeros(len(resPos))
closestDefect = ()

input = open(clusterFile, 'r')
for line in input:
    if not '#' in line:
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
            if isWithin(resX, xmin, xmax, x, pbcX) & isWithin(resY, ymin, ymax, y, pbcY):

                if len(closestDefect) > 0:
                    oldDist = rect2Distance(*closestDefect[0:12]) 
                    newDist = rect2Distance(resX, resY, x, y, size, xmin, xmax, ymin, ymax, pbcX, pbcY)
                    if oldDist > newDist:
                        closestDefect = (resX, resY, x, y, size, xmin, xmax, ymin, ymax, pbcX, pbcY)
                        defectSizes[frameIndex] = size
                else:
                    closestDefect = (resX, resY, x, y, size, xmin, xmax, ymin, ymax, pbcX, pbcY)
                    defectSizes[frameIndex] = size
        elif re.match(r'frame', line):	
            splitLine = line.split()
            currentFrame = int(splitLine[1])
            currentTime = float(splitLine[3])
            pbcX = float(splitLine[6])
            pbcY = float(splitLine[8])
            #print 'frame', currentFrame
            frameIndex += 1
            closestDefect = ()
            if frameIndex >= len(resPos):
                print 'break'
                break
            resX = resPos[frameIndex][0]
            resY = resPos[frameIndex][1]

output = open(outFile, 'w')

for i in range(len(defectSizes)):
    output.write("%d %.3f\n" % (i, defectSizes[i]))
output.close()