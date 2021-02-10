__author__ = "Ivana Klindo."
"""
Subject:
    Bus component (OpenDSS)

Description:
    This test verifies functionality of the bus component.
"""

import typhoon.api.hil as hil
from typhoon.api.schematic_editor import model
import os
import typhoon.test.signals as signal
import numpy as np
import pytest
from pytest import assume
import logging
from pathlib import Path
import typhoon.test.capture as capture

logger = logging.getLogger(__name__)  
FILE_DIR_PATH = Path(__file__).parent
(script_dir, script_file) = os.path.split(os.path.abspath(__file__))

MODEL_NAME_1 = "test_bus_component_1.tse"
MODEL_NAME_2 = "test_bus_component_2.tse"
MODEL_NAME_3 = "test_bus_component_3.tse"

component_name = "Bus1"

model_path_1 = str(FILE_DIR_PATH / 'hil_model' / MODEL_NAME_1)
model_path_2 = str(FILE_DIR_PATH / 'hil_model' / MODEL_NAME_2)
model_path_3 = str(FILE_DIR_PATH / 'hil_model' / MODEL_NAME_3)

compiled_model_path_1 = model.get_compiled_model_file(model_path_1)
compiled_model_path_2 = model.get_compiled_model_file(model_path_2)
compiled_model_path_3 = model.get_compiled_model_file(model_path_3)

required_features = ["hw_capture", "hw_pe_fsm"]


@pytest.fixture(scope="module")
def setup_function_1():
    # load schematic
    model.load(model_path_1)
    try:
        hw_settings = model.detect_hw_settings()
        vhil_device = False
        logger.info("{} {} device is used".format(hw_settings[0], hw_settings[2]))
    except Exception:
        vhil_device = True

    model.compile()
    hil.load_model(compiled_model_path_1, vhil_device=vhil_device)


def test_bus_component_1(setup_function_1):
    """
    This test function verify bus component.
    """

    SIGNALS = ["Vs1", "Va"]
    # set input
    voltage_src = 10e3
    hil.set_source_sine_waveform("Vs1", rms=voltage_src, frequency=50)

    hil.start_simulation()
    capture.start_capture(0.1, signals=SIGNALS)
    capture.wait_capture_finish()
    #flag_status = util.get_simulation_flag_status()
    hil.stop_simulation()

    cap_data = capture.get_capture_results()
    Vsource = cap_data["Vs1"]
    Va = cap_data["Va"]

    with assume:
        signal.assert_follows_reference(Va, Vsource,tol=5, strictness=0.99)
    # with assume:
    #    assert not flag_status, "Flag check"


@pytest.fixture(scope="module")
def setup_function_2():
     # load schematic
    model.load(model_path_2)
    try:
        hw_settings = model.detect_hw_settings()
        vhil_device = False
        logger.info("{} {} device is used".format(hw_settings[0], hw_settings[2]))
    except Exception:
        vhil_device = True

    model.compile()
    hil.load_model(compiled_model_path_2, vhil_device=vhil_device)


def test_bus_component_2(setup_function_2):
    """
    This test function verify internal measurements of bus component.
    """

    SIGNALS = ["Vs1_b", "Vb", "Bus1.Vbc.Vinst"]
    # set inputs
    voltage_src = 10e3
    hil.set_source_sine_waveform("Vs1", rms=voltage_src, frequency=50)

    hil.start_simulation()
    capture.start_capture(0.1, signals=SIGNALS)
    capture.wait_capture_finish()
    #flag_status = util.get_simulation_flag_status()
    hil.stop_simulation()

    cap_data = capture.get_capture_results()
    Vsource_b = cap_data["Vs1_b"]
    Vb = cap_data["Vb"]
    Vbc = cap_data["Bus1.Vbc.Vinst"]

    expected_amplitude = voltage_src * np.sqrt(2) * np.sqrt(3)

    max_meas = np.max(Vbc)

    tolerance = 0.15

    with assume:
        signal.assert_follows_reference(Vb, Vsource_b, tol=5, strictness=0.99)
    with assume:
        assert pytest.approx(expected_amplitude, abs=tolerance) == max_meas
    # with assume:
    #    assert not flag_status, "Flag check"


@pytest.fixture(scope="module")
def setup_function_3():
     # load schematic
    model.load(model_path_3)
    try:
        hw_settings = model.detect_hw_settings()
        vhil_device = False
        logger.info("{} {} device is used".format(hw_settings[0], hw_settings[2]))
    except Exception:
        vhil_device = True

    model.compile()
    hil.load_model(compiled_model_path_3, vhil_device=vhil_device)


def test_bus_component_3(setup_function_3):
    """
    This test function verify internal measurements of bus component with 3 connectors.
    """

    SIGNALS = ["Vs1_a", "Vs1_c", "Va", "Vc", "Bus1.Vab.Vinst", "Bus1.Vca.Vinst"]
    # set inputs
    voltage_src = 10e3
    hil.set_source_sine_waveform("Vs1", rms=voltage_src, frequency=50)

    hil.start_simulation()
    capture.start_capture(0.1, signals=SIGNALS)
    capture.wait_capture_finish()
    # flag_status = util.get_simulation_flag_status()
    hil.stop_simulation()

    cap_data = capture.get_capture_results()
    Vsource_a = cap_data["Vs1_a"]
    Vsource_c = cap_data["Vs1_c"]
    Va = cap_data["Va"]
    Vc = cap_data["Vc"]
    Vab = cap_data["Bus1.Vab.Vinst"]
    Vca = cap_data["Bus1.Vca.Vinst"]

    expected_amplitude = voltage_src * np.sqrt(2) * np.sqrt(3)

    max_meas_Vab = np.max(Vab)
    max_meas_Vca = np.max(Vca)

    tolerance = 0.15

    with assume:
        signal.assert_follows_reference(Va, Vsource_a, tol=5, strictness=0.99)
    with assume:
        signal.assert_follows_reference(Vc, Vsource_c, tol=5, strictness=0.99)
    with assume:
        assert pytest.approx(expected_amplitude, abs=tolerance) == max_meas_Vab == max_meas_Vca
    # with assume:
    #    assert not flag_status, "Flag check"