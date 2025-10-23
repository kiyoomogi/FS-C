find "/home/manuus/Desktop/FS-C/model/injection_model" -mindepth 1 -maxdepth 1 \
  \( -name 'INCON' -o -name 'INFILE' -o -name 'MESH' -o -name 'mesh.pickle' -o -name 'CO2TAB' \) -prune -o \
  -exec rm -rf {} +
