#!/bin/bash
./clean.sh
cp ../MESH MESH
cp ../INCON INCON
time tough3-flac-eco2n 2dldV6i.dat
