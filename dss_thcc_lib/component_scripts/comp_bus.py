import dss_thcc_lib.component_scripts.util as util
old_state = {}


def get_sld_conversion_info(mdl, mask_handle, props_state, apply_modification=""):

    phase_a = props_state.get("phase_a")
    phase_b = props_state.get("phase_b")
    phase_c = props_state.get("phase_c")
    phase_n = props_state.get("phase_n")
    sides_conf = props_state.get("conf")
    second_side_is_multiline = props_state.get("second_side_is_multiline")
    num_phases = sum((phase_a, phase_b, phase_c, phase_n))

    #
    # Which ports are expected
    #
    if apply_modification == "second_side_is_multiline":
        bus_port_1_name = "2"
        new_ports_1 = {
            "A2": phase_a,
            "B2": phase_b,
            "C2": phase_c,
            "N2": phase_n,
        }
    else:
        bus_port_1_name = "1"
        new_ports_1 = {
            "A1": phase_a,
            "B1": phase_b,
            "C1": phase_c,
            "N1": phase_n,
        }
    multiline_ports_1 = [port for port, checked in new_ports_1.items() if checked]

    if sides_conf == "on both sides" and not second_side_is_multiline:
        bus_port_2_name = "2"
        new_ports_2 = {
                "A2": phase_a,
                "B2": phase_b,
                "C2": phase_c,
                "N2": phase_n,
        }
        multiline_ports_2 = [port for port, checked in new_ports_2.items() if checked]

    port_config_dict = {
        bus_port_1_name: {
            "multiline_ports": multiline_ports_1,
            "side": "left",
            "bus_terminal_position": (-8, 0),
            "hide_name": True,
        },
    }

    if sides_conf == "on both sides" and not second_side_is_multiline:
        port_config_dict.update(
            {
                bus_port_2_name: {
                    "multiline_ports": multiline_ports_2,
                    "side": "right",
                    "bus_terminal_position": (8, 0),
                    "hide_name": True,
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
        term_y = 32 * idx - (image_size / 2 - 16)
        return term_x, term_y

    terminal_positions = {
        term_name: calc_term_position("left", term_name, idx)
        for idx, term_name in enumerate(multiline_ports_1)
    }
    if sides_conf == "on both sides" and not second_side_is_multiline:
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
    comp_handle = mdl.get_parent(mask_handle)

    if prop_handle:
        calling_prop_name = mdl.get_name(prop_handle)
    else:
        calling_prop_name = "init_code"

    #
    # Get new property values to be applied
    #
    new_prop_values = {}
    current_pass_prop_values = mdl.get_property_values(comp_handle)
    for prop in mdl.get_property_values(comp_handle):
        p = mdl.prop(mask_handle, prop)
        new_prop_values[prop] = mdl.get_property_disp_value(p)

    global old_state

    if calling_prop_name == "init_code":
        sld_mode = current_pass_prop_values["sld_mode"]
        second_side_is_multiline = current_pass_prop_values["second_side_is_multiline"]
        if sld_mode and second_side_is_multiline:
            sld_info = get_sld_conversion_info(
                mdl,
                mask_handle,
                current_pass_prop_values,
                apply_modification="second_side_is_multiline"
            )
            util.convert_to_multiline(mdl, mask_handle, sld_info)
        else:
            sld_info = get_sld_conversion_info(
                mdl,
                mask_handle,
                current_pass_prop_values
            )
            util.convert_to_multiline(mdl, mask_handle, sld_info)
        return

    if calling_prop_name == "sld_mode":
        old_state[comp_handle] = current_pass_prop_values
        sld_info = get_sld_conversion_info(mdl, mask_handle, current_pass_prop_values)
        if new_value:
            if new_value != old_value:
                util.convert_to_sld(mdl, mask_handle, sld_info)
        else:
            util.convert_to_multiline(mdl, mask_handle, sld_info)
        return

    if calling_prop_name == "second_side_is_multiline_prop":
        old_state[comp_handle] = current_pass_prop_values
        if new_value != old_value:
            if current_pass_prop_values["sld_mode"]:
                if current_pass_prop_values["second_side_is_multiline_prop"]:
                    sld_info = get_sld_conversion_info(
                        mdl,
                        mask_handle,
                        current_pass_prop_values,
                        apply_modification="second_side_is_multiline"
                    )
                    util.convert_to_multiline(mdl, mask_handle, sld_info)
        return

    # Topology dynamics need to be applied on multiline format
    currently_sld = mdl.get_item("1", parent=comp_handle, item_type="port")
    if currently_sld:
        # The terminal related to the current property hasn't been created yet
        modified_prop_values = dict(current_pass_prop_values)
        modified_prop_values[calling_prop_name] = old_value
        sld_info = get_sld_conversion_info(mdl, mask_handle, modified_prop_values)
        util.convert_to_multiline(mdl, mask_handle, sld_info)

    #
    # If the property values are the same as on the previous run, stop
    #
    if new_prop_values == old_state.get(comp_handle):
        return

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
            if included:
                port_1 = mdl.get_item(port_1_name, parent=comp_handle, item_type="port")
                port_2 = mdl.get_item(port_2_name, parent=comp_handle, item_type="port")
                mdl.create_connection(port_1, port_2)

    old_state[comp_handle] = new_prop_values

    #
    # Save value to the retro-compatibility property
    #
    type_prop = mdl.prop(mask_handle, "type_prop")
    retro_string = ""
    retro_string += phase_a * "A" + phase_b * "B" + phase_c * "C" + phase_n * "N"
    mdl.set_property_value(type_prop, retro_string)

    # When property values reached the final state, return to single-line if needed
    if new_prop_values == current_pass_prop_values:
        if new_prop_values.get("sld_mode") in ("True", True):
            sld_info = get_sld_conversion_info(mdl, mask_handle, current_pass_prop_values)
            util.convert_to_sld(mdl, mask_handle, sld_info)


def mask_dialog_dynamics(mdl, mask_handle, prop_handle, new_value):
    conf_prop = mdl.prop(mask_handle, "conf")
    sld_mode_prop = mdl.prop(mask_handle, "sld_mode")
    second_side_is_multiline_prop = mdl.prop(mask_handle, "second_side_is_multiline")
    phase_a_prop = mdl.prop(mask_handle, "phase_a")
    phase_b_prop = mdl.prop(mask_handle, "phase_b")
    phase_c_prop = mdl.prop(mask_handle, "phase_c")
    phase_n_prop = mdl.prop(mask_handle, "phase_n")

    conf = mdl.get_property_disp_value(conf_prop)
    phase_a = mdl.get_property_disp_value(phase_a_prop)
    phase_b = mdl.get_property_disp_value(phase_b_prop)
    phase_c = mdl.get_property_disp_value(phase_c_prop)
    phase_n = mdl.get_property_disp_value(phase_n_prop)
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

    phase_a = mdl.get_property_disp_value(mdl.prop(mask_handle, "phase_a"))
    phase_b = mdl.get_property_disp_value(mdl.prop(mask_handle, "phase_b"))
    phase_c = mdl.get_property_disp_value(mdl.prop(mask_handle, "phase_c"))
    phase_n = mdl.get_property_disp_value(mdl.prop(mask_handle, "phase_n"))
    sld_mode = mdl.get_property_disp_value(mdl.prop(mask_handle, "sld_mode"))
    second_side_is_multiline_prop = mdl.get_property_disp_value(
        mdl.prop(mask_handle, "second_side_is_multiline")
    )

    if sld_mode and not second_side_is_multiline_prop:
        image = f"images/bus_1ph.svg"
    else:
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
