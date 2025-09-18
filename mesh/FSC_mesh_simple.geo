SetFactory("OpenCASCADE");

WidthCube    = 30;
HeightCube   = 20;
Dip          = 60*Pi/180;     // dip angle
Strike       = -40*Pi/180;     // strike measured from X (East), which is 40° with respect to Y (North)
FaultThick   = 0.55;
Height_Injec = 3; 
Angle_Injec  = 10*Pi/180;
Radius_Injec = 0.073;


Point(999) = {0,0,0};
Box(1) = {-WidthCube/2,-WidthCube/2,-HeightCube/2, WidthCube,WidthCube,HeightCube};
Rectangle(101) = {-30, -30, FaultThick/2, 60, 60};

// ---- parameters
Icl = 10*Pi/180;      // inclination from vertical
Az  = 319*Pi/180;     // azimuth, clockwise from North
Len = 1;            // borehole length in model units
R   = 0.06;          // radius

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
  Surface{101};  
}
Rotate { {0, 0, 1}, {0, 0, 0}, 90 * Pi/180 } {  //let it dip to east with strike to 0N
  Surface{101};  
}
Rotate { {0, 0, 1}, {0, 0, 0}, Strike } {  //let it strike 60°N
  Surface{101};  
}


// ---- Normal components after the two rotations
sinDip = Sin(Dip);
cosDip = Cos(Dip);
sinStr = Sin(Strike);
cosStr = Cos(Strike);

// n = (-sinDip*sinStr, -sinDip*cosStr, cosDip)
nx = -sinDip * sinStr;
ny = -sinDip * cosStr;
nz =  cosDip;


out[] = Extrude {-nx*FaultThick, -ny*FaultThick, -nz*FaultThick } {
  Surface{101}; Layers{4}; Recombine;
};

Cylinder(301) = { x0, y0, z0,  dx, dy, dz,  R };

// --- clip both tools to the box (keep only inside-the-box parts)
fault_in[] = BooleanIntersection{ Volume{1}; }{ Volume{ out[1] }; Delete; };
cyl_in[]   = BooleanIntersection{ Volume{1}; }{ Volume{301};     Delete; };

// --- fragment box, fault, and cylinder together (no overlaps; conformal interfaces)
parts[] = BooleanFragments{
  Volume{1}; Delete;
}{
  Volume{ fault_in[], cyl_in[] }; Delete;
};

Extrude {0,0, 0.5} {   
  Surface{4,13,21}; Layers{1}; Recombine;
}

Extrude {0,0, -0.5} {   
  Surface{22,14,6}; Layers{1}; Recombine; 
}

// Pick your target sizes (in model units)
h_fault = 1.9;   // fine near/inside the fault
h_out   = 5;   // coarser elsewhere
ramp    = 10;   // distance over which to transition to h_out

// ---- your distance field near the fault faces
Field[1] = Distance;
Field[1].SurfacesList = {12,3};

Field[2] = Threshold;
Field[2].InField = 1;
Field[2].SizeMin = h_fault;   // fine near the fault
Field[2].SizeMax = h_out;     // coarse far away
Field[2].DistMin = 1.0;
Field[2].DistMax = ramp;

// ---- your distance field near the injection cylinder
Field[3] = Distance;
Field[3].SurfacesList = {17};

Field[4] = Threshold;
Field[4].InField = 3;
Field[4].SizeMin = 0.1;   
Field[4].SizeMax = h_out;     // coarse far away
Field[4].DistMin = 0.06;
Field[4].DistMax = 14;

Field[99] = Min;
Field[99].FieldsList = {2,4};
Background Field = 99;


Physical Volume("CLAY ") = {1,3};
Physical Volume("FAULT") = {2};
Physical Volume("INJEC") = {4,5,6};
Physical Volume("BNDTO") = {7,8,9};
Physical Volume("BNDBO") = {10,11,12};



