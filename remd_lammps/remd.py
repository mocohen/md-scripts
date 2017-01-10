from lammps import lammps
import numpy as np

import os, getopt
import sys
import threading
import datetime

begin = datetime.datetime.now()
print begin.strftime('%H:%M:%S')

totalSteps=100
runNumber = 0
writeRestart = totalSteps

lammpsInstances = []
for i in range(4):
    lammpsInstances.append(lammps())

opts, args = getopt.getopt(sys.argv[1:], "c:")

fromRestart = False
for opt, arg in opts:
    if opt == '-c':
        checkpoint = arg
        fromRestart = True

  


temps = [310, 410, 510, 610]
tempIndex = {temps[0]: 0, temps[1]: 1, temps[2]: 2, temps[3]: 3}

class OutputGrabber(object):
    """
    Class used to grab standard output or another stream.
    """
    escape_char = "\b"

    def __init__(self, stream=None, threaded=False):
        self.origstream = stream
        self.threaded = threaded
        if self.origstream is None:
            self.origstream = sys.stdout
        self.origstreamfd = self.origstream.fileno()
        self.capturedtext = ""
        # Create a pipe so the stream can be captured:
        self.pipe_out, self.pipe_in = os.pipe()
        pass

    def start(self):
        """
        Start capturing the stream data.
        """
        self.capturedtext = ""
        # Save a copy of the stream:
        self.streamfd = os.dup(self.origstreamfd)
        # Replace the Original stream with our write pipe
        os.dup2(self.pipe_in, self.origstreamfd)
        if self.threaded:
            # Start thread that will read the stream:
            self.workerThread = threading.Thread(target=self.readOutput)
            self.workerThread.start()
            # Make sure that the thread is running and os.read is executed:
            time.sleep(0.01)
        pass
    def stop(self):
        """
        Stop capturing the stream data and save the text in `capturedtext`.
        """
        # Flush the stream to make sure all our data goes in before
        # the escape character.
        self.origstream.flush()
        # Print the escape character to make the readOutput method stop:
        self.origstream.write(self.escape_char)
        if self.threaded:
            # wait until the thread finishes so we are sure that
            # we have until the last character:
            self.workerThread.join()
        else:
            self.readOutput()
        # Close the pipe:
        os.close(self.pipe_out)
        # Restore the original stream:
        os.dup2(self.streamfd, self.origstreamfd)
        pass

    def readOutput(self):
        """
        Read the stream data (one byte at a time)
        and save the text in `capturedtext`.
        """
        while True:
            data = os.read(self.pipe_out, 1)  # Read One Byte Only
            if self.escape_char in data:
                break
            if not data:
                break
            self.capturedtext += data
        pass

def readRestart():
    print 'read restart'
    chkInfo = np.loadtxt(checkpoint, int)
    i = 1
    for theTemp in tempIndex:
        tempIndex[theTemp] = chkInfo[i]
        i += 1
    return chkInfo[0]

# def restartfromCheckpoint(ind1):
#     t1 = temps[ind1]
#     with open('template.restart.in') as f:
#         restartInput = f.read().splitlines()
#     for line in restartInput:
#         line = line.replace('AAAA', str(ind1))
#         line = line.replace('BBBB', str(runNumber) )
#         line = line.replace('CCCC', str(runNumber - 1) )
#         line = line.replace('DDDD', str(t1))
#         lammpsInstances[ind1].command(line)

def chop_microseconds(delta):
    return delta - datetime.timedelta(microseconds=delta.microseconds)

# multiple by gas constant in kcal/mol/K
betas = np.full(len(temps),1.0) / (temps* np.full(len(temps),0.0019872))
potEnergies = np.zeros(len(temps))
numSwaps = np.zeros(len(temps))



output = open('temperatures.dat', 'w')
output.write('#nstep  ')
for i in range(len(temps)):
    output.write('%6d ' % temps[i]) 
output.write('\n')

def swap(ind1, ind2):
    t1 = temps[ind1]
    t2 = temps[ind2]

    rescale1 = np.sqrt(t2/t1)
    rescale2 = np.sqrt(t1/t2)

    tind1 = tempIndex[t1]
    tind2 = tempIndex[t2]

    lammps1 = lammpsInstances[tind1]
    lammps2 = lammpsInstances[tind2]
    natoms = lammps1.extract_global("natoms",0)

    v1 = lammps1.extract_atom("v", 3)
    v2 = lammps1.extract_atom("v", 3)

    for i in range(natoms):
        for j in range(3):
            v1[i][j] *= rescale1
            v2[i][j] *= rescale2

    tempIndex[t1] = tind2
    tempIndex[t2] = tind1

    text1 = 'unfix eq'
    text2 = 'unfix eqr'
    textA = 'fix eq realAtoms langevin %d %d 10.0 8329798' % (t2, t2)
    textB = 'fix eq realAtoms langevin %d %d 10.0 8329798' % (t1, t1)
    text3 = 'fix eqr all nve' 
    
    lammps1.command(text1)
    lammps2.command(text1)
    lammps1.command(text2)
    lammps2.command(text2)
    lammps1.command(textA)
    lammps2.command(textB)
    lammps1.command(text3)
    lammps2.command(text3)


def checkSwap(ind1, ind2):
    tind1 = tempIndex[temps[ind1]]
    tind2 = tempIndex[temps[ind2]]
    ene1 = potEnergies[tind1]
    ene2 = potEnergies[tind2]
    dU = ene2 - ene1
    dBeta = betas[ind1] - betas[ind2]
    delta = dBeta*dU
    rand = np.random.rand()
    #print 'dU', dU, 'dBeta', dBeta, 'delta', delta, 'prob', prob, 'rand', rand
    if delta <= 0.0 or np.exp(-1.0*delta) > rand:
        return True
    return False

if fromRestart:
    runNumber = readRestart()

isFirst = True
for nsteps in range(totalSteps):
    print 'step', nsteps, chop_microseconds(datetime.datetime.now()-begin)
    j = 1
    for lmp in lammpsInstances:
        if isFirst:
            out = OutputGrabber()
            out.start()
            if fromRestart:
                t1 = temps[j-1]
                with open('template.restart.in') as f:
                    restartInput = f.read().splitlines()
                for line in restartInput:
                    line = line.replace('AAAA', str(j))
                    line = line.replace('BBBB', str(runNumber) )
                    line = line.replace('CCCC', str(runNumber - 1) )
                    line = line.replace('DDDD', str(t1))
                    lmp.command(line)
            else:
                lmp.file('sim'+str(j)+'/mccg.in')
            out.stop()	
        #print 'run!'
        out = OutputGrabber()

        #if isFirst and fromRestart:
        #    lmp.command('run 1000')
        #else:
        out.start()
        lmp.command('run 1000 pre yes post no')
        out.stop()

        bufferPointer = 0
        potentialEnergy = 0.0
        if('ERROR:' in out.capturedtext):
            print 'ERROR'
        while (out.capturedtext.find('MCCG:', bufferPointer) > 0):
            newPoint = out.capturedtext.find('MCCG:', bufferPointer)
            bufferPointer = newPoint+40
            line = out.capturedtext[newPoint:bufferPointer]
            potentialEnergy = float(line.split()[2])
        potEnergies[j-1] = potentialEnergy
        j += 1
    #print potEnergies

    if (nsteps % 2)  == 0:
        for i in range(int(len(temps) / 2)):
            in1 = 2*i
            in2 = (2*i) + 1
            if checkSwap(in1, in2):
                #print 'swap'
                swap(in1, in2)
                numSwaps[in1] += 1
    else:
        for i in range(int( (len(temps) - 1)/ 2)):
            in1 = (2*i) + 1
            in2 = (2*i) + 2
            if checkSwap(in1, in2):
                #print 'swap'
                swap(in1, in2)
                numSwaps[in1] += 1

    output.write('%8d' % nsteps)
    for i in range(len(temps)):
        output.write('%6d ' % tempIndex[temps[i]]) 
    output.write('\n')

    if (nsteps % writeRestart) == (writeRestart - 1) and not isFirst:
        for lmp in lammpsInstances:
            lmp.command('write_restart ${input}.%d.restart' % int(runNumber))
    isFirst = False


checkpoint = open('run.chk', 'w')
checkpoint.write(str(runNumber + 1))
for i in range(len(temps)):
    checkpoint.write(' %6d' % tempIndex[temps[i]]) 
checkpoint.close()

output.write('#swap info\n#     ')
for i in range(len(temps)):
    output.write('%6d ' % numSwaps[i]) 
output.close()
final = datetime.datetime.now()

print 'This run took', chop_microseconds(final-begin)




