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

f = open(inFile, "r")
o = open(outFile, "w")

isFirst = True
timestep = 0
nAtoms = 22

masses = {}

# nm to angs
distConv = 10.0
#kj/mol-nm to kcal/mol-A
forceConv = 0.0239


######## Read PDB
pdb = np.loadtxt('sim.pdb', usecols=(1, 2, 3, 4, 10), dtype={'names': ('index', 'atomType', 'resType', 'resNum', 'element'), 'formats': ('i4', 'S4', 'S4', 'i4', 'S1')})
atomTypes = {}
atomResNums = {}

print len(pdb)
for line in pdb:
    atom = line[4]
    index = line[0]
    atomTypes[index] = line[1]
    atomResNums[index] = line[3]
    if atom == 'H':
        masses[index] = 1.0080
    elif atom == 'C':
        masses[index] = 12.0110
    elif atom == 'O':
        masses[index] = 15.999
    elif atom == 'N':
        masses[index] = 14.0070
    elif atom == 'S':
        masses[index] = 32.0600
    else:
        print 'error', atom
        exit()





forces = np.zeros((nAtoms, 3))
positions = np.zeros((nAtoms, 3))




for line in f:
    if 'frame' in line:
        split = line.split()
        if isFirst:
            isFirst = False
        else:
            o.write("ITEM: TIMESTEP\n")
            o.write("%i\n" % timestep)
            o.write("ITEM: NUMBER OF ATOMS\n")
            o.write("%i\n" % nAtoms)
            o.write("ITEM: BOX BOUNDS pp pp pp\n")
            o.write("0 100.0\n0 100.0\n0 100.0\n")
            o.write("ITEM: ATOMS id type x y z fx fy fz \n")
            for i in range(nAtoms):
                o.write("%d %d %.4f %.4f %.4f %.4f %.4f %.4f\n" % (i+1, i+1, 
                    positions[i][0], positions[i][1], positions[i][2], forces[i][0], forces[i][1], forces[i][2] ))
        timestep = int(split[2].strip(":"))
        forces = np.zeros((nAtoms, 3))
        positions = np.zeros((nAtoms, 3))

    if 'f[' in line:
        split = line.strip().split("=")
        fs = split[1].strip("{}").split()
        atomNum = int(split[0].strip("f[]"))
        for i in range(3):
            fi = fs[i].strip(",")
            forces[atomResNums[atomNum + 1] - 1][i] += forceConv*float(fi)
    elif ' x[' in line:
        split = line.strip().split("=")
        xs = split[1].strip("{}").split()
        atomNum = int(split[0].strip("x[]"))
        if atomTypes[atomNum + 1] == 'CA':
            for i in range(3):
                xi = xs[i].strip(",")
                positions[atomResNums[atomNum + 1] - 1][i] = float(xi)*distConv

