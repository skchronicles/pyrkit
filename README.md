# pyrkit

![Build](https://github.com/skchronicles/pyrkit/workflows/ci/badge.svg)  [![GitHub issues](https://img.shields.io/github/issues/skchronicles/pyrkit)](https://github.com/skchronicles/pyrkit/issues) [![GitHub license](https://img.shields.io/github/license/skchronicles/pyrkit)](https://github.com/skchronicles/pyrkit/blob/master/LICENSE)  

`pyrkit` is tool to archive and co-locate NGS data with project-level, sample-level, and analysis-level metadata. It automates the process of moving data from the cluster to cloud storage in HPC DME.

### Overview
![DME Heirarchy](./assets/DME_Upload_Hierarchy.svg)

Along with capturing analysis-specific metadata for reproducibility, quality-control metadata is captured for each sample.

> **Please Note**: Some of the metadata listed in the example above is pipeline-specific (i.e. only for the [RNA-seq pipeline](https://ccbr.github.io/pipeliner-docs/RNA-seq/Gene-and-isoform-expression-overview/)).

### Installation
```bash
# Clone the Repository
git clone https://github.com/skchronicles/pyrkit.git
# Create a virtual environment
python3 -m venv .venv
# Activate the virtual environment
. .venv/bin/activate
# Update pip
pip install --upgrade pip
# Download Dependencies
pip install -r requirements.txt
```

