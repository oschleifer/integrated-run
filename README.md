# UCG-mini-MuMMI: Automatic refinement of intramolecular interactions

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

If you are running this on a new system, please recompile the executables by running:
```
cd henm/bin
gcc -o hetero-enm hetero-enm-src/heteroenm.c hetero-enm-src/smalloc.c -llapack -lblas -lm
gcc -o mkgromax mkgromax-src/mkgromax.c mkgromax-src/smalloc.c
```

To run this as a job on an HPC system such as Lassen at Lawrence Livermore National Laboratory:

```
bsub < scripts/refine.sh
```

## Components

`gromacs`: scripts to run CG Martini simulations using GROMACS on an HPC system such as Lassen. 

`lammps`: input files and scripts required to run UCG simulations in LAMMPS. 

`scripts`: scripts used to run experiments with the hENM code.

`figures`: code and data to reproduce figures from our manuscript.

`henm`: source code for a Python package that uses CG simulation outputs to generate bond coefficients for the corresponding UCG model.

## Steps

The main component is the `henm` package.

**Inputs:** The CG simulations will produce two main files - a GROMACS structure file (.gro) and trajectory file (.trr/.xtc). 

### 1. Alignment

**Purpose**: Extracts only the protein from the CG trajectory and aligns it to remove rotational and translational motion, isolating intramolecular interactions. 

**Scripts**: `align.py`


### 2. Parameter estimation

**Purpose**: Use aligned trajectory to estimate the harmonic bond coefficients of the UCG model.

**Scripts**: `estimate.py`

This script calls two other Python scripts:

`fluc_scripts/fluc-match-8f.py`: Refines the bond coefficients iteratively to match the desired interaction strength.

`fluc_scripts/fluc-match-str-pdb.py`: Generates the final file containing the optimized bond coefficient data.


These files are also necessary for this step, which involves short GROMACS simulations:

`bin`: contains executables that efficiently prepare input files for GROMACS and their C source code.

`input-files`: contains fixed files needed for estimation

- `amino-acid-masses.txt`: the mass of each amino acid.
- `aminoacids.dat`: a list of amino acids and other related molecules.
- `ba.dat`: a mapping of each of the 320 amino acids in the RAS-RBDCRD protein complex to 40 UCG sites.

- `ffcharmm27bon.itp`, `steep.mdp`: files needed to run GROMACS.

**Outputs** for the ith input file:

- `cgk_{i}.dat`: A four-column output file with first UCG site, second UCG site, equilibrium bond distance, and harmonic bond coefficient.
- `cg1_{i}.xyz`: A four-column output file with a UCG site followed by its coordinates.
- `mass_{i}.dat`: A two-column output file with a UCG site followed by its mass.

### 3. Averaging

**Purpose**: If inputs from multiple CG trajectories were provided, average the results to obtain one set of parameters.

**Scripts**: `average.py`

**Outputs**
- `cgk.dat`
- `cg1.xyz`
- `mass.dat`: This does not need to be averaged since the number of amino acids in each UCG site is fixed.

### 4. Writing LAMMPS input

**Purpose**: Use the new positions and bond coefficients to write LAMMPS input file.

**Scripts**: `write.py`

**Outputs**
- `lammpsdata.dat`: input file for starting a new LAMMPS simulation.
- `lammpsbondcoeff.dat`: writes a record of the bond coefficients.

## Acknowledgments

This work is part of the UCG-mini-MuMMI project at Harvey Mudd College Clinic Program with Lawrence Livermore National Laboratory.
