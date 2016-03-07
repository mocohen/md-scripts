#!/bin/bash

vmd='/Users/mocohen/Work/source/VMD.1.9.2.app/Contents/MacOS/startup.command'

CCC=PHE
DDD=ILE

sed -i '.bak' "s/AAA/$CCC/g" backbone.pdb
sed -i '.bak' "s/BBB/$DDD/g" backbone.pdb


sed -i '.bak' "s/AAA/$CCC/g" build_peptide.tcl
sed -i '.bak' "s/BBB/$DDD/g" build_peptide.tcl

$vmd -dispdev text -e build_peptide.tcl


python ~/GitHub/md-scripts/build_peptide/fix_header.py -i solvate.psf -o final.psf
python ~/GitHub/md-scripts/namd-to-gromacs/psf2itp.py ~/GitHub/md-scripts/namd-to-gromacs/toppar final.psf 