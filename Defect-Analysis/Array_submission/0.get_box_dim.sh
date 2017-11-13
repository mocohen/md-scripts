#!/bin/bash

#printf "[ System ]\n   1   " > temp.ndx

#$GMX trjconv -f /project/gavoth/mocohen/ccta/POPC-DOPE-SAPI/40-patch/build_box/droplet.40/3.run/run.xtc -s /project/gavoth/mocohen/ccta/POPC-DOPE-SAPI/40-patch/build_box/droplet.40/3.run/run.tpr -o temp.pdb -n temp.ndx -dt 1

grep "CRYST1" temp.pdb > cryst.dat
grep "TITLE" temp.pdb > title.dat

paste title.dat cryst.dat | awk '{print $4, $6, $7}' > box.dim.xvg

rm -f cryst.dat title.dat temp.ndx temp.ndx
