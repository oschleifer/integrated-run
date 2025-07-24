import os
import argparse
from henm.align import alignMDA
from henm.estimate import estimate
from henm.average import average_results
from henm.write import write_lammps_files

def parse_infile(infile_path):
    """
    Parse a tab-separated file containing GRO/TRR pairs.

    Args:
        infile_path (str): Path to the input file.

    Returns:
        list of tuples: List of (gro_path, trr_path) pairs.
    """
    gro_trr_pairs = []
    with open(infile_path, 'r') as infile:
        for line in infile:
            parts = line.strip().split(',')
            if len(parts) != 2:
               raise ValueError(f"Invalid line in infile, {line}, {len(parts)}")
            gro_trr_pairs.append((parts[0], parts[1]))
    return gro_trr_pairs

def run_pipeline(gro_trr_pairs, output_dir, lammps_dir, stride):
    """
    Run the full UCG parameter pipeline:
    1. Align trajectories
    2. Estimate parameters using fluc scripts
    3. Average all outputs

    Args:
        gro_trr_pairs (list of tuples): List of (gro_path, trr_path) input files
        output_dir (str): Where to store outputs
        lammps_dir (str): Directory to write LAMMPS files
        stride (int): Stride value for alignment
    """
    os.makedirs(output_dir, exist_ok=True)

    aligned_structs = []
    aligned_trajs = []

    for i, (gro_path, trr_path) in enumerate(gro_trr_pairs, 1):
        struc_out = os.path.abspath(os.path.join(output_dir, f"struc_ave_{i}.pdb"))
        traj_out = os.path.abspath(os.path.join(output_dir, f"traj_sup_{i}.pdb"))

        print(f"[{i}] Aligning {gro_path} and {trr_path} with stride {stride}")
        alignMDA(gro_path, trr_path, struc_out, traj_out, stride=stride)

        aligned_structs.append(struc_out)
        aligned_trajs.append(traj_out)

    for i, (struc, traj) in enumerate(zip(aligned_structs, aligned_trajs), 1):
        print(f"[{i}] Estimating parameters from aligned PDBs")
        estimate(struc, traj, output_dir, i)

    print(f"Averaging results across {len(gro_trr_pairs)} runs...")
    average_results(output_dir, len(gro_trr_pairs))
    
    print(f"Writing new LAMMPS files to {lammps_dir}...")
    write_lammps_files(output_dir, lammps_dir)
    
    print("Done.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run full UCG parameter pipeline.")
    parser.add_argument(
        "--inputs",
        nargs="+",
        help="List of input files as GRO/TRR pairs: gro1 trr1 gro2 trr2 ..."
    )
    parser.add_argument(
        "--infile",
        help="Path to a tab-separated file containing GRO/TRR pairs."
    )
    parser.add_argument(
        "--out",
        required=True,
        help="Directory to write output files (cgk.dat and mass.dat)"
    )
    parser.add_argument(
        "--lammps",
        required=True,
        help="Directory to write new files for LAMMPS simulation software"
    )
    parser.add_argument(
        "--stride",
        type=int,
        default=1,
        help="Stride value for alignment (default: 1)"
    )

    args = parser.parse_args()

    if args.inputs and args.infile:
        raise ValueError("You cannot specify both --inputs and --infile. Choose one.")

    if args.infile:
        gro_trr_pairs = parse_infile(args.infile)
    elif args.inputs:
        if len(args.inputs) % 2 != 0:
            raise ValueError("Input files must be provided in GRO/TRR pairs.")
        gro_trr_pairs = [
            (args.inputs[i], args.inputs[i + 1])
            for i in range(0, len(args.inputs), 2)
        ]
    else:
        raise ValueError("You must specify either --inputs or --infile.")

    run_pipeline(gro_trr_pairs, args.out, args.lammps, args.stride)
