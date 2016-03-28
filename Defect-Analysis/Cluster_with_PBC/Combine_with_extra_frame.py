import sys, getopt, os
#, errno

opts, args = getopt.getopt(sys.argv[1:], "o:f:n:")


for opt, arg in opts:
    if opt == '-o':
        outDir = arg
    elif opt == '-f':
        fileDir = arg
    elif opt == '-n':
        fName = arg

output = open(outDir + fName, 'w')


for i in range(100):
    filePref = fileDir + '/step' + str(i) + '/'
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
            if localFrame < 751:
                output.write(line)
        inFile.close()
output.close()


