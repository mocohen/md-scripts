import sys, getopt, os, errno, re, string, math
#import matplotlib.cm as cm

opts, args = getopt.getopt(sys.argv[1:], "i:o:")
for opt, arg in opts:
    if opt == '-i':
        inFile = arg
    elif opt == '-o':
        outFile = arg

output = open(inFile, "w")
input = open(outFile, "r")
r = []
e = []

isFirst = True
for line in input:
	if isFirst:
		output.write("%s XPLOR\n" % line.strip())
		isFirst = False
	else:
		output.write(line)

output.close()
