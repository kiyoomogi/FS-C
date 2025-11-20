Disclaimer
----------

This document is an adaptation of the original instruction document written by Jonny Rutqvist (LBNL, July 2016). Coupling of TOUGH3 and FLAC3D has been done by Antonio Pio Rinaldi and Python packaging by Keurfon Luu.

To run coupled TOUGH-FLAC, a user needs the following:

1. A standard FLAC3D license,
2. A TOUGH3 license,
3. A set of modified Fortran source files to run TOUGH-FLAC simulations when compiling TOUGH3,
4. TOUGH3-FLAC Python library :mod:`toughflac` source files.

The user needs knowledge of the TOUGH3 and FLAC3D codes, and of the operational instructions for running the coupled TOUGH3 and FLAC3D analysis. Currently, the FLAC3D code runs only under Windows, i.e. a coupled TOUGH3 and FLAC3D analysis should be conducted on a Windows platform.

The approach developed for coupled TOUGH3 and FLAC3D and application examples described in this document was developed for earlier FLAC3D versions, but has here been updated for the latest FLAC3D. The TOUGH3-FLAC Python library :mod:`toughflac` has been tested on FLAC3D v6 (Python 2.7) and FLAC3D v7 (Python 3.6).
