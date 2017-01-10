import sys, getopt
import numpy as np
#from scipy.optimize import curve_fit
#from scipy.signal import savgol_filter
#import matplotlib.pyplot as plt
#import matplotlib.cm as cm

opts, args = getopt.getopt(sys.argv[1:], "i:o:")

for opt, arg in opts:
    if opt == '-i':
        inFile = arg
    elif opt == '-o':
        outFile = arg

o = open(outFile, "w")


inputFile = np.loadtxt(inFile,
        dtype={'names': ('index1', 'index2', 'min', 'max', 'switch'), 'formats': ('i4', 'i4', 'S8', 'S8', 'S4')})

for line in inputFile:
    if '-1.0' in line[2]:
        line[4] = 'none'
    if float(line[2]) > 9.0:
        line[4] = 'none'
    o.write("%d %d %s %s %s\n" % tuple(line))


o.close()