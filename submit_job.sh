#!/bin/bash
#PBS -N LID_Toolkit_Trial
#PBS -l select=1:ncpus=4:mem=16GB
#PBS -l walltime=02:00:00
#PBS -m be
#PBS -M 25167626@sun.ac.za

# 1. Secure your data and set up scratch space [cite: 230, 1866]
umask 0077
SPACED="$(echo ${PBS_JOBID} | cut -d. -f1)"
TMP=/scratch-small-local/${SPACED}
mkdir -p ${TMP}

# 2. Copy your toolkit from home to the high-speed local disk [cite: 1891, 1899]
echo "Copying toolkit to ${TMP}..."
/usr/bin/rsync -vax "${PBS_O_WORKDIR}/" "${TMP}/"
cd ${TMP}

# 3. Install Miniconda locally on the compute node [cite: 1881, 1882]
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh
bash miniconda.sh -b -p ./miniconda
source ./miniconda/bin/activate

# 4. Build and activate your environment from the .yml file [cite: 1894, 1905]
echo "Building Conda environment..."
conda env create -f environment.yml
conda activate language_identification_project

# 5. Run your Python script [cite: 1919]
echo "Starting Language Identification script..."
python predict_fasttext_x_test.py

# 6. Copy results back to your home directory [cite: 1913, 1920]
echo "Copying results back to ${PBS_O_WORKDIR}..."
/usr/bin/rsync -vax "${TMP}/fasttext_predictions_hpc.csv" "${PBS_O_WORKDIR}/"

# 7. Clean up the scratch space [cite: 228, 1916]
[ $? -eq 0 ] && /bin/rm -rf ${TMP}
