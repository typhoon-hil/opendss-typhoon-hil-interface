# Imports
import pytest
import os
from pathlib import Path
from typhoon.api.schematic_editor import model as mdl
import typhoon.api.hil as hil
from typhoon.test.capture import start_capture, get_capture_results
import typhoon.test.signals as sig
from typhoon.test.ranges import around
import sys
import pathlib
from tests import utils

# OpenDSS API
import opendssdirect as dss

# Use VHIL
use_vhil = True

# Name of this test file
test_file_name = Path(__file__).stem
# Folder where this file is located
current_test_dir = Path(__file__).parent
# Folder where the importer output TSE file are placed
importer_output_dir = current_test_dir.joinpath("importer_output")
# e.g.: path_and_file = ("path/to/this/directory", "test_single_phase_contactor")
parent_dir_path_and_filename = (current_test_dir, test_file_name)

# Cleanup files
clean_files = {
    "tpt_out": importer_output_dir.joinpath(f"{test_file_name} Target files", "dss", f"{test_file_name}_master.dss"),
    "tse_out": importer_output_dir.joinpath(f"{test_file_name}.tse")
}

# Conversion test
@pytest.mark.pre_cleanup
@pytest.mark.parametrize("pre_cleanup", [clean_files], indirect=True)
def test_clean(pre_cleanup):
    assert pre_cleanup

# DSS file import test
@pytest.mark.importing
@pytest.mark.parametrize("import_tpt_model", [parent_dir_path_and_filename], indirect=True)
def test_import_tpt_model(import_tpt_model):
    output_path = import_tpt_model
    assert os.path.isfile(output_path)

# Conversion test
@pytest.mark.importing
@pytest.mark.parametrize("convert_to_tpt", [(importer_output_dir, test_file_name)], indirect=True)
def test_conversion_to_tpt(reload_hil_libraries, convert_to_tpt):
    reload_hil_libraries
    output_path = convert_to_tpt
    assert os.path.isfile(output_path)

# Test loading original file with third-party tool
@pytest.mark.importing
@pytest.mark.parametrize("compile_tpt_model", [str(current_test_dir.joinpath("test_importer_1.dss"))], indirect=True)
def test_compile_tpt_model(compile_tpt_model):
    compilation_result = compile_tpt_model
    assert compilation_result == ''  # A successful compilation will not return text

# Specific test for this file
@pytest.mark.importing
def test_compare_dss_results():

    # Get the current value from the original DSS file snapshot
    irms_original = utils.get_element_current(elem_name="1-2", elem_class="Line").get("mag_a")

    # Compile the converted DSS and get the current value
    converted_dss = current_test_dir.joinpath("importer_output", f"{test_file_name} Target files",
                                              "dss", f"{test_file_name}_master.dss")
    utils.compile_dss_model(str(converted_dss))  # Compile converted dss model
    irms_converted = utils.get_element_current(elem_name="LINE_1-2", elem_class="Line").get("mag_a")

    # Compare the values with 0.5% error tolerance
    assert abs(irms_converted - irms_original) <= 0.005*abs(irms_converted)

