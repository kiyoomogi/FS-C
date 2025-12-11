SetFactory("OpenCASCADE");

WidthCube    = 50;
HeightCube   = 40;
zTop         = 10;  // keep this as the original top elevation
Dip      = 55*Pi/180;
Strike  =  -52 * Pi/180; //-66*Pi/180;   // strike measured clockwise from North
FaultThick   = 2.8;


Box(1) = { -WidthCube/2, -WidthCube/2, zTop - HeightCube,
            WidthCube,    WidthCube,    HeightCube };
Rotate {{0, 0, 1}, {0, 0, 0}, 50*Pi/180} {
  Volume{1};
}


surfAbove[] = Surface In BoundingBox{-1e9, -1e9, 9.9, 1e9, 1e9, 1e9};
surfBelow[] = Surface In BoundingBox{-1e9, -1e9, -1e9, 1e9,  1e9, -29.9};

Extrude {0,0, 0.5} {   
  Surface{surfAbove[]}; Layers{1}; Recombine;
}

Extrude {0,0, -0.5} {   
  Surface{surfBelow[]}; Layers{1}; Recombine; 
}



volAbove[] = Volume In BoundingBox{-1e9, -1e9, 9.9, 1e9, 1e9, 1e9};
volBelow[] = Volume In BoundingBox{-1e9, -1e9, -1e9, 1e9,  1e9, -29.9};


MeshSize{ PointsOf{ Volume{1}; } } = 5; //CLAY


Physical Volume("CLAY ") = {1};
Physical Volume("BNDTO") = {volAbove[]};
Physical Volume("BNDBO") = {volBelow[]};
