# load the MDAnalysis and numpy modules
import numpy as np
import sys, getopt, os, errno, re, string, math
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import sqlite3


opts, args = getopt.getopt(sys.argv[1:], "d:o:")



for opt, arg in opts:
    if opt == '-o':
    	outDir = arg
    elif opt == '-d':
    	dbFile = arg

bigFont = 24

conn= sqlite3.connect(dbFile)
c = conn.cursor()   

# Get all Systems in DB 	
c.execute('''SELECT key, membraneType, S.protein, runNumber, count 
    FROM Systems S, (SELECT Count(*) as count, protein FROM Residues GROUP BY protein) R WHERE S.protein = R.protein''')
systems = c.fetchall()


# Loop Through Systems
for row in systems:
	# set System info
    key = row[0]
    membType = row[1].upper()
    protein = row[2].upper()
    runNumber = row[3]
    numRes = row[4]

    # Set title and output name
    title = ('%s %s %s' % (membType, protein, runNumber))
    outName = ('%s.%s.%s' % (membType, protein, runNumber))
    print(title)
   
    # Define Plot size based on number of residues
    if numRes == 25:
        xdim = 25
        ydim = 25
        a = 5
        b = 5
    elif numRes > 25 and numRes <= 28:
        xdim = 35
        ydim = 20
        a = 4
        b = 7
    elif numRes > 50 and numRes <= 54:
        xdim = 36
        ydim = 24
        a = 6
        b = 9
    # Create Plot
    fig, axs = plt.subplots(a,b, sharex=True, sharey=True, figsize=(xdim,ydim))
    axd = axs.ravel()
    

    
    # Get residues in protein
    c.execute('''   SELECT R.key, R.resNum, A.resAbbrev, A.resType 
                    FROM Residues R, AminoAcids A 
                    WHERE R.aaKey = A.key AND Protein=?''', (protein,))
    residues = c.fetchall()
    

    # Loop through residues
    for i in range(len(residues)):
    	
        residue = residues[i]
        
        # Set Residue Info
        resNum = residue[1]
        resTitle = residue[2]
        resType = residue[3]
        
        # Set color for plotting residue
        if resType in 'hydrophobic':
            color = 'r'
        elif resType in 'polar':
            color = 'm'
        elif resType in 'NA':
            color = 'c'
        elif resType in 'positive':
            color = 'b'
        elif resType in 'negative':
            color = 'g'
        else:
            raise NameError('Unknown residue\n')
        
        # Get residue data from DB
        c.execute('''SELECT timestep, distance 
                        FROM ProteinPositions 
                        WHERE systemID=? AND resKey=?''', (key, residue[0]))
        results = c.fetchall()
        
        # Change to Numpy Array and Transpose
        npResults = np.array(results).T
        
        #Plot Data
        axd[i].plot([0,2000], [0.0, 0.0], 'k', npResults[0], npResults[1], color)
        axd[i].set_title(resTitle+str(resNum))
        i += 1

	#Set plot Formatting and Save
    plt.axis([0,2000, -10, 40])
    fig.text(0.5, 0.04, 'Time (ns)', ha='center', fontsize=bigFont)
    fig.text(0.5, 0.96, title, ha='center', fontsize=bigFont)
    fig.text(0.04, 0.5, 'Distance to Membrane ($\AA$)', va='center', rotation='vertical', fontsize=bigFont)
    plt.savefig(outDir + outName + '.png')
    plt.close()