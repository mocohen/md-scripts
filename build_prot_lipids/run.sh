#!/bin/bash

vmd=/Users/mocohen/Work/source/VMD\ 1.9.2.app/Contents/MacOS/startup.command

"$vmd" "-dispdev text -e ~/GitHub/md-scripts/build_prot_lipids/1.make_prot_lipid.tcl"
"$vmd" "-dispdev text -e ~/GitHub/md-scripts/build_prot_lipids/2.create_psf.tcl"
"$vmd" "-dispdev text -e ~/GitHub/md-scripts/build_prot_lipids/3.solvate.ionize.tcl"

python ~/GitHub/md-scripts/build_prot_lipids/4.fix_header.py
python ~/GitHub/md-scripts/namd-to-gromacs/psf2itp.py ~/GitHub/md-scripts/namd-to-gromacs/toppar final.ionized.psf 

mkdir output/restraints