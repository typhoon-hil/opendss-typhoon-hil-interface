from ..tse2tpt_base_converter import tse_functions as tse_fns
import json

# Use default mapping
from .default_mapping import map
from .default_mapping import constants


def return_bus_connections(tse_component, num_buses, num_phases, floating_neutral):
    """ Returns a list of strings that define how the element is connected to buses.
    Example:
        * 2-phase element
        * connected to 3 AB-type buses and 1 AC-type
        * wires 1 and 2 swapped on busAB3
    [busAB1.1.2, busAB2.1.2, busAB3.2.1, busAC4.1.3]"""

    print(f"{tse_component.name=}")
    print(f"{num_phases=}")


    bus_connections = []
    # General objects are not connected to buses
    if num_phases == 0 or num_buses == 0:
        return None

    # With a floating neutral, connect to the same bus, but on an unused node
    if floating_neutral:
        num_buses = num_buses - 1

    # List of characters according to the number of Phases: 1->A, 2->B, 3->C, 4->D, etc.
    # The component terminals in TSE must follow the same naming scheme
    phase_letters = [chr(65 + n) for n in range(num_phases)] + ["N"]

    # Terminal groups are numbered from 1 to n_buses
    n_groups = range(1, num_buses + 1)

    # Create a dict with all the terminal groups and names
    terminal_groups_dict = {}
    for n in n_groups:
        terminal_list = []
        terminal_groups_dict.update({n: terminal_list})
        for p in phase_letters:
            terminal_list.append(f"{p}{n}")

    # Find the Bus components that are connected to the current component
    connected_buses = tse_fns.connected_components(tse_component, comp_type=constants.DSS_BUS)

    # Raise error if more than the expect number of buses are connected
    if len(connected_buses) > num_buses:
        bus_names = ", ".join([b.name for b in connected_buses])
        raise (Exception(f"Component {tse_component.name} is connected to more than {num_buses} buses ({bus_names})."))
    elif len(connected_buses) == 0:
        raise Exception(f"Component {tse_component.name} is not connected to any bus.")

    # Go through each group (must be ordered) and find which bus is connected to it.
    for group, term_list in terminal_groups_dict.items():
        print(f"{term_list=}")
        for bus in connected_buses:
            # Get the dictionary of connections between tse_component and bus
            connected_terminals_dict = tse_fns.connected_terminals(tse_component, bus, term_list)
            print(f"{connected_terminals_dict=}")
            # Iterate over the terminals of the component and find the bus terminal it is connected to
            # This will determine the order of the connections
            if connected_terminals_dict:
                order = []
                for terminal in term_list:
                    term_connected = connected_terminals_dict.get(terminal)
                    if term_connected:
                        bus_terminals = [t[0] for t in term_connected]  # Only the letter
                        order.extend(bus_terminals[0])

                terminal_order = []
                for phase_name in order:
                    if phase_name in ['A', 'B', 'C']:
                        terminal_order.append(str(ord(phase_name[0]) - 64))
                    elif phase_name == "N":
                        terminal_order.append(str(num_phases + 1))
                terminal_order = '.'.join(terminal_order)
                bus_connections.append(f'"{bus.name.upper()}.{terminal_order}"')

    if floating_neutral:
        # Connect to unused bus node (working only for single bus components)
        p = num_phases + 1
        for conn_bus in connected_buses:
            bus_connections.append(f"{conn_bus.name}.{p}.{p}.{p}")

    print(f"{bus_connections=}")
    return bus_connections


def verify_duplicate_names(tse_model):
    """ OpenDSS is not case sensitive while TSE is. Avoid duplicates. """

    converted_components = []
    all_components = tse_model.components
    for component in all_components:
        if map.ignore_component(component.comp_type):
            converted_components.append(component)
        elif map.map_component(component.comp_type):
            converted_components.append(component)

    all_fqns_lower = [n.fqn.lower() for n in converted_components]
    duplicates = []
    for idx, name in enumerate(all_fqns_lower):
        if all_fqns_lower.count(name) > 1:
            duplicates.append(converted_components[idx].name)

    if len(duplicates) > 0:
        raise Exception(f"OpenDSS is case insensitive. "
                        f"Please change the name of the following conflicting components: {duplicates}")


def verify_directly_connected_buses(tse_model):
    """ OpenDSS buses are nodes. Component terminals can only connect to one node. """

    all_components = tse_model.components
    for component in all_components:
        if component.comp_type == constants.DSS_BUS:
            detected_connected_buses = tse_fns.connected_components(component, comp_type=constants.DSS_BUS)
            if detected_connected_buses:
                conn_buses_str = ", ".join([f"{bus.name}" for bus in detected_connected_buses])
                if len(detected_connected_buses) == 1:
                    exception_str = f"{component.name} is connected directly to other bus: {conn_buses_str}"
                elif len(detected_connected_buses) > 1:
                    exception_str = f"{component.name} is connected directly to other buses: {conn_buses_str}"
                raise Exception(exception_str)


def merge_terminals(tse_component):
    """ Merge the terminals of ignored components """

    merge_dict = map.ignore_component(tse_component.comp_type)

    # Get the merge information from merge_dict
    for merge_to_terminal, other_terms_list in merge_dict.items():
        # Find the terminal (dict key) other terminals are being merged to
        for t_name, t_instance in tse_component.terminals.items():
            if t_name == merge_to_terminal:
                # Get the node of the terminal
                merge_to_node = t_instance.node
                # Loop again through all the terminals to find the other terminal instances
                for other_term_name in other_terms_list:
                    for other_t_name, other_t_instance in tse_component.terminals.items():
                        if other_term_name == other_t_name:
                            # Get all terminals from all components connected to this terminal node
                            all_terminals = other_t_instance.node.terminals
                            for t in all_terminals:
                                # Connect this terminal to the merge_to_node
                                t.node = merge_to_node
                                merge_to_node.add_terminal(t)
                            # Remove the merged terminals from the node
                            merge_to_node.remove_terminal(t_instance)
                            merge_to_node.remove_terminal(other_t_instance)


def create_general_objects_from_saved_json(tse_model, output_circuit):
    """ Instantiates general objects from the JSON file created by the TSE GUI """

    from .default_mapping.class_picker import create_comp_instance

    dss_data_path = output_circuit.simulation_parameters.get("dss_data_path")
    obj_json_file = dss_data_path.joinpath("general_objects.json")
    added_objs = []
    if obj_json_file.is_file():
        with open(obj_json_file, 'r') as f:
            # Get the general objects dictionary
            general_objects = json.loads(f.read())
            for converted_comp_type in list(general_objects.keys()):
                # For each converted type (e.g. linecodes, loadshapes)
                for obj_name, saved_properties_dict in general_objects.get(converted_comp_type).items():
                    add_obj = False
                    # Only add the object if it is being used by a component in the TSE model
                    # Get the properties of all elements and check converted_comp_type[:-1] + "_name" (eg linecode_name)
                    # and selected_object properties for the saved object name
                    for comp in tse_model.components:
                        properties_dict = {str(k): str(v.value) for k, v in comp.properties.items()}
                        if properties_dict.get(converted_comp_type[:-1] + "_name", "").upper() == obj_name.upper():
                            add_obj = True if obj_name not in added_objs else False
                            break
                        elif properties_dict.get("selected_object", "").upper() == obj_name.upper():
                            add_obj = True if obj_name not in added_objs else False
                            break

                    if add_obj:
                        # Remove blank property entries
                        for k in list(saved_properties_dict.keys()):
                            if not saved_properties_dict[k]:
                                saved_properties_dict.pop(k)
                        if saved_properties_dict.get("mode"):
                            # Remove mode
                            saved_properties_dict.pop("mode")

                        if converted_comp_type == "loadshapes":

                            interval_type = saved_properties_dict.pop("interval_unit", 'h')
                            if interval_type == 'm':
                                saved_properties_dict['minterval'] = saved_properties_dict.pop("interval", '1')
                            elif interval_type == 's':
                                saved_properties_dict['sinterval'] = saved_properties_dict.pop("interval", '1')

                            if saved_properties_dict.pop("csv_file", None) == "True":
                                loadshape_from_file_path = saved_properties_dict.pop("csv_path", None)
                                headers = "yes" if saved_properties_dict.pop("headers", "False") == "True" else "no"
                                column = saved_properties_dict.pop("column", "1")
                                saved_properties_dict["mult"] =\
                                    f"""(file='{loadshape_from_file_path}', header={headers}, col={column})"""
                            else:
                                saved_properties_dict.pop("csv_path", None)
                                saved_properties_dict.pop("headers", None)
                                saved_properties_dict.pop("column", None)

                        # Create a new converted component instance
                        comp_data = {"name": obj_name,
                                     "circuit": output_circuit,
                                     "tse_component": None,
                                     "tse_properties": saved_properties_dict}

                        new = create_comp_instance(converted_comp_type[:-1].upper(), comp_data)
                        added_objs.append(obj_name)
                        output_circuit.components.append(new)


def create_monitors(converted_component, tse_properties, tse_component):
    """ Create monitor components if the checkbox is selected on TSE. """

    from .default_mapping.component_classes.base import Monitor

    if tse_properties.get("enable_monitoring") == "True" and converted_component.circuit.simulation_parameters["sim_mode"] == "Time Series":

        # Voltage monitors
        for bus_n in range(1, converted_component.num_buses + 1):
            monitor_properties = {"element": converted_component.identifier(),
                                  "mode": "0",
                                  "terminal": f"{bus_n}"
                                  }

            new_monitor = Monitor(name=f'{converted_component.name}_VOLTAGE_{bus_n}',
                                  circuit=converted_component.circuit,
                                  monitor_properties=monitor_properties)

            converted_component.created_instances_list.append(new_monitor)

        # Power monitors
        for bus_n in range(1, converted_component.num_buses + 1):
            monitor_properties = {"element": converted_component.identifier(),
                                  "mode": "1",
                                  "ppolar": "no",
                                  "terminal": f"{bus_n}"
                                  }

            new_monitor = Monitor(name=f'{converted_component.name}_POWER_{bus_n}',
                                  circuit=converted_component.circuit,
                                  monitor_properties=monitor_properties)

            converted_component.created_instances_list.append(new_monitor)

