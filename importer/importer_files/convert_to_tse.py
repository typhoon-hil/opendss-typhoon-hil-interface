import opendssdirect as dss
from import_to_tse.classes import base
from import_to_tse.classes import auto_place, placer_update

from components import (
    component_mapping,
    schematic_prop_conversion,
    mask_prop_conversion,
    port_mapping,
)


def create_importer_components_props() -> dict:
    """
    Keys in the importer component properties are the full name of the OpenDSS objects.

    Returns:
        importer_components_props: dictionary with the properties for each converted component
    """

    importer_components_props = {}
    elements_to_remove = {}

    # Total number of buses
    num_buses = dss.Circuit.NumBuses()

    # Go through all Buses and add sets of nodes for each
    # side (Bus components may be two-sided in TSE)
    for bus_idx in range(num_buses):
        dss.Circuit.SetActiveBusi(bus_idx)

        objects_in_bus = dss.Bus.AllPCEatBus() + dss.Bus.AllPDEatBus()

        # Instantiate importer bus component
        bus_name = dss.Bus.Name()
        bus_mask_properties = mask_prop_conversion.convert_mask_properties(
            "Bus", obj_name=bus_name
        )
        bus_schematic_properties = schematic_prop_conversion.get_schematic_properties(
            "Bus",
            obj_name=bus_name,
            mask_properties=bus_mask_properties,
        )
        bus_schematic_properties["type_name"] = "OpenDSS/Bus"

        bus_prop_dict = {
            "mask_properties": bus_mask_properties,
            "schematic_properties": bus_schematic_properties,
        }

        importer_components_props[f"Bus.{bus_name}"] = bus_prop_dict

        # Instantiate other objects connected to the bus
        for obj_full_name in objects_in_bus:
            obj_class, obj_name = obj_full_name.split(".")
            supported_comp = component_mapping.get_component_conversion_dict(
                opendss_class=obj_class,
                obj_name=obj_name,
            )
            if supported_comp:
                mask_properties = mask_prop_conversion.convert_mask_properties(
                    obj_class,
                    obj_name=obj_name,
                )
                if mask_properties:
                    schematic_properties = (
                        schematic_prop_conversion.get_schematic_properties(
                            obj_class,
                            obj_name=obj_name,
                            mask_properties=mask_properties,
                        )
                    )
                    if "type_name" in mask_properties:
                        schematic_properties['type_name'] = mask_properties.pop('type_name')
                    else:
                        schematic_properties["type_name"] = supported_comp.get("type_name")
                    prop_dict = {
                        "mask_properties": mask_properties,
                        "schematic_properties": schematic_properties,
                    }
                    importer_components_props[obj_full_name] = prop_dict
    return importer_components_props


def create_component_instances(schematic, importer_components_props):
    importer_components_instances = {}

    for object_full_name, prop_dict in importer_components_props.items():
        schematic_properties = prop_dict["schematic_properties"]
        mask_properties = prop_dict["mask_properties"]
        new_importer_comp = base.Component(
            schematic, schematic_properties, mask_properties, parent=None
        )

        importer_components_instances[object_full_name] = new_importer_comp

    return importer_components_instances


def create_bus_nodes(importer_schematic):
    """
    Each Bus in OpenDSS may define one or two nodes.

    Args:
        importer_schematic: the created importer schematic

    Returns:
        node_dict: A dictionary with the Lines and their corresponding Nodes
    """
    node_dict = {}

    # Total number of buses
    num_buses = dss.Circuit.NumBuses()

    # Go through all Buses and add sets of nodes for each
    # side (Bus components may be two-sided in TSE)
    for bus_idx in range(num_buses):
        dss.Circuit.SetActiveBusi(bus_idx)
        # num_nodes = dss.Bus.NumNodes()
        num_nodes = 3

        node_dict[f"Bus.{dss.Bus.Name()}"] = {
            1: {"nodes": [], "connected": False},
            2: {"nodes": [], "connected": False},
        }
        for side in [1, 2]:
            for _ in range(num_nodes):
                node = base.Node(importer_schematic)
                node_dict[f"Bus.{dss.Bus.Name()}"][side]["nodes"].append(node)

    return node_dict


def set_component_nodes(
    importer_schematic,
    importer_components_props,
    importer_components_instances,
    node_dict,
):
    # components_nodes = {}
    for obj_full_name in importer_components_instances:
        comp_nodes = {}
        obj_class, obj_name = obj_full_name.split(".")
        if obj_class == "Bus":
            # Skip buses
            continue
        dss.Circuit.SetActiveElement(f"{obj_full_name}")

        bus_idx = 1
        for bus_string in dss.CktElement.BusNames():
            bus_name = bus_string.split(".")[0]
            bus_node_numbers = bus_string.split(".")[1:]
            if not bus_node_numbers:
                node_order = [n for n in range(1, dss.CktElement.NumPhases() + 1)]
            else:
                node_order = [int(n) for n in bus_string.split(".")[1:]]

            # for side in bus_side_order:
            for side in [1, 2]:
                selected_side = side
                side_is_connected = node_dict.get(f"Bus.{bus_name}")[side]["connected"]
                if not side_is_connected:
                    node_dict.get(f"Bus.{bus_name}")[side]["connected"] = True
                    break

            nodes = []
            bus_nodes = node_dict.get(f"Bus.{bus_name}")[selected_side]["nodes"]
            for n in node_order:
                if 0 < n < 4:
                    nodes.append(bus_nodes[n - 1])

            comp_nodes.update(
                {
                    bus_idx: {
                        "bus_name": f"Bus.{bus_name}",
                        "bus_side": selected_side,
                        "nodes": nodes,
                    }
                }
            )
            bus_idx += 1

        node_dict[obj_full_name] = comp_nodes


def create_terminals(
    importer_schematic,
    node_dict,
    importer_components_instances,
    importer_components_props,
):
    """
    Create a terminal for node of the component.
    """

    for obj_full_name in importer_components_instances:
        obj_class, obj_name = obj_full_name.split(".")
        port_names_dict = port_mapping.get_port_mapping(
            obj_class,
            obj_name,
            component_properties=importer_components_props[obj_full_name],
        )

        # Bus terminals
        if obj_class == "Bus":
            for side_number, port_names in port_names_dict.items():
                for idx, port_name in enumerate(port_names):
                    t = base.Terminal(
                        schematic=importer_schematic,
                        node=node_dict[obj_full_name][side_number]["nodes"][idx],
                        parent=importer_components_instances[obj_full_name],
                        origin_name=f"{idx}",
                        destination_name=port_name,
                        position=("left" if side_number == 1 else "right", f"{idx}"),
                    )
        # Other component terminals
        else:
            comp_properties = importer_components_props[obj_full_name]
            terminal_number_side = (
                schematic_prop_conversion.get_terminal_number_side_dict(
                    obj_class,
                    mask_properties=comp_properties["mask_properties"],
                )
            )
            for side_number, port_names in port_names_dict.items():
                nodes = node_dict[obj_full_name][side_number]["nodes"]
                for node_idx, node in enumerate(nodes):
                    t = base.Terminal(
                        schematic=importer_schematic,
                        node=node,
                        parent=importer_components_instances[obj_full_name],
                        origin_name=f"{node_idx}",
                        destination_name=port_names[node_idx],
                        position=(terminal_number_side[side_number], f"{node_idx}"),
                    )


def place_components(importer_schematic, mode):
    importer_components = importer_schematic.components

    # Create neighbors dict
    neighbors_dict = {}
    for tse_component in importer_components:
        neighbors_dict[tse_component] = tse_component.get_connected_components()

    gains = charge_gain, spring_gain, friction_gain, time = [4500000, 1.7, 5, 0.36]
    canvas_scale = 1

    component_data = {}
    for tse_component in importer_components:
        component_data[tse_component] = {
            "neighbors": neighbors_dict.get(tse_component, []),
            "initialize_pos": True,
            "initialize_sides": True,
            "initialize_velocity": True,
            "locked_position": False,
            "locked_sides": False,
        }

    placer = auto_place.ComponentPlacer(
        component_data,
        canvas_scale=canvas_scale,
        iterations=250,
        gains=gains,
        grid_size=192,
        seed_component_type="OpenDSS/Vsource",
    )
    placer.gui_mode = True if mode == "gui" else False
    placer.filter_parallel_components(fork_component_type="OpenDSS/Bus")
    placer.find_cycles_and_paths()

    # Grow tree of components
    tree = placer.find_complete_tree()
    placer.grow_tree(tree)

    # Get final component positions
    final_positions = placer.final_positions
    simdss_pos = min([tuple(pos) for pos in final_positions.values()])
    simdss_pos = (simdss_pos[0] - 100, -simdss_pos[1] - 100)

    # Set importer component instances positions
    for component, position in final_positions.items():
        component.position = (position[0], -position[1])

    return simdss_pos


def convert_to_tse(dss_file_path, output_path, auto_place_mode="charge-spring"):
    print("Compiling OpenDSS model....")
    dss.Basic.AllowEditor(0)
    comm_result = dss.run_command(f'Compile "{dss_file_path}"')
    if comm_result:
        print(comm_result)
    else:
        print("Successfully compiled model.")

    # Create schematic
    print("Creating new SchematicAPI model...")
    schematic_properties = {}
    new_schematic = base.Schematic(schematic_properties)

    # Create components and set their properties (may affect the number of terminals)
    importer_components_props = create_importer_components_props()

    print("Creating importer component instances...")
    importer_components_instances = create_component_instances(
        new_schematic, importer_components_props
    )

    # Create nodes
    print("Creating nodes...")
    node_dict = create_bus_nodes(new_schematic)
    set_component_nodes(
        new_schematic,
        importer_components_props,
        importer_components_instances,
        node_dict,
    )

    # Create terminals
    print("Creating terminals...")
    create_terminals(
        new_schematic,
        node_dict,
        importer_components_instances,
        importer_components_props,
    )

    if auto_place_mode == "charge-spring":
        print("Placing components without position information...")
        simdss_pos = place_components(new_schematic, auto_place_mode)
    elif auto_place_mode == "center-expanding":
        # Using the new placement algorithm
        placer_update.place_components(new_schematic)
        new_schematic.save_model(file_path=output_path)
        new_schematic.close_model()
        print("Model successfully imported.")
        return

    print("Adding components to the TSE schematic...")

    if simdss_pos:
        # Add a SimDSS component to the Schematic
        simdss_component = base.Component(
            new_schematic,
            schematic_properties={
                "name": "SimDSS",
                "type_name": "OpenDSS/SimDSS",
                "position": simdss_pos,
            },
            mask_properties={},
            parent=None,
        )
        simdss_component.add_to_schematic()

    for idx, (comp_name, component) in enumerate(importer_components_instances.items()):
        print(f"{idx + 1}/{len(importer_components_instances)} Adding {comp_name}")
        component.add_to_schematic()

    # Connect terminals
    print("Connecting components...")
    new_schematic.create_connections()

    # Save and close the model
    new_schematic.save_model(file_path=output_path)
    new_schematic.close_model()

    print("Model successfully imported.")
