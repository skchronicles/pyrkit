# biowulf2DME

biowulf2DME is tool to annotate and co-locate NGS data with project-level, sample-level, and pipeline-level metadata. biowulf2DME automates the process of moving data from the cluster to cloud storage in DME.

### Overview
![DME Heirarchy](./assets/DME_Upload_Hierarchy.svg)

**Please Note**: Some of the metadata listed above is pipeline-specific (i.e. only for the RNA-seq pipeline).

### Installation
```bash
# Clone the Repository
git clone https://github.com/skchronicles/pipeliner-docs.git
# Create a virtual environment
python3 -m venv .venv
# Activate the virtual environment
. .venv/bin/activate
# Update pip
pip install --upgrade pip
# Download Dependencies
pip install -r requirements.txt
```
