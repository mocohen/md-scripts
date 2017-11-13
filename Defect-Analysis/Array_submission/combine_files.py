import sys, getopt, os
#, errno

opts, args = getopt.getopt(sys.argv[1:], "o:n:")


for opt, arg in opts:
    if opt == '-o':
        outDir = arg
    elif opt == '-n':
        fName = arg

output = open(outDir + fName, 'w')

totalFrame = 0

isTracking = False
if 'TRACKING' in fName:
    raise NameError('Cannot do tracking with this script')
    isTracking = True


try:
    runDir = '../'
    localFrame = 0
    for j in range(1000):
        filePref = runDir + 'step' + str(j) + '/'
        fileName = filePref + fName
        print fileName
        if not os.path.isfile(fileName):
            print fileName
            raise NameError('Could not find file. Please specify file that exists')
        else:
            inFile = open(fileName, 'r')
            localFrame = 0
            for line in inFile:
                if 'frame' in line:
                    localFrame += 1
                    totalFrame += 1
                    split = line.split()
                    output.write("frame: %6d time: %.4f ns pbcX: %6.2f  pbcY: %6.2f\n" % (totalFrame, (totalFrame - 1)/2000.0, float(split[6]), float(split[8])))   
                else:
                    output.write(line)
            inFile.close()
except:
    print "didn't work"
output.close()


# frame: 200001 time: 100.000 ns pbcX: 111.77  pbcY: 111.77

