#!/bin/bash
rm -rf `ls | grep -v "^clean.sh$\|^run.sh$\|^CO2TAB$\|^INCON$\|^INFILE_coupled$"`
rm -rf TABLE .OUTPUT_*