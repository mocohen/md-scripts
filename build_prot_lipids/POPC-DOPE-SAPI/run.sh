#!/bin/bash

vmd=/Users/mocohen/Work/source/VMD.1.9.2.app/Contents/MacOS/startup.command

"$vmd" "-dispdev text -e ~/GitHub/md-scripts/build_prot_lipids/1.make_prot_lipid.tcl"
"$vmd" "-dispdev text -e ~/GitHub/md-scripts/build_prot_lipids/2.create_psf.tcl"
"$vmd" "-dispdev text -e ~/GitHub/md-scripts/build_prot_lipids/3.solvate.ionize.tcl"

python ~/GitHub/md-scripts/build_prot_lipids/4.fix_header.py
python ~/GitHub/md-scripts/namd-to-gromacs/psf2itp.py ~/GitHub/md-scripts/namd-to-gromacs/toppar final.ionized.psf 

mkdir output/restraints
cp /Users/mocohen/GitHub/md-scripts/build_prot_lipids/restraints/*.itp ./output/restraints


python ~/GitHub/md-scripts/build_prot_lipids/restraints/prot_restraints.py -i output/toppar/PROT.itp -o output/restraints/PROT_rest.itp

sed -i '' -e '$ d' output/toppar/ION.itp 
sed -i '' -e '$ d' output/toppar/ION.itp 
sed -i '' -e '$ d' output/toppar/ION.itp 

gmx_mpi_d make_ndx -f final.ionized.pdb -o output/index.ndx < /Users/mocohen/GitHub/md-scripts/build_prot_lipids/make_index.dat
