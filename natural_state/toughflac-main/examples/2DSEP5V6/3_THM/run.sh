#!/bin/bash
./clean.sh
cp ../MESH .
sed "/+++/Q" < ../1_TH_INI/SAVE > INCON
echo "" >> INCON
cp ../flac3d.py .
cp ../tf_in.f3sav tf_in.f3sav
time mpiexec -n 6 tough3-eco2n 2DSEP5V6.dat
