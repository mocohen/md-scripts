#mol new ionizeBuried.psf psf waitfor all
#animate read pdb ionizeBuried.pdb
# Periodic Boundary Conditions
set sel [atomselect top all]
set cen [measure center $sel]
set mm [measure minmax $sel]
puts $mm
set vmin [lindex $mm 0]
set vmax [lindex $mm 1]
set vdif [vecsub $vmax $vmin]
set xx [lindex $vdif 0]
set yy [lindex $vdif 1]
set zz [lindex $vdif 2]
set cenx [lindex $cen 0]
set ceny [lindex $cen 1]
set cenz [lindex $cen 2]
set padding 0
# PME (for full-system periodic electrostatics)
package require pmepot
set gridsizex [::PMEPot::good_fft_dim $xx]
set gridsizey [::PMEPot::good_fft_dim $yy]
set gridsizez [::PMEPot::good_fft_dim $zz]
puts "TO_NAMD:cellBasisVector1    [expr $xx+$padding]    0.   0."
puts "TO_NAMD:cellBasisVector2     0.   [expr $yy+$padding]   0."
puts "TO_NAMD:cellBasisVector3     0.    0   [expr $zz+$padding]"
puts "TO_NAMD:cellOrigin          $cenx $ceny $cenz"
puts "TO_NAMD:wrapAll             on"
puts "TO_NAMD:PME                 yes"
puts "TO_NAMD:PMEGridSizeX        $gridsizex"
puts "TO_NAMD:PMEGridSizeY        $gridsizey"
puts "TO_NAMD:PMEGridSizeZ        $gridsizez"
#exit
