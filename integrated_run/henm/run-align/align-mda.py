import MDAnalysis as mda
import MDAnalysis.transformations as trans
from MDAnalysis.transformations.positionaveraging import PositionAverager

# Load in the reference structure
ref_structure = "../input-files/protein_initial_unaligned.gro"
ref = mda.Universe(ref_structure)
atoms_ref_kras_bb = ref.select_atoms("name BB")

# Load in the trajectory
traj_file = "../input-files/protein_bb_unaligned_pbc_fixed.trr"
mobile = mda.Universe(ref_structure, traj_file, in_memory=True)
atoms_mobile_kras_bb = mobile.select_atoms("name BB")

# Transforms:
# 1) Center on KRAS CYF B
# 2) translate up in z axes 
# 3) wrap all particles into the box 

# TODO: what's the best residue to center on
atoms_mobile_kras_CYF_bb  = mobile.select_atoms("index 250")
transforms = [trans.center_in_box(atoms_mobile_kras_CYF_bb),
              trans.translate([0,0,40]),
              trans.wrap(mobile.atoms)]
mobile.trajectory.add_transformations(*transforms)

NUMMDL = len(mobile.trajectory)

# Alignment:
aligner = mda.analysis.align.AlignTraj(mobile, ref, select="name BB", in_memory=True).run()

with mda.Writer("../input-files/mda_traj_sup.pdb", mobile.atoms.n_atoms) as writer:
    for ts in mobile.trajectory:
        writer.write(mobile)

# Step 2: Open the file, read its contents, and prepend the custom header
with open("../input-files/mda_traj_sup.pdb", "r+") as pdb_file:
    content = pdb_file.read()
    pdb_file.seek(0, 0)
    pdb_file.write(f"NUMMDL   {NUMMDL}\n" + content)

# Compute average structure across all frames

aligned_traj_file = "../input-files/mda_traj_sup.pdb"
mobile_aligned = mda.Universe(aligned_traj_file)

transformation = PositionAverager(NUMMDL, check_reset=True)
mobile_aligned.trajectory.add_transformations(transformation)

for ts in mobile_aligned.trajectory:
    # applies transformation across all frames
    pass

with mda.Writer("../input-files/mda_structure_ave.pdb", mobile_aligned.atoms.n_atoms) as writer:
    writer.write(mobile_aligned.atoms)

