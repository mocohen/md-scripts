#psf and dcd
set begin [clock seconds]
#set psf stripped.psf
#set dcd production/step1/stripped.ranDefLipid3.1ns.dcd 

if { [llength $argv] < 3} {
	puts "Specify three arguments!"
	exit
}

set firstFrame 0
# Set intput variables
set psf [lindex $argv 0] 
set dcd [lindex $argv 1] 
set outDir [lindex $argv 2] 
if { [llength $argv] >  3} {
	set firstFrame [lindex $argv 3]
}

# VMD requires the same number of atoms in an xyz file
# This will print out a file that will contain max_defects 
#    number of atoms at each time step
# If there are more than max_defects number of defects in any frame
#    it will crash. Simply increase max_defects and run again 
set max_defects 3000

# width of slices along bilayer
#set delta_x 40.0
set delta_x 0.4
# radius of probe for SASA calc. 3.0 Ang is roughly the size of a bulky aliphatic side chain
set probe_radius 3.0
# width of buffer to eliminate contributions to SASA from edges
set buffer 12.0

set ofile [open ${outDir}topAndBottom.xyz w]
set ofile_top [open ${outDir}top.xyz w]
set ofile_top_vmd [open ${outDir}top_vmd.xyz w]
set ofile_bot [open ${outDir}bottom.xyz w]
set ofile_bot_vmd [open ${outDir}bottom_vmd.xyz w] 




#load trajectory
mol load psf $psf dcd $dcd
set first_frame 0
set num_frames [molinfo top get numframes]
# trajectory step size - set to 1 to include all frames
set step_size 10

#select not head groups with x and y exclusions
set text1 "(resname DOPG and not (name H13A or name C13 or name H13A or name H13B or name OC3 or name HO3"
set text2 " or name C12 or name H12A or name OC2 or name HO2 or name C11 or name H11A or name H11B"
set text3 " or name P or name O11 or name O12 or name O13 or name O14 or name C1 or name HA or name HB"
set text4 " or name HS or name C2 or name C3 or name HX or name HY))"
set text5 " or (resname DOPE and not (name N or name HN1 or name HN2 or name HN3"
set text6 " or name C12 or name H12A or name H12B or name C11 or name H11A or name H11B"
set text7 " or name O11 or name O12 or name O13 or name O14 or name P or name C1 or name HA or name HB"
set text8 " or name HS or name C2 or name C3 or name HX or name HY))"


#load frame here...
for {set f $first_frame} {$f < [expr $num_frames / $step_size] } {incr f} {

	set theFrame [expr ($f * $step_size) + $firstFrame]
	#set f 2
	molinfo top set frame $theFrame
	puts "working on frame $theFrame"
	
	# center bilayer
	#$sel_P frame $theFrame
	
	set sel_P [atomselect top "name P"]
	set centerOfP [measure center $sel_P]
	set x [expr -1.0*[lindex $centerOfP 0]]
	set y [expr -1.0*[lindex $centerOfP 1]]
	set z [expr -1.0*[lindex $centerOfP 2]]
	set all [atomselect top "all"]
	set move_vec [list $x $y $z] 
	$all moveby $move_vec
	
	
	#average z coords of phosphates in slices of width delta_x to define the membrane midplane
	#set sel_P [atomselect top "name P"]
	set pMinMax [measure minmax $sel_P]
	set x_min [lindex [lindex $pMinMax 0] 0]
	set x_max [lindex [lindex $pMinMax 1] 0]
	set numbins [expr int(($x_max - $x_min)/$delta_x)]
	
	set sasa_y_min [expr [lindex [lindex $pMinMax 0] 1] + $buffer] 
	set sasa_y_max [expr [lindex [lindex $pMinMax 1] 1] - $buffer]
	set sasa_x_min [expr [lindex [lindex $pMinMax 0] 0] + $buffer]
	set sasa_x_max [expr [lindex [lindex $pMinMax 1] 0] - $buffer]
	
	set text9 " and y > $sasa_y_min and y < $sasa_y_max and x > $sasa_x_min and x < $sasa_x_max"
	set seltext "${text1}${text2}${text3}${text4}${text5}${text6}${text7}${text8}${text9}"
	
	set tails [atomselect top $seltext]
	puts [$tails num]

	set bilayer [atomselect top "resname DOPE or resname DOPG"]

	measure sasa $probe_radius $bilayer -points sasa_surface -restrict $tails
	
	#set debug [open debug.txt w]
	set numpoints [llength $sasa_surface]
	#puts $numpoints
	#puts $sasa_surface
	#puts $ofile "$numpoints"
	#puts $ofile "frame $theFrame"

	$sel_P delete
	$tails delete
	$bilayer delete

	
	#set ofile [open debug.txt w]
	
	#this list will hold the projected points after the first iteration
	#set projected_points [list]
	#Test
	set topDat {}
	set bottomDat {}
	foreach point $sasa_surface {
		#project sasa points onto the local midplane
		set x [lindex $point 0]		
		set y [lindex $point 1]		
		set z [lindex $point 2]
		if {$z > 0 && $x > $sasa_x_min && $x < $sasa_x_max && $y > $sasa_y_min && $y < $sasa_y_max  } {		
			lappend topDat $point
		} elseif { $z <= 0 && $x > $sasa_x_min && $x < $sasa_x_max && $y > $sasa_y_min && $y < $sasa_y_max } {
			lappend bottomDat $point
		}
	}
	set numTop [llength $topDat]
	set numBot [llength $bottomDat]
	if {$numBot > $max_defects || $numTop > $max_defects} {
		puts "ERROR: Increase max_defects and run again"
		puts "max_defects should be greater than $numBot and $numTop"
		exit
	}
	set numTot [expr $numTop + $numBot]
	puts $ofile "$numTot"
	puts $ofile "frame $theFrame"
	puts $ofile_top "$numTop"
	puts $ofile_top "frame $theFrame"
	puts $ofile_top_vmd "$max_defects"
	puts $ofile_top_vmd "frame $theFrame"
	foreach point $topDat {
		set x [lindex $point 0]
		set y [lindex $point 1]
		puts $ofile "T $x $y 0.0"
		puts $ofile_top "T $x $y 0.0"
		puts $ofile_top_vmd "T $x $y 0.0"

	}
	
	for {set i $numTop} {$i < $max_defects } {incr i} {
		puts $ofile_top_vmd "T -100.0 -100.0 -10.0"
	}
	
	puts $ofile_bot "$numBot"
	puts $ofile_bot "frame $theFrame"
	puts $ofile_bot_vmd "$max_defects"
	puts $ofile_bot_vmd "frame $theFrame"
	foreach point $bottomDat {
		set x [lindex $point 0]
		set y [lindex $point 1]
		puts $ofile "B $x $y 0.0"
		puts $ofile_bot "B $x $y 0.0"
		puts $ofile_bot_vmd "B $x $y 0.0"
	}
	
	for {set i $numBot} {$i < $max_defects } {incr i} {
		puts $ofile_bot_vmd "B -100.0 -100.0 -10.0"
	}

	
}

flush $ofile
close $ofile

flush $ofile_top
close $ofile_top

flush $ofile_top_vmd
close $ofile_top_vmd

flush $ofile_bot
close $ofile_bot

flush $ofile_bot_vmd
close $ofile_bot_vmd

#flush $ofile
#close $ofile

#flush $ofile_xy
#close $ofile_xy
set end [clock seconds]
set total_time [expr $end - $begin]
set minutes [ expr $total_time / 60.0 ]
puts "Time: $total_time seconds or $minutes minutes"

exit 
