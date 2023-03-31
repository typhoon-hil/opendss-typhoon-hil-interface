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
    type_prop = mdl.prop(container_handle, "type_prop")
    ground_prop = mdl.prop(container_handle, "ground_prop")
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
        # Short Circuit Vars
        sc_labels = ["SCA", "SCB", "SCC"]
        sc_handles = [mdl.get_item(p_name, parent=comp_handle) for p_name in sc_labels]
        sc_position = [mdl.get_position(handle) for handle in sc_handles]

        # Updating the Terminal Positions
        for cnt, handle in enumerate(comp_port_handles):
            if handle:
                mdl.set_port_properties(handle, terminal_position=port_attributes[comp_port_labels[cnt]]["term_pos"])

        if new_value == "on one side":
            # delete all downstream ports and short circuit the meter ports
            for cnt, handle in enumerate(comp_port_handles):
                if comp_port_handles[cnt]:
                    mdl.delete_item(comp_port_handles[cnt])
                    # Changing to OC to avoid bad voltage loops
                    mdl.delete_item(sc_handles[cnt])
                    new_sc = mdl.create_component("core/Open Circuit",
                                                  name=sc_labels[cnt],
                                                  parent=comp_handle,
                                                  position=sc_position[cnt])
                    mdl.create_connection(meas_port_handles[cnt], mdl.term(new_sc, "n_node"))
                    mdl.create_connection(mdl.term(new_sc, "p_node"), meas_port_handles[cnt + 3])
        else:
            # Create downstream ports depending on comp_type
            for cnt, action in enumerate(create_delete_ports):
                if not comp_port_handles[cnt] and action:
                    # mdl.delete_item(mdl.find_connections(mdl.term(sc_handles[cnt], "n_node"))[0])
                    # Changed SC to OC to avoid bad voltage loops / Returning to SC
                    mdl.delete_item(sc_handles[cnt])
                    new_sc = mdl.create_component("core/Short Circuit",
                                                  name=sc_labels[cnt],
                                                  parent=comp_handle,
                                                  position=sc_position[cnt])
                    new_port = mdl.create_port(name=comp_port_labels[cnt],
                                               parent=comp_handle,
                                               kind="pe",
                                               direction="in",
                                               position=port_attributes[comp_port_labels[cnt]]["pos"],
                                               terminal_position=port_attributes[comp_port_labels[cnt]]["term_pos"],
                                               flip="flip_horizontal")
                    mdl.create_connection(mdl.term(new_sc, "n_node"), new_port)
                    mdl.create_connection(mdl.term(new_sc, "p_node"), meas_port_handles[cnt + 3])

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
        comp_port_labels = ["A1", "B1", "C1", "A2", "B2", "C2", "GND", "OUT"]
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
        # Short Circuit Vars
        sc_labels = ["SCA", "SCB", "SCC"]
        sc_handles = [mdl.get_item(p_name, parent=comp_handle) for p_name in sc_labels]
        sc_position = [mdl.get_position(handle) for handle in sc_handles]

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
                    if conf == "on both sides":
                        mdl.delete_item(sc_handles[cnt])
                        # mdl.delete_item(mdl.find_connections(mdl.term(sc_handles[cnt], "n_node"))[0])
                        # Changed SC to OC to avoid bad voltage loops / Returning to SC
                        new_sc = mdl.create_component("core/Short Circuit",
                                                      name=sc_labels[cnt],
                                                      parent=comp_handle,
                                                      position=sc_position[cnt])

                        new_port = mdl.create_port(name=comp_port_labels[cnt+3],
                                                   parent=comp_handle,
                                                   kind="pe",
                                                   direction="in",
                                                   position=port_attributes[comp_port_labels[cnt+3]]["pos"],
                                                   terminal_position=port_attributes[comp_port_labels[cnt+3]]["term_pos"],
                                                   flip="flip_horizontal")
                        mdl.create_connection(mdl.term(new_sc, "n_node"), new_port)
                        mdl.create_connection(mdl.term(new_sc, "p_node"), meas_port_handles[cnt+3])

            else:
                # Upstream Logic
                if comp_port_handles[cnt]:
                    mdl.delete_item(comp_port_handles[cnt])
                # Downstream Logic
                if comp_port_handles[cnt+3]:
                    mdl.delete_item(comp_port_handles[cnt+3])
                    # Changing SC to OC to avoid bad voltage loops
                    mdl.delete_item(sc_handles[cnt])
                    new_sc = mdl.create_component("core/Open Circuit",
                                                  name=sc_labels[cnt],
                                                  parent=comp_handle,
                                                  position=sc_position[cnt])
                    mdl.create_connection(meas_port_handles[cnt], mdl.term(new_sc, "n_node"))
                    mdl.create_connection(mdl.term(new_sc, "p_node"), meas_port_handles[cnt+3])

        # Updating the icon
        mdl.refresh_icon(container_handle)
        # Measurements Check
        check_measurements(mdl, container_handle)

    # ------------------------------------------------------------------------------------------------------------------
    #  "ground" property code
    # ------------------------------------------------------------------------------------------------------------------
    if caller_prop_handle == ground_prop:
        comp_handle = mdl.get_parent(container_handle)
        junction = mdl.get_item("Junction_gnd", parent=comp_handle, item_type="junction")
        comp_type = mdl.get_property_disp_value(type_prop)
        port_attributes = get_port_const_attributes(comp_type)

        if new_value:
            gnd_oc = mdl.create_component("core/Open Circuit",
                                          name="GND_OC",
                                          parent=comp_handle,
                                          position=(7536, 8224),
                                          rotation="right")

            new_port = mdl.create_port(name="GND",
                                       parent=comp_handle,
                                       label="0",
                                       position=port_attributes["GND"]["pos"],
                                       kind="pe",
                                       direction="in",
                                       terminal_position=port_attributes["GND"]["term_pos"],
                                       rotation="left")
            mdl.create_connection(new_port, mdl.term(gnd_oc, "n_node"))
            mdl.create_connection(junction, mdl.term(gnd_oc, "p_node"))
        else:
            gnd_handle = mdl.get_item("GND", parent=comp_handle, item_type="port")
            if gnd_handle:
                mdl.delete_item(gnd_handle)
            gnd_oc = mdl.get_item("GND_OC", parent=comp_handle)
            if gnd_oc:
                mdl.delete_item(gnd_oc)

    # ------------------------------------------------------------------------------------------------------------------
    #  "Measurements" properties code
    # ------------------------------------------------------------------------------------------------------------------
    if caller_prop_handle in [i_rms_meas_prop, i_inst_meas_prop, v_line_rms_meas_prop, v_line_inst_meas_prop,
                              v_phase_rms_meas_prop, v_phase_inst_meas_prop, freq_meas_prop, power_meas_prop]:

        check_measurements(mdl, container_handle)

    # ------------------------------------------------------------------------------------------------------------------
    #  "enable_output_prop" property code
    # ------------------------------------------------------------------------------------------------------------------
    if caller_prop_handle == enable_output_prop:

        comp_handle = mdl.get_parent(container_handle)
        comp_type = mdl.get_property_disp_value(type_prop)
        port_attributes = get_port_const_attributes(comp_type)
        meas_handle = mdl.get_item("Measurements", parent=comp_handle)

        mdl.set_property_value(mdl.prop(meas_handle, "enable_out"), new_value)
        if new_value:
            new_port = mdl.create_port(name="OUT",
                                       parent=comp_handle,
                                       position=port_attributes["OUT"]["pos"],
                                       kind="sp",
                                       direction="out",
                                       terminal_position=port_attributes["OUT"]["term_pos"],
                                       rotation="left",
                                       hide_name=True)
            mdl.create_connection(mdl.term(meas_handle, "Out"), new_port)

        else:
            new_port = mdl.get_item("OUT", parent=comp_handle, item_type="port")
            if new_port:
                mdl.delete_item(new_port)


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
    type_prop = mdl.prop(container_handle, "type_prop")
    ground_prop = mdl.prop(container_handle, "ground_prop")
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
        if new_value == "on one side":
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
             for prop in [i_rms_meas_prop, i_inst_meas_prop, v_phase_rms_meas_prop, v_phase_inst_meas_prop,
                          freq_meas_prop]]
            if init:
                [mdl.set_property_value(prop, True)
                 for prop in [i_rms_meas_prop, i_inst_meas_prop, v_phase_rms_meas_prop, v_phase_inst_meas_prop,
                              freq_meas_prop]]
            [mdl.disable_property(prop)
             for prop in [i_rms_meas_prop, i_inst_meas_prop, v_phase_rms_meas_prop, v_phase_inst_meas_prop,
                          freq_meas_prop]]
        else:
            [mdl.enable_property(prop)
             for prop in [i_rms_meas_prop, v_phase_rms_meas_prop, freq_meas_prop]]


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

    comp_type = mdl.get_property_value(mdl.prop(container_handle, "type_prop"))
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
                 "A2": {"pos": (7792, 7856), "term_pos": term_positions[1]},
                 "B1": {"pos": (7400, 7952), "term_pos": term_positions[2]},
                 "B2": {"pos": (7792, 7952), "term_pos": term_positions[3]},
                 "C1": {"pos": (7400, 8048), "term_pos": term_positions[4]},
                 "C2": {"pos": (7792, 8048), "term_pos": term_positions[5]},
                 "GND": {"pos": (7536, 8320), "term_pos": [0, 16*len(comp_type)]},
                 "OUT": {"pos": (7536, 7760), "term_pos": [0, -16*len(comp_type)]}}

    return port_dict


def check_measurements(mdl, container_handle):
    """

    """
    comp_handle = mdl.get_parent(container_handle)
    # Meter vars
    meter_handle = mdl.get_item("Measurements", parent=comp_handle)
    meter_props_dict = {"v_phase_inst_meas": ["VAn", "VBn", "VCn"],  # "VN" Neutral Voltage not used for now
                        "v_line_inst_meas": ["VAB", "VBC", "VCA"],
                        "i_inst_meas": ["IA", "IB", "IC"],  # "IN" Neutral Current not used for now
                        "freq_meas": ["freq"],
                        "v_phase_rms_meas": ["VLn_rms", "VLn_avg_rms"],  # "VN_rms" Neutral Voltage not used for now
                        "v_line_rms_meas": ["VLL_rms", "VLL_avg_rms"],
                        "i_rms_meas": ["I_rms", "I_avg_rms"],  # "IN_rms" Neutral Voltage not used for now
                        "power_meas": ["P_meas"]}
    # Component Props
    comp_type = mdl.get_property_disp_value(mdl.prop(container_handle, "type_prop"))
    enabled_phase = [phase in comp_type for phase in ["A", "B", "C"]]
    comp_conf = mdl.get_property_disp_value(mdl.prop(container_handle, "conf"))

    # Enable/Disable the assigned properties
    # per phase props
    for cnt, action in enumerate(enabled_phase):
        i_inst = mdl.get_property_disp_value(mdl.prop(container_handle, "i_inst_meas"))
        mdl.set_property_value(mdl.prop(meter_handle, meter_props_dict["i_inst_meas"][cnt]), action and i_inst)

        v_line = mdl.get_property_disp_value(mdl.prop(container_handle, "v_line_inst_meas"))
        mdl.set_property_value(mdl.prop(meter_handle, meter_props_dict["v_line_inst_meas"][cnt]), action and v_line)

        v_phase = mdl.get_property_disp_value(mdl.prop(container_handle, "v_phase_inst_meas"))
        mdl.set_property_value(mdl.prop(meter_handle, meter_props_dict["v_phase_inst_meas"][cnt]), action and v_phase)

    # Three-Phase props (There are some miss measurements depending on comp_type)
    # Edit Handlers of the Meter is not called from external components (just GUI)
    i_rms_meas = mdl.get_property_disp_value(mdl.prop(container_handle, "i_rms_meas"))
    mdl.set_property_value(mdl.prop(meter_handle, meter_props_dict["i_rms_meas"][0]), i_rms_meas)
    if i_rms_meas:
        [mdl.set_property_value(mdl.prop(meter_handle, prop), True) for prop in meter_props_dict["i_inst_meas"]]

    v_line_rms_meas = mdl.get_property_disp_value(mdl.prop(container_handle, "v_line_rms_meas"))
    mdl.set_property_value(mdl.prop(meter_handle, meter_props_dict["v_line_rms_meas"][0]), v_line_rms_meas)
    if v_line_rms_meas:
        [mdl.set_property_value(mdl.prop(meter_handle, prop), True) for prop in meter_props_dict["v_line_inst_meas"]]

    v_phase_rms_meas = mdl.get_property_disp_value(mdl.prop(container_handle, "v_phase_rms_meas"))
    mdl.set_property_value(mdl.prop(meter_handle, meter_props_dict["v_phase_rms_meas"][0]), v_phase_rms_meas)
    if v_phase_rms_meas:
        [mdl.set_property_value(mdl.prop(meter_handle, prop), True) for prop in meter_props_dict["v_phase_inst_meas"]]

    freq_meas = mdl.get_property_disp_value(mdl.prop(container_handle, "freq_meas"))
    mdl.set_property_value(mdl.prop(meter_handle, meter_props_dict["freq_meas"][0]), freq_meas)

    power_meas = mdl.get_property_disp_value(mdl.prop(container_handle, "power_meas"))
    mdl.set_property_value(mdl.prop(meter_handle, meter_props_dict["power_meas"][0]), power_meas)
    # RMS calculation needs all instantaneous measurements (and frequency/voltage)
    if i_rms_meas or v_line_rms_meas or v_phase_rms_meas or freq_meas or power_meas:
        mdl.set_property_value(mdl.prop(meter_handle, meter_props_dict["freq_meas"][0]), True)
        [mdl.set_property_value(mdl.prop(meter_handle, prop), True) for prop in meter_props_dict["v_phase_inst_meas"]]
