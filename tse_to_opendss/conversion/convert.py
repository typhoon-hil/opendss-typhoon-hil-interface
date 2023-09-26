from . import output_functions
import pathlib
import os

from ..tse2tpt_base_converter import tse_functions as tse_fns
import json

# Use default mapping
from .default_mapping import constants
from .default_mapping import class_picker
from .default_mapping import map
from .default_mapping.component_classes.base import Circuit
from .default_mapping.component_classes import *

def convert(tse_model, input_json_path, simulation_parameters):
    """
    Main conversion function.

    Args:
        tse_model(ModelPartition): ModelPartition object created by the tse_model_load.load_json function.
        input_json_path(str): Path to the original JSON file.
        simulation_parameters(str): Simulation parameters.

    Returns:
        converted_dict(dict): Dictionary with the new model data.
    """

    # Validate the model
    output_functions.verify_duplicate_names(tse_model)
    output_functions.verify_directly_connected_buses(tse_model)

    # Paths
    dss_folder_path = pathlib.Path(input_json_path).parent.joinpath('dss')
    dss_data_path = dss_folder_path.joinpath('data')
    simulation_parameters.update(
        {
            "dss_folder_path": dss_folder_path,
            "dss_data_path": dss_data_path
        }
    )

    # Create new output circuit
    circuit_name = tse_model.parent.name
    output_circuit = Circuit(circuit_name, simulation_parameters)

    components = tse_model.components

    # Add Container components
    for c in tse_model.parent_components:
        if "dss_container_comp_identifier" in c.properties:
            c.comp_type = constants.DSS_CONTAINER
            tse_model.add_component(c)

    # Merge terminals of ignored components
    remove_list = []

    for component in components:
        if component.comp_type == "OpenDSS/Monitor":
            connected_to_mon = tse_fns.connected_components(component, comp_type="all")
            for comp_mon in connected_to_mon:
                if not comp_mon.comp_type == constants.DSS_BUS:
                    if "enable_monitoring" in comp_mon.properties:
                        comp_mon.properties.get("enable_monitoring").value = True

    for component in components:
        if map.ignore_component(component.comp_type):
            output_functions.merge_terminals(component)
            remove_list.append(component)
    for component in remove_list:
        tse_model.remove_component_by_fqn(component.fqn)

    # Instantiate general objects from the JSON file created by the TSE GUI
    output_functions.create_general_objects_from_saved_json(tse_model, output_circuit)

    # Create the output circuit model
    for component in components:
        # Buses are not components in OpenDSS, but nodes
        if not component.comp_type == constants.DSS_BUS:

            comp_data = {}

            # Define name (if the component is inside a subsystem, use a modified FQN)
            name = component.name
            if component.parent_comp:
                name = component.fqn.replace(".", "-")
                if component.parent_comp.comp_type == constants.DSS_CONTAINER:
                    continue  # Ignore components below Container components

            # Create properties dictionary
            properties_dict = {str(k): str(v.value) for k, v in component.properties.items()}

            # Create the component data dictionary
            comp_data.update({"name": name,
                              "circuit": output_circuit,
                              "tse_component": component,
                              "tse_properties": properties_dict}
                             )

            # Create instances of the converted components (may be more than one per TSE component)
            mapped_types = map.map_component(component.comp_type)
            if mapped_types:
                for converted_comp_type in mapped_types:
                    converted_comp_handle = class_picker.create_comp_instance(converted_comp_type, comp_data)
                    converted_comp_list = converted_comp_handle.created_component_instances()
                    for comp in converted_comp_list:
                        output_circuit.components.append(comp)

    return output_circuit


def generate_output_files(output_circuit):
    """
        Creates all the output files necessary for the simulation with the 3rd party tool.

        Args:
            output_circuit(Circuit): New circuit model.

        Returns:
            Debug information.
        """

    circuit_name = output_circuit.name
    components = output_circuit.components

    # Master dss file path. Inside the target_files folder.
    dss_folder_path = output_circuit.simulation_parameters.get("dss_folder_path")
    if not dss_folder_path.is_dir():
        os.makedirs(dss_folder_path)
    # Data folder inside the dss folder.
    dss_data_path = dss_folder_path.joinpath('data')
    if not dss_data_path.is_dir():
        os.makedirs(dss_data_path)

    # Solve mode
    number_sims = output_circuit.simulation_parameters.pop("number", None)
    sim_mode = output_circuit.simulation_parameters.pop("sim_mode")
    if sim_mode == "Time Series":
        solve_mode = "daily"
    elif output_circuit.simulation_parameters["loadmodel"] == "Power flow":
        solve_mode = sim_mode
    else:
        solve_mode = "direct"

    # Set of component types after conversion
    converted_component_types = set(comp.type for comp in components if comp.type)

    # Add general objects (may be created by the TSE GUI)
    if dss_data_path.joinpath("linecodes.dss").is_file():
        converted_component_types.add("LINECODE")
    if dss_data_path.joinpath("loadshapes.dss").is_file():
        converted_component_types.add("LOADSHAPE")
    if dss_data_path.joinpath("xycurves.dss").is_file():
        converted_component_types.add("XYCURVE")
    if dss_data_path.joinpath("tshapes.dss").is_file():
        converted_component_types.add("TSHAPE")

    # Write the output lines
    for converted_comp_type in converted_component_types:
        first_of_this_type = True
        for comp in components:
            if comp.type == converted_comp_type:
                # Rewrite the file if the element is the first of the type, otherwise append new lines
                if first_of_this_type:
                    with open(f"{dss_data_path.joinpath(comp.type.lower() + 's.dss')}", 'w') as f:
                        f.write(f"! Automatically generated by the Typhoon HIL TSE to OpenDSS converter.\n\n")
                        first_of_this_type = False
                with open(f"{dss_data_path.joinpath(comp.type.lower() + 's.dss')}", 'a') as f:
                    f.write(comp.output_line())

    # Create the lines for the simulation parameters
    simulation_parameter_lines = ""
    for par, val in output_circuit.simulation_parameters.items():
        if type(val) == str:
            simulation_parameter_lines += f'set {par} = {val.replace(" ", "")} \n'
    # Redirect lines for each component type
    converted_component_types = [comp.lower() for comp in converted_component_types]
    # Some objects need to be in the correct order
    converted_component_types.sort(key=lambda x: x in ['xycurve', 'tshape', 'linecode', 'loadshape'], reverse=True)
    if "regcontrol" in converted_component_types:
        converted_component_types.append(converted_component_types.pop(converted_component_types.index('regcontrol')))
    if "monitor" in converted_component_types:
        converted_component_types.append(converted_component_types.pop(converted_component_types.index('monitor')))
    redirect_paths = "\n".join([f'redirect {t.lower()}s.dss' for t in converted_component_types])

    # Appended commands from TSE component
    appended_commands_before_file = 'appended_commands_before.dss'
    appended_commands_after_file = 'appended_commands_after.dss'
    if dss_data_path.joinpath(appended_commands_before_file).is_file():
        append_commands_before = f"redirect {appended_commands_before_file}\n\n"
    else:
        append_commands_before = ""
    if dss_data_path.joinpath(appended_commands_after_file).is_file():
        append_commands_after = f"redirect {appended_commands_after_file}\n\n"
    else:
        append_commands_after = ""

    # Main dss file
    main_dss_file_text = (
        f'// Automatically generated by the Typhoon HIL TSE to OpenDSS converter\n\n'

        f'Clear\n\n'
        f'// Circuit name is the same as the converted .tse file\n'
        f'new "Circuit.{circuit_name}"\n\n'
        f'// Default source is not used\n'
        f'Vsource.Source.Enabled=No\n\n'
        
        f'{"// Simulation parameters" + chr(10) if simulation_parameter_lines else ""}'
        f'{simulation_parameter_lines}\n'

        f'// Load all components from the files inside the "data" folder\n'
        f'set Datapath=data\n\n'
        f'{redirect_paths}\n\n'

        f'{"// User-appended commands from TSE before the solution" + chr(10) if append_commands_before else ""}'
        f'{append_commands_before}'

        f'// Calculate the voltage bases\n'
        f'Calcv\n\n'

        f'// Solve the circuit model\n'
        f'Solve mode={solve_mode}{" number=" + str(number_sims) if sim_mode=="Time Series" else ""}\n\n'

        f'{"// User-appended commands from TSE after the solution" + chr(10) if append_commands_after else ""}'
        f'{append_commands_after}'

        f'!END\n'
    )

    # Write master file
    with open(f"{dss_folder_path.joinpath(f'{circuit_name}_master.dss')}", 'w') as f:
        f.write(main_dss_file_text)

    return [True, "OpenDSS conversion successful."]
