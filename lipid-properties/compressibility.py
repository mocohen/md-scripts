import sys, getopt, os, errno, re, string

opts, args = getopt.getopt(sys.argv[1:], "i:o:")
for opt, arg in opts:
    if opt == '-i':
        inFile = arg
    elif opt == '-o':
        outFile = arg

input = open(inFile, "r").readlines()

arr = []
i = 0.0
sum = 0.0
sumOfSquares = 0.0
for line in input:
    newLine = re.sub(r' +',' ', line).strip().split(" ")
    new = float(newLine[1])
    sum += new
    sumOfSquares += (new * new)
    i += 1.0

    
print "Sum"
print sum
print sumOfSquares

avgOfSum = sum / i
avgOfSquares = sumOfSquares / i

sumSquare = avgOfSum * avgOfSum 

print avgOfSum
print avgOfSquares
print sumSquare

var = avgOfSquares - sumSquare


#boltzmann constant is
# 1.38065 g Angs^2/(s^2K)  (gram ångströms squared per second squared kelvin)
 
# at 310 K, K_b * T = 428.001 g * Angs^2 / s^2 or 428.001 angs^2 * dyn/cm  
ans = 428 * avgOfSum / ( 150 * var) 
	
print ans