import os
import glob
import numpy as np

def get_bond_coeff(fout, cgkfile):
    """
    Write LAMMPS bond coefficients.
    Args:
        fout: File object to write to.
        cgkfile: Path to the bond coefficients file.
    """
    
    flist = glob.glob(cgkfile)

    for fname in flist:
        a = np.loadtxt(fname)
        for i in range(0,len(a[:,1])):
                fout.write('%s\t%d\t%s\t%5.4f\t%5.4f\n' % ("bond_coeff", i+1, "harmonic",  a[i,3],  a[i,2]))
    fout.close()   

def get_data(fout, massfile, cgkfile, cg1file):
    """
    Write LAMMPS data file.
    Args:
        fout: File object to write to.
        massfile: Path to the mass file.
        cgkfile: Path to the bond coefficients file.
        cg1file: Path to the atom coordinates file.
    """
    
    cgsites = 40
    natmtypes = 1
    nbonds = 780
    nbondtypes = 780

    fout.write('%s\n' % ("Lammps data file"))

    fout.write('\t%d %s\n' % (cgsites, "atoms"))
    fout.write('\t%d %s\n' % (nbonds, "bonds"))
    fout.write('\t%d %s\n' % (0, "angles"))
    fout.write('\t%d %s\n' % (0, "dihedrals"))
    fout.write('\t%d %s\n' % (0, "impropers"))
    fout.write('\t%d %s\n' % (cgsites, "atom types"))
    fout.write('\t%d %s\n' % (nbondtypes, "bond types"))
    fout.write('\t%d %s\n' % (0, "angle types"))
    fout.write('\t%d %s\n' % (0, "dihedral types"))
    fout.write('\t%d %s\n' % (0, "improper types"))

    fout.write('%5.6f %5.6f %s\n' % (-1000.000000, 1000.000000, "xlo xhi"))
    fout.write('%5.6f %5.6f %s\n' % (-1000.000000, 1000.000000, "ylo yhi"))
    fout.write('%5.6f %5.6f %s\n' % (-1000.000000, 1000.000000, "zlo zhi"))

    fout.write('%s\n' % (" "))
    fout.write('%s\n' % (" "))

    # Write masses
    
    fout.write('%s\n%s\n' % ("Masses", " "))
    
    flist = glob.glob(massfile)

    for fname in flist:
            a = np.loadtxt(fname, usecols=(1,))
            
            for i in range(0,len(a[:])):
                    fout.write('%d\t%5.4f\n' % (i+1, a[i]))

    fout.write('%s\n' % (" "))
    
    # Write atoms
                
    fout.write('%s\n' % ("Atoms"))

    fout.write('%s\n' % (" "))
                    
    f4list = glob.glob(cg1file)
                    
    for fname in f4list:
        a4 = np.loadtxt(fname,skiprows=2,usecols=(1,2,3))

        for i in range(0,len(a4[:,1])):
                fout.write('%d %d %d %5.4f %5.4f %5.4f\n' % (i+1, 1, i+1, a4[i,0], a4[i,1], a4[i,2]))

    fout.write('%s\n' % (" "))
    
    # Write bonds

    fout.write('%s\n' % ("Bonds"))

    fout.write('%s\n' % (" "))

    f5list = glob.glob(cgkfile)

    for fname in f5list:
            a5 = np.loadtxt(fname)

            for i in range(0,len(a5[:,1])):
                    fout.write('%d %d %d %d\n' % (i+1, i+1, a5[i,0], a5[i,1]))

    fout.close()  

def write_lammps_files(output_dir, lammps_dir):
    """
    Write LAMMPS data files from the output directory.

    Args:
        output_dir (str): Directory containing the output files.
        lammps_dir (str): Directory to write the LAMMPS data files.
    """
    # Ensure the output directory exists
    os.makedirs(lammps_dir, exist_ok=True)

    # Define file paths
    massfile = os.path.join(output_dir, "mass_1.dat")
    cgkfile = os.path.join(output_dir, "cgk_avg.dat")
    cg1file = os.path.join(output_dir, "cg1_avg.xyz")
    
    # Write bond coefficients
    bond_coeff_file = os.path.join(lammps_dir, "lammpsbondcoeff.dat")
    with open(bond_coeff_file, "w") as fout:
        get_bond_coeff(fout, cgkfile)

    # Write data file
    data_file = os.path.join(lammps_dir, "lammpsdata.dat")
    with open(data_file, "w") as fout:
        get_data(fout, massfile, cgkfile, cg1file)