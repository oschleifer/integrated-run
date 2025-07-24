import subprocess
import os
import shutil
import glob

def estimate(struc_ave_pdb, traj_sup_pdb, output_dir, run_id):
    # Create a temp directory for intermediate files
    tmp_dir = os.path.join(output_dir, f"tmp_run_{run_id}")
    os.makedirs(tmp_dir, exist_ok=True)

    # Path to input_files directory inside henm/
    script_dir = os.path.dirname(__file__)         # henm/
    input_dir = os.path.join(script_dir, "input_files")

    # Copy all files from input_files/ to tmp_dir
    for file in glob.glob(os.path.join(input_dir, "*")):
        if os.path.isfile(file):
            shutil.copy(file, tmp_dir)

    # Set the project root for PYTHONPATH so fluc scripts can import correctly
    project_root = os.path.abspath(os.path.join(script_dir, ".."))

    try:
        # Run the first fluc script (fluc_match_str_pdb.py)
        subprocess.run([
            "python3", "-m", "henm.fluc_scripts.fluc_match_str_pdb",
            os.path.abspath(struc_ave_pdb),
            os.path.abspath(traj_sup_pdb),
            "ba.dat", "bondfile", "flucfile", "10000", "1"
        ],
        cwd=tmp_dir,  # Run inside tmp dir
        env={**os.environ, "PYTHONPATH": project_root},
        check=True)
        
        # Run the second fluc script (fluc_match_8f.py)
        subprocess.run([
            "python3", "-m", "henm.fluc_scripts.fluc_match_8f",
            "bondfile", "flucfile", "40", "10000", "0"
        ],
        cwd=tmp_dir,
        env={**os.environ, "PYTHONPATH": project_root},
        check=True)

        # Copy mass.dat and cgk.dat to output_dir with run-specific names
        shutil.move(os.path.join(tmp_dir, "mass.dat"), os.path.join(output_dir, f"mass_{run_id}.dat"))
        shutil.move(os.path.join(tmp_dir, "cgk.dat"), os.path.join(output_dir, f"cgk_{run_id}.dat"))
        shutil.move(os.path.join(tmp_dir, "cg1.xyz"), os.path.join(output_dir, f"cg1_{run_id}.xyz"))

    finally:
        # Optional: clean up tmp_dir
        os.chdir(project_root)
        # shutil.rmtree(tmp_dir)
