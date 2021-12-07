This directory contains the python scripts that make up the OpenDSS2Typhoon importer. The importer can be run directly from the OpenDSS2Typhoon.exe executable file and does not require that these scripts be present. If you whish to analyze or modify the functionalty of the importer, however, you can run the importer from the source scripts instead. To run the importer, you will need to install the following dependencies:

numpy==1.20.1
Typhoon-HIL-API==1.13.0
OpenDSSDirect.py==0.6.1
OpenDSSDirect.py[extras]
Pillow==7.2.0
tqdm==4.61.1

With these packages installed, you can run the importer by calling main.py. The files main.py, modules.py and elements.py serve the following roles:

> main.py : main function for the OpenDSS2Typhoon importer.
> modules.py : contains functions used by the importer to perform various importation tasks. e.g. load a .dss file for analysis, determine the placement of components in the .tse file, and generate a .tse file.
> elements.py : contains information on how each OpenDSS element type is imported into the Typhoon HIL environment.