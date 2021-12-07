# Currently uses OpenDSS.exe specified in the sytem path
import modules as dsm
import inspect
import os
import opendssdirect as dss
import statistics
import numpy as np
from typhoon.api.schematic_editor import SchematicAPI


## Console output formatting
pad_char = '*'
pad_size = 8
blank_lines = 2
print('OpenDSS Importer\n')


sec =  ''' Set up temporary environment '''
#   Set up a temporary directory within the current working directory.
cwd = os.getcwd()
temp_file = cwd+'\\temp'
if not os.path.isdir(temp_file):
    os.mkdir(temp_file)
temp_dir = temp_file


sec = ''' Get a all circuit elements '''
# Identify all active circuit elements and prepare for .tse generation
print(pad_char*pad_size+sec+pad_char*pad_size)
file = dsm.loadDSS(cwd, temp_dir)
comp_dict, circuit_name, loadshapes = dsm.getElements(file)
print(pad_char*(2*pad_size+len(sec))+'\n'*blank_lines)


sec =  ''' Generate TSE placement info '''
#   Generate information about TSE placement. For each component, determine
#   corresponding TSE component, position, and rotation.
print(pad_char*pad_size+sec+pad_char*pad_size)
placement_info = dsm.generatePlacementInfo(comp_dict)
print(pad_char*(2*pad_size+len(sec))+'\n'*blank_lines)


sec =  ''' Create model in TSE '''
print(pad_char*pad_size+sec+pad_char*pad_size)
model = dsm.generateSchematic(comp_dict, placement_info)
save_dir = cwd+'\\schematics'
if not os.path.isdir(save_dir):
    os.mkdir(save_dir)
file_name = os.path.join(save_dir, circuit_name + ".tse")
k = 0
while os.path.isfile(file_name):
    k += 1
    file_name = os.path.join(save_dir, circuit_name + f"({k}).tse")
model.save_as(file_name)
print(f"\nModel saved as '{file_name}'")
if loadshapes:
    object_file = circuit_name
    if k:
        object_file += f'({k})'
    dsm.writeLoadShapes(loadshapes, save_dir, object_file)

os.system(f'start {save_dir} .')
print(pad_char*(2*pad_size+len(sec))+'\n'*blank_lines)


print('')
input('Press enter to close...')
