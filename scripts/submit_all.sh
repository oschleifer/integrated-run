#!/bin/bash

lengths=(1 5 10 15 20 25 30 35 40 45 50 55 60 65 70 75 80 85 90 95 100)

# Prepare
mkdir -p out_files
echo "files,time_seconds" > filetimes.txt

for ((i=0; i<${#lengths[@]}; i++)); do
    len=${lengths[$i]}
    jobscript="refine_${len}.sh"

    # Create job script from template
    sed "s/XX/${len}/g" refine_template.sh > "$jobscript"

    # Submit job and get job ID
    jobid=$(bsub < "$jobscript" | awk '{print $2}' | tr -d '<>')
    echo "Submitted job $jobid for length $len"

    # Wait for job to finish
    echo "Waiting for job $jobid to finish..."
    while true; do
        status=$(bjobs "$jobid" 2>&1)
        if echo "$status" | grep -E -q "DONE|EXIT|not found"; then
            echo "Job $jobid finished."
            break
        else
            sleep 10
        fi
    done

    # Delete output directory after every job except the last
    if [ $i -lt $((${#lengths[@]} - 1)) ]; then
        echo "Deleting output directory after length $len"
        rm -rf output
    fi
done

