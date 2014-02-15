#!/bin/bash
ext=".png"
Liste="$(find *.jpg -type f -prune)"
for fic in $Liste; do
	convert "$fic" ${fic%%.*}$ext
done
