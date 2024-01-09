#!/bin/bash
prefix=$1
output=$2
filenames=$(ls -1v $prefix.*)
filenames="$filenames $prefix"
for file in $filenames; do
	cat $file >> $output;
done;
