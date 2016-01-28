# load the MDAnalysis and numpy modules
import numpy as np
import sys, getopt, os, errno, re, string, math
import matplotlib.pyplot as plt
import matplotlib.cm as cm

opts, args = getopt.getopt(sys.argv[1:], "n:p:o:t:")

#opts = (('-o','pic.png'),  ('-t','Bilayer Alps C'),  ('-n', 'dist.all.xvg'), ('-p', 'alps'))

alps_prot = ('PHE','LEU','ASN','ASN','ALA','MET','SER','SER','LEU','TYR','SER','GLY','TRP',
		'SER','SER','PHE','THR','THR','GLY','ALA','SER','ARG','PHE','ALA','SER')

m_prot = ('HSE', 'LEU', 'GLN', 'GLU', 'ARG', 'VAL', 'ASP', 'LYS', 'VAL', 'LYS', 'LYS', 'LYS', 'VAL',
		'LYS', 'ASP', 'VAL', 'GLU', 'GLU', 'LYS', 'SER', 'LYS', 'GLU', 'PHE', 'VAL', 'GLN', 'LYS', 'VAL',
		'GLU', 'GLU', 'LYS', 'SER', 'ILE', 'ASP', 'LEU', 'ILE', 'GLN', 'LYS', 'TRP', 'GLU', 'GLU', 
		'LYS', 'SER', 'ARG', 'GLU', 'PHE', 'ILE', 'GLY', 'SER', 'PHE', 'LEU', 'GLU', 'MET', 'PHE', 'GLY'   )

p2_prot = ('VAL', 'GLU', 'GLU', 'LYS', 'SER', 'ILE', 'ASP', 'LEU', 'ILE', 'GLN', 'LYS', 'TRP', 'GLU', 'GLU', 
		   'LYS', 'SER', 'ARG', 'GLU', 'PHE', 'ILE', 'GLY', 'SER', 'PHE', 'LEU', 'GLU', 'MET', 'PHE', 'GLY' )

for opt, arg in opts:
    if opt == '-o':
    	output = arg
    elif opt == '-t':
    	title = arg
    elif opt == '-n':
    	inFile = arg
    elif opt == '-p':
    	prot = arg

dat = np.loadtxt(inFile, comments=('#', '@'))

numRes = ((len(dat[0]) - 1) / (2*3)) - 1

skipNum = 10
bigFont = 24

timeVals = np.zeros(len(dat))
resPosZ = np.zeros((numRes,len(dat)))

for i in range(len(dat)):
	#First get time at frame
	timeVals[i] = dat[i][0] / 1000.0
	
	first = False
	#check if first closer
	if(-1.0*dat[i][3] < dat[i][6]):
		first = True
	
	for j in range(numRes):
		index = 0
		sign = 1.0
		indexA = (j*6) + 9
		indexB = (j*6) + 12
		if -1.0*dat[i][indexA] < dat[i][indexB]:
			index = indexA
			sign = -1.0
		else:
			index = indexB
			sign = 1.0
		# switch to angs from gromacs units (nm)	
		resPosZ[j][i] = 10*sign*dat[i][index]
# 		if j == 0 and i % 1000 == 0:
# 			print timeVals[i], index, dat[i][indexA], dat[i][indexB], sign 
	

np.savetxt(inFile+'.dat', resPosZ[0], fmt='%10.5f')

restypes = {}

restypes['ALA'] = restypes['ILE'] = restypes['LEU'] = restypes['MET'] = restypes['PHE'] = 'r'
restypes['TRP'] = restypes['TYR'] = restypes['VAL'] = 'r'
restypes['SER'] = restypes['THR'] = restypes['ASN'] = restypes['GLN'] =  'm'
restypes['ARG'] = restypes['HSE'] = restypes['LYS'] = 'b'
restypes['ASP'] = restypes['GLU'] = 'g'
restypes['CYS'] = restypes['SEC'] = restypes['GLY'] = restypes['PRO'] = 'c'

if 'alps' in prot:
	resNames = alps_prot
	xdim = 25
	ydim = 25
	a = 5
	b = 5

if 'M' in prot:
	resNames = m_prot
	xdim = 36
	ydim = 24
	a = 6
	b = 9

if 'p2' in prot:
	resNames = p2_prot
	xdim = 35
	ydim = 20
	a = 4
	b = 7
		

fig, axs = plt.subplots(a,b, sharex=True, sharey=True, figsize=(xdim,ydim))

#print axs

axd = axs.ravel()

for i in range(len(resNames)):
	resname = resNames[i]
	axd[i].plot([0,1000], [0.0, 0.0], 'k', timeVals[0::skipNum], resPosZ[i][0::skipNum], restypes[resname])
	if 'p2' in prot:
		axd[i].set_title(resname + str(i+27))
	else:
		axd[i].set_title(resname + str(i+1))
	#axd[i].set_xlabel('Time (xx)')
	#axd[i].set_ylabel('Distance to Membrane ($\AA$)')
	i += 1

for ax in axs.flat[axs.size - 1:len(resNames) - 1:-1]:
    ax.set_visible(False)

#line1a, line1b = plt.plot([0,2000], [0.0, 0.0], 'k', data[i][0::skipNum], resPosZ[i][0::skipNum], restypes[resname])

#plt.legend([line1a, line2a, line3a, line5a], ['40 $\AA$', '60 $\AA$', '80 $\AA$', 'flat bilayer'])
plt.axis([0,1000, -5, 30])
#plt.title(resname)
#plt.axis([minx, maxx, miny, maxy])
#plt.ylabel('Distance to Membrane ($\AA$)')
#plt.xlabel('Time (xx)')
fig.text(0.5, 0.04, 'Time (ns)', ha='center', fontsize=bigFont)
fig.text(0.5, 0.96, title, ha='center', fontsize=bigFont)
fig.text(0.04, 0.5, 'Distance to Membrane ($\AA$)', va='center', rotation='vertical', fontsize=bigFont)
plt.savefig(output)
