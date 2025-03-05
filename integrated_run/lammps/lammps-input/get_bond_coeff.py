import matplotlib.pyplot as plt
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
flist = glob.glob('../run-py/cgk.dat')
#fout.write('#dist-avg\dist-std\n')

cgsites = 40

for fname in flist:
        a = np.loadtxt(fname)
        
        for i in range(0,len(a[:,1])):
                fout.write('%s\t%d\t%s\t%5.4f\t%5.4f\n' % ("bond_coeff", i+1, "harmonic",  a[i,3],  a[i,2]))
                        


fout.close()  
