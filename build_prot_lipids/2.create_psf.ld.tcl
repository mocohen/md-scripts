package require psfgen

topology /Users/mocohen/Work/ccta/POPC-DOPE-SAPI/protein_sims/alps/droplet.40/top_all36_lipid.rtf
topology /Users/mocohen/Work/ccta/POPC-DOPE-SAPI/protein_sims/alps/droplet.40/top_all36_prot.rtf
topology /Users/mocohen/Work/ccta/POPC-DOPE-SAPI/protein_sims/alps/droplet.40/top_all36_carb.rtf
topology /Users/mocohen/Work/ccta/POPC-DOPE-SAPI/protein_sims/alps/droplet.40/toppar_all36_lipid_inositol.str
topology /Users/mocohen/Work/ccta/toppar/CholesterylOleate.top
topology /Users/mocohen/Work/ccta/toppar/Triolein.top

segment PROT { pdb prot_moved.pdb }
segment M1 { 
	pdb ../../bilayer.pdbs/popc.pdb 
}
segment M2 { 
	pdb ../../bilayer.pdbs/dope.pdb
}
segment M3 { 
	pdb ../../bilayer.pdbs/sapi.pdb
}
segment O1 { 
        pdb ../../droplet.pdbs/trio.pdb 
}
segment O2 { 
        pdb ../../droplet.pdbs/clol.pdb
}

coordpdb prot_moved.pdb PROT
coordpdb ../../bilayer.pdbs/popc.pdb M1
coordpdb ../../bilayer.pdbs/dope.pdb M2
coordpdb ../../bilayer.pdbs/sapi.pdb M3
coordpdb ../../droplet.pdbs/trio.pdb O1
coordpdb ../../droplet.pdbs/clol.pdb O2

guesscoord
writepsf x-plor memb_prot.psf
writepdb memb_prot.pdb 

exit
