# Imports
import pytest
import os
from pathlib import Path
from typhoon.api.schematic_editor import model as mdl
import typhoon.api.hil as hil
from typhoon.test.capture import start_capture, get_capture_results
import typhoon.test.signals as sig
from typhoon.test.ranges import around
from typhoon.test.reporting.tables import attach_table
import sys
import pathlib
from tests import utils
import numpy as np
import pandas as pd

# Use VHIL
use_vhil = True


FILE_DIR_PATH = Path(__file__).parent

# Path to model file and to compiled model file
model_file_name = "cigre_european_mv"
examples_folder_path = FILE_DIR_PATH / ".." / ".." / ".." / "examples" / "Package Examples"
model_folder_path = examples_folder_path / "Cigre European MV" / "models" / "Benchmarks" / "Cigre European MV"
model_file_path = model_folder_path / f"{model_file_name}"
parent_dir_path_and_filename = (model_folder_path, model_file_name)

# Cleanup files
clean_files = {
    "tpt_out": model_folder_path.joinpath(f"{model_file_name} Target files", "dss", f"{model_file_name}_master.dss")
}

# Signals Data
hil_bus0_va = "Grid_Monitor.meter_ABC.VAn_RMS"
hil_bus1_va = "Load_1.Monitor.meter_ABC.VAn_RMS"
hil_bus2_va = "Bus2_Monitor.meter_ABC.VAn_RMS"
hil_bus3_va = "Load_3.Monitor.meter_ABC.VAn_RMS"
hil_bus4_va = "Load_4.Monitor.meter_ABC.VAn_RMS"
hil_bus5_va = "Load_5.Monitor.meter_ABC.VAn_RMS"
hil_bus6_va = "Load_6.Monitor.meter_ABC.VAn_RMS"
hil_bus7_va = "Load_7.Monitor.meter_ABC.VAn_RMS"
hil_bus8_va = "Load_8.Monitor.meter_ABC.VAn_RMS"
hil_bus9_va = "Load_9.Monitor.meter_ABC.VAn_RMS"
hil_bus10_va = "Load_10.Monitor.meter_ABC.VAn_RMS"
hil_bus11_va = "Load_11.Monitor.meter_ABC.VAn_RMS"
hil_bus12_va = "Load_12.Monitor.meter_ABC.VAn_RMS"
hil_bus13_va = "Load_13.Monitor.meter_ABC.VAn_RMS"
hil_bus14_va = "Load_14.Monitor.meter_ABC.VAn_RMS"
hil_bus_signals = [hil_bus0_va, hil_bus1_va, hil_bus2_va, hil_bus3_va, hil_bus4_va, hil_bus5_va,
                   hil_bus6_va, hil_bus7_va, hil_bus8_va, hil_bus9_va, hil_bus10_va, hil_bus11_va,
                   hil_bus12_va, hil_bus13_va, hil_bus14_va]


@pytest.fixture(scope='session')
def summary_data():
    test_st_data = pd.DataFrame(
        columns=["Bus", "VLL CIGRE [kV]", "VLL DSS [kV]", "VLL HIL [kV]", "Error DSS [%]", "Error HIL [%]"])
    yield test_st_data


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
def test_simulation_hil(load_and_compile_to_hil, summary_data):
    """"
    Compare phase A voltage of CIGRE, DSS, and HIL
    """
    # CIGRE Voltages
    ref_voltages_phase_a = get_cigre_voltage_ref()

    # DSS Voltages
    dss_bus_list_names = [f"Bus{number}" for number in range(0, 15)]
    dss_voltages = [utils.get_bus_voltages(bus_name) for bus_name in dss_bus_list_names]
    dss_voltages_phase_a = {bus_name: volt.get("phase").get("mag_1") / 1000
                            for bus_name, volt in zip(dss_bus_list_names, dss_voltages)}

    # Start capture
    start_capture(
        duration=1.0,
        signals=hil_bus_signals,
        executeAt=1.0,
    )

    # Start simulation
    hil.start_simulation()

    # Data acquisition
    df_capture = get_capture_results(wait_capture=True)

    # Stop simulation
    hil.stop_simulation()

    # HIL Voltages
    hil_voltages_phase_a = {bus_name: df_capture[signal] / 1000
                            for bus_name, signal in zip(dss_bus_list_names, hil_bus_signals)}

    # Representing DSS values as dataframes to use the sig.assertion function
    dss_voltages_phase_a_df = {}
    dummy_df = df_capture[hil_bus0_va]
    for bus in dss_bus_list_names:
        dss_voltage = dss_voltages_phase_a.get(bus)
        dummy_df[:] = dss_voltage
        dummy_df.name = f"DSS - {bus}.Va"
        dss_voltages_phase_a_df.update({bus: dummy_df.copy()})

    # Compare DSS-CIGRE and HIL-CIGRE signals with 0.5% error tolerance
    tol_p = 0.005
    for bus in dss_bus_list_names:
        ref_bus_voltage = ref_voltages_phase_a.get(bus)
        dss_bus_voltage = dss_voltages_phase_a_df.get(bus)
        hil_bus_voltage = hil_voltages_phase_a.get(bus)
        cigre_tol = around(val=ref_bus_voltage, tol_p=tol_p)

        with pytest.assume:
            # Compare DSS to CIGRE
            sig.assert_is_constant(
                signal=dss_bus_voltage,
                at_value=cigre_tol,
            )

        with pytest.assume:
            # Compare HIL to CIGRE
            sig.assert_is_constant(
                signal=hil_bus_voltage,
                at_value=cigre_tol,
            )

    # Table Routine
    for idx, bus in enumerate(dss_bus_list_names):
        # Converted to line-line voltages
        ref_bus_voltage = ref_voltages_phase_a.get(bus)*np.sqrt(3)
        dss_bus_voltage = dss_voltages_phase_a_df.get(bus).mean()*np.sqrt(3)
        hil_bus_voltage = hil_voltages_phase_a.get(bus).mean()*np.sqrt(3)
        dss_error = 100 * (dss_bus_voltage - ref_bus_voltage) / ref_bus_voltage
        hil_error = 100 * (hil_bus_voltage - ref_bus_voltage) / ref_bus_voltage

        summary_data.at[idx+1, "Bus"] = bus
        summary_data.at[idx+1, "VLL CIGRE [kV]"] = f"{ref_bus_voltage:.2f}"
        summary_data.at[idx+1, "VLL DSS [kV]"] = f"{dss_bus_voltage:.2f}"
        summary_data.at[idx+1, "VLL HIL [kV]"] = f"{hil_bus_voltage:.2f}"
        summary_data.at[idx+1, "Error DSS [%]"] = f"{dss_error:.2f}"
        summary_data.at[idx+1, "Error HIL [%]"] = f"{hil_error:.2f}"


def test_summary(summary_data):
    attach_table(summary_data, allure_title="Results Tabble", caption="Bus Voltages")


def get_cigre_voltage_ref():
    """"
    The CIGRE documentation show the Line Voltages in KV
    As the system is balanced, it will be converted for Phase Voltages and only one phase will be used
    """
    ref_data = {
        "Bus0": 110 / np.sqrt(3),
        "Bus1": 20.52 / np.sqrt(3),
        "Bus2": 20.09 / np.sqrt(3),
        "Bus3": 19.43 / np.sqrt(3),
        "Bus4": 19.40 / np.sqrt(3),
        "Bus5": 19.38 / np.sqrt(3),
        "Bus6": 19.35 / np.sqrt(3),
        "Bus7": 19.33 / np.sqrt(3),
        "Bus8": 19.33 / np.sqrt(3),
        "Bus9": 19.31 / np.sqrt(3),
        "Bus10": 19.29 / np.sqrt(3),
        "Bus11": 19.29 / np.sqrt(3),
        "Bus12": 20.04 / np.sqrt(3),
        "Bus13": 19.94 / np.sqrt(3),
        "Bus14": 19.88 / np.sqrt(3),
    }

    return ref_data
