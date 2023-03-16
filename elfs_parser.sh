#!/bin/bash

elf_parser() {
	if [ "$(file $1 | grep ELF)" ]; then
		echo -n "File: "
		echo $1
		echo $(readelf -h $1 | awk '$1 == "Machine:" {print $0}')
		echo -n "Libraries: "
		echo $(readelf -d $1 | awk '$2 == "(NEEDED)" {print $5}')
	fi
}

iterate_path() {
	local path=$1
	local FILES=$path/*
	for FILE in $FILES; do
		if [ -d $FILE ]; then
			continue
		else
			elf_parser $FILE
		fi
	done
    
	for FILE in $FILES; do
        if [ -d $FILE ]; then
			iterate_path $FILE
		fi
	done
}

path=$(pwd)
if [ $# -eq 1 ];then
    [ ! -d $1 ] && [ ! -f $1 ] && echo "Wrong Path" && exit 1
	path=$1
fi
IFS=$(echo -en "\n\b")
[ -d $1 ] && iterate_path $1
[ -f $1 ] && elf_parser $1 
IFS=$SAVEIFS
