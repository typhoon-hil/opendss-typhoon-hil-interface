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
# e.g.: path_and_file = ("path/to/this/directory", "test_single_phase_contactor")
parent_dir_path_and_filename = (current_test_dir, test_file_name)

# Cleanup files
clean_files = {
    "tpt_out": current_test_dir.joinpath(f"{test_file_name} Target files", "dss", f"{test_file_name}_master.dss")
}

# Delete previously converted files
@pytest.mark.pre_cleanup
@pytest.mark.parametrize("pre_cleanup", [clean_files], indirect=True)
def test_clean(pre_cleanup):
    assert pre_cleanup

# Conversion test
@pytest.mark.exporting
@pytest.mark.parametrize("convert_to_tpt", [parent_dir_path_and_filename], indirect=True)
def test_conversion_to_tpt(reload_hil_libraries, convert_to_tpt):
    reload_hil_libraries
    output_path = convert_to_tpt
    assert os.path.isfile(output_path)

# Test loading with third-party tool
@pytest.mark.exporting
@pytest.mark.parametrize("compile_tpt_model", [clean_files["tpt_out"]], indirect=True)
def test_compile_tpt_model(compile_tpt_model):
    compilation_result = compile_tpt_model
    assert compilation_result == ''

# Specific test for this file
@pytest.mark.exporting
@pytest.mark.parametrize("load_and_compile_to_hil", [(parent_dir_path_and_filename, use_vhil)], indirect=True)
def test_line_hil(load_and_compile_to_hil):

    # Get from the DSS simulation a current value to compare
    expected_Irms1 = utils.get_element_current(elem_name="Line1", elem_class="Line").get("mag_a")

    # Start capture
    start_capture(duration=0.2, signals=['Irms1'], executeAt=0)

    # Start simulation
    hil.start_simulation()

    # Data acquisition
    capture = get_capture_results(wait_capture=True)
    Irms1 = capture['Irms1']

    # Compare HIL and DSS outputs with 0.5% error tolerance
    sig.assert_is_constant(Irms1, during=(0.15 - 0.001, 0.15 + 0.001), at_value=around(expected_Irms1, tol_p=0.005))

    # Stop simulation
    hil.stop_simulation()
