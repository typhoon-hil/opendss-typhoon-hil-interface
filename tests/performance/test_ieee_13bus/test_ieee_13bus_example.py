# Imports
import pytest
import os
from pathlib import Path
from typhoon.api.schematic_editor import model as mdl
import typhoon.api.hil as hil
import typhoon.test.capture as cap
import typhoon.test.signals as sig
from typhoon.test.ranges import around
from typhoon.test.reporting.tables import attach_table
from typhoon.test.reporting.messages import report_step
from tests import utils
import numpy as np
import pandas as pd

# Use VHIL
use_vhil = True

FILE_DIR_PATH = Path(__file__).parent

# Path to model file and to compiled model file
model_file_name = "ieee_13bus"
examples_folder_path = FILE_DIR_PATH / ".." / ".." / ".." / "examples" / "Package Examples"
model_folder_path = examples_folder_path / "IEEE 13 Bus" / "models" / "Benchmarks" / "IEEE 13 Bus"
model_file_path = model_folder_path / f"{model_file_name}"
parent_dir_path_and_filename = (model_folder_path, model_file_name)

# Cleanup files
clean_files = {
    "tpt_out": model_folder_path.joinpath(f"{model_file_name} Target files", "dss", f"{model_file_name}_master.dss")
}

# Signals Data
load_names = ["Load 632", "Load 634", "Load 645", "Load 646", "Load 671", "Load 652", "Load 611", "Load 692", "Load 675"]


@pytest.fixture(scope='session')
def summary_data():
    test_st_data = pd.DataFrame(
        columns=["Load - Node", "IEEE", "DSS", "SCADA", "Error DSS [%]", "Error HIL [%]"])
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

    # Start simulation
    hil.start_simulation()

    # Wait the Tap changer
    hil.wait_sec(500)

    # IEEE Voltages
    ref_voltages = get_ieee_voltage_ref()

    load_data = {}
    for load_name in load_names:
        with report_step(f"Reading {load_name}"):
            load_data[load_name] = {}
            tse_load_parent = mdl.get_item(load_name)
            if not tse_load_parent:
                tse_load_parent = mdl.get_item(f"Dist {load_name}")
            dss_loads = utils.get_all_dss_elements(mdl, comp_type=["Load"], parent_comp=tse_load_parent)
            load_data.get(load_name).update({"Voltages": {"REF": {}, "DSS": {}, "HIL": {}}})
            for dss_load in dss_loads:
                dss_load_name = mdl.get_fqn(dss_load).replace(".", "-")
                dss_load_voltages = utils.get_load_voltages(load_name=dss_load_name).get("phase")
                for key, val in dss_load_voltages.items():
                    phase = chr(64 + int(key[-1]))
                    ref_voltage = ref_voltages.get(load_name).get(f"V{phase}")
                    load_data.get(load_name).get("Voltages").get("REF").update({f"V{phase}": ref_voltage})
                    # Voltages
                    if "mag" in key:
                        load_data.get(load_name).get("Voltages").get("DSS").update({f"V{phase}": val})
                        meter_name = "Monitor"
                        meter_handle = mdl.get_item(meter_name, parent=tse_load_parent)
                        meter_fqn = mdl.get_fqn(meter_handle)
                        is3ph = True if mdl.get_item("meter_ABC", parent=meter_handle) else False
                        if is3ph:
                            hil_signal = f"{meter_fqn}.meter_ABC.V{phase}n_RMS"
                        else:
                            hil_signal = f"{meter_fqn}.meter_{phase}.V_RMS"

                        hil_voltage = cap.read(hil_signal, avg_reads=10)
                        load_data.get(load_name).get("Voltages").get("HIL").update({f"V{phase}": hil_voltage})

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
            # Voltages
            ref_voltages = load_val.get("Voltages").get("REF")
            dss_voltages = load_val.get("Voltages").get("DSS")
            hil_voltages = load_val.get("Voltages").get("HIL")

            with report_step(f"IEEE vs DSS"):
                for voltage_key in ref_voltages.keys():
                    ref_voltage = ref_voltages.get(voltage_key)
                    dss_voltage = dss_voltages.get(voltage_key)
                    hil_voltage = hil_voltages.get(voltage_key)
                    around_voltage = around(ref_voltage, tol_p=tol_p)

                    dss_voltage_df = df_capture["const_0"]
                    dss_voltage_df[:] = dss_voltage
                    dss_voltage_df.name = f"{load_key} - {voltage_key}"

                    with pytest.assume:
                        sig.assert_is_constant(
                            signal=dss_voltage_df,
                            at_value=around_voltage,
                        )

            with report_step(f"IEEE vs SCADA"):
                for voltage_key in ref_voltages.keys():
                    hil_voltage_df = df_capture["const_0"]
                    hil_voltage_df[:] = hil_voltage
                    hil_voltage_df.name = f"{load_key} - {voltage_key}"

                    with pytest.assume:
                        sig.assert_is_constant(
                            signal=hil_voltage_df,
                            at_value=around_voltage,
                        )

    # Table Routine
    idx = 0
    for load_name in load_data.keys():

        for node in load_data.get(load_name).get("Voltages").get("REF").keys():

            ref_voltage = load_data.get(load_name).get("Voltages").get("REF").get(node)
            dss_voltage = load_data.get(load_name).get("Voltages").get("DSS").get(node)
            hil_voltage = load_data.get(load_name).get("Voltages").get("HIL").get(node)
            dss_error = 100 * (ref_voltage - dss_voltage) / ref_voltage
            hil_error = 100 * (ref_voltage - hil_voltage) / ref_voltage

            summary_data.at[idx+1, "Load - Node"] = f"{load_name} - {node}"
            summary_data.at[idx+1, "IEEE"] = f"{ref_voltage:.2f}"
            summary_data.at[idx+1, "DSS"] = f"{dss_voltage:.2f}"
            summary_data.at[idx+1, "SCADA"] = f"{hil_voltage:.2f}"
            summary_data.at[idx+1, "Error DSS [%]"] = f"{dss_error:.2f}"
            summary_data.at[idx+1, "Error HIL [%]"] = f"{hil_error:.2f}"
            idx = idx + 1


def test_summary(summary_data):
    attach_table(summary_data, allure_title="Results Table", caption="Load Voltages")


def get_ieee_voltage_ref():
    """"
    IEEE Voltage data are in pu values
    """
    ref_data = {
        "Load 632": {
            "VA": 1.0210 * 4.16e3 / np.sqrt(3),
            "VB": 1.0420 * 4.16e3 / np.sqrt(3),
            "VC": 1.0174 * 4.16e3 / np.sqrt(3),
        },
        "Load 634": {
            "VA": 0.9940 * 0.48e3 / np.sqrt(3),
            "VB": 1.0218 * 0.48e3 / np.sqrt(3),
            "VC": 0.9960 * 0.48e3 / np.sqrt(3),
        },
        "Load 645": {
            "VB": 1.0329 * 4.16e3 / np.sqrt(3),
        },
        "Load 646": {
            "VB": 1.0311 * 4.16e3 / np.sqrt(3),
            "VC": 1.0134 * 4.16e3 / np.sqrt(3),
        },
        "Load 671": {
            "VA": 0.9900 * 4.16e3 / np.sqrt(3),
            "VB": 1.0529 * 4.16e3 / np.sqrt(3),
            "VC": 0.9778 * 4.16e3 / np.sqrt(3),
        },
        "Load 652": {
            "VA": 0.9825 * 4.16e3 / np.sqrt(3),
        },
        "Load 611": {
            "VC": 0.9738 * 4.16e3 / np.sqrt(3),
        },
        "Load 692": {
            "VA": 0.9900 * 4.16e3 / np.sqrt(3),
            "VC": 0.9777 * 4.16e3 / np.sqrt(3),
        },
        "Load 675": {
            "VA": 0.9835 * 4.16e3 / np.sqrt(3),
            "VB": 1.0553 * 4.16e3 / np.sqrt(3),
            "VC": 0.9758 * 4.16e3 / np.sqrt(3),
        },
    }

    return ref_data
