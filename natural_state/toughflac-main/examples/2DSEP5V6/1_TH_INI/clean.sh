#!/bin/bash
rm -rf `ls | grep -v "^clean.sh$\|^run.sh$\|^CO2TAB$\|^2DSEP5V6i.dat$"`
rm -rf TABLE .OUTPUT_*