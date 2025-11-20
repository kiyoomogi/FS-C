.. _introduction:

Introduction
============

This document describes how to run a coupled TOUGH3 and FLAC3D simulation for the analysis of coupled multiphase fluid flow and geomechanical processes. This document is intended for research collaborators, scientists and engineers who would like to apply coupled TOUGH3 and FLAC3D simulations in collaborative research projects. The TOUGH-FLAC simulator, which is a coupled code linking two existing simulators (TOUGH3 and FLAC3D), has been developed over the past several years to enable the analysis of coupled thermo-hydro-mechanical processes in geological media under multiphase flow conditions. A great benefit with this approach is that the two codes are well established in their respective fields; they have been applied and tested by many groups all over the world.

The earliest developments are presented in :cite:`Rutqvist2002a` and :cite:`Rutqvist2003`, and the approach have been applied to study coupled geomechanical aspects under multi-phase flow conditions for a wide range of applications, including nuclear waste disposal (:cite:`Rutqvist2003a`, :cite:`Rutqvist2005`, :cite:`Rutqvist2008`, :cite:`Rutqvist2009`), CO\ :sub:`2` sequestration (:cite:`Rutqvist2002`, :cite:`Rutqvist2005a`, :cite:`Rutqvist2007`, :cite:`Rutqvist2008a`, :cite:`Rutqvist2010a`, :cite:`Cappa2011`, :cite:`Cappa2011a`), geothermal energy extraction (e.g. :cite:`Rutqvist2006`), naturally occurring CO\ :sub:`2` upwelling with surface deformations (:cite:`Todesco2004`, :cite:`Cappa2009`), gas production from hydrate bearing sediments (:cite:`Rutqvist2007a`, :cite:`Rutqvist2009a`, :cite:`Kim2011`), and underground compressed air energy storage (:cite:`Rutqvist2012a`, :cite:`Kim2012`).

First, the general outline for developing a coupled TOUGH-FLAC simulation is presented. Then detailed step-by-step hands-on instructions are given to describe development and execution of specific problems.
