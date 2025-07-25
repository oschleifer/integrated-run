import warnings
warnings.filterwarnings("ignore")

import MDAnalysis as mda
import MDAnalysis.transformations as trans
from MDAnalysis.transformations.positionaveraging import PositionAverager
import argparse


def fix_residues_and_chain(universe):
    for res in universe.residues:
        # Truncate residue names to max 3 characters (PDB standard)
        if len(res.resname) > 3:
            res.resname = res.resname[:3]

def alignMDA(ref_structure, traj_file, output_ave, output_traj, stride=50):
    # Load full reference and trajectory
    ref = mda.Universe(ref_structure)
    mobile = mda.Universe(ref_structure, traj_file, in_memory=True)

    # Select only BB atoms (these are AtomGroups, not new Universes)
    ref_bb = ref.select_atoms("name BB")
    mobile_bb = mobile.select_atoms("name BB")

    # Transformations (optional: still use full mobile for wrapping)
    atoms_mobile_kras_CYF_bb = mobile.select_atoms("index 250")
    transforms = [
        trans.center_in_box(atoms_mobile_kras_CYF_bb),
        trans.wrap(mobile.atoms)
    ]
    mobile.trajectory.add_transformations(*transforms)

    # Alignment using only BB atoms
    aligner = mda.analysis.align.AlignTraj(
        mobile, ref, select="name BB", in_memory=True
    ).run()

    # Subsample frames
    selected_frames = list(range(0, len(mobile.trajectory), stride))
    NUMMDL = len(selected_frames)

    # Write only BB atoms
    fix_residues_and_chain(mobile_bb)
    with mda.Writer(output_traj, mobile_bb.n_atoms) as writer:
        for i, ts in enumerate(mobile.trajectory):
            if i in selected_frames:
                writer.write(mobile_bb)

    # Prepend NUMMDL line to output PDB
    with open(output_traj, "r+") as pdb_file:
        content = pdb_file.read()
        pdb_file.seek(0, 0)
        pdb_file.write(f"NUMMDL   {NUMMDL}\n" + content)

    # Compute average structure (again, use only BB atoms)
    mobile_aligned = mda.Universe(output_traj)
    mobile_aligned_bb = mobile_aligned.select_atoms("name BB")

    transformation = PositionAverager(NUMMDL, check_reset=True)
    mobile_aligned.trajectory.add_transformations(transformation)

    for _ in mobile_aligned.trajectory:
        pass

    fix_residues_and_chain(mobile_aligned_bb)
    with mda.Writer(output_ave, mobile_aligned_bb.n_atoms) as writer:
        writer.write(mobile_aligned_bb)


def main():
    parser = argparse.ArgumentParser(
        description="Align Martini trajectory and compute average structure."
    )
    parser.add_argument(
        "--struc", required=True,
        help="Path to the input structure file (.gro)"
    )
    parser.add_argument(
        "--traj", required=True,
        help="Path to the input trajectory file (.xtc or .trr)"
    )
    parser.add_argument(
        "--out1", required=True,
        help="Path to write the aligned trajectory (.pdb)"
    )
    parser.add_argument(
        "--out2", required=True,
        help="Path to write the average structure (.pdb)"
    )
    parser.add_argument(
        "--stride", type=int, default=50,
        help="Frame stride (default: 50); lower = more frames used"
    )

    args = parser.parse_args()
    alignMDA(args.struc, args.traj, args.out1, args.out2, stride=args.stride)
