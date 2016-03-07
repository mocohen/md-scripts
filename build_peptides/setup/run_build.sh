#!/bin/bash

CCC=PHE
DDD=ILE

GITHUB=~/GITHUB
vmd=vmd

sed -i "s/AAA/$CCC/g" backbone.pdb
sed -i "s/BBB/$DDD/g" backbone.pdb


sed -i "s/AAA/$CCC/g" build_peptide.tcl
sed -i "s/BBB/$DDD/g" build_peptide.tcl

$vmd -dispdev text -e build_peptide.tcl


python $GITHUB/md-scripts/build_peptides/fix_header.py -i solvate.psf -o final.psf
python $GITHUB/md-scripts/namd-to-gromacs/psf2itp.py $GITHUB/md-scripts/namd-to-gromacs/toppar final.psf 
