SetFactory("OpenCASCADE");

// Define parameters
W = 0.054906; 
L = 0.074846; 
Guard = 3 / 1000; 

LayerAmount = 40; 


// Define inner geometry
Disk(1) = {0, 0, 0, W/2};
Disk(2) = {0, 0, 0, 10/1000};
Disk(3) = {0, 0, 0, W/2 - 6/1000};


s() = BooleanFragments{ Surface{1}; Delete; }{ Surface{2,3}; Delete; };


Extrude {0,0, 0.003} {   
  Surface{3,4,2}; Layers{1}; Recombine;
}
Extrude {0,0,L} {   
  Surface{7,9,10}; Layers{30}; Recombine;
}
Extrude {0,0, 0.003} {   
  Surface{13,15,16}; Layers{1}; Recombine;
}

MeshSize{ PointsOf{ Volume{1,2,3}; } } = 0.005;
MeshSize{ PointsOf{ Volume{4,5,6}; } } = 0.005;
MeshSize{ PointsOf{ Volume{7,8,9}; } } = 0.005;


Physical Volume("GRD_B") = {1};
Physical Volume("STEEL") = {2,8};
Physical Volume("PPINJ") = {3};
Physical Volume("CLAY") = {4,5,6};
Physical Volume("GRD_T") = {7};
Physical Volume("PPOUT") = {9};

