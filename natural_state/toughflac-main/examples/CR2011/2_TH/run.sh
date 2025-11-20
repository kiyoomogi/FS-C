#!/bin/bash
./clean.sh
cp ../MESH MESH
sed "/+++/Q" < ../1_TH_INI/SAVE > INCON
echo "" >> INCON
time mpiexec -n 4 tough3-eco2n CR2011.dat
