# Blob Inspector

Blob Inspector is a software designed to analyze blobs in biological images. It provides several common tools for computing metrics related to the blobs, such as coordinates, size, density, and distances.

## Tools

The software offers the following tools:
- Illumination correction
- Segmentation
- Labeling
- Contouring

Results can be saved in CSV files.

## About

Blob Inspector was authored by Laurent Busson as the final project for a Master's degree in Bioinformatics at the University of Bordeaux under the supervision of Marie Beurton-Aymar (LaBRI) and Lucie Brisson (BRIC).
It was developed in Python with the librairies PySide6, scikit-image, numpy, matplotlib and SciPy.
It is released under GNU GPL license.

## Installation

Before installing Blob Inspector, make sure Python is installed on your operating system. You will need administrator rights to do so.

### Windows and macOS
1. Download and install the latest version of Python from [Python's official website](https://www.python.org/).
   
### Linux
1. Open a terminal and type the following command:
```bash
sudo apt-get install python
```

Once Python is installed on your OS, open a terminal or PowerShell in the root directory of the program and run the following command to install all the required packages:
```bash
python install_packages.py
```
This command will install all the necessary dependencies for running the program.

## Running the software

To launch the software, open a terminal or PowerShell in the root directory of the program and run the following command:
```bash
python appli.py
```

For Windows users, you can also double click on the file "BlobInspectorWindows.bat"
