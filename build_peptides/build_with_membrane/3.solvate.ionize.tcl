#solvate
package require solvate
solvate {memb_prot.psf} {memb_prot.pdb} -o solvate.1 -minmax {{0.0 0.0 60.0 } {39.6164 39.6164 90.0}}

solvate {solvate.1.psf} {solvate.1.pdb} -o solvate.2 -minmax {{0.0 0.0 0.0 } {39.6164 39.6164 14.0}} -s WA

#remove bad waters

# mol load psf {solvate.psf} pdb {solvate.pdb} 
# 
# set membTop [atomselect top "name P and z > 0"]
# set membBot [atomselect top "name P and z < 0"]
# 
# set maxZ [lindex [measure minmax $membTop] 0 2]
# 
# set minZ [lindex [measure minmax $membBot] 1 2]
# 
# set notWat [atomselect top "not (same residue as (water and z > $minZ and z < $maxZ))"]
# 
# 
# $notWat writepsf "new.solvate.psf"
# $notWat writepdb "new.solvate.pdb"

package require autoionize

autoionize -psf {solvate.2.psf} -pdb {solvate.2.pdb} -sc 0.15

mol load psf {ionized.psf} pdb {ionized.pdb} 

set sel [atomselect top "resname DOPE or resname POPC or resname SAPI"]
$sel set segname "MEMB"

set all [atomselect top "all"]
$all writepsf "new.ionized.psf"
$all writepdb "new.ionized.pdb"
$all writepdb "final.ionized.pdb"

exit