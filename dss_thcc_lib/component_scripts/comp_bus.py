def pos_offset(pos):
    """
    Offset position from center of the schematic
    """
    x0, y0 = 8192, 8192

    pos_x, pos_y = pos

    return x0 + pos_x, y0 + pos_y


def circuit_dynamics(mdl, mask_handle, new_values=None):
    comp_handle = mdl.get_parent(mask_handle)

    # When loading a model
    if not new_values:
        new_values = mdl.get_property_values(comp_handle)

    mdl.info(f"{new_values=}")

    # conf_prop = mdl.prop(comp_handle, "conf")
    # type_prop = mdl.prop(comp_handle, "type_prop")

    #
    # Phases checkbox properties
    #
    phase_a = new_values.get("phase_a") in ("True", True)
    phase_b = new_values.get("phase_b") in ("True", True)
    phase_c = new_values.get("phase_c") in ("True", True)
    phase_n = new_values.get("phase_n") in ("True", True)

    #
    # Port altering properties
    #
    num_phases = sum((phase_a, phase_b, phase_c, phase_n))
    sides_conf = new_values.get("conf")

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


def mask_dialog_dynamics(mdl, container_handle, caller_prop_handle=None, init=False):
    """

    :param mdl:
    :param container_handle:
    :param caller_prop_handle:
    :param init:
    :return:
    """
    return
    # Property Registration
    conf_prop = mdl.prop(container_handle, "conf")
    type_prop = mdl.prop(container_handle, "type_prop")
    i_rms_meas_prop = mdl.prop(container_handle, "i_rms_meas")
    i_inst_meas_prop = mdl.prop(container_handle, "i_inst_meas")
    v_line_rms_meas_prop = mdl.prop(container_handle, "v_line_rms_meas")
    v_line_inst_meas_prop = mdl.prop(container_handle, "v_line_inst_meas")
    v_phase_rms_meas_prop = mdl.prop(container_handle, "v_phase_rms_meas")
    v_phase_inst_meas_prop = mdl.prop(container_handle, "v_phase_inst_meas")
    freq_meas_prop = mdl.prop(container_handle, "freq_meas")
    power_meas_prop = mdl.prop(container_handle, "power_meas")
    enable_output_prop = mdl.prop(container_handle, "enable_output")

    new_value = None

    if caller_prop_handle:
        new_value = mdl.get_property_disp_value(caller_prop_handle)

    # ------------------------------------------------------------------------------------------------------------------
    #  "conf" property code
    # ------------------------------------------------------------------------------------------------------------------
    if caller_prop_handle == conf_prop:
        comp_type = mdl.get_property_disp_value(type_prop)

        prop_list = [i_rms_meas_prop, i_inst_meas_prop, v_line_rms_meas_prop,
                     v_line_inst_meas_prop,
                     v_phase_rms_meas_prop, v_phase_inst_meas_prop, freq_meas_prop,
                     power_meas_prop,
                     enable_output_prop]
        if "ABC" in comp_type and new_value == "on both sides":
            [mdl.show_property(prop) for prop in prop_list]
        else:
            [mdl.hide_property(prop) for prop in prop_list]

    # ------------------------------------------------------------------------------------------------------------------
    #  "type" property code
    # ------------------------------------------------------------------------------------------------------------------
    if caller_prop_handle == type_prop:
        pass

    # ------------------------------------------------------------------------------------------------------------------
    #  "i_rms_meas_prop" properties code
    # ------------------------------------------------------------------------------------------------------------------
    if caller_prop_handle == i_rms_meas_prop:

        if new_value:
            mdl.set_property_disp_value(i_inst_meas_prop, True)
            if init:
                mdl.set_property_value(i_inst_meas_prop, True)
            mdl.disable_property(i_inst_meas_prop)
        else:
            mdl.enable_property(i_inst_meas_prop)

    # ------------------------------------------------------------------------------------------------------------------
    #  "v_line_rms_meas_prop" properties code
    # ------------------------------------------------------------------------------------------------------------------
    if caller_prop_handle == v_line_rms_meas_prop:

        if new_value:
            mdl.set_property_disp_value(v_line_inst_meas_prop, True)
            if init:
                mdl.set_property_value(v_line_inst_meas_prop, True)
            mdl.disable_property(v_line_inst_meas_prop)
        else:
            mdl.enable_property(v_line_inst_meas_prop)

    # ------------------------------------------------------------------------------------------------------------------
    #  "v_phase_rms_meas_prop" properties code
    # ------------------------------------------------------------------------------------------------------------------
    if caller_prop_handle == v_phase_rms_meas_prop:

        if new_value:
            mdl.set_property_disp_value(v_phase_inst_meas_prop, True)
            if init:
                mdl.set_property_value(v_phase_inst_meas_prop, True)
            mdl.disable_property(v_phase_inst_meas_prop)
        else:
            mdl.enable_property(v_phase_inst_meas_prop)

    # ------------------------------------------------------------------------------------------------------------------
    #  "freq_meas_prop" properties code
    # ------------------------------------------------------------------------------------------------------------------
    if caller_prop_handle == freq_meas_prop:

        if new_value:
            mdl.set_property_disp_value(v_phase_inst_meas_prop, True)
            if init:
                mdl.set_property_value(v_phase_inst_meas_prop, True)
            mdl.disable_property(v_phase_inst_meas_prop)
        else:
            mdl.enable_property(v_phase_inst_meas_prop)

    # ------------------------------------------------------------------------------------------------------------------
    #  "power_meas_prop" properties code
    # ------------------------------------------------------------------------------------------------------------------
    if caller_prop_handle == power_meas_prop:

        if new_value:
            [mdl.set_property_disp_value(prop, True)
             for prop in [i_rms_meas_prop, i_inst_meas_prop, v_phase_rms_meas_prop,
                          v_phase_inst_meas_prop,
                          freq_meas_prop]]
            if init:
                [mdl.set_property_value(prop, True)
                 for prop in [i_rms_meas_prop, i_inst_meas_prop, v_phase_rms_meas_prop,
                              v_phase_inst_meas_prop,
                              freq_meas_prop]]
            [mdl.disable_property(prop)
             for prop in [i_rms_meas_prop, i_inst_meas_prop, v_phase_rms_meas_prop,
                          v_phase_inst_meas_prop,
                          freq_meas_prop]]
        else:
            [mdl.enable_property(prop)
             for prop in [i_rms_meas_prop, v_phase_rms_meas_prop, freq_meas_prop]]


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
