old_state = {}
import numpy as np


def pos_offset(pos):
    """
    Offset position from center of the schematic
    """
    x0, y0 = 8192, 8192

    pos_x, pos_y = pos

    return x0 + pos_x, y0 + pos_y


def topology_dynamics(mdl, mask_handle):
    comp_handle = mdl.get_parent(mask_handle)

    #
    # Get new property values to be applied (display values)
    #
    new_prop_values = {}
    for prop in mdl.get_property_values(comp_handle):
        p = mdl.prop(mask_handle, prop)
        new_prop_values[prop] = mdl.get_property_disp_value(p)
    #
    # If the property values are the same as on the previous run, stop
    #
    global old_state
    if new_prop_values == old_state.get(comp_handle):
        return

    # conf_prop = mdl.prop(comp_handle, "conf")
    # type_prop = mdl.prop(comp_handle, "type_prop")

    #
    # Phases checkbox properties
    #
    phase_a = new_prop_values.get("phase_a") in ("True", True)
    phase_b = new_prop_values.get("phase_b") in ("True", True)
    phase_c = new_prop_values.get("phase_c") in ("True", True)
    phase_n = new_prop_values.get("phase_n") in ("True", True)

    #
    # Port altering properties
    #
    num_phases = sum((phase_a, phase_b, phase_c, phase_n))
    sides_conf = new_prop_values.get("conf")

    #
    # Must select at least one phase
    #
    if num_phases == 0:
        phase_a = True
        mdl.set_property_value(mdl.prop(mask_handle, "phase_a"), True)
        num_phases = 1
        mdl.info(f"{mdl.get_name(comp_handle)}: "
                 f"At least one phase must be selected. Setting to A.")

    #
    # Update ports
    #
    all_port_names = dict()
    all_port_names[1] = [f"{phase}1" for phase in "ABCN"]
    all_port_names[2] = [f"{phase}2" for phase in "ABCN"]

    # Port positions
    port_positions = {
        "A1": pos_offset((-200, -200)),
        "B1": pos_offset((-200, 0)),
        "C1": pos_offset((-200, 200)),
        "N1": pos_offset((-200, 400)),
        "A2": pos_offset((200, -200)),
        "B2": pos_offset((200, 0)),
        "C2": pos_offset((200, 200)),
        "N2": pos_offset((200, 400)),
    }

    # Which ports should be added
    new_ports = {
        "A1": phase_a,
        "B1": phase_b,
        "C1": phase_c,
        "N1": phase_n,
    }
    if sides_conf == "on both sides":
        new_ports.update(
            {
                "A2": phase_a,
                "B2": phase_b,
                "C2": phase_c,
                "N2": phase_n,
            }
        )

    for side, port_names in all_port_names.items():
        count_port = 0
        for port_name in all_port_names[side]:
            # Find existing port handle
            port = mdl.get_item(port_name, parent=comp_handle, item_type="port")
            # Boolean to determine port addition or removal
            included_port = new_ports.get(port_name)

            # Calculate terminal position
            image_size = 32 * num_phases
            term_x = -8 if side == 1 else 8
            term_y = 32 * count_port - (image_size / 2 - 16)
            term_pos = term_x, term_y

            if included_port:
                count_port += 1
                if not port:
                    # Add the port
                    mdl.create_port(name=port_name,
                                    parent=comp_handle,
                                    flip="flip_horizontal" if side == 2 else None,
                                    position=port_positions[port_name],
                                    terminal_position=term_pos,
                                    )
                else:
                    # Move the terminal into the new position
                    mdl.set_port_properties(port, terminal_position=term_pos)
            else:
                if port:
                    # Remove port
                    mdl.delete_item(port)

    #
    # Create connections
    #
    if sides_conf == "on both sides":

        # Remove any existing connection
        for conn in mdl.get_items(parent=comp_handle, item_type="connection"):
            mdl.delete_item(conn)

        # Connect ports to each other
        for port_1_name, port_2_name in zip(all_port_names[1], all_port_names[2]):
            included = new_ports.get(port_1_name)
            # WorkAround - When we have device marker, the bus is not exported to Json
            sc_item = mdl.get_item(f"SC_{port_1_name[0]}", parent=comp_handle)
            if sc_item:
                mdl.delete_item(sc_item)
            if included:
                port_1 = mdl.get_item(port_1_name, parent=comp_handle, item_type="port")
                port_2 = mdl.get_item(port_2_name, parent=comp_handle, item_type="port")
                port_1_pos = mdl.get_position(port_1)
                port_2_pos = mdl.get_position(port_2)
                # WorkAround - When we have device marker, the bus is not exported to Json
                sc_item = mdl.get_item(f"SC_{port_1_name[0]}", parent=comp_handle)
                if not sc_item:
                    sc_item = mdl.create_component("core/Short Circuit",
                                                   name=f"SC_{port_1_name[0]}",
                                                   position=(np.mean([port_1_pos[0], port_2_pos[0]]), port_1_pos[1]),
                                                   parent=comp_handle)
                mdl.create_connection(port_1, mdl.term(sc_item, "p_node"))
                mdl.create_connection(mdl.term(sc_item, "n_node"), port_2)

    old_state[comp_handle] = new_prop_values

    #
    # Save value to the retro-compatibility property
    #
    type_prop = mdl.prop(mask_handle, "type_prop")
    retro_string = ""
    retro_string += phase_a * "A" + phase_b * "B" + phase_c * "C" + phase_n * "N"
    mdl.set_property_value(type_prop, retro_string)

def define_icon(mdl, mask_handle):
    """
    Defines the component icon based on the number of phases
    """

    phase_a = mdl.get_property_disp_value(mdl.prop(mask_handle, "phase_a"))
    phase_b = mdl.get_property_disp_value(mdl.prop(mask_handle, "phase_b"))
    phase_c = mdl.get_property_disp_value(mdl.prop(mask_handle, "phase_c"))
    phase_n = mdl.get_property_disp_value(mdl.prop(mask_handle, "phase_n"))

    num_phases = sum((phase_a, phase_b, phase_c, phase_n))
    image = f"images/bus_{num_phases}ph.svg"
    mdl.set_component_icon_image(mask_handle, image)


def retro_compatibility(mdl, mask_handle):
    phase_a_prop = mdl.prop(mask_handle, "phase_a")
    phase_b_prop = mdl.prop(mask_handle, "phase_b")
    phase_c_prop = mdl.prop(mask_handle, "phase_c")
    phase_n_prop = mdl.prop(mask_handle, "phase_n")

    prop_mapping = {
        "A": phase_a_prop,
        "B": phase_b_prop,
        "C": phase_c_prop,
        "N": phase_n_prop,
    }

    type_prop = mdl.prop(mask_handle, "type_prop")
    old_type_value = mdl.get_property_value(type_prop)

    # Mark the correspondent checkbox for each letter in the old value
    for letter in "ABCN":
        if letter in old_type_value:
            mdl.set_property_value(prop_mapping[letter], True)
        else:
            mdl.set_property_value(prop_mapping[letter], False)
