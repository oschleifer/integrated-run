# Parse arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --in1) IN1="$2"; shift ;;
        --in2) IN2="$2"; shift ;;
        --out1) OUT1="$2"; shift ;;
        --out2) OUT2="$2"; shift ;;
        *) echo "Unknown parameter passed: $1"; exit 1 ;;
    esac
    shift
done

# Check that all required arguments are provided
if [[ -z "$IN1" || -z "$IN2" || -z "$OUT1" || -z "$OUT2" ]]; then
    echo "Usage: $0 --in1 <traj_sup.pdb> --in2 <structure_ave.pdb> --out1 <mass_output> --out2 <cgk_output>"
    exit 1
fi

# Run the Python scripts with appropriate inputs
python3 fluc-match-str-pdb.py "$IN1" "$IN2" ../input-files/ba.dat bondfile flucfile 200 1
python3 fluc-match-8f.py bondfile flucfile 40 10000 0

# Copy outputs to desired locations
cp mass.dat "$OUT1"
cp cgk.dat "$OUT2"

