#!/usr/bin/perl -w
use Time::localtime;

#  This script opens SLURM batch script and NAMD input
#   and prepares them for another run.  Assumes
#   NAMD INPUT/OUTPUT FILE: dyna.inp / step###.out
#   PBS FILE: myjob.sub
#   NAMD OUTPUT FOLDER: ../step###/
#   NAMD DYNAMICS: 1000000 steps

$jobname='';
$resubmit=0;
$system="surfaceHelix";

# Open PBS batch file to see what job just ended.
open (SUB,"myjob.sub") or die "No myjob.sub batch script. DIE!\n";
while (<SUB>) {
	if ($_=~/step(\d+).out/) {
		$done=$1;
		$next=$done + 1;
		$old=$done - 1;
		$oldtime=$old *1000000;
		$nexttime=$next * 1000000;
		$donetime=$done * 1000000;
	}
	$jobname=$1 if ($_=~/PBS -N (\w+)/);		
}
# Check output file for job completion
open (OUT,"../step$done/step$done.out") or die "NO step$done.out\nDid you run this script twice?\n";
while (<OUT>) {
	if ($_=~/CPUTime/) {
	print "Normal NAMD Termination in step$done.out\n";
		$resubmit=1;
	}
}


# Job didn't complete, email me and DIE!
if ($resubmit==0) {
	print "NAMD did not terminate normally in step$done.out.\n";
	$subject="Something is wrong on Ranger";
	$email="9176993314\@messaging.sprintpcs.com";
	$body="A NAMD job didn't finish on GROTTHUS.  Look at system $system job $jobname $done in step$done.out.\n";
	open (MIL,"|/usr/sbin/sendmail -t");
	print( MIL "From: death\@tonka.bu.edu\n"); 
	print(MIL "Date: ".ctime()."\n");
	print(MIL "To: $email\n");
	print(MIL "Subject: $subject\n");
	print(MIL "\n");
	print(MIL "$body\n");
	close(MIL);
	die;
}

# remove stupid NAMD files since job died ok
system("rm -f ../step$done/*.restart.* ../step$done/*.old ../output/step$done/*.BAK");

# write a new SLURM submission file
open (SUB,"<myjob.sub") or die "No myjob.sub\n";
open (NEWSUB,">myjob_new.sh") or die "Cannot open myjob.sub\n";
while (<SUB>) {
  	$_=~s/step$done/step$next/;
	$_=~s/step$done/step$next/;
	print NEWSUB $_;
}
close (SUB);
close (NEWSUB);

# read old dyna.inp and make new dyna.inp
#   assuming 500,000 steps in each run!!!!
open (IN,"<../input/dyna.inp") or die "Cannot open dyna.in\n";
open (NEWIN,">../input/dyna_new.inp") or die "Cannot open dyna_new.inp\n";
while (<IN>) {
	$_=~s/step$done/step$next/;
	$_=~s/step$old/step$done/;
	$_=~s/$system.$done/$system.$next/;
	$_=~s/$system.$old/$system.$done/;
	$_=~s/$donetime/$nexttime/;
	$_=~s/$oldtime/$donetime/;
	print NEWIN $_;
}

# replace old PBS and DYN scripts 
system ("mv myjob_new.sh myjob.sub");
system ("mv dyna_new.inp dyna.inp");


print "resubmitting next run\n";
system ("mkdir ../step$next");
system ("sbatch myjob.sub") if ($resubmit==1);
