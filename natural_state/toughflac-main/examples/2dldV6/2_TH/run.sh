#!/bin/bash
./clean.sh
cp ../MESH MESH
sed "/+++/Q" < ../1_TH_INI/SAVE > INCON
echo "" >> INCON
time tough3-eco2n 2dldV6.dat