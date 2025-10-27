SetFactory("OpenCASCADE");

WidthCube    = 30;
HeightCube   = 20;
Dip      = 55*Pi/180;
Strike  =  -46*Pi/180;   // strike measured clockwise from North
FaultThick   = 0.5;


Point(999) = {0,0,0};
Box(1) = {-WidthCube/2,-WidthCube/2,-HeightCube/2, WidthCube,WidthCube,HeightCube};
Rectangle(101) = {-30, -30, FaultThick/2, 60, 60};
Rectangle(102) = {-2, -2, FaultThick/2, 4, 4};


// ---- parameters
Icl = 10*Pi/180;      // inclination from vertical
Az  = 319*Pi/180;     // azimuth, clockwise from North
Len = 0.3;            // borehole length in model unitsQ
R   = 0.207/2;        // radius

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



Rotate { {1, 0, 0}, {0, 0, 0}, Dip } {
  Surface{101,102};  
}
Rotate { {0, 0, 1}, {0, 0, 0}, 90 * Pi/180 } {  //let it dip to east with strike to 0N
  Surface{101,102};  
}
Rotate { {0, 0, 1}, {0, 0, 0}, Strike } {  //let it strike 60°N
  Surface{101,102};  
}


// ---- Normal components that match the actual rotated plane
sinDip = Sin(Dip);
cosDip = Cos(Dip);
sinStr = Sin(Strike);
cosStr = Cos(Strike);

nx =  sinDip * cosStr;
ny =  sinDip * sinStr;
nz =  cosDip;

// Extrude orthogonal to the plane by FaultThick
out[] = Extrude { -nx*FaultThick, -ny*FaultThick, -nz*FaultThick } {
  Surface{101,102};
};

v() = BooleanFragments{ Volume{3}; Delete; }{ Volume{1}; Delete; };

//Point(789) = {10.576, 8.696, -1.559};


// --- clip both tools to the box (keep only inside-the-box parts)
fault_in[] = BooleanIntersection{ Volume{4}; }{ Volume{ out[1] }; Delete; };

// --- fragment box, fault, and cylinder together (no overlaps; conformal interfaces)
parts[] = BooleanFragments{
  Volume{4}; Delete;
}{
  Volume{ fault_in[]}; Delete;
};

Cylinder(301) = { x0, y0, z0,  dx, dy, dz,  R };
w() = BooleanFragments{ Volume{3}; Delete; }{ Volume{301}; Delete; };

Extrude {0,0, 0.5} {   
  Surface{135,122,129}; Layers{1}; Recombine;
}

Extrude {0,0, -0.5} {   
  Surface{131,124,136}; Layers{1}; Recombine; 
}
// Pick your target sizes (in model units)
h_fault = 1.2;   // fine near/inside the fault
h_out   = 5;   // coarser elsewhere
ramp    = 10;   // distance over which to transition to h_out

// ---- your distance field near the fault faces
Field[1] = Distance;
Field[1].SurfacesList = {102,112,123,121};

Field[2] = Threshold;
Field[2].InField = 1;
Field[2].SizeMin = h_fault;   // fine near the fault
Field[2].SizeMax = h_out;     // coarse far away
Field[2].DistMin = 1.0;
Field[2].DistMax = ramp;

// ---- your distance field near the injection cylinder
Field[3] = Distance;
Field[3].SurfacesList = {139,140,141};

Field[4] = Threshold;
Field[4].InField = 0.1;
Field[4].SizeMin = 0.06;   
Field[4].SizeMax = h_out;     // coarse far away
Field[4].DistMin = 1;
Field[4].DistMax = 14;

Field[99] = Min;
Field[99].FieldsList = {2,4};
Background Field = 99;

Physical Volume("CLAY ") = {4,5};
Physical Volume("FAULT") = {2};
Physical Volume("INJEC") = {301};
Physical Volume("BNDTO") = {303,304,305};
Physical Volume("BNDBO") = {306,307,308};
Physical Volume("CLAYI") = {302};


