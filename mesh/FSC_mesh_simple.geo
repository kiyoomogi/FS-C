SetFactory("OpenCASCADE");

WidthCube    = 50;
HeightCube   = 40;
zTop         = 10;  // keep this as the original top elevation

Dip      = 58*Pi/180;
Strike  =  -66*Pi/180;   // strike measured clockwise from North
FaultThick   = 2;


Point(999) = {0,0,0};
Box(1) = { -WidthCube/2, -WidthCube/2, zTop - HeightCube,
            WidthCube,    WidthCube,    HeightCube };

Rectangle(101) = {-100, -100, FaultThick/2, 200, 200};

// ---- parameters
Icl = 10*Pi/180;      // inclination from vertical
Az  = 319*Pi/180;     // azimuth, clockwise from North
Len = 2;            // borehole length in model unitsQ
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



Rotate { {1, 0, 0}, {0, 0, 0}, Dip } {
  Surface{101};  
}
Rotate { {0, 0, 1}, {0, 0, 0}, 90 * Pi/180 } {  //let it dip to east with strike to 0N
  Surface{101};  
}
Rotate { {0, 0, 1}, {0, 0, 0}, Strike } {  //let it strike 60°N
  Surface{101};  
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
  Surface{101}; Layers{4}; Recombine;
};

Cylinder(301) = { x0, y0, z0,  dx, dy, dz,  R };

Point(789) = {14.668, 4.132, -3.507};
Point(790) = {10.789, 4.052, -1.099};

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
  Surface{125,120,113}; Layers{1}; Recombine;
}

Extrude {0,0, -0.5} {   
  Surface{126,121,115}; Layers{1}; Recombine; 
}

// Pick your target sizes (in model units)
h_fault = 1.6;   // fine near/inside the fault
h_out   = 5;   // coarser elsewhere
ramp    = 10;   // distance over which to transition to h_out

// ---- your distance field near the fault faces
Field[1] = Distance;
Field[1].SurfacesList = {112,119};

Field[2] = Threshold;
Field[2].InField = 1;
Field[2].SizeMin = h_fault;   // fine near the fault
Field[2].SizeMax = h_out;     // coarse far away
Field[2].DistMin = 1.0;
Field[2].DistMax = ramp;

// ---- your distance field near the injection cylinder
Field[3] = Distance;
Field[3].SurfacesList = {107,109,108};

Field[4] = Threshold;
Field[4].InField = 3;
Field[4].SizeMin = 0.1;   
Field[4].SizeMax = h_out;     // coarse far away
Field[4].DistMin = 0.06;
Field[4].DistMax = 14;

Field[99] = Min;
Field[99].FieldsList = {2,4};
Background Field = 99;


Physical Volume("CLAY ") = {302,304};
Physical Volume("FAULT") = {303};
Physical Volume("INJEC") = {301};
Physical Volume("BNDTO") = {305,306,307};
Physical Volume("BNDBO") = {308,309,310};


