#!/bin/bash

folder=$2
if [ ! -d $1/$folder ]
then
	mkdir $1/$folder
fi

type=`ls $folder | grep centric | head -1`

if [ ! -d $1/$folder/$type ]
then
	mkdir $1/$folder/$type
fi

for subfolder in `ls $folder/$type`
do
	if [ ! -d $1/$folder/$type/$subfolder ]
	then
		mkdir $1/$folder/$type/$subfolder
	fi
	for file in `ls $folder/$type/$subfolder`
	do
		echo $folder/$type/$subfolder/$file
		if [ -f $1/$folder/$type/$subfolder/$file ]
		then
			continue
		fi
		python /home/ubuntu/scripts/gdc_control_access.py -i $folder/$type/$subfolder/$file -o $1/$folder/$type/$subfolder/$file -t $type
	done
done
