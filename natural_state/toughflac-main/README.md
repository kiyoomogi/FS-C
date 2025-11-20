# toughflac

![license](https://img.shields.io/badge/license-BSD--3--Clause-green)
![version](https://img.shields.io/badge/version-1.2.0-blue)
![black](https://img.shields.io/badge/style-black-black)

The TOUGH-FLAC simulator, which is a coupled code linking two existing simulators (TOUGH3 and FLAC3D), has been developed over the past several years to enable the analysis of coupled thermo-hydro-mechanical processes in geological media under multiphase flow conditions. A great benefit with this approach is that the two codes are well established in their respective fields; they have been applied and tested by many groups all over the world.

TOUGH3-FLAC Python library **`toughflac`** has been designed to make coupled simulations more user-friendly by extensively using Python capabilities. It relies on [**`toughio`**](https://github.com/keurfonluu/toughio) for the processing of TOUGH3 inputs and outputs.

## Features

**`toughflac`** is organized as submodules and functions consistent with FLAC3D's own Python module **`itasca`** in terms of hierarchy and naming. It allows pre- and post-processing for TOUGH-FLAC to be entirely carried out in FLAC3D. The different submodules are organized as follow:

-   **coupling**: functions required to run a coupled TOUGH-FLAC simulation,
-   **model**: functions to reset, save and restore FLAC3D and Python states,
-   **plot**: functions to facilitate plotting in a pythonic manner,
-   **utils**: functions to help developing a model,
-   **zone**: functions to facilitate pre- and post-processing for coupled TOUGH-FLAC simulation,
-   **zonearray**: functions to easily access extra variable arrays.

## Installation

To install, simply run the batch script _setup.bat_ and follow the instructions on screen. You may have to edit the file if FLAC3D is not installed in its default location.

## Usage

**`toughflac`** can be imported in FLAC3D IPython console or in a Python script (to execute in FLAC3D) following

```python
import toughflac as tf
```

## Requirements

The user requires a standard FLAC3D license and a TOUGH3 license. This repository does not provide the modified TOUGH3 source code to run a coupled simulation. However, **`toughflac`** module can still be used for TOUGH3 multiphase flow simulations using FLAC3D as a pre- and post-processor.
