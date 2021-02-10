import json
import os
import time
import pathlib

import schematic_converter.elements as elements
from schematic_converter.libfqn_dict import determine_elem
from schematic_converter.libfqn_dict import collapse_nodes


# Converts jsonfile to an OpenDSS compatible syntax
def convert(jsonfile, sim_parameters):
    # List of nodes and to what buses they are connected
    buses_dict = {}

    bus_list = []
    non_bus_list = []
    switch_command_lines = []

    t0 = time.time()

    with open(jsonfile) as f:
        data = json.load(f)

    # Model name
    circuit_name = data["name"]
    # List of subsystems present in the JSON
    subsys_list = data["dev_partitions"][0]["parent_components"]
    # List of elements present in the JSON
    elem_list = data["dev_partitions"][0]["components"]
    # List of nodes present in the JSON
    node_data = data["dev_partitions"][0]["nodes"]
    # Initialization of the output text variables
    lines = ""

    def create_fqn(elem_json):
        # Create a proper preceding string if the component is located inside subsystem(s)
        elem_name = elem_json["name"]
        subsys_id = elem_json["parent_comp_id"]
        prefix_subs = ""
        while subsys_id:
            for subsystem in subsys_list:
                if subsystem["id"] == subsys_id:
                    prefix_subs = subsystem["name"] + "-" + prefix_subs
                    subsys_id = subsystem["parent_comp_id"]
        elem_name = prefix_subs + elem_name
        return elem_name

    # Verify duplicate names (OpenDSS is not case sensitive)
    all_fqns = [create_fqn(elem) for elem in elem_list]
    all_fqns_lower = [n.lower() for n in all_fqns]
    duplicates = []
    for idx, name in enumerate(all_fqns_lower):
        if all_fqns_lower.count(name) > 1:
            duplicates.append(str(elem_list[idx].get("lib_fqn"))+":"+str(all_fqns[idx]))

    if len(duplicates)>0:
        raise Exception(f"OpenDSS is case insensitive. Please change the name of the following conflicting elements: {duplicates}")

    def get_node(terminal):
        """ Returns the handle of the node to which the terminal is connected """
        for n in node_data:
            if terminal["id"] in n["terminals"]: # If terminal is contained in this node's terminals list
                return n

    def get_terminal(elem, terminal_name):
        """ Returns the terminal handle """
        for term in elem["terminals"]:
            if terminal_name == term["name"]:  # If terminal is contained in this node's terminals list
                return term

    def get_elem_data(elem_json):
        """ Returns the pertinent data of an element in the JSON file. """
        elem_name = create_fqn(elem_json)
        # Cannot have spaces in the name
        elem_name = elem_name.replace(" ", "_")
        # Determine the element type by searching for the libfqn entry
        # using libfqn_dict.py
        elem_type = determine_elem(elem_json["lib_fqn"])
        # Initialization of the data to be returned
        elem_data = {}

        def elem_get_nodes():
            # elem_json is a name in the scope of the parent function
            nonlocal elem_json
            nodes_dict = {}
            for term in elem_json["terminals"]:
                # Check every circuit node for the presence of the terminal id.
                for n in node_data:
                    # If terminal is contained in this node's terminals list
                    if term["id"] in n["terminals"]:
                        # Entry example: "p_node":"123456789"
                        nodes_dict.update({term["name"]: str(n["id"])})
            return nodes_dict

        # In the case of every element contained in the new library
        if elem_json["masks"] and not elem_type in ["BUS"]:
            prop_list = elem_json["masks"][0]["properties"]
            # Return the dict based on the element properties
            init_dict = {prop["name"]: str(prop["value"]) for prop in prop_list}
            # Relevant data for instantiation
            elem_data = {
                "name": elem_name, "nodes": elem_get_nodes(),
                "init_data": init_dict
            }
        elif elem_json["masks"] and elem_type == "BUS":
            elem_data = {
                "name": elem_name, "nodes": elem_get_nodes()
            }
            # Check for incorrectly placed Bus objects
            for bus in buses_dict.keys():
                for existing_node in buses_dict[bus].values():
                    for node in elem_data["nodes"].values():
                        if node == existing_node:
                            raise Exception(f"{bus} is connected directly to another bus: {elem_name}")
            # If no problems detected, update the Buses dictionary
            buses_dict.update({elem_name: elem_data["nodes"]})

        return (elem_type, elem_data)

    # Collapse the nodes of ignored components
    for elem in elem_list:
        c_nodes_dict = collapse_nodes(elem["lib_fqn"])
        if c_nodes_dict:
            # Collapse terminals in other_terms_list to terminal term_name
            for term_name, other_terms_list in c_nodes_dict.items():
                for terminal in elem["terminals"]:
                    if terminal["name"] == term_name:  # If this terminal should be collapsed
                        # Get the list of terminals connected to the same node as term_name
                        n_terms = get_node(terminal)["terminals"]
                        # For each other terminal of the component that should be collapsed into term_name,
                        # get the node and its respective list of terminals and add to the terminal list of
                        # term_name's node
                        for other_term in other_terms_list:
                            other_term_handle = get_terminal(elem, other_term)
                            other_node = get_node(other_term_handle)
                            for other_n_terminal in other_node["terminals"]:
                                n_terms.append(other_n_terminal)
                            # After merging, remove the original node
                            node_data.remove(other_node)

    for elem in elem_list:
        # Get the element type and the relevant data
        elem_type = determine_elem(elem["lib_fqn"])
        # Find all bus elements first to determine the connection names
        # for the rest of the components
        if elem_type != None:
            if elem_type == "BUS":
                bus_list.append(elem)
            else:
                non_bus_list.append(elem)

    for elem in bus_list:
        # Get the element type and the relevant data
        elem_type, elem_data = get_elem_data(elem)
        # Use the type and data to instantiate the correct class
        this_element = elements.Element.pick_correct_subclass(elem_type, elem_data)

    for elem in non_bus_list:
        # Get the element type and the relevant data
        elem_type, elem_data = get_elem_data(elem)
        # Pass buses_dict to determine the connections
        elem_data.update({"buses_dict": buses_dict})
        # Use the type and data to instantiate the correct class
        this_element = elements.Element.pick_correct_subclass(elem_type, elem_data)

        lines += this_element.dss_line()

    extra_parameters = {
        "basefrequency": sim_parameters.get("basefrequency"),
        "algorithm": sim_parameters.get("algorithm"),
        "maxiter": sim_parameters.get("maxiter"),
        "miniterations": sim_parameters.get("miniterations"),
        "voltagebases": sim_parameters.get("voltagebases")
    }

    parameter_lines = ""
    for par, val in extra_parameters.items():
        parameter_lines += f'set {par} = {val} \n'

    appended_commands_before_file = 'appended_commands_before.dss'
    appended_commands_after_file = 'appended_commands_after.dss'
    if pathlib.Path(jsonfile).parent.joinpath(appended_commands_before_file).is_file():
        append_commands_before = f"redirect {appended_commands_before_file}\n\n"
    else:
        append_commands_before = "\n"
    if pathlib.Path(jsonfile).parent.joinpath(appended_commands_after_file).is_file():
        append_commands_after = f"redirect {appended_commands_after_file}\n\n"
    else:
        append_commands_after = "\n"


    # Final syntax output
    output = (
        f'!Automatically generated by tse2opendss\n\n'
        f'Clear\n\n'
        
        f'new "Circuit.{circuit_name}"\n'
        f'edit vsource.source basekv=0.0001 bus1 = "not used" pu=0\n'
        f'{lines}\n\n'
        f'{parameter_lines}\n'
        #f'{append_commands_before}'
        f'Calcv\n\n'
        f'Solve Mode={sim_parameters.get("sim_mode") if sim_parameters["loadmodel"]=="Power flow" else "direct"}\n\n'
        #f'{"show faults" if sim_parameters.get("sim_mode")=="faultstudy" else ""}\n'
        #f'{append_commands_after}'
        f'!END\n'
    )

    # Write a .dss file with the same name as the JSON, and in the same folder
    with open(os.path.splitext(jsonfile)[0]+".dss", "w+") as f:
        f.write(output)

    # Program speed test
    print(f"Total conversion time: {time.time() - t0} seconds")

    return True

if __name__ == "__main__":
    import opendssdirect as dss
    import dss_conv.gui.report_functions as rf

    jsonfile = r"D:\Dropbox\Typhoon HIL\Repository\opendss_integration\examples\simple_dist_demo Target files\simple_dist_demo.json"
    sim_parameters = {"sim_mode": "faultstudy",
                  "basefrequency": "60",
                  "maxiter": "15",
                  "miniterations": "2",
                  "loadmodel": "Power flow",
                  "voltagebases": "[0.480, 12.47]"}
    convert(jsonfile, sim_parameters)
    dssfile = os.path.splitext(jsonfile)[0]+".dss"
    dss.utils.run_command(f'Compile "{dssfile}"')

    rf.generate_faultstudy_report("report")[1]