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

# Signals Data
meter_input_name = "Bus1 Monitor"
meter_output_name = "Bus2 Monitor"

hil_ia_input = f"{meter_input_name}.meter_ABC.IA_RMS"
hil_ib_input = f"{meter_input_name}.meter_ABC.IB_RMS"
hil_ic_input = f"{meter_input_name}.meter_ABC.IC_RMS"
hil_va_input = f"{meter_input_name}.meter_ABC.VAn_RMS"
hil_vb_input = f"{meter_input_name}.meter_ABC.VBn_RMS"
hil_vc_input = f"{meter_input_name}.meter_ABC.VCn_RMS"
hil_ia_output = f"{meter_output_name}.meter_ABC.IA_RMS"
hil_ib_output = f"{meter_output_name}.meter_ABC.IB_RMS"
hil_ic_output = f"{meter_output_name}.meter_ABC.IC_RMS"
hil_va_output = f"{meter_output_name}.meter_ABC.VAn_RMS"
hil_vb_output = f"{meter_output_name}.meter_ABC.VBn_RMS"
hil_vc_output = f"{meter_output_name}.meter_ABC.VCn_RMS"

# Delete previously converted files
@pytest.mark.pre_cleanup
@pytest.mark.parametrize("pre_cleanup", [clean_files], indirect=True)
def test_clean(pre_cleanup):
    assert pre_cleanup


# Conversion test
@pytest.mark.exporting
@pytest.mark.parametrize("convert_to_tpt", [parent_dir_path_and_filename], indirect=True)
def test_conversion_to_tpt(convert_to_tpt):

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

    # DSS Currents
    dss_line1_currents = utils.get_element_currents(elem_name="Line1", elem_class="Line")
    dss_line1_ia_input = dss_line1_currents.get("term1").get("mag_1")
    dss_line1_ib_input = dss_line1_currents.get("term1").get("mag_2")
    dss_line1_ic_input = dss_line1_currents.get("term1").get("mag_3")
    dss_line1_ia_output = dss_line1_currents.get("term2").get("mag_1")
    dss_line1_ib_output = dss_line1_currents.get("term2").get("mag_2")
    dss_line1_ic_output = dss_line1_currents.get("term2").get("mag_3")

    # DSS Voltages
    dss_line1_voltages_input = utils.get_bus_voltages("Bus1")
    dss_line1_va_input = dss_line1_voltages_input.get("phase").get("mag_1")
    dss_line1_vb_input = dss_line1_voltages_input.get("phase").get("mag_2")
    dss_line1_vc_input = dss_line1_voltages_input.get("phase").get("mag_3")
    dss_line1_voltages_output = utils.get_bus_voltages("Bus2")
    dss_line1_va_output = dss_line1_voltages_output.get("phase").get("mag_1")
    dss_line1_vb_output = dss_line1_voltages_output.get("phase").get("mag_2")
    dss_line1_vc_output = dss_line1_voltages_output.get("phase").get("mag_3")

    # Start capture
    start_capture(duration=1.0,
                  signals=[hil_ia_input, hil_ib_input, hil_ic_input,
                           hil_va_input, hil_vb_input, hil_vc_input,
                           hil_ia_output, hil_ib_output, hil_ic_output,
                           hil_va_output, hil_vb_output, hil_vc_output],
                  executeAt=1.0)

    # Start simulation
    hil.start_simulation()

    # Data acquisition
    df_capture = get_capture_results(wait_capture=True)
    hil_line1_ia_input = df_capture[hil_ia_input]
    hil_line1_ib_input = df_capture[hil_ib_input]
    hil_line1_ic_input = df_capture[hil_ic_input]
    hil_line1_ia_output = df_capture[hil_ia_output]
    hil_line1_ib_output = df_capture[hil_ib_output]
    hil_line1_ic_output = df_capture[hil_ic_output]
    hil_line1_va_input = df_capture[hil_va_input]
    hil_line1_vb_input = df_capture[hil_vb_input]
    hil_line1_vc_input = df_capture[hil_vc_input]
    hil_line1_va_output = df_capture[hil_va_output]
    hil_line1_vb_output = df_capture[hil_vb_output]
    hil_line1_vc_output = df_capture[hil_vc_output]

    # Stop simulation
    hil.stop_simulation()

    # Compare HIL and DSS signals with 0.5% error tolerance
    tol_p = 0.005

    # Input Currents
    hil_input_currents = [hil_line1_ia_input, hil_line1_ib_input, hil_line1_ic_input]
    dss_input_currents = [dss_line1_ia_input, dss_line1_ib_input, dss_line1_ic_input]
    for hil_current, dss_current in zip(hil_input_currents, dss_input_currents):
         with pytest.assume:
            sig.assert_is_constant(
                signal=hil_current,
                at_value=around(val=dss_current, tol_p=tol_p),
            )

    # Output Currents
    hil_output_currents = [hil_line1_ia_output, hil_line1_ib_output, hil_line1_ic_output]
    dss_output_currents = [dss_line1_ia_output, dss_line1_ib_output, dss_line1_ic_output]
    for hil_current, dss_current in zip(hil_output_currents, dss_output_currents):
         with pytest.assume:
            sig.assert_is_constant(
                signal=hil_current,
                at_value=around(val=dss_current, tol_p=tol_p),
            )

    # Input Voltages
    hil_input_voltages = [hil_line1_va_input, hil_line1_vb_input, hil_line1_vc_input]
    dss_input_voltages = [dss_line1_va_input, dss_line1_vb_input, dss_line1_vc_input]
    for hil_voltage, dss_voltage in zip(hil_input_voltages, dss_input_voltages):
         with pytest.assume:
            sig.assert_is_constant(
                signal=hil_voltage,
                at_value=around(val=dss_voltage, tol_p=tol_p),
            )

    # Output Voltages
    hil_output_voltages = [hil_line1_va_output, hil_line1_vb_output, hil_line1_vc_output]
    dss_output_voltages = [dss_line1_va_output, dss_line1_vb_output, dss_line1_vc_output]
    for hil_voltage, dss_voltage in zip(hil_output_voltages, dss_output_voltages):
         with pytest.assume:
            sig.assert_is_constant(
                signal=hil_voltage,
                at_value=around(val=dss_voltage, tol_p=tol_p),
            )
