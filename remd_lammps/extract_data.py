import numpy as np

import os, getopt, sys


for i in range(1):
    sims = []
    for j in range(4):
        filename = 'sim' + str(j+1) + '/mccg.' + str(i) + '.out'
        sims.append(np.loadtxt(filename))
        print len(sims)
        print len(sims[0])
    temperDat = np.loadtxt('temperatures.' + str(i) + '.dat')
    print len(temperDat)
    print len(temperDat[0])