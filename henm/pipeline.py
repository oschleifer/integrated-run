import os
from henm.align import alignMDA
from henm.estimate import estimate
from henm.average import average_results

def run_pipeline(gro_trr_pairs, output_dir):
    """
    Run the full UCG parameter pipeline:
    1. Align trajectories
    2. Estimate parameters using fluc scripts
    3. Average all outputs

    Args:
        gro_trr_pairs (list of tuples): List of (gro_path, trr_path) input files
        output_dir (str): Where to store outputs
    """
    os.makedirs(output_dir, exist_ok=True)
    
    aligned_structs = []
    aligned_trajs = []

    for i, (gro_path, trr_path) in enumerate(gro_trr_pairs, 1):
        struc_out = os.path.abspath(os.path.join(output_dir, f"struc_ave_{i}.pdb"))
        traj_out = os.path.abspath(os.path.join(output_dir, f"traj_sup_{i}.pdb"))
        
        print(f"[{i}] Aligning {gro_path} and {trr_path}")
        alignMDA(gro_path, trr_path, struc_out, traj_out)
            
        aligned_structs.append(struc_out)
        aligned_trajs.append(traj_out)

    for i, (struc, traj) in enumerate(zip(aligned_structs, aligned_trajs), 1):
        print(f"[{i}] Estimating parameters from aligned PDBs")
        estimate(struc, traj, output_dir, i)

    print(f"Averaging results across {len(gro_trr_pairs)} runs...")
    average_results(output_dir, len(gro_trr_pairs))
    print("Done.")
