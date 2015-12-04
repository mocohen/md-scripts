set pdb "newpuredopc.pdb"
set psf "newpuredopc.psf"
set segvar "O1"

package require psfgen

mol load psf $psf pdb $pdb
set all [atomselect top "all"]
set x [molinfo top get a]
set y [molinfo top get b]
set z [molinfo top get c]

#puts "$x $y $z"

#############################################  1ST LAYER   ###############################

mol load psf $psf pdb $pdb
set segD [atomselect top "segname O1"]
$segD set segname N11
set all [atomselect top "all"]
$all moveby "125 125 0"
$all writepdb moved11.pdb


mol load psf $psf pdb $pdb
set segD [atomselect top "segname O1"]
$segD set segname N12
set all [atomselect top "all"]
$all moveby "75 125 0"
$all writepdb moved12.pdb

mol load psf $psf pdb $pdb
set segD [atomselect top "segname O1"]
$segD set segname N13
set all [atomselect top "all"]
$all moveby "25 125 0"
$all writepdb moved13.pdb


mol load psf $psf pdb $pdb
set segD [atomselect top "segname O1"]
$segD set segname N14
set all [atomselect top "all"]
$all moveby "-25 125 0"
$all writepdb moved14.pdb

mol load psf $psf pdb $pdb
set segD [atomselect top "segname O1"]
$segD set segname N15
set all [atomselect top "all"]
$all moveby "-75 125 0"
$all writepdb moved15.pdb


mol load psf $psf pdb $pdb
set segD [atomselect top "segname O1"]
$segD set segname N16
set all [atomselect top "all"]
$all moveby "-125 125 0"
$all writepdb moved16.pdb

############################################### 2ND LAYER  #######################


mol load psf $psf pdb $pdb
set segD [atomselect top "segname O1"]
$segD set segname N21
set all [atomselect top "all"]
$all moveby "125 75 0"
$all writepdb moved21.pdb


mol load psf $psf pdb $pdb
set segD [atomselect top "segname O1"]
$segD set segname N22
set all [atomselect top "all"]
$all moveby "75 75 0"
$all writepdb moved22.pdb

mol load psf $psf pdb $pdb
set segD [atomselect top "segname O1"]
$segD set segname N23
set all [atomselect top "all"]
$all moveby "25 75 0"
$all writepdb moved23.pdb


mol load psf $psf pdb $pdb
set segD [atomselect top "segname O1"]
$segD set segname N24
set all [atomselect top "all"]
$all moveby "-25 75 0"
$all writepdb moved24.pdb

mol load psf $psf pdb $pdb
set segD [atomselect top "segname O1"]
$segD set segname N25
set all [atomselect top "all"]
$all moveby "-75 75 0"
$all writepdb moved25.pdb


mol load psf $psf pdb $pdb
set segD [atomselect top "segname O1"]
$segD set segname N26
set all [atomselect top "all"]
$all moveby "-125 75 0"
$all writepdb moved26.pdb

############################################### 3RD LAYER  #######################
mol load psf $psf pdb $pdb
set segD [atomselect top "segname O1"]
$segD set segname N31
set all [atomselect top "all"]
$all moveby "125 25 0"
$all writepdb moved31.pdb


mol load psf $psf pdb $pdb
set segD [atomselect top "segname O1"]
$segD set segname N32
set all [atomselect top "all"]
$all moveby "75 25 0"
$all writepdb moved32.pdb

mol load psf $psf pdb $pdb
set segD [atomselect top "segname O1"]
$segD set segname N33
set all [atomselect top "all"]
$all moveby "25 25 0"
$all writepdb moved33.pdb


mol load psf $psf pdb $pdb
set segD [atomselect top "segname O1"]
$segD set segname N34
set all [atomselect top "all"]
$all moveby "-25 25 0"
$all writepdb moved34.pdb

mol load psf $psf pdb $pdb
set segD [atomselect top "segname O1"]
$segD set segname N35
set all [atomselect top "all"]
$all moveby "-75 25 0"
$all writepdb moved35.pdb


mol load psf $psf pdb $pdb
set segD [atomselect top "segname O1"]
$segD set segname N36
set all [atomselect top "all"]
$all moveby "-125 25 0"
$all writepdb moved36.pdb

############################################### 4TH LAYER  #######################

mol load psf $psf pdb $pdb
set segD [atomselect top "segname O1"]
$segD set segname N41
set all [atomselect top "all"]
$all moveby "125 -25 0"
$all writepdb moved41.pdb


mol load psf $psf pdb $pdb
set segD [atomselect top "segname O1"]
$segD set segname N42
set all [atomselect top "all"]
$all moveby "75 -25 0"
$all writepdb moved42.pdb

mol load psf $psf pdb $pdb
set segD [atomselect top "segname O1"]
$segD set segname N43
set all [atomselect top "all"]
$all moveby "25 -25 0"
$all writepdb moved43.pdb


mol load psf $psf pdb $pdb
set segD [atomselect top "segname O1"]
$segD set segname N44
set all [atomselect top "all"]
$all moveby "-25 -25 0"
$all writepdb moved44.pdb

mol load psf $psf pdb $pdb
set segD [atomselect top "segname O1"]
$segD set segname N45
set all [atomselect top "all"]
$all moveby "-75 -25 0"
$all writepdb moved45.pdb


mol load psf $psf pdb $pdb
set segD [atomselect top "segname O1"]
$segD set segname N46
set all [atomselect top "all"]
$all moveby "-125 -25 0"
$all writepdb moved46.pdb

############################################### 5TH LAYER  #######################


mol load psf $psf pdb $pdb
set segD [atomselect top "segname O1"]
$segD set segname N51
set all [atomselect top "all"]
$all moveby "125 -75 0"
$all writepdb moved51.pdb


mol load psf $psf pdb $pdb
set segD [atomselect top "segname O1"]
$segD set segname N52
set all [atomselect top "all"]
$all moveby "75 -75 0"
$all writepdb moved52.pdb

mol load psf $psf pdb $pdb
set segD [atomselect top "segname O1"]
$segD set segname N53
set all [atomselect top "all"]
$all moveby "25 -75 0"
$all writepdb moved53.pdb


mol load psf $psf pdb $pdb
set segD [atomselect top "segname O1"]
$segD set segname N54
set all [atomselect top "all"]
$all moveby "-25 -75 0"
$all writepdb moved54.pdb

mol load psf $psf pdb $pdb
set segD [atomselect top "segname O1"]
$segD set segname N55
set all [atomselect top "all"]
$all moveby "-75 -75 0"
$all writepdb moved55.pdb


mol load psf $psf pdb $pdb
set segD [atomselect top "segname O1"]
$segD set segname N56
set all [atomselect top "all"]
$all moveby "-125 -75 0"
$all writepdb moved56.pdb

############################################### 6TH LAYER  #######################

mol load psf $psf pdb $pdb
set segD [atomselect top "segname O1"]
$segD set segname N61
set all [atomselect top "all"]
$all moveby "125 -125 0"
$all writepdb moved61.pdb


mol load psf $psf pdb $pdb
set segD [atomselect top "segname O1"]
$segD set segname N62
set all [atomselect top "all"]
$all moveby "75 -125 0"
$all writepdb moved62.pdb

mol load psf $psf pdb $pdb
set segD [atomselect top "segname O1"]
$segD set segname N63
set all [atomselect top "all"]
$all moveby "25 -125 0"
$all writepdb moved63.pdb


mol load psf $psf pdb $pdb
set segD [atomselect top "segname O1"]
$segD set segname N64
set all [atomselect top "all"]
$all moveby "-25 -125 0"
$all writepdb moved64.pdb

mol load psf $psf pdb $pdb
set segD [atomselect top "segname O1"]
$segD set segname N65
set all [atomselect top "all"]
$all moveby "-75 -125 0"
$all writepdb moved65.pdb


mol load psf $psf pdb $pdb
set segD [atomselect top "segname O1"]
$segD set segname N66
set all [atomselect top "all"]
$all moveby "-125 -125 0"
$all writepdb moved66.pdb

###############################################

exit
