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

// start point chosen so the cylinder is centered at the origin
dx = Len*ux;
dy = Len*uy;
dz = Len*uz;
R   = 0.146/2;        // radius

x0 = -0.5*dx;
y0 = -0.5*dy;
z0 = -0.5*dz;
Cylinder(1001) = {x0, y0, z0,  dx, dy, dz,  R};

allVols[] = {parts[]};   // all volumes before cylinder

allFrag[] = BooleanFragments{
  Volume{ allVols[] }; Delete;
}{
  Volume{1001}; Delete;
};


// Pick your target sizes (in model units)
h_fault = 1.5;   // fine near/inside the fault
h_out   = 8;   // coarser elsewhere
h_inj   = 0.1;   // fine near/inside the fault
h_injo  = 4;   // coarser elsewhere
ramp    = 4;   // distance over which to transition to h_out

// ---- your distance field near the fault faces
Field[1] = Distance;
Field[1].SurfacesList = {106,96,95,101}; 

Field[2] = Threshold;
Field[2].InField = 1;
Field[2].SizeMin = h_inj;   // fine near the fault
Field[2].SizeMax = h_injo;     // coarse far away
Field[2].DistMin = 0.06;
Field[2].DistMax = 5;

// ---- your distance field near the main fault
Field[3] = Distance;
Field[3].SurfacesList = {33,30}; 

Field[4] = Threshold;
Field[4].InField = 1;
Field[4].SizeMin = h_fault;   // fine near the fault
Field[4].SizeMax = h_out;     // coarse far away
Field[4].DistMin = 1.0;
Field[4].DistMax = ramp;

// ---- your distance field near the injection fault
Field[5] = Distance;
Field[5].SurfacesList = {18,16,92,90};

Field[6] = Threshold;
Field[6].InField = 3;
Field[6].SizeMin = h_fault/2;   
Field[6].SizeMax = h_out;     // coarse far away
Field[6].DistMin = 0.1;
Field[6].DistMax = 5;

Field[99] = Min;
Field[99].FieldsList = {2,4,6};
Background Field = 99;

Physical Volume("INJEC") = {22,24,26}; //v
Physical Volume("CLAY ") = {7,9,23,25}; //v
Physical Volume("FLT_I") = {21,3}; //v
Physical Volume("FLT_M") = {2,4,6}; //v
Physical Volume("BNDTO") = {11,12,13,14,15,16,17}; //v
Physical Volume("BNDBO") = {19,20,18}; //v

// Collect all surfaces whose bounding box intersects z >= 9.9

// Print them
//Printf("Surfaces with z >= 9.9:");
//For i In {0 : #surfAbove[] - 1}
//  Printf("  Surface %g", surfAbove[i]);
//EndForq
//+


