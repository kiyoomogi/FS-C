SetFactory("OpenCASCADE");

// Geometry: unit cube
Box(1) = {0, 0, 0, 1, 1, 1};

// Mesh settings (optional)
Mesh.CharacteristicLengthMin = 0.1;
Mesh.CharacteristicLengthMax = 0.1;

// Generate 3D mesh
Mesh 3;

// Save mesh automatically (so you can run just gmsh cube.geo)
Save "cube.msh";
