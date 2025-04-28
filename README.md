# mini-MuMMI: Automatic refinement of intramolecular interactions

## Overview

The goal of this project is to model proteins with harmonic bonds, refining harmonic bond constants based on data from finer-grained simulations (e.g., atomistic or coarse-grained Martini simulations). Specifically, we use this approach to refine interactions within ultra-coarse-grained (UCG) models of RAS proteins, using Martini coarse-grained (CG) trajectories as input. This is part of the mini-MuMMI project, designed to extend multiscale protein modeling workflows by enabling automatic refinement of intramolecular interactions.

The `henm` Python package reimplements automatic refinement in Python, following the methodology described in [Lyman 2008](https://pmc.ncbi.nlm.nih.gov/articles/PMC2567941/) (Systematic Multiscale Parameterization of Heterogeneous Elastic Network Models of Proteins). The original Perl-based implementation is available [here](https://github.com/uchicago-voth/MSCG-models/tree/master/HIV_CASP1/extra_codes/henm).

## Quick start

To install `henm` as a package, run `pip install -e .`

This package automates processing CG Martini simulations to refine the parameters of UCG simulations.

Example:
```
python -m henm.pipeline \
    --inputs input/example_1.gro input/example_1.trr \
             input/example_2.gro input/example_2.trr \
             input/example_3.gro input/example_3.trr \
             input/example_4.gro input/example_4.trr \
    --out output/
   --lammps lammps/
```

If processing a larger number of files, read in the paired structure and trajectory files as a csv.

```
python -m henm.pipeline \
--infile input/martinifiles.csv \
--out output/
--lammps lammps/
```

If you are running this on a new system, please first run:
```
cd henm/bin
gcc -o hetero-enm hetero-enm-src/heteroenm.c hetero-enm-src/smalloc.c -llapack -lblas -lm
gcc -o mkgromax mkgromax-src/mkgromax.c mkgromax-src/smalloc.c
```

To run this as a job on an HPC system such as Lassen:

```
bsub < scripts/refine.sh
```

## Components

## Inputs

## Outputs

## Folder Structure
