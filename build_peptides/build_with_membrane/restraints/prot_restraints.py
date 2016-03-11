import sys, getopt, os, errno, re, string

opts, args = getopt.getopt(sys.argv[1:], "i:o:")
for opt, arg in opts:
    if opt == '-i':
        inFile = arg
    elif opt == '-o':
        outFile = arg
        

input = open(inFile, "r").readlines()

output = open(outFile, "w")

output.write('''#ifdef STEP6_0
#define fc_bb 4000.0
#define fc_sc 2000.0
#endif
#ifdef STEP6_1
#define fc_bb 4000.0
#define fc_sc 2000.0
#endif
#ifdef STEP6_2
#define fc_bb 2000.0
#define fc_sc 1000.0
#endif
#ifdef STEP6_3
#define fc_bb 1000.0
#define fc_sc 500.0
#endif
#ifdef STEP6_4
#define fc_bb 500.0
#define fc_sc 200.0
#endif
#ifdef STEP6_5
#define fc_bb 200.0
#define fc_sc 50.0
#endif
#ifdef STEP6_6
#define fc_bb 50.0
#define fc_sc 0.0
#endif
#ifdef STEP7
#define fc_bb 0.0
#define fc_sc 0.0
#endif

[ position_restraints ]\n''')



isAtom = False
for line in input:
	if 'bonds' in line:
		isAtom = False
	if isAtom and not line.startswith(';') and len(line.strip()) > 0:
		#print "isAtom", line
		split = line.split()
		#print split
		if split[4] == 'N' or split[4] == 'CA' or split[4] == 'C' or split[4] == 'O':
			output.write("%5s     1    fc_bb    fc_bb    fc_bb\n" % split[0])
		elif split[4].startswith('C') or split[4].startswith('S') or split[4].startswith('O') or split[4].startswith('N'):
			output.write("%5s     1    fc_sc    fc_sc    fc_sc\n" % split[0])
	if 'atoms' in line:
		isAtom = True

	
	
	
output.close()	
	
	