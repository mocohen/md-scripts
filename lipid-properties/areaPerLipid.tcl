##########################################
##  Calculate Area per Lipid
##########################################


##########################################
##  Output
## [total area] [area / lipid]
##########################################

#psf and dcd

set begin [clock seconds]
set psf md.convert.final.dms
set dcd workdir/jobsteps/000009-2013.07.10.15.49.1373485753/run.dtr

set numLipids 150


set ofile [open analysis/areaPerLipid.9.dat w]

#Chose one
mol load dms $psf dtr $dcd

#mol load psf $psf dcd $dcd

set step_size 1
set num_frames [molinfo top get numframes]


#load frame here...
for {set f 0} {$f < [expr $num_frames / $step_size] } {incr f} {

	set theFrame [expr $f * $step_size]
	#set f 2
	molinfo top set frame $theFrame
	puts "working on frame $theFrame"
	
	#select waters 
	set sel [atomselect top "water"]
	
	
	#calculate min and max coordinates of the waters
	set minAndMax [measure minmax $sel]
	set xlength [expr [lindex [lindex $minAndMax 1] 0] - [lindex [lindex $minAndMax 0] 0] ]
	set ylength [expr [lindex [lindex $minAndMax 1] 1] - [lindex [lindex $minAndMax 0] 1] ]
	set area [expr $xlength * $ylength]
	set apl [expr $area / $numLipids]
	
	puts $ofile "$area $apl"
	
}

flush $ofile
close $ofile

set end [clock seconds]
set total_time [expr $end - $begin]
set minutes [ expr $total_time / 60.0 ]
puts "Time: $total_time seconds or $minutes minutes"

exit 
