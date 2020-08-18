# biowulf2DME

![badge](https://action-badges.now.sh/skchronicles/biowulf2DME?action=ci)  [![GitHub issues](https://img.shields.io/github/issues/skchronicles/biowulf2DME)](https://github.com/skchronicles/biowulf2DME/issues)  [![GitHub license](https://img.shields.io/github/license/skchronicles/biowulf2DME)](https://github.com/skchronicles/biowulf2DME/blob/master/LICENSE)

`biowulf2DME` is tool to archive and co-locate NGS data with project-level, sample-level, and analysis-level metadata. It automates the process of moving data from the cluster to cloud storage in DME.

Along with capturing analysis-specific metadata for reproducibility, quality-control metadata is captured for each sample.

### Overview
![DME Heirarchy](./assets/DME_Upload_Hierarchy.svg)

> **Please Note**: Some of the metadata listed above is pipeline-specific (i.e. only for the RNA-seq pipeline).

### Installation
```bash
# Clone the Repository
git clone https://github.com/skchronicles/biowulf2DME.git
# Create a virtual environment
python3 -m venv .venv
# Activate the virtual environment
. .venv/bin/activate
# Update pip
pip install --upgrade pip
# Download Dependencies
pip install -r requirements.txt
```
