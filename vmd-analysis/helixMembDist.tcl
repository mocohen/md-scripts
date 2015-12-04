# This script calculates the depth the helix is buried in 2 ways
# One by simply calculating the average z coord of all P atoms and protein backbone and 
# taking the difference. The second method only calculates the z coord of close P 
# atoms instead of all.

# first argument is psf
# second argument is dcd
# third argument is output file
# fourth argument is starting frame

# Output
# ts allP-Zcoord closeP-Zcoord backbone-Zcoord dist_all-backbone dist_close-backbone

if { [llength $argv] < 3} {
	puts "Specify three arguments!"
	exit
}

set firstFrame 0
# Set intput variables
set fPsf [lindex $argv 0] 
set fDcd [lindex $argv 1] 
set fOut [lindex $argv 2] 
if { [llength $argv] >  3} {
	set firstFrame [lindex $argv 3]
}

# Can hardcode files if necessary
#set fPsf "../../equilibration/ionized.psf"
#set fDcd "../step1/ranDefLipid1.1ns.dcd"
#set fOut "a.out"

# load psf and dcd
mol load psf $fPsf dcd $fDcd


##### make allPections
# Select P of head group for top leaflet
set allP [atomselect top "name P and z > 0"]
# allPect protein backbone 
set backbone [atomselect top "backbone"] 
# close P to protein
set closeP [atomselect top "(same residue as (within 10 of protein)) and not protein and name P and z > 0"]

# calculate number of atoms in each allPection
set numAllP [$allP num]
set numBackbone [$backbone num]
set numCloseP [$closeP num]

# open output file
set output [open $fOut w]

# Calculate number of frames in trajectory
set nf [molinfo top get numframes]


# iterate through trajectory
for {set i 0} {$i < $nf} {incr i} {

	# move allPections to current frame
	$allP frame $i
	$backbone frame $i
	$closeP frame $i

	# set sum to zero, and then interate through membrane P Atoms to get z coord
	set sum 0.0
	foreach coord [$allP get {z}] {
		set sum [expr {$sum + $coord}]
	}
	# calculate average z coord
	set avg [expr $sum / $numAllP]

	# Now do same for protein backbone
	set sum2 0.0
	foreach coord [$backbone get {z}] {
		set sum2 [expr {$sum2 + $coord}] 
	}
	set avg2 [expr $sum2 / $numBackbone]

	# Do same for close P
	set sum3 0.0
	foreach coord [$closeP get {z}] {
		set sum3 [expr {$sum3 + $coord}]
	}
	set avg3 [expr $sum3 / $numCloseP ]

	# calculate 'depth' of helix
	set diff [expr $avg2 - $avg]
	set diff2 [expr $avg2 - $avg3]
	set ts [expr ($i + $firstFrame) / 1000.0]
	puts $output "$ts $avg $avg3 $avg2 $diff $diff2"

}

close $output
exit

