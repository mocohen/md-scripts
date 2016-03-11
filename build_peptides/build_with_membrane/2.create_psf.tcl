package require psfgen
set topDir "/Users/mocohen/GitHub/md-scripts/namd-to-gromacs/toppar/"

topology "${topDir}top_all36_lipid.rtf"
topology "${topDir}top_all36_prot.rtf"
topology "${topDir}top_all36_carb.rtf"
topology "${topDir}toppar_all36_lipid_inositol.str"
topology "${topDir}top_water_ions.rtf"

alias residue HIS HSE

segment PROT { 
	first ACE 
	pdb prot_moved.pdb 
	last CT1
}
segment M1 { 
	pdb ../../bilayer.pdbs/popc.pdb 
}
segment M2 { 
	pdb ../../bilayer.pdbs/dope.pdb
}
segment M3 { 
	pdb ../../bilayer.pdbs/sapi.pdb
}

segment WT0 {
	pdb ../../bilayer.pdbs/close_water.pdb
}


coordpdb prot_moved.pdb PROT
coordpdb ../../bilayer.pdbs/popc.pdb M1
coordpdb ../../bilayer.pdbs/dope.pdb M2
coordpdb ../../bilayer.pdbs/sapi.pdb M3
coordpdb ../../bilayer.pdbs/close_water.pdb WT0

guesscoord
writepsf x-plor memb_prot.psf
writepdb memb_prot.pdb 

exit
