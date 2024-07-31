import dss_thcc_lib.component_scripts.util as util
import importlib
import re


def update_library_version_info(mdl, mask_handle):
    util.set_component_library_version(mdl, mask_handle)


def get_sld_conversion_info(mdl, mask_handle, props_state, to_sld=True):
    comp_handle = mdl.get_parent(mask_handle)
    sides_conf = props_state.get("conf")
    second_side_is_multiline = props_state.get("second_side_is_multiline") in ("True", True)
    num_phases = 4

    #
    # Which ports are expected
    #
    if second_side_is_multiline:
        bus_port_1_name = "SLD2"
        bus_port_1_side = "right"
        bus_port_1_term_pos = (8, 0)
        multiline_ports_1 = ["A2", "B2", "C2", "N2"]
    else:
        bus_port_1_name = "SLD1"
        bus_port_1_side = "left"
        bus_port_1_term_pos = (-8, 0)
        multiline_ports_1 = ["A1", "B1", "C1", "N1"]

    #
    # Find the current status when returning to multiline
    #
    bus2 = mdl.get_item("SLD2", parent=comp_handle, item_type="port")

    if (bus2 and not to_sld) or (sides_conf == "on both sides" and not second_side_is_multiline):
        bus_port_2_name = "SLD2"

    multiline_ports_2 = ["A2", "B2", "C2", "N2"]

    port_config_dict = {
        bus_port_1_name: {
            "multiline_ports": multiline_ports_1,
            "side": bus_port_1_side,
            "bus_terminal_position": bus_port_1_term_pos,
            "hide_name": props_state.get("sld_mode") in ("True", True),
        },
    }

    if (bus2 and not to_sld) or (to_sld and sides_conf == "on both sides" and not second_side_is_multiline):
        port_config_dict.update(
            {
                bus_port_2_name: {
                    "multiline_ports": multiline_ports_2,
                    "side": "right",
                    "bus_terminal_position": (8, 0),
                    "hide_name": props_state.get("sld_mode") in ("True", True),
                }
            }
        )

    #
    # Tag info
    #
    tag_config_dict = {}

    #
    # Terminal positions
    #
    def calc_term_position(side, term_name, idx):
        image_size = 32 * num_phases
        term_x = -8 if side == "left" else 8
        term_y = 32 * idx - image_size / 2 + 16
        return term_x, term_y

    terminal_positions = {
        term_name: calc_term_position(bus_port_1_side, term_name, idx)
        for idx, term_name in enumerate(multiline_ports_1)
    }
    if to_sld and sides_conf == "on both sides" and not second_side_is_multiline:
        terminal_positions.update(
            {
                term_name: calc_term_position("right", term_name, idx)
                for idx, term_name in enumerate(multiline_ports_2)
            }
        )

    return port_config_dict, tag_config_dict, terminal_positions


def pos_offset(pos):
    """
    Offset position from center of the schematic
    """
    x0, y0 = 8192, 8192

    pos_x, pos_y = pos

    return x0 + pos_x, y0 + pos_y


def topology_dynamics(mdl, mask_handle, prop_handle, new_value, old_value):
    importlib.reload(util)
    comp_handle = mdl.get_parent(mask_handle)

    if prop_handle:
        calling_prop_name = mdl.get_name(prop_handle)
    else:
        calling_prop_name = "init_code"

    #
    # Get new property values to be applied
    # If multiple properties are changed, there is a temporary mismatch between
    # display values (the final values) and current values.
    #
    new_prop_values = {}
    current_pass_prop_values = {
        k: str(v) for k, v in mdl.get_property_values(comp_handle).items()
    }
    for prop in mdl.get_property_values(comp_handle):
        p = mdl.prop(mask_handle, prop)
        disp_value = str(mdl.get_property_disp_value(p))
        new_prop_values[prop] = disp_value

    #
    # Topology dynamics need to be applied on multiline format
    #
    currently_sld = mdl.get_item("SLD1", parent=comp_handle, item_type="port")
    if currently_sld:
        # The terminal related to the current property hasn't been created yet
        modified_prop_values = dict(current_pass_prop_values)
        modified_prop_values[calling_prop_name] = old_value
        # Remove conversion
        sld_info = get_sld_conversion_info(
            mdl,
            mask_handle,
            current_pass_prop_values,
            to_sld=False,
        )
        util.convert_to_multiline(mdl, mask_handle, sld_info, hide_names=False)

    #
    # Perform the port / connection changes
    #

    # Phases checkbox properties
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
            term_y = 32 * count_port - image_size / 2 + 16
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

        # Remove connections
        for conn in mdl.get_items(parent=comp_handle, item_type="connection"):
            if not mdl.get_name(conn).startswith("conn_gnd"):
                mdl.delete_item(conn)

        # Connect ports to each other
        for port_1_name, port_2_name in zip(all_port_names[1], all_port_names[2]):
            included = new_ports.get(port_1_name)
            if included and not port_1_name.startswith("G"):
                port_1 = mdl.get_item(port_1_name, parent=comp_handle, item_type="port")
                port_2 = mdl.get_item(port_2_name, parent=comp_handle, item_type="port")
                mdl.create_connection(port_1, port_2)

        #
        # TAG names
        #
        all_tag_names = dict()
        all_tag_names[1] = [f"{phase}1_repl" for phase in "ABCN"]
        all_tag_names[2] = [f"{phase}2_repl" for phase in "ABCN"]

        # WorkAround to ensure Json export - Connect a dummy circuit
        dummy_circuit = mdl.get_item("Dummy Circuit", parent=comp_handle)
        dummy_port = mdl.term(dummy_circuit, "Conn")
        current_connections = mdl.find_connections(dummy_port)

        if current_connections:
            mdl.delete_item(current_connections[0])
        dummy_con = 0

        port_items = [mdl.get_item(pname, parent=comp_handle, item_type="port")
                      for pname in all_port_names[1] + all_port_names[2]]

        tag_items = [mdl.get_item(tname, parent=comp_handle, item_type="tag")
                      for tname in all_tag_names[1] + all_tag_names[2]]

        for comp_tag in tag_items:
            if dummy_con == 0 and comp_tag:
                mdl.create_connection(comp_tag, dummy_port)
                dummy_con = 1
                break

        for comp_port in port_items:
            if dummy_con == 0 and comp_port:
                mdl.create_connection(comp_port, dummy_port)
                dummy_con = 1
                break


    #
    # Save value to the retro-compatibility property
    #
    type_prop = mdl.prop(mask_handle, "type_prop")
    retro_string = ""
    retro_string += phase_a * "A" + phase_b * "B" + phase_c * "C" + phase_n * "N"
    mdl.set_property_value(type_prop, retro_string)

    #
    # When property values reach the final state, return to single-line if needed
    #
    values_equal = []
    for prop_name in new_prop_values:
        cur_pass_value = current_pass_prop_values[prop_name]
        new_value = new_prop_values[prop_name]
        if util.is_float(cur_pass_value) or util.is_float(new_value):
            if float(cur_pass_value) == float(new_value):
                values_equal.append(True)
                continue
        else:
            if current_pass_prop_values[prop_name] == new_prop_values[prop_name]:
                values_equal.append(True)
                continue
        values_equal.append(False)

    final_state = all(values_equal)

    if final_state:
        if new_prop_values.get("sld_mode") in ("True", True):
            sld_info = get_sld_conversion_info(mdl, mask_handle, current_pass_prop_values)
            util.convert_to_sld(mdl, mask_handle, sld_info)

    sld_post_processing(mdl, mask_handle)


def sld_post_processing(mdl, mask_handle):
    pass


def mask_dialog_dynamics(mdl, mask_handle, prop_handle, new_value):
    conf_prop = mdl.prop(mask_handle, "conf")
    sld_mode_prop = mdl.prop(mask_handle, "sld_mode")
    second_side_is_multiline_prop = mdl.prop(mask_handle, "second_side_is_multiline")
    phase_a_prop = mdl.prop(mask_handle, "phase_a")
    phase_b_prop = mdl.prop(mask_handle, "phase_b")
    phase_c_prop = mdl.prop(mask_handle, "phase_c")
    phase_n_prop = mdl.prop(mask_handle, "phase_n")
    phase_props = [phase_a_prop, phase_b_prop, phase_c_prop, phase_n_prop]

    conf = mdl.get_property_disp_value(conf_prop)
    phase_a = mdl.get_property_disp_value(phase_a_prop) in ("True", True)
    phase_b = mdl.get_property_disp_value(phase_b_prop) in ("True", True)
    phase_c = mdl.get_property_disp_value(phase_c_prop) in ("True", True)
    phase_n = mdl.get_property_disp_value(phase_n_prop) in ("True", True)
    sld_mode = mdl.get_property_disp_value(sld_mode_prop) in ("True", True)

    if sld_mode:
        [mdl.disable_property(ph) for ph in phase_props]
        [mdl.set_property_disp_value(ph, True) for ph in phase_props]
        num_phases = 4
    else:
        [mdl.enable_property(ph) for ph in phase_props]
        num_phases = sum((phase_a, phase_b, phase_c, phase_n))

    if num_phases < 2:
        mdl.disable_property(sld_mode_prop)
        mdl.set_property_disp_value(sld_mode_prop, "False")
    else:
        mdl.enable_property(sld_mode_prop)

    sld_mode = mdl.get_property_disp_value(sld_mode_prop)
    if conf == "on both sides" and sld_mode in (True, "True"):
        mdl.show_property(second_side_is_multiline_prop)
    else:
        mdl.hide_property(second_side_is_multiline_prop)


def define_icon(mdl, mask_handle):
    """
    Defines the component icon based on the number of phases
    """

    phase_a = mdl.get_property_value(mdl.prop(mask_handle, "phase_a"))
    phase_b = mdl.get_property_value(mdl.prop(mask_handle, "phase_b"))
    phase_c = mdl.get_property_value(mdl.prop(mask_handle, "phase_c"))
    phase_n = mdl.get_property_value(mdl.prop(mask_handle, "phase_n"))
    sld_mode = mdl.get_property_value(mdl.prop(mask_handle, "sld_mode"))
    second_side_is_multiline_prop = mdl.get_property_value(
        mdl.prop(mask_handle, "second_side_is_multiline")
    )

    if sld_mode and not second_side_is_multiline_prop:
        image = f"images/bus_1ph.svg"
    else:
        num_phases = sum((phase_a, phase_b, phase_c, phase_n))
        image = f"images/bus_{num_phases}ph.svg"

    mdl.set_component_icon_image(mask_handle, image)


def retro_compatibility(mdl, mask_handle):
    comp_handle = mdl.get_parent(mask_handle)

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


    sld_mode_prop = mdl.prop(mask_handle, "sld_mode")
    libver_prop = mdl.prop(mask_handle, "library_version")
    lib_version = mdl.get_property_value(libver_prop)

    # Pre-SLD compatibility
    if lib_version < 51:
        mdl.set_property_value(sld_mode_prop, False)