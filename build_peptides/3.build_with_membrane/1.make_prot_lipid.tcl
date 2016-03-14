#display resetview
#mol addrep 0
#display resetview
mol new {/project/gavoth/mocohen/ccta/peptides/bilayer.pdbs/membrane.pdb} type {pdb} first 0 last -1 step 1 waitfor 1
#animate style Loop
#display resetview
#mol addrep 1
#display resetview
mol new {prot.pdb} type {pdb} first 0 last -1 step 1 waitfor 1
#animate style Loop



set membTop [atomselect 0 "name P and z > 30"]
set posMembTop [measure center $membTop]
set prot [atomselect 1 "protein"]
set posProt [measure center $prot]

set moving [vecsub $posMembTop $posProt]
set theMove [vecadd $moving {0 0 20}]
$prot moveby $theMove
$prot writepdb "prot_moved.pdb"

set minMax [measure minmax $prot]
set minZ [lindex $minMax 0 2]
set tempZ [expr $minZ - [lindex $posMembTop 2]]
set moveZ [expr 20 - $tempZ]
set theTemp [list 0 0 $moveZ]
$prot moveby $theTemp
$prot writepdb "prot_moved.pdb"


exit
