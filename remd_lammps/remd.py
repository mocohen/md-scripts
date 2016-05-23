from lammps import lammps
import numpy as np

import os
import sys
import threading

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




lmp1 = lammps()
lmp2 = lammps()
lmp3 = lammps()
lmp4 = lammps()
lammpsInstances = [lmp1, lmp2, lmp3, lmp4]
temps = [310, 410, 510, 610]
# multiple by gas constant in kcal/mol/k
temps_b = temps* 0.0019872 
potEnergies = np.zeros(4)

isFirst = True

for nsteps in range(10):
	j = 1
	for lmp in lammpsInstances:
		out = OutputGrabber()
		out.start()
		if isFirst:
			lmp.file('sim'+str(j)+'/mccg.in')	
		else:
			lmp.command('run 1000')
		out.stop()
		print 'end sim'
		bufferPointer = 0
		potentialEnergy = 0.0
		while (out.capturedtext.find('MCCG:', bufferPointer) > 0):
			newPoint = out.capturedtext.find('MCCG:', bufferPointer)
			bufferPointer = newPoint+40
			line = out.capturedtext[newPoint:bufferPointer]
			potentialEnergy = float(line.split()[2])
		potEnergies[j-1] = potentialEnergy
		j += 1
	print potEnergies
	isFirst = False





