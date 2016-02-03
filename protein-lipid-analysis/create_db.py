import sys, getopt, os, errno, re, string
import numpy as np

from datetime import datetime, tzinfo
import sqlite3

opts, args = getopt.getopt(sys.argv[1:], "d:")
for opt, arg in opts:
    if opt == '-d':
    	dbFile = arg





if os.path.isfile(dbFile):
	raise NameError('Database file already exists. Please remove and/or backup old DB file\n')
	
	
conn= sqlite3.connect(dbFile)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS Systems 
			(key 				INTEGER PRIMARY KEY,
			membraneType 		TEXT,
			lipidType			TEXT,
			lipidComposition 	TEXT,
			protein				TEXT,
			runNumber			INTEGER)''')

c.execute('''CREATE TABLE IF NOT EXISTS ProteinPositions 
			(key 		INTEGER PRIMARY KEY,
			systemID   	INTEGER,
			timestep	real,
			distance 	real,
			reskey		INTEGER)''')
			
c.execute('''CREATE TABLE IF NOT EXISTS Residues 
			(key 				INTEGER PRIMARY KEY,
			aaKey				INTEGER,
			protein				TEXT,
			resNum				INTEGER)
			''')			

c.execute('''CREATE TABLE IF NOT EXISTS AminoAcids
			(key 				INTEGER PRIMARY KEY,
			resName				TEXT, 
			resLetter			TEXT,
			resAbbrev			TEXT,
			resType				TEXT)''')
			
						

conn.commit()

resNumOffset = 0

alps_prot = ('PHE','LEU','ASN','ASN','ALA','MET','SER','SER','LEU','TYR','SER','GLY','TRP',
		'SER','SER','PHE','THR','THR','GLY','ALA','SER','ARG','PHE','ALA','SER')

m_prot = ('HIS', 'LEU', 'GLN', 'GLU', 'ARG', 'VAL', 'ASP', 'LYS', 'VAL', 'LYS', 'LYS', 'LYS', 'VAL',
		'LYS', 'ASP', 'VAL', 'GLU', 'GLU', 'LYS', 'SER', 'LYS', 'GLU', 'PHE', 'VAL', 'GLN', 'LYS', 'VAL',
		'GLU', 'GLU', 'LYS', 'SER', 'ILE', 'ASP', 'LEU', 'ILE', 'GLN', 'LYS', 'TRP', 'GLU', 'GLU', 
		'LYS', 'SER', 'ARG', 'GLU', 'PHE', 'ILE', 'GLY', 'SER', 'PHE', 'LEU', 'GLU', 'MET', 'PHE', 'GLY'   )

p2_prot = ('VAL', 'GLU', 'GLU', 'LYS', 'SER', 'ILE', 'ASP', 'LEU', 'ILE', 'GLN', 'LYS', 'TRP', 'GLU', 'GLU', 
		   'LYS', 'SER', 'ARG', 'GLU', 'PHE', 'ILE', 'GLY', 'SER', 'PHE', 'LEU', 'GLU', 'MET', 'PHE', 'GLY' )	
		   

ala = (1, 	'alanine', 		'A', 'ALA', 'hydrophobic')
ile = (2, 	'isoleucine', 	'I', 'ILE', 'hydrophobic')
leu = (3, 	'leucine', 		'L', 'LEU', 'hydrophobic')
met = (4, 	'methionine', 	'M', 'MET', 'hydrophobic')
phe = (5, 	'phenylalanine','F', 'PHE', 'hydrophobic')
trp = (6, 	'tryptophan', 	'W', 'TRP', 'hydrophobic')
tyr = (7, 	'tyrosine', 	'Y', 'TYR', 'hydrophobic')
val = (8, 	'valine',		'V', 'VAL', 'hydrophobic')
ser = (9, 	'serine', 		'S', 'SER', 'polar')
thr = (10, 	'threonine',	'T', 'THR', 'polar')
asn = (11, 	'asparagine', 	'N', 'ASN', 'polar')
gln = (12, 	'glutamine',	'Q', 'GLN', 'polar')
cys = (13, 	'cysteine',		'C', 'CYS', 'NA')
sec = (14, 	'selenocysteine','U', 'SEC', 'NA')
gly = (15, 	'glycine',		'G', 'GLY', 'NA')
pro = (16, 	'proline',		'P', 'PRO', 'NA')
arg = (17, 	'arginine',		'R', 'ARG', 'positive')
his = (18, 	'histidine',	'H', 'HIS', 'positive')
lys = (19, 	'lysine',		'K', 'LYS', 'positive')
asp = (20, 	'aspartic acid','D', 'ASP', 'negative')
glu = (21, 	'glutamic acid','E', 'GLU', 'negative')

aminoAcidInfo = [ala, ile, leu, met, phe, trp, tyr, val, ser, thr, asn, gln, cys, sec, gly, pro, arg, his, lys, asp, glu]

c.executemany(''' INSERT INTO AminoAcids (key, resName, resLetter, resAbbrev, resType) VALUES (?,?,?,?,?)''',
					aminoAcidInfo)	

conn.commit()


residueDict = {}
for row in c.execute('SELECT key, resAbbrev FROM AminoAcids'):
	residueDict[row[1]] = row[0]




def createSQLResInfo (resNames, resOffset, protName):
	sqlInfo = []
	i = 0
	for residue in resNames:
		theKey = residueDict[residue]
		sqlInfo.append((theKey, protName, resOffset + i))
		i += 1
	return sqlInfo

p2SQL = createSQLResInfo(p2_prot, 27, 'P2')
mSQL = createSQLResInfo(m_prot, 1, 'M')
alpsSQL = createSQLResInfo(alps_prot, 1, 'ALPS')
protSQL = p2SQL + mSQL + alpsSQL

c.executemany(''' INSERT INTO Residues (aaKey, protein, resNum) VALUES (?,?,?)''', protSQL)

conn.commit()
conn.close()
