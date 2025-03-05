from pylab import *
import scipy
import sys
import glob
import numpy as np

fout = open(sys.argv[1],'w')

#ffs = sys.argv[2]
#lfs = sys.argv[3]
#print ffs,lfs
#fframe = int(ffs)
#lframe = int(lfs)
flist = glob.glob('../run-py/mass.dat')


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

fout.write('%s\n%s\n' % ("Masses", " "))

for fname in flist:
        a = np.loadtxt(fname, usecols=(1,))
        
        for i in range(0,len(a[:])):
                fout.write('%d\t%5.4f\n' % (i+1, a[i]))
                



fout.write('%s\n' % (" "))
            
fout.write('%s\n' % ("Atoms"))

fout.write('%s\n' % (" "))
                
                
f4list = glob.glob('../run-py/cg1.xyz')
                
for fname in f4list:
       a4 = np.loadtxt(fname,skiprows=2,usecols=(1,2,3))

       for i in range(0,len(a4[:,1])):
               fout.write('%d %d %d %5.4f %5.4f %5.4f\n' % (i+1, 1, i+1, a4[i,0], a4[i,1], a4[i,2]))
               


fout.write('%s\n' % (" "))

fout.write('%s\n' % ("Bonds"))

fout.write('%s\n' % (" "))

f5list = glob.glob('../run-py/cgk.dat')


for fname in f5list:
        a5 = np.loadtxt(fname)

        for i in range(0,len(a5[:,1])):
                fout.write('%d %d %d %d\n' % (i+1, i+1, a5[i,0], a5[i,1]))


                
fout.close()  
