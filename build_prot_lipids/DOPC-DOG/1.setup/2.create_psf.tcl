package require psfgen

set theDir "/Users/mocohen/Work/ccta/DOPC-DOG/bilayer_membrane/2.toppar"

topology ${theDir}/top_all36_lipid.rtf
topology ${theDir}/top_all36_prot.rtf
topology ${theDir}/top_all36_carb.rtf
topology ${theDir}/toppar_all36_lipid_inositol.str
topology ${theDir}/top_all36_DOG.rtf 

alias residue HIS HSE

segment PROT { pdb prot_moved.pdb }
segment M1 { 
	pdb ../../../bilayer.pdbs/dopc.pdb 
}
segment M2 { 
	pdb ../../../bilayer.pdbs/dog.pdb
}


coordpdb prot_moved.pdb PROT
coordpdb ../../../bilayer.pdbs/dopc.pdb M1
coordpdb ../../../bilayer.pdbs/dog.pdb M2

guesscoord
writepsf x-plor memb_prot.psf
writepdb memb_prot.pdb 

exit
