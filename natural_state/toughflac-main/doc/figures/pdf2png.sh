#!/bin/bash

ARG1="."
ARG2=300

while [[ $# -gt 0 ]] && [[ ."$1" = .--* ]]; do
  opt="$1";
  shift
  case "$opt" in
    "--" ) break 2;;
    "--indir" )
      ARG1=$1; shift;;
    "--dpi" )
      ARG2=$1; shift;;
    *) echo >&2 "Invalid option: $@"; exit 1;;
  esac
done

for infile in $ARG1/*.pdf; do
  filename=$(basename $infile .pdf)
  outfile="$ARG1/${filename}.png"
  echo "Converting $infile -> $outfile ($ARG2 dpi)"
  pdftoppm -r $ARG2 -png -aa yes $infile > $outfile
  #convert -density $ARG2 $infile -quality 100 $outfile
done
