# command line arguments: 1-psf, 2-pdb, 3-dcd, 4- output xyz
# pdb coordinates are not considered for calculations, this is simply to read protein structure


set psf [lindex $argv 0] 
set pdb [lindex $argv 1] 
set dcd [lindex $argv 2] 
set out [lindex $argv 3]

#set step_size [lindex $argv 4]
#set num_frames [lindex $argv 5]

set step_size 1


mol load psf $psf pdb $pdb
animate read dcd $dcd skip $step_size waitfor all

set num_frames [expr [molinfo top get numframes] - 1]

set sel1 [atomselect top "protein and resid 1 to 5"]
set sel2 [atomselect top "protein and resid 6 to 8"]
set sel3 [atomselect top "protein and resid 9 to 11"]
set sel4 [atomselect top "protein and resid 12 to 16"]
set sel5 [atomselect top "protein and resid 17 to 19"]
set sel6 [atomselect top "protein and resid 20 to 22"]

set mass1 447.551
set mass2 371.526
set mass3 412.450
set mass4 558.681
set mass5 314.318
set mass6 301.367



set ofile [open $out w]


for {set frame 1} {$frame <= $num_frames/$step_size } {incr frame} {

	puts $ofile "6"
	puts $ofile "frame $frame"
	molinfo top set frame $frame
	set pos1 [measure center $sel1 weight mass]
	set pos2 [measure center $sel2 weight mass]
	set pos3 [measure center $sel3 weight mass]
	set pos4 [measure center $sel4 weight mass]
	set pos5 [measure center $sel5 weight mass]
	set pos6 [measure center $sel6 weight mass]
	
	set x1 [lindex $pos1 0]
	set y1 [lindex $pos1 1]
	set z1 [lindex $pos1 2]
	puts $ofile "C1 $x1 $y1 $z1"
	
	set x2 [lindex $pos2 0]
	set y2 [lindex $pos2 1]
	set z2 [lindex $pos2 2]
	puts $ofile "C2 $x2 $y2 $z2"

	set x3 [lindex $pos3 0]
	set y3 [lindex $pos3 1]
	set z3 [lindex $pos3 2]
	puts $ofile "C3 $x3 $y3 $z3"
	
	set x4 [lindex $pos4 0]
	set y4 [lindex $pos4 1]
	set z4 [lindex $pos4 2]
	puts $ofile "C4 $x4 $y4 $z4"
	
	set x5 [lindex $pos5 0]
	set y5 [lindex $pos5 1]
	set z5 [lindex $pos5 2]
	puts $ofile "C5 $x5 $y5 $z5"
	
	set x6 [lindex $pos6 0]
	set y6 [lindex $pos6 1]
	set z6 [lindex $pos6 2]
	puts $ofile "C6 $x6 $y6 $z6"

}

exit
