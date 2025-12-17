SetFactory("OpenCASCADE");

WidthCube    = 50;
HeightCube   = 40;
zTop         = 10;  // keep this as the original top elevation
Dip      = 60*Pi/180;
Strike  =  -90 * Pi/180; //-66*Pi/180;   // strike measured clockwise from North
FaultThick   = 2.8;


Point(999) = {0,0,0, 0.05};
Box(1) = { -WidthCube/2, -WidthCube/2, zTop - HeightCube,
            WidthCube,    WidthCube,    HeightCube };

Rectangle(101) = {-100, -100, 0, 200, 200};


// ---- parameters
Icl = 55*Pi/180;      // inclination from vertical
Az  = -52*Pi/180;     // azimuth, clockwise from North
Len = 0.5;            // borehole length in model unitsQ
R   = 0.25;        // radius
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
  Surface{101}; Layers{12}; Recombine;
};


Point(789) = {7.434, 8.137, -0.900}; //B1
Point(790) = {1.904, 5.158, 7.779};
Point(791) = {10.1119, 5.72288, -3.66476};


// --- clip both tools to the box (keep only inside-the-box parts)
fault_in[] = BooleanIntersection{ Volume{1}; }{ Volume{ out[1] }; Delete; };
//cyl_in[]   = BooleanIntersection{ Volume{1}; }{ Volume{301};     Delete; };

// --- fragment box, fault, and cylinder together (no overlaps; conformal interfaces)
parts[] = BooleanFragments{
  Volume{1}; Delete;
}{
  Volume{ fault_in[]}; Delete;
};





// --- now fragment box + faults + fault cylinder together
parts[] = BooleanFragments{
  Volume{parts[]}; Delete;
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

// Pick your target sizes (in model units)
h_fault = 1.5;   // fine near/inside the fault
h_out   = 15;   // coarser elsewhere
ramp    = 10;   // distance over which to transition to h_out

// ---- your distance field near the fault faces
Field[1] = Distance;
Field[1].SurfacesList = {11,9};

Field[2] = Threshold;
Field[2].InField = 1;
Field[2].SizeMin = h_fault;   // fine near the fault
Field[2].SizeMax = h_out;     // coarse far away
Field[2].DistMin = 1.0;
Field[2].DistMax = ramp;

// ---- your distance field near the injection cylinder

Field[3] = Distance;
Field[3].PointsList = {999};

Field[4] = Threshold;
Field[4].InField  = 3;
Field[4].SizeMin  = 0.25;
Field[4].SizeMax  = 5;
Field[4].DistMin  = 0.75;
Field[4].DistMax  = ramp*2;

Field[99] = Min;
Field[99].FieldsList = {2,4};
Background Field = 99;

volAbove[] = Volume In BoundingBox{-1e9, -1e9, 9.9, 1e9, 1e9, 1e9};
volBelow[] = Volume In BoundingBox{-1e9, -1e9, -1e9, 1e9,  1e9, -29.9};

Physical Volume("CLAY") = {3,4};
Physical Volume("FAULT") = {2};
Physical Volume("BNDTO") = {volAbove[]};
Physical Volume("BNDBO") = {volBelow[]};


