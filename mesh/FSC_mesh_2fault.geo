SetFactory("OpenCASCADE");

WidthCube    = 50;
HeightCube   = 40;
zTop         = 10;  // keep this as the original top elevation

Dip_Inj      = 37*Pi/180;
Strike_Inj   = -39 * Pi/180; //-66*Pi/180;   // strike measured clockwise from North
Dip_M        = 60*Pi/180;
Strike_M     = -50 * Pi/180;

FaultThick   = 0.2;
FaultThick_M = 2.5;

Box(1) = { -WidthCube/2, -WidthCube/2, zTop - HeightCube,
            WidthCube,    WidthCube,    HeightCube };
Rotate {{0, 0, 1}, {0, 0, 0}, -50*Pi/180} {
  Volume{1};
}

Rectangle(101) = {-100, -100, FaultThick/2, 200, 200};
Rectangle(102) = {-100, -100, FaultThick/2 - 3.4 + FaultThick_M/2, 200, 200};


// ---- parameters
Icl = 10*Pi/180;      // inclination from vertical
Az  = 319*Pi/180;     // azimuth, clockwise from North
Len = 0.5;            // borehole length in model unitsQ
R   = 0.146/2;        // radius

// direction cosines (X=East, Y=North, Z=Up)
ux = Sin(Icl)*Sin(Az);
uy = Sin(Icl)*Cos(Az);
uz = -Cos(Icl);

// start point chosen so the cylinder is centered at the origin
dx = Len*ux;
dy = Len*uy;
dz = Len*uz;

x0 = -0.5*dx;
y0 = -0.5*dy;
z0 = -0.5*dz;


//INJECTION FAULT
Rotate { {1, 0, 0}, {0, 0, 0}, Dip_Inj } {
  Surface{101};  
}
Rotate { {0, 0, 1}, {0, 0, 0}, 90 * Pi/180 } {  //let it dip to east with strike to 0N
  Surface{101};  
}
Rotate { {0, 0, 1}, {0, 0, 0}, Strike_Inj } {  //let it strike 60°N
  Surface{101};  
}

//MAIN FAULT
Rotate { {1, 0, 0}, {0, 0, 0}, Dip_M } {
  Surface{102};  
}
Rotate { {0, 0, 1}, {0, 0, 0}, 90 * Pi/180 } {  //let it dip to east with strike to 0N
  Surface{102};  
}
Rotate { {0, 0, 1}, {0, 0, 0}, Strike_M } {  //let it strike 60°N
  Surface{102};  
}

// ---- Normal components that match the actual rotated plane
sinDip = Sin(Dip_Inj);
cosDip = Cos(Dip_Inj);
sinStr = Sin(Strike_Inj);
cosStr = Cos(Strike_Inj);

sinDipM = Sin(Dip_M);
cosDipM = Cos(Dip_M);
sinStrM = Sin(Strike_M);
cosStrM = Cos(Strike_M);

nx =  sinDip * cosStr;
ny =  sinDip * sinStr;
nz =  cosDip;

nx_M =  sinDipM * cosStrM;
ny_M =  sinDipM * sinStrM;
nz_M =  cosDipM;

// Extrude orthogonal to the plane by FaultThick
out[] = Extrude { -nx*FaultThick, -ny*FaultThick, -nz*FaultThick } {
  Surface{101}; Layers{4}; Recombine;
};

out_M[] = Extrude { -nx_M*FaultThick_M, -ny_M*FaultThick_M, -nz_M*FaultThick_M } {
  Surface{102}; Layers{4}; Recombine;
};

//Cylinder(102) = {x0, y0, z0,  dx, dy, dz,  R * 3};



Point(789) = {7.434, 8.137, -0.900};
//Point(790) = {1.904, 5.158, 7.779};
Point(791) = {0,0,0};

// --- clip both tools to the box (keep only inside-the-box parts)
fault_in[] = BooleanIntersection{ Volume{1}; }{ Volume{ out[1], out_M[1]}; Delete; };

// --- fragment box, fault, and cylinder together (no overlaps; conformal interfaces)
parts[] = BooleanFragments{
  Volume{1}; Delete;
}{
  Volume{ fault_in[]}; Delete;
};

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

volClay[] = Volume In BoundingBox{-1e9, -1e9, -30.1,  1e9, 1e9, 10.1};


// start point chosen so the cylinder is centered at the origin
dx = Len*ux;
dy = Len*uy;
dz = Len*uz;
R   = 0.146/2;        // radius

x0 = -0.5*dx;
y0 = -0.5*dy;
z0 = -0.5*dz;
Cylinder(1001) = {x0, y0, z0,  dx, dy, dz,  R};

// --- intersect cylinder ONLY with the fault zone inside the box
cyl_fault[] = BooleanIntersection{
  Volume{1001}; Delete;        // delete original full cylinder
}{
  Volume{fault_in[]};          // only keep part inside the fault
};

// --- now fragment box + faults + fault cylinder together
parts[] = BooleanFragments{
  Volume{parts[]}; Delete;
}{
  Volume{ fault_in[], cyl_fault[]}; Delete;
};

// Pick your target sizes (in model units)
h_fault = 0.8;   // fine near/inside the fault
h_out   = 8;   // coarser elsewhere
h_inj   = 0.1;   // fine near/inside the fault
h_injo  = 4;   // coarser elsewhere
ramp    = 4;   // distance over which to transition to h_out

MeshSize{ PointsOf{ Volume{7,8,9,10}; } } = 7; //CLAY
MeshSize{ PointsOf{ Volume{2,6,1001}; } } = 5; //FLT_M
MeshSize{ PointsOf{ Volume{3,4,1002}; } } = 1.2; //FLT_I


Physical Volume("INJEC") = {1001}; //v
Physical Volume("CLAY ") = {7,8,9,10}; //v
Physical Volume("FLT_I") = {3,1002}; //v
Physical Volume("FLT_M") = {2,4,6}; //v
Physical Volume("BNDTO") = {volAbove[]}; //v
Physical Volume("BNDBO") = {volBelow[]}; //v

// Collect all surfaces whose bounding box intersects z >= 9.9

// Print them
Printf("Volumes with z >= 9.9:");
For i In {0 : #volClay[] - 1}
  Printf("  Volumes %g", volClay[i]);
EndFor

////+
//Show "*";
////+
//Hide {
//  Volume{volClay[]}; 
//}
