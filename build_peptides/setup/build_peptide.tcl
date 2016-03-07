package require psfgen
package require solvate 




topology ~/GITHUB/md-scripts/namd-to-gromacs/toppar/top_all36_prot.rtf


segment PROT {
	first ACE
	residue 1 ALA
	residue 2 AAA
	residue 3 BBB
	residue 4 ALA
	last CT1
}

coordpdb backbone.pdb PROT

guesscoord

writepsf "peptide.psf"
writepdb "peptide.pdb"

solvate {peptide.psf} {peptide.pdb} -o solvate -minmax {{-20 -20 -20} {20 20 20}}

exit
