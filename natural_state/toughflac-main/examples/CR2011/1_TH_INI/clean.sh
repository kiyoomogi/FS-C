#!/bin/bash
rm -rf `ls | grep -v "^clean.sh$\|^run.sh$\|^CO2TAB$\|^CR2011i.dat$"`
rm -rf TABLE .OUTPUT_*