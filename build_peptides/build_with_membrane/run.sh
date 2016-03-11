#!/bin/bash

module unload vmd
module load vmd

vmd=vmd



"$vmd" "-dispdev text -e ~/GITHUB/md-scripts/build_peptides/build_with_membrane/1.make_prot_lipid.tcl"
"$vmd" "-dispdev text -e ~/GITHUB/md-scripts/build_peptides/build_with_membrane/2.create_psf.tcl"
"$vmd" "-dispdev text -e ~/GITHUB/md-scripts/build_peptides/build_with_membrane/3.solvate.ionize.tcl"

python ~/GITHUB/md-scripts/build_peptides/build_with_membrane/4.fix_header.py
python ~/GITHUB/md-scripts/namd-to-gromacs/psf2itp.py ~/GITHUB/md-scripts/namd-to-gromacs/toppar final.ionized.psf 

mkdir output/restraints
cp ~/GITHUB/md-scripts/build_peptides/build_with_membrane/restraints/*.itp ./output/restraints


python ~/GITHUB/md-scripts/build_peptides/build_with_membrane/restraints/prot_restraints.py -i output/toppar/PROT.itp -o output/restraints/PROT_rest.itp

sed -i '' -e '$ d' output/toppar/ION.itp 
sed -i '' -e '$ d' output/toppar/ION.itp 
sed -i '' -e '$ d' output/toppar/ION.itp 

gmx_mpi make_ndx -f final.ionized.pdb -o output/index.ndx < ~/GITHUB/md-scripts/build_peptides/build_with_membrane/make_index.dat