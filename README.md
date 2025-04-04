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
```