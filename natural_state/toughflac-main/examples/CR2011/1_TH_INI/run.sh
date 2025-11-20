#!/bin/bash
./clean.sh
cp ../MESH MESH
cp ../INCON INCON
time mpiexec -n 4 tough3-eco2n CR2011i.dat
