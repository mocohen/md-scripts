#!/bin/bash

mkdir ./combined_files/
python combine_files.py -n TOP-LEAF-CLUSTERS.dat -o ./combined_files/
python combine_files.py -n BOTTOM-LEAF-CLUSTERS.dat -o ./combined_files/

#python combine_tracking.py -n TOP-TRACKING.dat -o ./combined_files/
#python combine_tracking.py -n BOTTOM-TRACKING.dat -o ./combined_files/

