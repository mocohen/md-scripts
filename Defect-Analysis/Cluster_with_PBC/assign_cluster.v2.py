import sys, getopt, os, errno, re, string
import Queue
from datetime import datetime, tzinfo
import numpy as np


# get adjacency matrix and distance matrix for list of defects with PBC
def get_adjacency_matrix(defects_list, pbcX, pbcY, cutoff):
    total_points = len(defects_list)

    adj_matrix = np.zeros((total_points, total_points), dtype=bool)
    dist_matrix = np.zeros((total_points, total_points))

    for i in range(total_top_points):
        for j in range(i+1, total_top_points):

            # get shortest periodic distance
            dx = (defects_list[i][0] - defects_list[j][0]) - pbcX*np.round((defects_list[i][0] - defects_list[j][0]) / pbcX)
            dy = (defects_list[i][1] - defects_list[j][1]) - pbcY*np.round((defects_list[i][1] - defects_list[j][1]) / pbcY)
            dist =  np.sqrt( np.square(dx) +  np.square(dy))
            dist_matrix[i][j] = dist

            # add to adjacency matrix if distance below cutoff
            if dist < cutoff:
                adj_matrix[i][j] = True
                adj_matrix[j][i] = True
    return (adj_matrix, dist_matrix)


# Cluster defects for a frame
def cluster_frame_defects(total_points, defect_location_matrix, adj_matrix, dist_matrix):
    cluster_summary = []

    k = 0
    points_left = total_points
    
    # assign all points to not belong to a cluster
    clust_member = np.full(total_points,-1, dtype=np.int)
    
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
        cluster_summary.append("Cluster %2d %8.3f %8.3f %8.3f %8.3f %8.3f %8.3f %8.3f\n" % 
                (k, np.mean(xDefectVals), np.mean(yDefectVals), numBins * np.square(grid_size), 
                    xMinDef, xMaxDef + grid_size, yMinDef, yMaxDef + grid_size))
        return (k, cluster_summary, defect_location_matrix)








# read in command line values for files to read
opts, args = getopt.getopt(sys.argv[1:], "i:o:p:")
for opt, arg in opts:
    if opt == '-i':
        inFile = arg
    elif opt == '-o':
        outDir = arg
    elif opt == '-p':
        pbcFile = arg


###########
# set paramters for clustering
cutoff = 2.5
min_cluster_size = 1
grid_size = 0.4



########## 
#these variables will be set for each frame

# number of defects read for current frame
count = 0
# current frame number
frame = 0

# total points in current frame
total_points = 0
# total top points in current frame
total_top_points = 0
# total bottom points in current frame
total_bot_points = 0

# current number of top points in current frame
top_point_count = 0
#current number of bottom points in current frame
bottom_point_count = 0


###########


########### READ IN PBC FILE
pbcInfo = np.loadtxt(pbcFile, comments=('#', '@'), unpack=True)

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
##############



###########
# write header info to output files
output_top = open(outDir + 'TOP-LEAF-CLUSTERS.dat', "w")
output_bot = open(outDir + 'BOTTOM-LEAF-CLUSTERS.dat', "w")
output_top.write(" #Cluster     #     xPos     yPos     size     xmin     xmax     ymin     ymax\n" )
output_bot.write(" #Cluster     #     xPos     yPos     size     xmin     xmax     ymin     ymax\n" )
###########


print 'beginning clustering'

with open(inFile, "r") as fp:
    for line in fp:
        split_line = line.split()
        if(len(split_line) == 3):

            total_points = int(split_line[0])
            top_point_count = -1
            bottom_point_count = -1
            total_top_points = int(split_line[1])
            total_bot_points = int(split_line[2])

            top_defects = np.zeros((total_top_points, 2))
            bot_defects = np.zeros((total_bot_points, 2))
            count = 0
        elif (len(split_line) == 2):
            frame = int(split_line[1])
            index = (frame - 1)*dt
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
                
                
                ###########################
                ## FIRST DO TOP LEAFLET ###
                ###########################
                
                ###########################
                print 'frame ', frame, "\nassigning clusters in top "


                adj_matrix, dist_matrix =  get_adjacency_matrix(top_defects, pbcX, pbcY, cutoff)                       
                
                ######################
                # BUILD matrix for storing defects
                xval = np.arange(minX, maxX, grid_size)
                yval = np.arange(minY, maxY, grid_size)
                defect_location_matrix = np.full((len(xval), len(yval)), -1, dtype=np.int)
                ########################

                topClustersNum, top_to_output, top_matrix = cluster_frame_defects(len(top_defects), defect_location_matrix, adj_matrix, dist_matrix)
                
                for line in top_to_output:
                    output_top.write(line)





                ###########################
                ## Next Do Bottom LEAFLET #
                ###########################
                print "assigning clusters in bottom \n",

                adj_matrix, dist_matrix =  get_adjacency_matrix(bot_defects, pbcX, pbcY, cutoff)                       
                
                ######################
                # BUILD matrix for storing defects
                xval = np.arange(minX, maxX, grid_size)
                yval = np.arange(minY, maxY, grid_size)            
                defect_location_matrix = np.full((len(xval), len(yval)), -1, dtype=np.int)
                ########################

                botClustersNum, bot_to_output, bot_matrix = cluster_frame_defects(len(bot_defects), defect_location_matrix, adj_matrix, dist_matrix)

                for line in bot_to_output:
                    output_bot.write(line)            

            
            
                        

output_top.close()
output_bot.close()


