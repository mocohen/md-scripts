#! /usr/bin/perl -w
$len = @ARGV;
if($len != 5 ){
	die "usage:  xyzfile  outDir  cutoff  gridsize min_clust_size\n";
}

$datafile = shift(@ARGV);
$outDir = shift(@ARGV);
$cutoff = shift(@ARGV); # cutoff distance for building adjacency matrix. 2.5 seems to work
$gridsize = shift(@ARGV); # size of the grid for estimating cluster size. 0.4 seems to make sense.
$min_c_size = shift(@ARGV); # clusters with fewer points than this will not be considered in the area calc

print "input params:\n";
print "datafile: $datafile\ncutoff: $cutoff\ngrid size: $gridsize\nmin clust size: $min_c_size\n";

# output files
open(CLUSTER_SIZES_TL, ">$outDir/TOP-LEAF-CLUSTERS.dat");
open(CLUSTER_SIZES_BL, ">$outDir/BOTTOM-LEAF-CLUSTERS.dat");


open(IN, "$datafile");
while(<IN>){

	@line = split;
	$len = @line;
	if($len == 1){
		# read number of points in this frame
		$total_points = $line[0];
		$top_point_count = 0;
		$bottom_point_count = 0;
		$count = 0;
	}
	elsif($len == 2){
		# read the number of this frame
		$frame = $line[1];
		print CLUSTER_SIZES_TL "frame: $frame\n";
		print CLUSTER_SIZES_BL "frame: $frame\n";
	}
	else{
		# read points
		$count++;
        	if(/T/){
                	$top_point_count++;
                	@line = split;
                	$x_top_point[$top_point_count] = $line[1];
                	$y_top_point[$top_point_count] = $line[2];
        	}
        	elsif(/B/){
                	$bottom_point_count++;
                	@line = split;
                	$x_bottom_point[$bottom_point_count] = $line[1];
                	$y_bottom_point[$bottom_point_count] = $line[2];
        	}
		if($count == $total_points){
			$num_top_points = $top_point_count;
			$num_bottom_points = $bottom_point_count;

			# done reading points for one frame

			###########################################################
			#							  #
			#		CLUSTER AND AREA CALC: TOP LEAFLET        #
			#							  #
			###########################################################
			
			# initialize adjacency matrix
			for($i=1;$i<=$num_top_points;$i++){
        			for($j=1;$j<=$num_top_points;$j++){
                			$adj[$i][$j] = 0;}}
			#compute pairwise distances and build (i) adjacency matrix adj[][] and (ii) neighbor list nl[]
			for($i=1;$i<=$num_top_points;$i++){
				for($j=$i+1;$j<=$num_top_points;$j++){
					$d[$i][$j] = sqrt(($x_top_point[$i] - $x_top_point[$j])**2 + ($y_top_point[$i] - $y_top_point[$j])**2);
					if($d[$i][$j] < $cutoff){
						$adj[$i][$j] = $adj[$j][$i] = 1;}}}
			# c_member[numpoints] will track cluster membership
			for($i=1;$i<=$num_top_points;$i++){
				$c_member[$i] = -1;}
			
			# point_list is an array which is 0 
			# every point in it. whenever a point is added to a cluster, it is removed from point_list.
			# whenever a new cluster is started, it starts at the first entry in point_list. (so i guess it's a queue)
			# when point_list is empty, we are done. (note that point_list is indexed from 0 so that shift() doesn't return an 
			# undefined entry)
			
			print "starting clustering calc for top leaflet of frame $frame...\n";		
	
			$k = 0;
			$points_left = $num_top_points;
			while($points_left > 0){

                # $k will be the index of the cluster. increment each time a new cluster starts
                $k++;
                # c_size will count points in the cluster
                $c_size = 0;
                
                for($i=1;$i<=$num_top_points;$i++){
                    if($c_member[$i] < 0){
                        # find the next point which has not yet been clustered to serve as the next starting point. 
                        # assign that point to $c_start. assign starting point to current cluster, 
                        # decrement points_left,  exit the loop
                        $c_start = $i;
                        $c_member[$c_start] = $k;
                        $points_left--;
                        $c_size++;
                        # these arrays will hold x, y coords of cluster points as it builds
                        $x_clust[$c_size] = $x_top_point[$i];
                        $y_clust[$c_size] = $y_top_point[$i];
                        last; 
                    }
                }
                
                # find neighbors of starting point and add them to the queue
                for($i=1;$i<=$num_top_points;$i++){
                    if($adj[$c_start][$i] == 1){
                        push(@queue,$i);
                        # a check on the scheme
                        if($c_member[$i] > 0){die "point i has already been clustered.\n";} 
                    }
                }
                # BF search
                while($i = shift(@queue)){
                    
                    #has i been visited yet? if not...
                    if($c_member[$i] < 0){
                        # i now marked as visited. decrement points_left. set points_list[$i] = 0
                        $c_member[$i] = $k;
                        $points_left--;
                        $c_size++;
                        $x_clust[$c_size] = $x_top_point[$i];
                        $y_clust[$c_size] = $y_top_point[$i];
                        #look at every neighbor of i
                        for($j=1;$j<=$num_top_points;$j++){
                            if($adj[$i][$j] == 1){
                                # i and j are neighbors. has j been visited? if not push j onto the end of the queue
                                if($c_member[$j] < 0){
                                    push(@queue, $j);
                                }
                            }
                        }
                    }
                    
                }# end breadth first search
                # calculate area of the just built cluster
                if($c_size > $min_c_size){
                    # set up grid for cluster size estimate
                    $x_min = 10e6;
                    $y_min = 10e6;
                    $x_max = -10000000;
                    $y_max = -10000000;
                    for($i=1;$i<=$c_size;$i++){
                        if($x_clust[$i] < $x_min){$x_min = $x_clust[$i];}
                        if($x_clust[$i] > $x_max){$x_max = $x_clust[$i];}
                        if($y_clust[$i] < $y_min){$y_min = $y_clust[$i];}
                        if($y_clust[$i] > $y_max){$y_max = $y_clust[$i];}
                    }
                    #initialize grid
                    $num_x_bins = int(($x_max - $x_min)/$gridsize) + 1;
                    $num_y_bins = int(($y_max - $y_min)/$gridsize) + 1;
                    for($i=1;$i<=$num_x_bins;$i++){
                        for($j=1;$j<=$num_y_bins;$j++){
                			$bin[$i][$j] = 0;
                        }
                    }
                    
                    $area = 0.0;
                    $perbin_area = $gridsize**2;
                    $x_com = 0.0;
                    $y_com = 0.0;
                    for($i=1;$i<=$c_size;$i++){
                        $x_bin = int(($x_clust[$i] - $x_min)/$gridsize) + 1;
                        $y_bin = int(($y_clust[$i] - $y_min)/$gridsize) + 1;
                        $x_com += $x_clust[$i];
                        $y_com += $y_clust[$i];
                        if($bin[$x_bin][$y_bin] == 0){
                            $bin[$x_bin][$y_bin]++;
                            $area += $perbin_area;
                        }
                    }
                    $x_com /= $c_size;
                    $y_com /= $c_size;
                    print CLUSTER_SIZES_TL "Cluster $k  $x_com  $y_com  $area\n";
                }
			} # end of while loop clustering all top leaf points
 
			###########################################################
			#							  #
			#		CLUSTER AND AREA CALC: BOTTOM LEAFLET     #
			#							  #
			###########################################################
			
			# initialize adjacency matrix
			for($i=1;$i<=$num_bottom_points;$i++){
        			for($j=1;$j<=$num_bottom_points;$j++){
                			$adj[$i][$j] = 0;}}
			#compute pairwise distances and build (i) adjacency matrix adj[][] and (ii) neighbor list nl[]
			for($i=1;$i<=$num_bottom_points;$i++){
				for($j=$i+1;$j<=$num_bottom_points;$j++){
					$d[$i][$j] = sqrt(($x_bottom_point[$i] - $x_bottom_point[$j])**2 + ($y_bottom_point[$i] - $y_bottom_point[$j])**2);
					if($d[$i][$j] < $cutoff){
						$adj[$i][$j] = $adj[$j][$i] = 1;}}}
			# c_member[numpoints] will track cluster membership
			for($i=1;$i<=$num_bottom_points;$i++){
				$c_member[$i] = -1;}
			
			# point_list is an array which is 0 
			# every point in it. whenever a point is added to a cluster, it is removed from point_list.
			# whenever a new cluster is started, it starts at the first entry in point_list. (so i guess it's a queue)
			# when point_list is empty, we are done. (note that point_list is indexed from 0 so that shift() doesn't return an 
			# undefined entry)
			
			print "starting clustering calc for bottom leaflet of frame $frame...\n";		
	
			$k = 0;
			$points_left = $num_bottom_points;
			while($points_left > 0){

			# $k will be the index of the cluster. increment each time a new cluster starts
			$k++;
			# c_size will count points in the cluster
			$c_size = 0;

			for($i=1;$i<=$num_bottom_points;$i++){
				if($c_member[$i] < 0){
					# find the next point which has not yet been clustered to serve as the next starting point. 
					# assign that point to $c_start. assign starting point to current cluster, 
					# decrement points_left,  exit the loop
					$c_start = $i;
					$c_member[$c_start] = $k;
					$points_left--;
					$c_size++;
					# these arrays will hold x, y coords of cluster points as it builds
					$x_clust[$c_size] = $x_bottom_point[$i];
					$y_clust[$c_size] = $y_bottom_point[$i];
					last; 
				}
			}

			# find neighbors of starting point and add them to the queue
			for($i=1;$i<=$num_bottom_points;$i++){
				if($adj[$c_start][$i] == 1){
					push(@queue,$i);
					# a check on the scheme
					if($c_member[$i] > 0){die "point i has already been clustered.\n";} 
				}
			}
 			# BF search
			while($i = shift(@queue)){
	
				#has i been visited yet? if not...
				if($c_member[$i] < 0){
					# i now marked as visited. decrement points_left. set points_list[$i] = 0
					$c_member[$i] = $k;
					$points_left--;
					$c_size++;
					$x_clust[$c_size] = $x_bottom_point[$i];
                                        $y_clust[$c_size] = $y_bottom_point[$i];
					#look at every neighbor of i
					for($j=1;$j<=$num_bottom_points;$j++){
						if($adj[$i][$j] == 1){
							# i and j are neighbors. has j been visited? if not push j onto the end of the queue
							if($c_member[$j] < 0){
								push(@queue, $j);
							}
						}
					}
				}

			}# end breadth first search
			# calculate area of the just built cluster
			if($c_size > $min_c_size){
			# set up grid for cluster size estimate
			$x_min = 10e6;
			$y_min = 10e6;
			$x_max = -10000000;
			$y_max = -10000000;
			for($i=1;$i<=$c_size;$i++){
				if($x_clust[$i] < $x_min){$x_min = $x_clust[$i];}
				if($x_clust[$i] > $x_max){$x_max = $x_clust[$i];}
				if($y_clust[$i] < $y_min){$y_min = $y_clust[$i];}
				if($y_clust[$i] > $y_max){$y_max = $y_clust[$i];}
			}
			#initialize grid
			$num_x_bins = int(($x_max - $x_min)/$gridsize) + 1;
			$num_y_bins = int(($y_max - $y_min)/$gridsize) + 1;
			for($i=1;$i<=$num_x_bins;$i++){
        			for($j=1;$j<=$num_y_bins;$j++){
                			$bin[$i][$j] = 0;
        			}
			}
			
			$area = 0.0;
			$perbin_area = $gridsize**2;
			$x_com = 0.0;
			$y_com = 0.0;
			for($i=1;$i<=$c_size;$i++){
        			$x_bin = int(($x_clust[$i] - $x_min)/$gridsize) + 1;
        			$y_bin = int(($y_clust[$i] - $y_min)/$gridsize) + 1;
				$x_com += $x_clust[$i];
				$y_com += $y_clust[$i];
				if($bin[$x_bin][$y_bin] == 0){
					$bin[$x_bin][$y_bin]++;
					$area += $perbin_area;
				}
			}
			$x_com /= $c_size;
			$y_com /= $c_size;
			
			print CLUSTER_SIZES_BL "Cluster $k  $x_com  $y_com  $area\n";
			}
			} # END WHILE LOOP CLUSTERING ALL BOTTOM LEAF POINTS 


		}# if statement, true = last point in frame, go into cluster building
	}#if statement, true = read point
}
close(IN);
close(CLUSTER_SIZES_BL);
close(CLUSTER_SIZES_TL);


