#!/bin/env bash
set -eu

# USAGE: sbatch -J "ccbrXYZ" --mem=24g --cpus-per-task=4 --time=24:00:00 submit.sh "/path/to/ccbrYXZ/RNA_OUT/DME/" "/path/to/dme/repo/HPC_DME_APIs/" "/CCBR_Archive"

# Launches a job to push local data into HPC DME
# @INPUT $1 = DME base directory for all intermediate output files (i.e. ${INPUT_DIRECTORY)/DME)
# @INPUT $2 = Path to local git installation of DME CLU toolkit
# @INPUT $3 = DME Vault to push data (i.e. /CCBR_Archive or /CCBR_EXT_Archive)

# Goto upload/ location which contains files and metadata to upload
cd "${1}"

# HPC DME API entry point
export HPC_DM_UTILS="${2%/}/utils"
source "$HPC_DM_UTILS/functions"

# Reformat Vault Name
VAULT="/${3#/}"
dm_register_directory -s -t ${SLURM_CPUS_PER_TASK:-4} -e <(echo '**.metadata.json') upload "${VAULT}"

echo "Exit status of upload: $?"
