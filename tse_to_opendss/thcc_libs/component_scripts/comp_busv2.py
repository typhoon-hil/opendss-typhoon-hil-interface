def circuit_dynamics(mdl, container_handle, caller_prop_handle=None, init=False):
    """

    :param mdl:
    :param container_handle:
    :param caller_prop_handle:
    :param init:
    :return:

    """
    # Property Registration
    conf_prop = mdl.prop(container_handle, "conf")
    type_prop = mdl.prop(container_handle, "type")
    ground_prop = mdl.prop(container_handle, "ground")
    i_rms_meas_prop = mdl.prop(container_handle, "i_rms_meas")
    i_inst_meas_prop = mdl.prop(container_handle, "i_inst_meas")
    v_line_rms_meas_prop = mdl.prop(container_handle, "v_line_rms_meas")
    v_line_inst_meas_prop = mdl.prop(container_handle, "v_line_inst_meas")
    v_phase_rms_meas_prop = mdl.prop(container_handle, "v_phase_rms_meas")
    v_phase_inst_meas_prop = mdl.prop(container_handle, "v_phase_inst_meas")
    freq_meas_prop = mdl.prop(container_handle, "freq_meas")
    power_meas_prop = mdl.prop(container_handle, "power_meas")

    new_value = None

    if caller_prop_handle:
        new_value = mdl.get_property_value(caller_prop_handle)

    # ------------------------------------------------------------------------------------------------------------------
    #  "conf" property code
    # ------------------------------------------------------------------------------------------------------------------
    if caller_prop_handle == conf_prop:
        comp_type = mdl.get_property_disp_value(type_prop)
        # Components Vars
        comp_handle = mdl.get_parent(container_handle)
        comp_port_labels = ["A2", "B2", "C2"]
        comp_port_handles = [mdl.get_item(p_name, item_type="port", parent=comp_handle)
                             for p_name in comp_port_labels]
        # Three-Phase Meter Vars
        meas_handle = mdl.get_item("Measurements", parent=comp_handle)
        meas_port_labels = ["A+", "B+", "C+", "A-", "B-", "C-"]
        meas_port_handles = [mdl.get_item(p_name, item_type="terminal", parent=meas_handle)
                             for p_name in meas_port_labels]
        # Port Vars
        port_attributes = get_port_const_attributes(comp_type)
        create_delete_ports = [phase in comp_type for phase in ["A", "B", "C"]]

        # Updating the Terminal Positions
        for cnt, handle in enumerate(comp_port_handles):
            if handle:
                mdl.set_port_properties(handle, terminal_position=port_attributes[comp_port_labels[cnt]]["term_pos"])

        if new_value == "On one side":
            # delete all downstream ports and short circuit the meter ports
            for cnt, handle in enumerate(comp_port_handles):
                if comp_port_handles[cnt]:
                    mdl.delete_item(comp_port_handles[cnt])
                    mdl.create_connection(meas_port_handles[cnt], meas_port_handles[cnt+3])
        else:
            # Create downstream ports depending on comp_type
            for cnt, action in enumerate(create_delete_ports):
                if not comp_port_handles[cnt] and action:
                    mdl.delete_item(mdl.find_connections(meas_port_handles[cnt+3])[0])
                    new_port = mdl.create_port(name=comp_port_labels[cnt],
                                               parent=comp_handle,
                                               kind="pe",
                                               direction="in",
                                               position=port_attributes[comp_port_labels[cnt]]["pos"],
                                               terminal_position=port_attributes[comp_port_labels[cnt]]["term_pos"],
                                               flip="flip_horizontal")
                    mdl.create_connection(meas_port_handles[cnt+3], new_port)

        # Updating the icon (not mandatory)
        mdl.refresh_icon(container_handle)
        # Measurements Check (mandatory)
        check_measurements(mdl, container_handle)

    # ------------------------------------------------------------------------------------------------------------------
    #  "type" property code
    # ------------------------------------------------------------------------------------------------------------------
    if caller_prop_handle == type_prop:
        conf = mdl.get_property_disp_value(conf_prop)
        # Component Vars
        comp_handle = mdl.get_parent(container_handle)
        comp_port_labels = ["A1", "B1", "C1", "A2", "B2", "C2", "GND"]
        comp_port_handles = [mdl.get_item(p_name, item_type="port", parent=comp_handle)
                             for p_name in comp_port_labels]
        # Three-Phase Meter Vars
        meas_handle = mdl.get_item("Measurements", parent=comp_handle)
        meas_port_labels = ["A+", "B+", "C+", "A-", "B-", "C-"]
        meas_port_handles = [mdl.get_item(p_name, item_type="terminal", parent=meas_handle)
                             for p_name in meas_port_labels]
        # Port Vars
        port_attributes = get_port_const_attributes(new_value)
        create_delete_ports = [phase in new_value for phase in ["A", "B", "C"]]

        # Updating the Terminal Positions
        for cnt, handle in enumerate(comp_port_handles):
            if handle:
                mdl.set_port_properties(handle, terminal_position=port_attributes[comp_port_labels[cnt]]["term_pos"])

        # Creating/Deleting Ports
        for cnt, action in enumerate(create_delete_ports):
            if action:
                # Upstream Logic
                if not comp_port_handles[cnt]:
                    new_port = mdl.create_port(name=comp_port_labels[cnt],
                                               parent=comp_handle,
                                               kind="pe",
                                               direction="in",
                                               position=port_attributes[comp_port_labels[cnt]]["pos"],
                                               terminal_position=port_attributes[comp_port_labels[cnt]]["term_pos"])
                    mdl.create_connection(new_port, meas_port_handles[cnt])
                # Downstream Logic
                if not comp_port_handles[cnt+3]:
                    if conf == "On both sides":
                        mdl.delete_item(mdl.find_connections(meas_port_handles[cnt+3])[0])
                        new_port = mdl.create_port(name=comp_port_labels[cnt+3],
                                                   parent=comp_handle,
                                                   kind="pe",
                                                   direction="in",
                                                   position=port_attributes[comp_port_labels[cnt+3]]["pos"],
                                                   terminal_position=port_attributes[comp_port_labels[cnt+3]]["term_pos"],
                                                   flip="flip_horizontal")
                        mdl.create_connection(meas_port_handles[cnt+3], new_port)

            else:
                # Upstream Logic
                if comp_port_handles[cnt]:
                    mdl.delete_item(comp_port_handles[cnt])
                # Downstream Logic
                if comp_port_handles[cnt+3]:
                    mdl.delete_item(comp_port_handles[cnt+3])
                    mdl.create_connection(meas_port_handles[cnt], meas_port_handles[cnt+3])

        # Updating the icon
        mdl.refresh_icon(container_handle)
        # Measurements Check
        check_measurements(mdl, container_handle)

    # ------------------------------------------------------------------------------------------------------------------
    #  "ground" property code
    # ------------------------------------------------------------------------------------------------------------------
    if caller_prop_handle == ground_prop:
        comp_handle = mdl.get_parent(container_handle)
        meas_handle = mdl.get_item("Measurements", parent=comp_handle)
        comp_type = mdl.get_property_disp_value(type_prop)
        port_attributes = get_port_const_attributes(comp_type)

        if new_value:
            new_port = mdl.create_port(name="GND",
                                       parent=comp_handle,
                                       label="0",
                                       position=port_attributes["GND"]["pos"],
                                       kind="pe",
                                       direction="in",
                                       terminal_position=port_attributes["GND"]["term_pos"],
                                       rotation="left")
            mdl.create_connection(new_port, mdl.term(meas_handle, "GND"))
        else:
            gnd_handle = mdl.get_item("GND", parent=comp_handle, item_type="port")
            if gnd_handle:
                mdl.delete_item(gnd_handle)

    # ------------------------------------------------------------------------------------------------------------------
    #  "Measurements" properties code
    # ------------------------------------------------------------------------------------------------------------------
    if caller_prop_handle in [i_rms_meas_prop, i_inst_meas_prop, v_line_rms_meas_prop, v_line_inst_meas_prop,
                              v_phase_rms_meas_prop, v_phase_inst_meas_prop, freq_meas_prop, power_meas_prop]:
        check_measurements(mdl, container_handle)


def mask_dialog_dynamics(mdl, container_handle, caller_prop_handle=None, init=False):
    """

    :param mdl:
    :param container_handle:
    :param caller_prop_handle:
    :param init:
    :return:
    """
    # Property Registration
    conf_prop = mdl.prop(container_handle, "conf")
    type_prop = mdl.prop(container_handle, "type")
    ground_prop = mdl.prop(container_handle, "ground")
    i_rms_meas_prop = mdl.prop(container_handle, "i_rms_meas")
    i_inst_meas_prop = mdl.prop(container_handle, "i_inst_meas")
    v_line_rms_meas_prop = mdl.prop(container_handle, "v_line_rms_meas")
    v_line_inst_meas_prop = mdl.prop(container_handle, "v_line_inst_meas")
    v_phase_rms_meas_prop = mdl.prop(container_handle, "v_phase_rms_meas")
    v_phase_inst_meas_prop = mdl.prop(container_handle, "v_phase_inst_meas")
    freq_meas_prop = mdl.prop(container_handle, "freq_meas")
    power_meas_prop = mdl.prop(container_handle, "power_meas")

    new_value = None

    if caller_prop_handle:
        new_value = mdl.get_property_disp_value(caller_prop_handle)

    # ------------------------------------------------------------------------------------------------------------------
    #  "conf" property code
    # ------------------------------------------------------------------------------------------------------------------
    if caller_prop_handle == conf_prop:

        comp_type = mdl.get_property_disp_value(type_prop)
        if new_value == "On one side":
            # Disable Current properties
            [mdl.set_property_disp_value(prop, False) for prop in [i_rms_meas_prop, i_inst_meas_prop,
                                                                   power_meas_prop]]
            [mdl.disable_property(prop) for prop in [i_rms_meas_prop, i_inst_meas_prop,
                                                     power_meas_prop]]
        else:
            # Enable Current Properties depending on component type
            [mdl.enable_property(prop) for prop in [i_inst_meas_prop]]
            if len(comp_type) == 3:
                [mdl.enable_property(prop) for prop in [i_rms_meas_prop, power_meas_prop]]

    # ------------------------------------------------------------------------------------------------------------------
    #  "type" property code
    # ------------------------------------------------------------------------------------------------------------------
    if caller_prop_handle == type_prop:

        if len(new_value) == 1:
            [mdl.set_property_disp_value(prop, True) for prop in [ground_prop]]
            [mdl.disable_property(prop) for prop in [ground_prop]]
        else:
            [mdl.enable_property(prop) for prop in [ground_prop]]

        """ There are some miss measurements depending on the comp_type
        if len(new_value) == 3:
            # Enable Line and rms properties
            [mdl.enable_property(prop) for prop in [v_line_inst_meas_prop, v_line_rms_meas_prop,
                                                    i_rms_meas_prop, power_meas_prop, freq_meas_prop, ground_prop]]
        else:
            # Disable Line and rms properties
            [mdl.set_property_disp_value(prop, False) for prop in [v_line_inst_meas_prop, v_line_rms_meas_prop,
                                                                   i_rms_meas_prop, power_meas_prop, freq_meas_prop,
                                                                   v_phase_rms_meas_prop]]
            [mdl.disable_property(prop) for prop in [v_line_inst_meas_prop, v_line_rms_meas_prop,
                                                     i_rms_meas_prop, power_meas_prop, freq_meas_prop,
                                                     v_phase_rms_meas_prop]]
            if len(new_value) == 1:
                [mdl.set_property_disp_value(prop, True) for prop in [ground_prop]]
                [mdl.disable_property(prop) for prop in [ground_prop]]
            else:
                [mdl.enable_property(prop) for prop in [ground_prop]]
        """


def define_icon(mdl, container_handle):
    """
    Defines the component icon based on its type

    :param mdl: Schematic API
    :param container_handle: Component Handle
    :return: no return
    """
    images = {
        "A": "images/bus_1ph.svg",
        "B": "images/bus_1ph.svg",
        "C": "images/bus_1ph.svg",
        "AB": "images/bus_2ph.svg",
        "AC": "images/bus_2ph.svg",
        "BC": "images/bus_2ph.svg",
        "ABC": "images/bus_3ph.svg"
    }

    comp_type = mdl.get_property_value(mdl.prop(container_handle, "type"))
    comp_handle = mdl.get_parent(container_handle)
    mask_handle = mdl.get_mask(comp_handle)
    mdl.set_component_icon_image(mask_handle, images[comp_type])


def get_port_const_attributes(comp_type):
    """

    """
    term_positions = []
    if comp_type == "ABC":
        term_positions = [(-8.0, -32.0), (8.0, -32.0), (-8.0, 0), (8.0, 0), (-8.0, 32.0), (8.0, 32.0)]
    elif comp_type == "AB":
        term_positions = [(-8.0, -16), (8.0, -16), (-8.0, 16), (8.0, 16), (0, 0), (0, 0)]
    elif comp_type == "AC":
        term_positions = [(-8.0, -16), (8.0, -16), (0, 0), (0, 0), (-8.0, 16), (8.0, 16)]
    elif comp_type == "BC":
        term_positions = [(0, 0), (0, 0), (-8.0, -16), (8.0, -16), (-8.0, 16), (8.0, 16)]
    elif comp_type == "A":
        term_positions = [(-8.0, 0), (8.0, 0), (0, 0), (0, 0), (0, 0), (0, 0)]
    elif comp_type == "B":
        term_positions = [(0, 0), (0, 0), (-8.0, 0), (8.0, 0), (0, 0), (0, 0)]
    elif comp_type == "C":
        term_positions = [(0, 0), (0, 0), (0, 0), (0, 0), (-8.0, 0), (8.0, 0)]

    port_dict = {"A1": {"pos": (7400, 7856), "term_pos": term_positions[0]},
                 "A2": {"pos": (7672, 7856), "term_pos": term_positions[1]},
                 "B1": {"pos": (7400, 7952), "term_pos": term_positions[2]},
                 "B2": {"pos": (7672, 7952), "term_pos": term_positions[3]},
                 "C1": {"pos": (7400, 8048), "term_pos": term_positions[4]},
                 "C2": {"pos": (7672, 8048), "term_pos": term_positions[5]},
                 "GND": {"pos": (7552, 8144), "term_pos": [0, 16*len(comp_type)]}}

    return port_dict


def check_measurements(mdl, container_handle):
    """

    """
    comp_handle = mdl.get_parent(container_handle)
    # Meter vars
    meter_handle = mdl.get_item("Measurements", parent=comp_handle)
    meter_props_dict = {"v_phase_inst_meas": ["VAn", "VBn", "VCn", "VN"],
                        "v_line_inst_meas": ["VAB", "VBC", "VCA"],
                        "i_inst_meas": ["IA", "IB", "IC", "IN"],
                        "freq_meas": ["freq"],
                        "v_phase_rms_meas": ["VLn_rms", "VLn_avg_rms", "VN_rms"],
                        "v_line_rms_meas": ["VLL_rms", "VLL_avg_rms"],
                        "i_rms_meas": ["I_rms", "I_avg_rms", "IN_rms"],
                        "power_meas": ["P_meas"]}
    # Component Props
    comp_type = mdl.get_property_disp_value(mdl.prop(container_handle, "type"))
    enabled_phase = [phase in comp_type for phase in ["A", "B", "C"]]
    comp_conf = mdl.get_property_disp_value(mdl.prop(container_handle, "conf"))

    # Enable the assigned properties
    # per phase props
    for cnt, action in enumerate(enabled_phase):
        if mdl.get_property_disp_value(mdl.prop(container_handle, "i_inst_meas")) is True:
            mdl.set_property_value(mdl.prop(meter_handle, meter_props_dict["i_inst_meas"][cnt]), action)
        if mdl.get_property_disp_value(mdl.prop(container_handle, "v_line_inst_meas")) is True:
            mdl.set_property_value(mdl.prop(meter_handle, meter_props_dict["v_line_inst_meas"][cnt]), action)
        if mdl.get_property_disp_value(mdl.prop(container_handle, "v_phase_inst_meas")) is True:
            mdl.set_property_value(mdl.prop(meter_handle, meter_props_dict["v_phase_inst_meas"][cnt]), action)

    # Three-Phase props (There are some miss measurements depending on comp_type)
    if mdl.get_property_disp_value(mdl.prop(container_handle, "i_rms_meas")) is True:
        mdl.set_property_value(mdl.prop(meter_handle, meter_props_dict["i_rms_meas"][0]), True)
    if mdl.get_property_disp_value(mdl.prop(container_handle, "v_line_rms_meas")) is True:
        mdl.set_property_value(mdl.prop(meter_handle, meter_props_dict["v_line_rms_meas"][0]), True)
    if mdl.get_property_disp_value(mdl.prop(container_handle, "v_phase_rms_meas")) is True:
        mdl.set_property_value(mdl.prop(meter_handle, meter_props_dict["v_phase_rms_meas"][0]), True)
    if mdl.get_property_disp_value(mdl.prop(container_handle, "freq_meas")) is True:
        mdl.set_property_value(mdl.prop(meter_handle, meter_props_dict["freq_meas"][0]), True)
    if mdl.get_property_disp_value(mdl.prop(container_handle, "power_meas")) is True:
        mdl.set_property_value(mdl.prop(meter_handle, meter_props_dict["power_meas"][0]), True)
