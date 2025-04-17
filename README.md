# LLNL Clinic Project

Automated run of ultra coarse-grained molecular dynamics.

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

Temporary Lassen instructions for clinic teammates (TBD remove from final README):

```
git clone git@github.com:oschleifer/integrated-run.git
git switch -c rohan origin/rohan

# recompile C code for lassen
cd integrated-run/henm/bin
gcc -o hetero-enm hetero-enm-src/heteroenm.c hetero-enm-src/smalloc.c -llapack -lblas -lm
gcc -o mkgromax mkgromax-src/mkgromax.c mkgromax-src/smalloc.c

# setup MuMMI Spack environment
cd ..
source ~/.mummi/config.mummi.sh
# may need to delete your outdated environment and reinstall everything
rm -rf $MUMMI_ROOT/$MUMMI_VENV
source $MUMMI_APP/setup/setup.env.sh
pip install .

# try to run stuff (replace with actual filepaths)
python -m henm.pipeline --infile input/martinifiles.csv --out output/ --lammps lammps/
```
