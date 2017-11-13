############## Check for input variables ##################

package require pbctools
package require psfgen
set begin [clock seconds]

set topDir1 /home/mocohen/GITHUB/md-scripts/namd-to-gromacs/ 
set topDir2 /project/gavoth/mocohen/charmm_param/
topology ${topDir1}toppar/top_all36_lipid.rtf
topology ${topDir1}toppar/top_all36_prot.rtf
topology ${topDir1}toppar/top_all36_carb.rtf
topology ${topDir1}toppar/toppar_all36_lipid_inositol.str
topology ${topDir2}CholesterylOleate.top
topology ${topDir2}Triolein.top


puts "read arguments"

if { [llength $argv] < 3} {
	puts "Specify three arguments!"
	exit
}

set firstNum 0


############## Set intput variables #######################
puts "set input variables"
set psf [lindex $argv 0] 
set dcd [lindex $argv 1] 
set outDir [lindex $argv 2] 
if { [llength $argv] >  3} {
	set firstNum [expr [lindex $argv 3] * 100]
}

# VMD requires the same number of atoms in an xyz file
# This will print out a file that will contain max_defects 
#    number of atoms at each time step
# If there are more than max_defects number of defects in any frame
#    it will crash. Simply increase max_defects and run again 
set max_defects 2000


# trajectory step size - set to 1 to include all frames
set step_size 1





############## Number of frames to run ####################

#set firstFrame [expr $firstNum * 125]
#set lastFrame [expr $firstFrame + 125]

#first frame in loaded trajectory
set first_frame 1
set firstFrame [expr 1 + $firstNum]




############## Set SASA input variables ###################

# width of slices along bilayer
#set delta_x 40.0
set delta_x 0.4
# radius of probe for SASA calc. 3.0 Ang is roughly the size of a bulky aliphatic side chain
set probe_radius 3.0
# width of buffer to eliminate contributions to SASA from edges
set buffer 12.0




############## Set output files ###########################
set ofile [open ${outDir}topAndBottom.xyz w]
set ofile_top [open ${outDir}top.xyz w]
set ofile_top_vmd [open ${outDir}top_vmd.xyz w]
set ofile_bot [open ${outDir}bottom.xyz w]
set ofile_bot_vmd [open ${outDir}bottom_vmd.xyz w] 

set tempDir "${outDir}temp/"
file mkdir $tempDir

#foreach pdb [lsort [glob ${tempDir}*.pdb]] {
#	file delete $pdb
#} 



############## load trajectory ############################
puts "read trajectory"
mol load gro $psf 
mol addfile $dcd waitfor all


set num_frames [molinfo top get numframes]





############## Define selection ###########################

#select not head groups with x and y exclusions
set text0 "(resname POPC and not (name C13 or name H13A or name H13B or name H13C or name N"
set text1 " or name C14 or name H14A or name H14B or name H14C or name C15 or name H15A or name H15B or name H15C"
set text2 " or name C12 or name H12A or name H12B or name C11 or name H11A or name H11B"
set text3 " or name P or name O11 or name O12 or name O13 or name O14 or name C1 or name HA or name HB"
set text4 " or name HS or name C2 or name C3 or name HX or name HY))"
set text5 " or (resname POPE and not (name N or name HN1 or name HN2 or name HN3"
set text6 " or name C12 or name H12A or name H12B or name C11 or name H11A or name H11B"
set text7 " or name O11 or name O12 or name O13 or name O14 or name P or name C1 or name HA or name HB"
set text8 " or name HS or name C2 or name C3 or name HX or name HY)) or resname CLOL or resname TRIO"
set text10 " or (resname SAPI and not (name C13 or name H3 or name O3 or name HO3 or name C11 or name H1"
set text11 " or name C12 or name H2 or name O2 or name HO2 or name C14 or name H4 or name O4 or name HO4"
set text12 " or name C15 or name H5 or name O5 or name HO5 or name C16 or name H6 or name O6 or name HO6"
set text13 " or name P or name O11 or name O12 or name O13 or name O14 or name C1 or name HA or name HB"
set text14 " or name HS or name C2 or name C3 or name HX or name HY)) or resname CLOL or resname TRIO"


############## Loop through frames ########################

for {set f $first_frame} {$f < [expr $num_frames / $step_size] } {incr f} {

	
	
	############## set current frame ##########################
	set dcdFrame [expr $f * $step_size]
	set theFrame [expr $dcdFrame + $firstFrame]
	molinfo top set frame $dcdFrame
	puts "working on frame $theFrame"
	
	
	
	############## Get box vectors ############################
	set xx [molinfo top get a]
	set yy [molinfo top get b]
	set zz [molinfo top get c]
	
	
	
	############## join bilayer in one image ##################
	
	set sel_move [atomselect top "not water and not ion and not protein and z > 50"]
	set thePBC [pbc get]
	set toMove [expr [lindex $thePBC 0 2] * -1]
	$sel_move moveby [list 0 0 $toMove] 
	

	############## move bilayer to center #####################
	
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
	set min [expr -1.0 * $xx / 2]
	set max [expr 1.0 * $xx / 2]
	set numbins [expr int(($max - $min)/$delta_x)]
	
	
	set text9 " and y > $min and y < $max and x > $min and x < $max"
	set seltext "${text0}${text1}${text2}${text3}${text4}${text5}${text6}${text7}${text8}${text10}${text11}${text12}${text13}${text14}${text9}"


	
	#######################################################
	############## create giant patch #####################
	#######################################################

	set sel [atomselect top "not water and not ion and not protein"]
	$sel set segname M0
	$sel writepdb ${tempDir}center.pdb

	set molList {}

	lappend molList [mol load pdb ${tempDir}center.pdb]
	set sel [atomselect top all]
	$sel set segname M1
	$sel moveby [list $xx $yy 0]
	$sel writepdb ${tempDir}moved1.pdb

	lappend molList [mol load pdb ${tempDir}center.pdb]
	set sel [atomselect top all]
	$sel set segname M2
	$sel moveby [list -$xx $yy 0]
	$sel writepdb ${tempDir}moved2.pdb

	lappend molList [mol load pdb ${tempDir}center.pdb]
	set sel [atomselect top all]
	$sel set segname M3
	$sel moveby [list -$xx -$yy 0]
	$sel writepdb ${tempDir}moved3.pdb

	lappend molList [mol load pdb ${tempDir}center.pdb]
	set sel [atomselect top all]
	$sel set segname M4
	$sel moveby [list $xx -$yy 0]
	$sel writepdb ${tempDir}moved4.pdb

	lappend molList [mol load pdb ${tempDir}center.pdb]
	set sel [atomselect top all]
	$sel set segname M5
	$sel moveby [list 0 $yy 0]
	$sel writepdb ${tempDir}moved5.pdb

	lappend molList [mol load pdb ${tempDir}center.pdb]
	set sel [atomselect top all]
	$sel set segname M6
	$sel moveby [list 0 -$yy 0]
	$sel writepdb ${tempDir}moved6.pdb

	lappend molList [mol load pdb ${tempDir}center.pdb]
	set sel [atomselect top all]
	$sel set segname M7
	$sel moveby [list -$xx 0 0]
	$sel writepdb ${tempDir}moved7.pdb

	lappend molList [mol load pdb ${tempDir}center.pdb]
	set sel [atomselect top all]
	$sel set segname M8
	$sel moveby [list $xx 0 0]
	$sel writepdb ${tempDir}moved8.pdb
	
	set nseg 1 
	
	foreach pdb [lsort [glob ${tempDir}*.pdb]] {
	  set segid V$nseg 
	  segment $segid { 
		first NONE
		last NONE
		pdb $pdb 
	  } 
	  coordpdb $pdb $segid
	  incr nseg
	} 
	guesscoord
	writepdb ${tempDir}mergedpdb.pdb
	resetpsf


	lappend molList [mol load pdb ${tempDir}mergedpdb.pdb]
	

	foreach pdb [lsort [glob ${tempDir}*.pdb]] {
		file delete $pdb
	} 
	

	#######################################################
	############## begin calculation ######################
	#######################################################

	
	set tails [atomselect top $seltext]
	#puts [$tails num]

	set bilayer [atomselect top "resname SAPI or resname DOPE or resname POPC or resname TRIO or resname CLOL"]

	measure sasa $probe_radius $bilayer -points sasa_surface -restrict $tails
	
	#set debug [open debug.txt w]
	set numpoints [llength $sasa_surface]
	#puts $numpoints
	#puts $sasa_surface
	#puts $ofile "$numpoints"
	#puts $ofile "frame $theFrame"
	
	#$sel_move delete
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
		if {$z > 0 && $x > $min && $x < $max && $y > $min && $y < $max  } {		
			lappend topDat $point
		} elseif { $z <= 0 && $x > $min && $x < $max && $y > $min && $y < $max } {
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
	puts $ofile "$numTot $numTop $numBot"
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

	foreach molPDB $molList {
		mol delete $molPDB
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
