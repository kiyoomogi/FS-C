SetFactory("OpenCASCADE");

WidthCube    = 100;
HeightCube   = 80;
zTop         = 32;  // keep this as the original top elevation
Dip      = 55*Pi/180;
Strike  =  -60 * Pi/180; //-66*Pi/180;   // strike measured clockwise from North
FaultThick   = 2.0;


Point(999) = {0,0,0, 0.05};
Point(888) = {-7.7629759,1.007833e1,1.678793e1};

Box(1) = { -WidthCube/2, -WidthCube/2, zTop - HeightCube,
            WidthCube,    WidthCube,    HeightCube };
Rotate {{0, 0, 1}, {0, 0, 0}, 50*Pi/180} {
  Volume{1};
}

surfAbove[] = Surface In BoundingBox{-1e9, -1e9, 9.9, 1e9, 1e9, 1e9};
surfBelow[] = Surface In BoundingBox{-1e9, -1e9, -1e9, 1e9,  1e9, -47.9};

Extrude {0,0, 4} {   
  Surface{surfAbove[]}; Layers{1}; Recombine;
}

Extrude {0,0, -4} {   
  Surface{surfBelow[]}; Layers{1}; Recombine; 
}

// Pick your target sizes (in model units)
h_fault = 8;   // fine near/inside the fault
h_out   = 40;   // coarser elsewhere
ramp    = 6;   // distance over which to transition to h_out


Physical Volume("CLAY") = {1};
Physical Volume("BNDTO") = {2};
Physical Volume("BNDBO") = {3};
