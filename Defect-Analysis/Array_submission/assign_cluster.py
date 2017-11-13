import sys, getopt, os, errno, re, string
import Queue
from datetime import datetime, tzinfo
#import matplotlib.pyplot as plt
#import matplotlib.dates as mdates
import numpy as np
frameShift = 0
opts, args = getopt.getopt(sys.argv[1:], "i:o:p:s:")
for opt, arg in opts:
    if opt == '-i':
        inFile = arg
    elif opt == '-o':
        outDir = arg
    elif opt == '-p':
    	pbcFile = arg
    elif opt == '-s':
        frameShift = int(arg)
        
print "frameShift", frameShift
sys.stdout.flush()

cutoff = 2.5
min_cluster_size = 1
grid_size = 0.4
doCenterPercentage = False
doTrackDefectsTraj = False

output_top = open(outDir + 'TOP-LEAF-CLUSTERS.dat', "w")
output_bot = open(outDir + 'BOTTOM-LEAF-CLUSTERS.dat', "w")

input = open(inFile, "r")

total_points = 0
total_top_points = 0
total_bot_points = 0
top_point_count = 0
bottom_point_count = 0

topClustersNum = 0
botClustersNum = 0
prevTopClustersNum = 0
prevBotClustersNum = 0


count = 0
frame = 0



top_defects = np.zeros(1)
bot_defects = np.zeros(1)


if doCenterPercentage:
    output_top_suri = open(outDir + 'TOP-AREA.dat', "w")
    output_bot_suri = open(outDir + 'BOTTOM-AREA.dat', "w")


if doTrackDefectsTraj:
    lastTop = np.zeros(1)
    lastBot = np.zeros(1)
    output_top_tracking = open(outDir + 'TOP-TRACKING.dat', "w")
    output_bot_tracking = open(outDir + 'BOTTOM-TRACKING.dat', "w")


########### READ IN PBC FILE
pbcT, pbcX, pbcY  = np.loadtxt(pbcFile, comments=('#', '@')).T

#might need to convert from nm to angs
pbcInfo = [pbcT, pbcX*1.0, pbcY*1.0]

maxA = np.amax(pbcInfo[1])
maxB = np.amax(pbcInfo[2])

# dt of boxdim in terms of trajectory
dt = 1
pbcX = 0.0
pbcY = 0.0

minX = -1.0 * maxA / 2.0
minY = -1.0 * maxB / 2.0
maxX =  1.0 * maxA / 2.0
maxY =  1.0 * maxB / 2.0


output_top.write(" #Cluster     #     xPos     yPos     size     xmin     xmax     ymin     ymax\n" )
output_bot.write(" #Cluster     #     xPos     yPos     size     xmin     xmax     ymin     ymax\n" )

print 'beginning clustering'
#outTemp = open('test.dat', "w")
for line in input:
	split_line = line.split()
	if(len(split_line) == 3):
		#print split_line
		total_points = int(split_line[0])
		top_point_count = -1
		bottom_point_count = -1
		total_top_points = int(split_line[1])
		total_bot_points = int(split_line[2])
		#print total_top_points, total_bot_points
		top_defects = np.zeros((total_top_points, 2))
		bot_defects = np.zeros((total_bot_points, 2))
		count = 0
	elif (len(split_line) == 2):
		frame = int(split_line[1]) + frameShift
		index = (frame - 2)*dt
		#print 'frame', frame
		pbcX = pbcInfo[1][index]*1.0
		pbcY = pbcInfo[2][index]*1.0
		output_top.write("frame: %6d time: %.3f ns pbcX: %6.2f  pbcY: %6.2f\n" % (frame, pbcInfo[0][index] / 1000.0, pbcX, pbcY))
		output_bot.write("frame: %6d time: %.3f ns pbcX: %6.2f  pbcY: %6.2f\n" % (frame, pbcInfo[0][index] / 1000.0, pbcX, pbcY))



	else:
		count += 1
		if(split_line[0] == 'T'):
			top_point_count += 1
			top_defects[top_point_count][0] = split_line[1]
			top_defects[top_point_count][1] = split_line[2]
			
		elif(split_line[0] == 'B'):		
			bottom_point_count += 1
			bot_defects[bottom_point_count][0] = split_line[1]
			bot_defects[bottom_point_count][1] = split_line[2]
		
		if(total_points == count):
			#print "initializing arrays ..."
			
			
			###########################
			## FIRST DO TOP LEAFLET ###
			###########################
			
			###########################
			#Create adjacency matrix and distance matrix			
			adj_matrix = np.zeros((total_top_points, total_top_points), dtype=bool)
			dist_matrix = np.zeros((total_top_points, total_top_points))
			#print adj_matrix
			# evaluate all distances

			for i in range(total_top_points):
				for j in range(i+1, total_top_points):
					dx = (top_defects[i][0] - top_defects[j][0]) - pbcX*np.round((top_defects[i][0] - top_defects[j][0]) / pbcX)
					dy = (top_defects[i][1] - top_defects[j][1]) - pbcY*np.round((top_defects[i][1] - top_defects[j][1]) / pbcY)
					dist = 	np.sqrt( np.square(dx) +  np.square(dy))
					dist_matrix[i][j] = dist
					if dist < cutoff:
						adj_matrix[i][j] = True
						adj_matrix[j][i] = True

			###########################
			
			
						
			print 'frame ', frame, "\nassigning clusters in top "
			
			k = 0
			points_left = total_top_points
			
			# assign all points to not belong to a cluster
			clust_member = np.full(total_top_points,-1, dtype=np.int)
			
			######################
			# BUILD matrix for storing defects
			xval = np.arange(minX, maxX, grid_size)
			yval = np.arange(minY, maxY, grid_size)
			#print len(xval), len(yval)
			
			## NOTE X value is first index
			defect_location_matrix = np.full((len(xval), len(yval)), -1, dtype=np.int)
			########################
			
			
			while(points_left > 0):
				#print "points left:", points_left
				k += 1
				c_start = 0
				point_found = False
				i = 0
				pointsInCluster = Queue.Queue()
				numPointsInCluster = 0
				
				
				########################
				# Find next point to begin clustering
				while point_found == False:
					#print "finding clusters", i, clust_member[i]
					if(clust_member[i] < 0):
						c_start = i
						clust_member[i] = k
						points_left -= 1
						point_found = True
						pointsInCluster.put(i)
						numPointsInCluster += 1
					i += 1
				########################
				
				theQueue = Queue.Queue()
				
				########################
				# add adjacent points to the queue	
				for i in range(total_top_points):
					if adj_matrix[c_start][i] == True:
						theQueue.put(i)
						if clust_member[i] > 0:
							print "i:", i, clust_member[i]
							print c_start, dist_matrix[c_start][i]
							print clust_member
							raise NameError('point has already been clustered')
				########################
				
				
				########################
				# add adjacent points to the current cluster
				# Find adjacent points to the adjacent points, also add them to the queue
				# loop through until finished		
				while not theQueue.empty():
					curr = theQueue.get()
					
					#print curr
					
					# check to make sure current point has not been visited yet
					if clust_member[curr] < 0:
						#print "not yet a member"
						clust_member[curr] = k
						points_left -= 1
						pointsInCluster.put(curr)
						numPointsInCluster += 1
						
						# find neighbors of current point and add to the queue
						for i in range(total_top_points):
							if adj_matrix[curr][i] == True and clust_member[i] < 0:
								theQueue.put(i)
				########################
				
				########################
				#Acquire statistics about cluster
				#Add cluster to master grid
				xDefectVals = np.zeros(numPointsInCluster, dtype=np.float)
				yDefectVals = np.zeros(numPointsInCluster, dtype=np.float)
				i = 0
				numBins = 0
				#print k, numPointsInCluster
				while not pointsInCluster.empty():
					curr = pointsInCluster.get()
					defect = top_defects[curr]
					#print defect[0], defect[1]
					xDefectVals[i] = defect[0]
					yDefectVals[i] = defect[1]
					
					indexX = int( (defect[0] - minX)/ grid_size)
					indexY = int((defect[1] - minY) / grid_size)
					
					
					if defect_location_matrix[indexX][indexY] < 0:
						#print "in if"
						defect_location_matrix[indexX][indexY] = clust_member[curr]
						numBins += 1
					elif clust_member[curr] != defect_location_matrix[indexX][indexY]:
						print curr
						raise NameError('Point has already been added to this location. Consider increasing your grid_size')
					
					i += 1
				if (np.amax(xDefectVals)- np.amin(xDefectVals)) > pbcX / 2.0:
					for ind in range(len(xDefectVals)):
						if xDefectVals[ind] < 0:
							xDefectVals[ind] += pbcX
				if (np.amax(yDefectVals)- np.amin(yDefectVals)) > pbcY / 2.0:
					for ind in range(len(yDefectVals)):
						if yDefectVals[ind] < 0:
							yDefectVals[ind] += pbcY					
				xMinDef = np.amin(xDefectVals)
				xMaxDef = np.amax(xDefectVals)
				yMinDef = np.amin(yDefectVals)
				yMaxDef = np.amax(yDefectVals)  
				output_top.write("Cluster %2d %8.3f %8.3f %8.3f %8.3f %8.3f %8.3f %8.3f\n" % 
						(k, np.mean(xDefectVals), np.mean(yDefectVals), numBins * np.square(grid_size), 
							xMinDef, xMaxDef + grid_size, yMinDef, yMaxDef + grid_size))
				
			########################################################################

			top_matrix = defect_location_matrix
			topClustersNum = k
			
			###########################
			## Next Do Bottom LEAFLET #
			###########################
			
			###########################
			#Create adjacency matrix and distance matrix			
			adj_matrix = np.zeros((total_bot_points, total_bot_points), dtype=bool)
			dist_matrix = np.zeros((total_bot_points, total_bot_points))
			#print adj_matrix
			# evaluate all distances
			for i in range(total_bot_points):
				for j in range(i+1, total_bot_points):
					dx = (bot_defects[i][0] - bot_defects[j][0]) - pbcX*np.round((bot_defects[i][0] - bot_defects[j][0]) / pbcX)
					dy = (bot_defects[i][1] - bot_defects[j][1]) - pbcY*np.round((bot_defects[i][1] - bot_defects[j][1]) / pbcY)
					dist = 	np.sqrt( np.square(dx) +  np.square(dy))
					if dist < cutoff:
						adj_matrix[i][j] = True
						adj_matrix[j][i] = True
			###########################
			
			
						
			print "assigning clusters in bottom \n",
			
			k = 0
			points_left = total_bot_points
			
			# assign all points to not belong to a cluster
			clust_member = np.full(total_bot_points,-1, dtype=np.int)
			
			######################
			# BUILD matrix for storing defects
			xval = np.arange(minX, maxX, grid_size)
			yval = np.arange(minY, maxY, grid_size)
			#print len(xval), len(yval)
			
			## NOTE X value is first index
			defect_location_matrix = np.full((len(xval), len(yval)), -1, dtype=np.int)
			########################
			
			
			while(points_left > 0):
				#print "points left:", points_left
				k += 1
				c_start = 0
				point_found = False
				i = 0
				pointsInCluster = Queue.Queue()
				numPointsInCluster = 0
				
				
				########################
				# Find next point to begin clustering
				while point_found == False:
					#print "finding clusters", i, clust_member[i]
					if(clust_member[i] < 0):
						c_start = i
						clust_member[i] = k
						points_left -= 1
						point_found = True
						pointsInCluster.put(i)
						numPointsInCluster += 1
					i += 1
				########################
				
				theQueue = Queue.Queue()
				
				########################
				# add adjacent points to the queue	
				for i in range(total_bot_points):
					if adj_matrix[c_start][i] == True:
						theQueue.put(i)
						if clust_member[i] > 0:
							print "i:", i, clust_member[i]
							print c_start, dist_matrix[c_start][i]
							print clust_member
							raise NameError('point has already been clustered')
				########################
				
				
				########################
				# add adjacent points to the current cluster
				# Find adjacent points to the adjacent points, also add them to the queue
				# loop through until finished		
				while not theQueue.empty():
					curr = theQueue.get()
					
					#print curr
					
					# check to make sure current point has not been visited yet
					if clust_member[curr] < 0:
						#print "not yet a member"
						clust_member[curr] = k
						points_left -= 1
						pointsInCluster.put(curr)
						numPointsInCluster += 1
						
						# find neighbors of current point and add to the queue
						for i in range(total_bot_points):
							if adj_matrix[curr][i] == True and clust_member[i] < 0:
								theQueue.put(i)
				########################
				
				########################
				#Acquire statistics about cluster
				#Add cluster to master grid
				xDefectVals = np.zeros(numPointsInCluster, dtype=np.float)
				yDefectVals = np.zeros(numPointsInCluster, dtype=np.float)
				i = 0
				numBins = 0
				#print k, numPointsInCluster
				while not pointsInCluster.empty():
					curr = pointsInCluster.get()
					defect = bot_defects[curr]
					xDefectVals[i] = defect[0]
					yDefectVals[i] = defect[1]
					
					
					indexX = int( (defect[0] - minX)/ grid_size)
					indexY = int((defect[1] - minY) / grid_size)
					
					
					if defect_location_matrix[indexX][indexY] < 0:
						#print "in if"
						defect_location_matrix[indexX][indexY] = clust_member[curr]
						numBins += 1
					elif clust_member[curr] != defect_location_matrix[indexX][indexY]:
						print curr
						raise NameError('Point has already been added to this location. Consider increasing your grid_size')
					
					i += 1
				if (np.amax(xDefectVals)- np.amin(xDefectVals)) > pbcX / 2.0:
					for ind in range(len(xDefectVals)):
						if xDefectVals[ind] < 0:
							xDefectVals[ind] += pbcX
				if (np.amax(yDefectVals)- np.amin(yDefectVals)) > pbcY / 2.0:
					for ind in range(len(yDefectVals)):
						if yDefectVals[ind] < 0:
							yDefectVals[ind] += pbcY						
				xMinDef = np.amin(xDefectVals)
				xMaxDef = np.amax(xDefectVals)
				yMinDef = np.amin(yDefectVals)
				yMaxDef = np.amax(yDefectVals)  
				output_bot.write("Cluster %2d %8.3f %8.3f %8.3f %8.3f %8.3f %8.3f %8.3f\n" % 
						(k, np.mean(xDefectVals), np.mean(yDefectVals), numBins * np.square(grid_size), 
							xMinDef, xMaxDef + grid_size, yMinDef, yMaxDef + grid_size))
				
				########################################################################
			
			bottom_matrix = defect_location_matrix			
			botClustersNum = k	
			
			
			
			########################################################################	
			if doCenterPercentage:
				min = (len(xval) / 2 ) - 50
				max = (len(xval) / 2 ) + 50
				#print min, max, xval[min], xval[max]
				numTop = 0.0
				numBot = 0.0
				numTot = 0.0
				for i in range(min, max):
					for j in range(min, max):
						#print i, j, bottom_matrix[i][j], top_matrix[i][j]
						if bottom_matrix[i][j] > 0:
							numBot += 1.0
						if top_matrix[i][j] > 0:
							numTop += 1.0
						numTot += 1.0
				output_top_suri.write("%s %.6f \n" % (frame, numTop / numTot))
				output_bot_suri.write("%s %.6f \n" % (frame, numBot / numTot))
			
			
			
			########################################################################	
			if doTrackDefectsTraj and prevTopClustersNum > 0 and prevBotClustersNum > 0:
				output_top_tracking.write("frame %s\n" % frame)
				output_bot_tracking.write("frame %s\n" % frame)
				botClusters = np.zeros((botClustersNum + 1, prevBotClustersNum + 1), dtype=bool)
				topClusters = np.zeros((topClustersNum + 1, prevTopClustersNum + 1), dtype=bool)
				
				for i in range(len(xval)):
					for j in range(len(yval)):
						if top_matrix[i][j] > 0 and lastTop[i][j] > 0:
							topClusters[  top_matrix[i][j]  ][  lastTop[i][j]  ] = True
						if bottom_matrix[i][j] > 0 and lastBot[i][j] > 0:
							botClusters[  bottom_matrix[i][j]  ][  lastBot[i][j]  ] = True
				#print botClusters
				#print topClusters
				for i in range(len(topClusters)):
					for j in range(len(topClusters[0])):
						if topClusters[i][j]:
							output_top_tracking.write("Match %d %d\n" % (i, j))
				for i in range(len(botClusters)):
					for j in range(len(botClusters[0])):		
						if botClusters[i][j]:
							output_bot_tracking.write("Match %d %d\n" % (i, j))	
			
			
			lastTop = top_matrix
			lastBot = bottom_matrix			
			prevTopClustersNum = topClustersNum
			prevBotClustersNum = botClustersNum
						

output_top.close()
output_bot.close()
if doCenterPercentage:
    output_top_suri.close()
    output_bot_suri.close() 


if doTrackDefectsTraj:
    output_top_tracking.close()
    output_bot_tracking.close()

