# Imports
import pytest
import os
from pathlib import Path
from typhoon.api.schematic_editor import model as mdl
import typhoon.api.hil as hil
import typhoon.test.capture as cap
import typhoon.test.signals as sig
from typhoon.test.ranges import around
from typhoon.test.reporting.messages import report_step
import sys
import pathlib
from tests import utils
import numpy as np

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
load_names = ["Load1", "Load2", "Load3", "Load4", "Load5", "Load6", "Load7", "Load8", "Load9", "Load10"]
grid_source_name = "Grid"
internal_grid_source_names = [f"{grid_source_name}.Va", f"{grid_source_name}.Vb", f"{grid_source_name}.Vc"]

# Constants
voltage_base = 4.16e3


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
@pytest.mark.parametrize("grid_voltage_pu", [0.9, 1.0, 1.1])
def test_load_hil(grid_voltage_pu, load_and_compile_to_hil):

    vrms = grid_voltage_pu * voltage_base / (np.sqrt(3))

    # Setting voltage on HIL
    hil.set_source_sine_waveform(
        name=internal_grid_source_names,
        rms=[vrms]*3,
        frequency=[60]*3,
        phase=[0, -120, 120],
    )

    # Setting voltage on DSS
    utils.set_grid_voltage(grid_source_name, grid_voltage_pu)

    # Start simulation
    hil.start_simulation()

    hil.wait_sec(10)

    load_data = {}
    for load_name in load_names:
        with report_step(f"Reading {load_name}"):
            load_data[load_name] = {}
            dss_currents = utils.get_element_currents(elem_name=load_name, elem_class="Load").get("term1")
            dss_powers = utils.get_load_powers(load_name=load_name).get("term1")
            is3ph = True if len(dss_currents) == 6 else False
            load_data.get(load_name).update({"Currents": {"DSS": {}, "HIL": {}}})
            load_data.get(load_name).update({"Powers": {"DSS": {}, "HIL": {}}})
            for key, val in dss_currents.items():
                phase = chr(64 + int(key[-1]))
                # Currents
                if "mag" in key:
                    load_data.get(load_name).get("Currents").get("DSS").update({key: val})
                    if is3ph:
                        meter_name = f"{load_name} - Monitor"
                        hil_signal = f"{meter_name}.meter_ABC.I{phase}_RMS"
                    else:
                        meter_name = f"{load_name} - Monitor"
                        hil_signal = f"{meter_name}.meter_{phase}.I_RMS"

                    hil_current = cap.read(hil_signal, avg_reads=10)
                    load_data.get(load_name).get("Currents").get("HIL").update({key: hil_current})
            # Power
            for key, val in dss_powers.items():
                phase = chr(64 + int(key[-1]))
                load_data.get(load_name).get("Powers").get("DSS").update({key: val})
                if is3ph:
                    meter_name = f"{load_name} - Monitor"
                    if key[0] == "P":
                        hil_signal = f"{meter_name}.meter_ABC.POWER_P{phase}"
                    elif key[0] == "Q":
                        hil_signal = f"{meter_name}.meter_ABC.POWER_Q{phase}"
                else:
                    meter_name = f"{load_name} - Monitor"
                    if key[0] == "P":
                        hil_signal = f"{meter_name}.meter_{phase}.POWER_P"
                    elif key[0] == "Q":
                        hil_signal = f"{meter_name}.meter_{phase}.POWER_Q"
                hil_power = cap.read(hil_signal, avg_reads=10)
                load_data.get(load_name).get("Powers").get("HIL").update({key: hil_power})

    # Dummy signal to use as a df
    # Start capture
    cap.start_capture(
        duration=1.0,
        trigger_source="Forced",
        rate=1e3,
        signals=["const_0"],
    )
    df_capture = cap.get_capture_results(wait_capture=True)

    # Stop simulation
    hil.stop_simulation()

    # Compare HIL and DSS signals with 1% error tolerance
    tol_p = 0.01
    # Checking Signals
    for load_key, load_val in load_data.items():
        with report_step(f"Checking {load_key}"):
            with report_step(f"Currents"):
                # Currents
                dss_currents = load_val.get("Currents").get("DSS")
                hil_currents = load_val.get("Currents").get("HIL")
                current_keys_list = dss_currents.keys()
                for current_key in current_keys_list:
                    dss_current = dss_currents.get(current_key)
                    hil_current = hil_currents.get(current_key)
                    around_current = around(dss_current, tol_p=tol_p)

                    hil_current_df = df_capture["const_0"]
                    hil_current_df[:] = hil_current
                    hil_current_df.name = f"{load_key} - I{chr(64 + int(current_key[-1]))}"

                    with pytest.assume:
                        sig.assert_is_constant(
                            signal=hil_current_df,
                            at_value=around_current,
                        )
            with report_step(f"Powers"):
                # Powers
                dss_powers = load_val.get("Powers").get("DSS")
                hil_powers = load_val.get("Powers").get("HIL")
                power_keys_list = dss_powers.keys()
                for power_key in power_keys_list:
                    dss_power = dss_powers.get(power_key)
                    hil_power = hil_powers.get(power_key)
                    around_power = around(dss_power, tol_p=tol_p)

                    hil_power_df = df_capture["const_0"]
                    hil_power_df[:] = hil_power
                    hil_power_df.name = f"{load_key} - {power_key[0]}{chr(64 + int(power_key[-1]))}"

                    with pytest.assume:
                        sig.assert_is_constant(
                            signal=hil_power_df,
                            at_value=around_power,
                        )
