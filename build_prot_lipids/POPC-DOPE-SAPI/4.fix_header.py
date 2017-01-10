import sys, getopt, os, errno, re, string, math
#import matplotlib.cm as cm

opts, args = getopt.getopt(sys.argv[1:], "i:o:")


output = open('final.ionized.psf', "w")
input = open('new.ionized.psf', "r")
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