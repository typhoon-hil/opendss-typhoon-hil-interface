old_state = {}


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

    # When loading a model
    if not new_prop_values:
        new_prop_values = mdl.get_property_values(comp_handle)

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
    num_phases = sum((phase_a, phase_b, phase_c))

    #
    # Must select at least one phase
    #
    if num_phases == 0:
        phase_a = True
        mdl.set_property_value(mdl.prop(mask_handle, "phase_a"), True)
        num_phases = 1
        mdl.info(
            f"{mdl.get_name(comp_handle)}: "
            f"At least one phase must be selected. Setting to A."
        )

    phases_str = (
        ""
        + ("A" if phase_a else "")
        + ("B" if phase_b else "")
        + ("C" if phase_c else "")
    )

    #
    # Update ports
    #
    all_port_names = dict()
    all_port_names[1] = [f"{phase}1" for phase in "ABC"]
    all_port_names[2] = [f"{phase}2" for phase in "ABC"]

    # Port positions
    port_positions = {
        "A1": pos_offset((-200, -200)),
        "B1": pos_offset((-200, 0)),
        "C1": pos_offset((-200, 200)),
        "A2": pos_offset((200, -200)),
        "B2": pos_offset((200, 0)),
        "C2": pos_offset((200, 200)),
    }

    # Meter positions
    meter_positions = {
        "ABC": pos_offset((0, 0)),
        "A": pos_offset((0, -200)),
        "B": pos_offset((0, 0)),
        "C": pos_offset((0, 200)),
    }

    # Which ports should be added
    new_ports = {
        "A1": phase_a,
        "B1": phase_b,
        "C1": phase_c,
        "A2": phase_a,
        "B2": phase_b,
        "C2": phase_c,
        "N": phase_n
    }
    create_out_ports = new_prop_values.get("enable_output") in ("True", True)

    # Measurement components
    meas_components = []

    for side, port_names in all_port_names.items():
        count_port = 0
        for port_name in all_port_names[side]:
            # Find existing port handle
            port = mdl.get_item(port_name, parent=comp_handle, item_type="port")
            # Boolean to determine port addition or removal
            included_port = new_ports.get(port_name)

            # Calculate terminal position
            image_size = 32 * num_phases
            term_x = -24 if side == 1 else 24
            term_y = 32 * count_port - (image_size / 2 - 16)
            term_pos = term_x, term_y

            if included_port:
                count_port += 1
                if not port:
                    # Add the port
                    mdl.create_port(
                        name=port_name,
                        parent=comp_handle,
                        hide_name=True,
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
    # Three-phase case
    #
    if num_phases == 3:
        # Delete single phase meters, signal ports and tags
        for phase in "ABC":
            meter = mdl.get_item(f"meter_{phase}", parent=comp_handle)
            if meter:
                mdl.delete_item(meter)

            out_port = mdl.get_item(
                f"out_{phase}",
                parent=comp_handle,
                item_type="port",
            )
            if out_port:
                mdl.delete_item(out_port)

            tag = mdl.get_item(f"tag_{phase}", parent=comp_handle)
            if tag:
                mdl.delete_item(tag)

        # Create measurement component
        meter_abc = mdl.get_item(f"meter_ABC", parent=comp_handle)
        if not meter_abc:
            meter_abc = mdl.create_component(
                "core/Three-phase Meter",
                name="meter_ABC",
                parent=comp_handle,
                position=meter_positions["ABC"],
            )
            # Create ground tag
            tag_3_ph = mdl.create_tag(
                "gnd",
                name="tag_ABC",
                parent=comp_handle,
                scope="local",
                kind="pe",
                position=(
                    meter_positions["ABC"][0] - 40,
                    meter_positions["ABC"][1] + 200,
                ),
            )

            # Create connections
            # A
            port_a1 = mdl.get_item("A1", parent=comp_handle, item_type="port")
            term_a_plus = mdl.term(meter_abc, "A+")
            mdl.create_connection(term_a_plus, port_a1)
            port_a2 = mdl.get_item("A2", parent=comp_handle, item_type="port")
            term_a_minus = mdl.term(meter_abc, "A-")
            mdl.create_connection(term_a_minus, port_a2)
            # B
            port_b1 = mdl.get_item("B1", parent=comp_handle, item_type="port")
            term_b_plus = mdl.term(meter_abc, "B+")
            mdl.create_connection(term_b_plus, port_b1)
            port_b2 = mdl.get_item("B2", parent=comp_handle, item_type="port")
            term_b_minus = mdl.term(meter_abc, "B-")
            mdl.create_connection(term_b_minus, port_b2)
            # C
            port_c1 = mdl.get_item("C1", parent=comp_handle, item_type="port")
            term_c_plus = mdl.term(meter_abc, "C+")
            mdl.create_connection(term_c_plus, port_c1)
            port_c2 = mdl.get_item("C2", parent=comp_handle, item_type="port")
            term_c_minus = mdl.term(meter_abc, "C-")
            mdl.create_connection(term_c_minus, port_c2)
            # Tag
            port_gnd_meter = mdl.term(meter_abc, "GND")
            mdl.create_connection(port_gnd_meter, tag_3_ph)

        # Set inner measurement checkboxes (currently only for 3-phase)
        prop_mapping = {
            "v_phase_inst_meas": ["VAn", "VBn", "VCn"],
            "v_line_inst_meas": ["VAB", "VBC", "VCA"],
            "i_inst_meas": ["IA", "IB", "IC"],
            "v_phase_rms_meas": ["VLn_rms"],
            "v_line_rms_meas": ["VLL_rms"],
            "i_rms_meas": ["I_rms"],
            "freq_meas": ["freq"],
            "power_meas": ["P_meas"],
        }
        # Set RMS Power based mode to get phase measurements (before set the "power_meas" prop)
        mdl.set_property_value(mdl.prop(meter_abc, "P_method"), "RMS based")
        for prop_name, inner_prop_name_list in prop_mapping.items():
            prop_bool = new_prop_values.get(prop_name) in ("True", True)
            for inner_prop_name in inner_prop_name_list:
                prop = mdl.prop(meter_abc, inner_prop_name)
                mdl.set_property_value(prop, prop_bool)
        # Set execution rate
        ts_prop = mdl.prop(meter_abc, "Ts")
        mdl.set_property_value(ts_prop, "execution_rate")

        # Create output port if necessary
        if create_out_ports:
            # Calculate terminal position
            image_size = 32 * num_phases

            out_port = mdl.get_item(
                f"out_ABC",
                parent=comp_handle,
                item_type="port",
            )
            if not out_port:
                out_port = mdl.create_port(
                    name=f"out_ABC",
                    parent=comp_handle,
                    kind="sp",
                    direction="out",
                    position=(
                        meter_positions["ABC"][0] + 40,
                        meter_positions["ABC"][1] - 200,
                    ),
                    terminal_position=(0, -image_size / 2),
                )

                # Set inner property
                en_out_prop = mdl.prop(meter_abc, "enable_out")
                mdl.set_property_value(en_out_prop, True)

                # Connect
                port_signal_meter = mdl.term(meter_abc, "Out")
                mdl.create_connection(port_signal_meter, out_port)
        else:
            # Set inner property
            en_out_prop = mdl.prop(meter_abc, "enable_out")
            mdl.set_property_value(en_out_prop, False)

    #
    # Single or two phase case
    #
    else:
        # Delete meter, signal port and tag
        meter_abc = mdl.get_item("meter_ABC", parent=comp_handle)
        if meter_abc:
            mdl.delete_item(meter_abc)

        tag_abc = mdl.get_item("tag_ABC", parent=comp_handle)
        if tag_abc:
            mdl.delete_item(tag_abc)

        signal_port = mdl.get_item(
            f"out_ABC",
            parent=comp_handle,
            item_type="port",
        )
        if signal_port:
            mdl.delete_item(signal_port)

        # Create elements for each phase
        for idx, phase in enumerate(phases_str):

            # Delete measurements out from the phases_str
            for sp_meter_phase in ["A", "B", "C"]:
                sp_meter_handle = mdl.get_item(f"meter_{sp_meter_phase}", parent=comp_handle)
                if (sp_meter_phase not in phases_str) and sp_meter_handle:
                    mdl.delete_item(sp_meter_handle)
                    sp_tag_handle = mdl.get_item(f"tag_{sp_meter_phase}", parent=comp_handle, item_type="tag")
                    mdl.delete_item(sp_tag_handle) if sp_tag_handle else None

            # Create measurement component
            new_meter = mdl.get_item(f"meter_{phase}", parent=comp_handle)
            if not new_meter:
                new_meter = mdl.create_component(
                    "core/Single-phase Meter",
                    name=f"meter_{phase}",
                    parent=comp_handle,
                    position=meter_positions[f"{phase}"],
                )

                # Create ground tag
                new_tag = mdl.create_tag(
                    "gnd",
                    name=f"tag_{phase}",
                    parent=comp_handle,
                    scope="local",
                    kind="pe",
                    position=(
                        meter_positions[f"{phase}"][0] - 40,
                        meter_positions[f"{phase}"][1] + 80,
                    ),
                )

                # Create connections
                # Port 1
                port_1 = mdl.get_item(f"{phase}1", parent=comp_handle, item_type="port")
                term_in = mdl.term(new_meter, "in")
                mdl.create_connection(term_in, port_1)
                # Port 2
                port_2 = mdl.get_item(f"{phase}2", parent=comp_handle, item_type="port")
                term_out = mdl.term(new_meter, "out")
                mdl.create_connection(term_out, port_2)
                # Tag
                port_n_meter = mdl.term(new_meter, "N")
                mdl.create_connection(port_n_meter, new_tag)

            meas_components.append(new_meter)

            # Set execution rate
            ts_prop = mdl.prop(new_meter, "execution_rate")
            mdl.set_property_value(ts_prop, "execution_rate")
            # Set fgrid
            fgrid_prop = mdl.prop(new_meter, "fgrid")
            mdl.set_property_value(fgrid_prop, "replace_with_simdss_basefreq")

            # Create output port if necessary
            if create_out_ports:
                # Calculate terminal position
                image_size = 32 * num_phases
                term_x = - 8 * (num_phases - 1) + idx * 16

                out_port = mdl.get_item(
                    f"out_{phase}",
                    parent=comp_handle,
                    item_type="port",
                )
                if not out_port:
                    out_port = mdl.create_port(
                        name=f"out_{phase}",
                        parent=comp_handle,
                        kind="sp",
                        direction="out",
                        position=(
                            meter_positions[f"{phase}"][0] + 40,
                            meter_positions[f"{phase}"][1] - 80,
                        ),
                        terminal_position=(term_x, -image_size / 2),
                    )

                    # Set inner property
                    en_out_prop = mdl.prop(new_meter, "enable_out")
                    mdl.set_property_value(en_out_prop, True)

                    # Connect
                    port_signal_meter = mdl.term(new_meter, "meas out")
                    mdl.create_connection(port_signal_meter, out_port)
            else:
                # Set inner property
                en_out_prop = mdl.prop(new_meter, "enable_out")
                mdl.set_property_value(en_out_prop, False)

    # Neutral Port (Future)
    if new_ports["N"]:
        ground_handle = mdl.get_item("gnd", parent=comp_handle)
        gnd_tag_handle = mdl.get_item("gnd_tag", parent=comp_handle, item_type="tag")
        # Calculate terminal position
        image_size = 32 * num_phases
        term_pos = 0, image_size / 2
        if ground_handle:
            ground_position = mdl.get_position(ground_handle)
            mdl.delete_item(ground_handle)

            ground_handle = mdl.create_port(name="N",
                                            parent=comp_handle,
                                            position=ground_position,
                                            rotation="left",
                                            terminal_position=term_pos)
            mdl.create_connection(gnd_tag_handle, ground_handle)
        else:
            # Update position
            ground_handle = mdl.get_item("N", parent=comp_handle, item_type="port")
            mdl.set_port_properties(ground_handle, terminal_position=term_pos)
    else:
        ground_handle = mdl.get_item("N", parent=comp_handle, item_type="port")
        gnd_tag_handle = mdl.get_item("gnd_tag", parent=comp_handle, item_type="tag")
        if ground_handle:
            ground_position = mdl.get_position(ground_handle)
            mdl.delete_item(ground_handle)
            ground_handle = mdl.create_component("core/Ground",
                                                 name="gnd",
                                                 parent=comp_handle,
                                                 position=ground_position
                                                 )
            mdl.create_connection(gnd_tag_handle, mdl.term(ground_handle, "node"))

    old_state[comp_handle] = new_prop_values

    return


def mask_dialog_dynamics(mdl, mask_handle, caller_prop_handle=None, init=False):
    """
    """

    #
    # Phases checkbox properties
    #
    phase_a_prop = mdl.prop(mask_handle, "phase_a")
    phase_b_prop = mdl.prop(mask_handle, "phase_b")
    phase_c_prop = mdl.prop(mask_handle, "phase_c")
    # Current display values
    phase_a = mdl.get_property_disp_value(phase_a_prop) in ("True", True)
    phase_b = mdl.get_property_disp_value(phase_b_prop) in ("True", True)
    phase_c = mdl.get_property_disp_value(phase_c_prop) in ("True", True)

    #
    # Number of selected phases
    #
    num_phases = sum((phase_a, phase_b, phase_c))

    #
    # Measurement properties
    #
    v_phase_inst_meas_prop = mdl.prop(mask_handle, "v_phase_inst_meas")
    v_line_inst_meas_prop = mdl.prop(mask_handle, "v_line_inst_meas")
    i_inst_meas_prop = mdl.prop(mask_handle, "i_inst_meas")
    v_phase_rms_meas_prop = mdl.prop(mask_handle, "v_phase_rms_meas")
    v_line_rms_meas_prop = mdl.prop(mask_handle, "v_line_rms_meas")
    i_rms_meas_prop = mdl.prop(mask_handle, "i_rms_meas")
    freq_meas_prop = mdl.prop(mask_handle, "freq_meas")
    power_meas_prop = mdl.prop(mask_handle, "power_meas")
    all_meas_props = [
        v_phase_inst_meas_prop,
        v_line_inst_meas_prop,
        i_inst_meas_prop,
        v_phase_rms_meas_prop,
        v_line_rms_meas_prop,
        i_rms_meas_prop,
        freq_meas_prop,
        power_meas_prop,
    ]
    # Current display values
    v_phase_rms_meas = mdl.get_property_disp_value(v_phase_rms_meas_prop)
    v_line_rms_meas = mdl.get_property_disp_value(v_line_rms_meas_prop)
    i_rms_meas = mdl.get_property_disp_value(i_rms_meas_prop)
    freq_meas = mdl.get_property_disp_value(freq_meas_prop)
    power_meas = mdl.get_property_disp_value(power_meas_prop)

    #
    # Customize measurements of 3-phase meter
    #
    if num_phases == 3:
        for prop in all_meas_props:
            mdl.enable_property(prop)

        # RMS demands instantaneous
        # Frequency demands instantaneous voltage
        # Power demands all phase properties

        force_inst_line_voltage = v_line_rms_meas
        force_inst_phase_voltage = any(
            (freq_meas, power_meas, v_phase_rms_meas, v_line_rms_meas)
        )
        force_inst_current = any(
            (power_meas, i_rms_meas)
        )

        force_freq = power_meas
        force_rms_phase_voltage = power_meas
        force_rms_phase_current = power_meas

        # Mark and disable checkboxes
        if force_inst_line_voltage:
            mdl.disable_property(v_line_inst_meas_prop)
            mdl.set_property_disp_value(v_line_inst_meas_prop, True)
        else:
            mdl.enable_property(v_line_inst_meas_prop)

        if force_inst_current:
            mdl.disable_property(i_inst_meas_prop)
            mdl.set_property_disp_value(i_inst_meas_prop, True)
        else:
            mdl.enable_property(i_inst_meas_prop)

        if force_inst_phase_voltage:
            mdl.disable_property(v_phase_inst_meas_prop)
            mdl.set_property_disp_value(v_phase_inst_meas_prop, True)
        else:
            mdl.enable_property(v_phase_inst_meas_prop)

        if force_freq:
            mdl.disable_property(freq_meas_prop)
            mdl.set_property_disp_value(freq_meas_prop, True)
        else:
            mdl.enable_property(freq_meas_prop)

        if force_rms_phase_voltage:
            mdl.disable_property(v_phase_rms_meas_prop)
            mdl.set_property_disp_value(v_phase_rms_meas_prop, True)
        else:
            mdl.enable_property(v_phase_rms_meas_prop)

        if force_rms_phase_current:
            mdl.disable_property(i_rms_meas_prop)
            mdl.set_property_disp_value(i_rms_meas_prop, True)
        else:
            mdl.enable_property(i_rms_meas_prop)

    #
    # Single phase meter currently doesn't allow customization of measurements
    #
    else:
        # Mark and disable checkboxes
        for prop in all_meas_props:
            mdl.disable_property(prop)
            mdl.set_property_disp_value(prop, True)


def pre_compilation(mdl, mask_handle):
    comp_handle = mdl.get_parent(mask_handle)

    #
    # Updates the inner single-phase meters fgrid
    # based on the global basefrequency value
    #

    # Get global basefreq
    if "simdss_basefreq" in mdl.get_ns_vars():
        global_basefreq = mdl.get_ns_var("simdss_basefreq")
    else:
        mdl.error(
            "Add a SimDSS component to define the global frequency value.",
            context=comp_handle,
        )
        return

    for phase in "ABC":
        meter = mdl.get_item(f"meter_{phase}", parent=comp_handle)

        if meter:
            # Set fgrid
            fgrid_prop = mdl.prop(meter, "fgrid")
            mdl.set_property_value(fgrid_prop, global_basefreq)

def define_icon(mdl, mask_handle):
    """
    Defines the component icon based on the number of phases
    """

    phase_a = mdl.get_property_disp_value(mdl.prop(mask_handle, "phase_a"))
    phase_b = mdl.get_property_disp_value(mdl.prop(mask_handle, "phase_b"))
    phase_c = mdl.get_property_disp_value(mdl.prop(mask_handle, "phase_c"))

    num_phases = sum((phase_a, phase_b, phase_c))
    image = f"images/monitor_{num_phases}ph.svg"
    mdl.set_component_icon_image(mask_handle, image)
