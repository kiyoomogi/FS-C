SetFactory("OpenCASCADE");

WidthCube    = 140;
HeightCube   = 90;
zTop         = 32;  // keep this as the original top elevation
Dip      = 55*Pi/180;
Strike  =  -60 * Pi/180; //-66*Pi/180;   // strike measured clockwise from North
FaultThick   = 2.0;


Point(999) = {0,0,0, 0.05};
Box(1) = { -WidthCube/2, -WidthCube/2, zTop - HeightCube,
            WidthCube,    WidthCube,    HeightCube };
Rotate {{0, 0, 1}, {0, 0, 0}, 50*Pi/180} {
  Volume{1};
}
Rectangle(101) = {-100, -100, 0.3, 200, 200};


// ---- parameters
Icl = 55*Pi/180;      // inclination from vertical
Az  = -52*Pi/180;     // azimuth, clockwise from North
Len = 1;            // borehole length in model unitsQ
R   = 0.15;        // radius

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


Point(790) = {11.8685315  , 9.058115   , 2.72817964};
Point(791) = {9.55383428 , 5.01474972 ,-0.61983978};


// --- clip both tools to the box (keep only inside-the-box parts)
fault_in[] = BooleanIntersection{ Volume{1}; }{ Volume{ out[1] }; Delete; };
//cyl_in[]   = BooleanIntersection{ Volume{1}; }{ Volume{301};     Delete; };

// --- fragment box, fault, and cylinder together (no overlaps; conformal interfaces)
parts[] = BooleanFragments{
  Volume{1}; Delete;
}{
  Volume{ fault_in[]}; Delete;
};


//Cylinder(1001) = {x0, y0, z0,  dx, dy, dz,  R};

//// --- intersect cylinder ONLY with the fault zone inside the box
//cyl_fault[] = BooleanIntersection{
//  Volume{1001}; Delete;        // delete original full cylinder
//}{
//  Volume{fault_in[]};         // only keep part inside the fault
//};

// --- now fragment box + faults + fault cylinder together
parts[] = BooleanFragments{
  Volume{parts[]}; Delete;
}{
  Volume{ fault_in[]}; Delete; 
};


//// --- now fragment box + faults + fault cylinder together
//parts[] = BooleanFragments{
//  Volume{parts[]}; Delete;
//}{
//  Volume{ fault_in[], cyl_fault[]}; Delete; 
//};

surfAbove[] = Surface In BoundingBox{-1e9, -1e9, 9.9, 1e9, 1e9, 1e9};
surfBelow[] = Surface In BoundingBox{-1e9, -1e9, -1e9, 1e9,  1e9, -32.9};

Extrude {0,0, 0.5} {   
  Surface{surfAbove[]}; Layers{1}; Recombine;
}

Extrude {0,0, -0.5} {   
  Surface{surfBelow[]}; Layers{1}; Recombine; 
}

// Pick your target sizes (in model units)
h_fault = 8;   // fine near/inside the fault
h_out   = 40;   // coarser elsewhere
ramp    = 6;   // distance over which to transition to h_out



// ---- your distance field near the fault faces
Field[1] = Distance;
Field[1].SurfacesList = {24};

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
Field[4].SizeMin  = 1;
Field[4].SizeMax  = 14;
Field[4].DistMin  = 2;
Field[4].DistMax  = ramp*8;

Field[99] = Min;
Field[99].FieldsList = {2,4};  //was 2,4 before
Background Field = 99;

volAbove[] = Volume In BoundingBox{-1e9, -1e9, 9.9, 1e9, 1e9, 1e9};
volBelow[] = Volume In BoundingBox{-1e9, -1e9, -1e9, 1e9,  1e9, -32.9};

Physical Volume("CLAY") = {3,4};
Physical Volume("FAULT") = {5};
Physical Volume("BNDTO") = {volAbove[]};
Physical Volume("BNDBO") = {volBelow[]};

//+
Show "*";
//+
Hide {
  Point{1008}; Point{1009}; Point{1010}; Point{1011}; Point{1012}; Point{1013}; Point{1014}; Point{1015}; Point{1016}; Point{1017}; Point{1018}; Point{1019}; Point{1020}; Point{1021}; Point{1022}; Point{1023}; Point{1024}; Point{1027}; Point{1028}; Point{1029}; Curve{14}; Curve{16}; Curve{17}; Curve{19}; Curve{20}; Curve{21}; Curve{23}; Curve{24}; Curve{25}; Curve{26}; Curve{27}; Curve{28}; Curve{29}; Curve{30}; Curve{31}; Curve{32}; Curve{33}; Curve{34}; Curve{35}; Curve{36}; Curve{37}; Curve{38}; Curve{39}; Curve{40}; Curve{41}; Curve{46}; Curve{48}; Curve{49}; Curve{50}; Curve{51}; Curve{52}; Curve{53}; Surface{9}; Surface{11}; Surface{13}; Surface{14}; Surface{15}; Surface{16}; Surface{17}; Surface{18}; Surface{19}; Surface{20}; Surface{21}; Surface{22}; Surface{26}; Surface{28}; Surface{29}; Surface{30}; Surface{31}; Volume{3}; Volume{4}; Volume{6}; 
}
