import pathlib
import numpy as np

import typhoon.api.hil as hil
from typhoon.api.schematic_editor import model as mdl

# TSE to OpenDSS converter
import tse_to_opendss
from tse_to_opendss.tse2tpt_base_converter import tse2tpt

# OpenDSS API
import opendssdirect as dss

from typhoon.test.reporting.messages import report_message as log_msg
from typhoon.test.reporting.messages import report_step as log_step
from typhoon.api.package_manager import package_manager as pkm

import sys

###################################################


def reload_hil_libraries():
    mdl.reload_libraries()


def convert_to_dss(tse_file_path):
    load_tse_model(tse_file_path)
    mdl.export_model_to_json()

    # Paths
    parent_folder = pathlib.Path(tse_file_path).parent
    target_files_path = parent_folder.joinpath(str(pathlib.Path(tse_file_path).stem) + ' Target files')
    json_file_path = target_files_path.joinpath(str(pathlib.Path(tse_file_path).stem) + '.json')
    master_dss_file_path = target_files_path.joinpath("dss").joinpath(
        str(pathlib.Path(tse_file_path).stem) + '_master.dss')

    # Simulation parameters
    simdss_found = False
    for comp in mdl.get_items():
        # SimDSS component must be on the top level and named SimDSS1, otherwise load default parameters
        if mdl.get_component_type_name(comp) == "SimDSS":
            simdss_found = True
            break

    if simdss_found:
        sim_parameters = {
            "sim_mode": mdl.get_property_disp_value(mdl.prop(comp, "sim_mode")),
            "algorithm": mdl.get_property_disp_value(mdl.prop(comp, "algorithm")),
            "voltagebases": mdl.get_property_disp_value(mdl.prop(comp, "voltagebases")),
            "basefrequency": mdl.get_property_disp_value(mdl.prop(comp, "baseFreq")),
            "maxiter": mdl.get_property_disp_value(mdl.prop(comp, "maxiter")),
            "miniterations": mdl.get_property_disp_value(mdl.prop(comp, "miniterations")),
            "loadmodel": mdl.get_property_disp_value(mdl.prop(comp, "loadmodel")),
            "stepsize": mdl.get_property_disp_value(mdl.prop(comp, "tsstp")),
            "number": mdl.get_property_disp_value(mdl.prop(comp, "tspoints")),
            "stepsize_unit": mdl.get_property_disp_value(mdl.prop(comp, "tsstp_unit")),
        }
    else:
        sim_parameters = {
            "sim_mode": "Snap",
            "basefrequency": "60",
            "maxiter": "10",
            "miniterations": "2",
            "loadmodel": "Power flow",
            "voltagebases": "[0.480, 12.47]",
        }

    tse2tpt.start_conversion(json_file_path, tse_to_opendss, simulation_parameters=sim_parameters)

    return master_dss_file_path


def compile_dss_model(dss_file_path):
    comp_result = dss.run_command(f'Redirect "{str(dss_file_path)}"')
    return comp_result


def import_dss_model(dss_file_path):
    import importer.scripts.modules as dsm

    dss_file_name = pathlib.Path(dss_file_path).stem
    save_dir = pathlib.Path(dss_file_path).parent.joinpath("importer_output")
    save_dir.mkdir(parents=True, exist_ok=True)

    # Create TSE model using the importer
    comp_dict, circuit_name, loadshapes = dsm.getElements(dss_file_path)
    placement_info = dsm.generatePlacementInfo(comp_dict)
    mdl = dsm.generateSchematic(comp_dict, placement_info)
    output_file_name = str(save_dir.joinpath(f"{dss_file_name}.tse"))
    mdl.save_as(output_file_name)

    # Write loadshapes if they exist in the original DSS model
    if loadshapes:
        dsm.writeLoadShapes(loadshapes, str(save_dir), dss_file_name)

    return output_file_name


def load_tse_model(tse_file_path):
    # Open the converted tse file
    print(f"Load Model {tse_file_path}")
    print(f"{sys.path=}")
    mdl.load(tse_file_path)


def compile_model_and_load_to_hil(tse_file_path, use_vhil=True):
    # Compile the model
    print(f"Compile Model {tse_file_path}")
    print(f"{sys.path=}")

    mdl.compile()
    # Load to HIL
    parent_folder = pathlib.Path(tse_file_path).parent
    target_files_path = parent_folder.joinpath(str(pathlib.Path(tse_file_path).stem) + ' Target files')
    cpd_path = target_files_path.joinpath(str(pathlib.Path(tse_file_path).stem) + ".cpd")
    hil.load_model(file=cpd_path, offlineMode=False, vhil_device=use_vhil)


def get_element_currents(elem_name, elem_class):
    """"
    Returns a Dict with the mag and ang currents from each terminal of the component

    currents_dict = {
        "term1": {
            mag_"node": value,
            anf_"node": value,
            ...
        },
        "term2": {
            mag_"node": value,
            anf_"node": value,
            ...
        },
    }
    """
    currents_dict = {}

    dss.Circuit.SetActiveElement(f"{elem_class.upper()}.{elem_name}")
    current_meas = dss.CktElement.CurrentsMagAng()
    buses = dss.CktElement.BusNames()

    idx = 0
    for term_num, bus in enumerate(buses):
        term_dict = {}
        for node in bus.split(".")[1:]:
            term_dict.update({f"mag_{node}": current_meas[idx * 2]})
            term_dict.update({f"ang_{node}": current_meas[(idx * 2) + 1]})
            idx += 1
        currents_dict.update({f"term{term_num + 1}": term_dict})

    return currents_dict


def get_load_powers(load_name, elem_class="Load"):
    """"
    Returns a Dict with P and Q from the terminal of the Load Component

    currents_dict = {
        "term1": {
            P"node": value,
            Q"node": value,
            ...
        }
    }
    """
    powers_dict = {}

    dss.Circuit.SetActiveElement(f"{elem_class.upper()}.{load_name}")
    power_meas = dss.CktElement.Powers()
    buses = dss.CktElement.BusNames()

    idx = 0
    for term_num, bus in enumerate(buses):
        term_dict = {}
        for node in bus.split(".")[1:]:
            term_dict.update({f"P{node}": power_meas[idx * 2] * 1e3})
            term_dict.update({f"Q{node}": power_meas[(idx * 2) + 1] * 1e3})
            idx += 1
        powers_dict.update({f"term{term_num + 1}": term_dict})

    return powers_dict


def get_load_voltages(load_name, elem_class="Load"):
    """"
    Returns a Dict with the mag and ang voltages of the bus

    voltages_dict = {
        "phase": {
            mag_"node": value,
            anf_"node": value,
            ...
        },
    }
    """
    voltages_dict = {}

    dss.Circuit.SetActiveElement(f"{elem_class.upper()}.{load_name.lower()}")
    busname = dss.CktElement.BusNames()[0]
    load_phases = busname.split(".")[1:]

    dss.Circuit.SetActiveBus(busname)
    nodes = dss.Bus.Nodes()
    phase_meas = dss.Bus.VMagAngle()

    phase_dict = {}
    for idx, node in enumerate(nodes):
        if str(node) in load_phases:
            phase_dict.update({f"mag_{node}": phase_meas[2 * idx]})
            phase_dict.update({f"ang_{node}": phase_meas[(2 * idx) + 1]})

    voltages_dict.update({"phase": phase_dict})

    return voltages_dict


def get_bus_voltages(busname):
    """"
    Returns a Dict with the mag and ang voltages of the bus

    voltages_dict = {
        "phase": {
            mag_"node": value,
            anf_"node": value,
            ...
        },
    }
    """
    # TODO: Add per unit voltages
    # TODO: Add line voltages
    voltages_dict = {}

    dss.Circuit.SetActiveBus(busname)
    nodes = dss.Bus.Nodes()
    phase_meas = dss.Bus.VMagAngle()

    phase_dict = {}
    for idx, node in enumerate(nodes):
        phase_dict.update({f"mag_{node}": phase_meas[2 * idx]})
        phase_dict.update({f"ang_{node}": phase_meas[(2 * idx) + 1]})

    voltages_dict.update({"phase": phase_dict})

    return voltages_dict


def set_grid_voltage(grid_name, pu_val, elem_class="VSource"):

    dss.Circuit.SetActiveElement(f"{elem_class.upper()}.{grid_name}")
    dss.Vsources.PU(pu_val)
    dss.run_command("calcv")
    dss.run_command("Solve Mode=Snap")


def get_all_dss_elements(mdl, comp_type, parent_comp=None):

    component_list = []
    if parent_comp:  # Component inside a subsystem (recursive function)
        all_components = mdl.get_items(parent_comp)
    else:  # Top level call
        all_components = mdl.get_items()

    for comp in all_components:
        try:
            type_name = mdl.get_component_type_name(comp)
            if type_name and type_name in comp_type and mdl.is_enabled(comp):
                component_list.append(comp)
            elif not type_name:  # Component is a subsystem
                component_list.extend(get_all_dss_elements(mdl, comp_type, parent_comp=comp))
        except:
            # Some components (such as ports and connections) cannot be used with
            # get_component_type_name
            pass
    # Return the list of component handles
    return component_list


def get_item_by_fqn(mdl, fqn, parent=None):

    item_fqn_names = fqn.split(".")
    for item_name in item_fqn_names.copy():
        item_handle = mdl.get_item(item_name, parent=parent)
        item_fqn_names.remove(item_name)
        if item_fqn_names:
            item_handle = get_item_by_fqn(mdl, ".".join(item_fqn_names), parent=item_handle)
        return item_handle


def calculate_line_voltage(v1_mag, v1_phase, v2_mag, v2_phase):
    # Convert to cartesian
    v1_x, v1_y = pol2cart(v1_mag, v1_phase)
    v2_x, v2_y = pol2cart(v2_mag, v2_phase)

    # Subtract the coordinates
    v12_x = v1_x - v2_x
    v12_y = v1_y - v2_y

    # Convert back to polar
    return cart2pol(v12_x, v12_y)


def cart2pol(x, y):
    # From cartesian to polar
    rho = np.sqrt(x ** 2 + y ** 2)
    phi = np.arctan2(y, x)
    return (rho, phi)


def pol2cart(rho, phi):
    # From polar to cartesian
    x = rho * np.cos(phi)
    y = rho * np.sin(phi)
    return (x, y)


def clear_opendss():
    dss.run_command('ClearAll')


def update_package(path_to_new):
    with log_step("Updating Packages"):
        # Removes and install all Model packages
        for pkg in pkm.get_installed_packages():
            log_msg(f"Removing: {pkg.package_name}")
            pkm.uninstall_package(pkg.package_name)
        pkm.install_package(path_to_new)
        mdl.reload_libraries()