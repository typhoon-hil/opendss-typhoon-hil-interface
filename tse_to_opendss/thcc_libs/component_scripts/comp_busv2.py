def v_meas_changed(mdl, mask_handle, v_meas_on, created_ports=None):
    """

    :param mdl:
    :param mask_handle:
    :param v_meas_on:
    :param created_ports:
    :return:
    """
    comp_handle = mdl.get_parent(mask_handle)
    phases = mdl.get_property_value(mdl.prop(mask_handle, "type"))

    j1a = mdl.get_item(name="Aj", parent=comp_handle, item_type="junction")
    j1b = mdl.get_item(name="Bj", parent=comp_handle, item_type="junction")
    j1c = mdl.get_item(name="Cj", parent=comp_handle, item_type="junction")

    for it in ["vAB_RMS", "vBC_RMS", "vCA_RMS", "verticalA", "verticalB", "verticalC"]:
        handle = mdl.get_item(it, parent=comp_handle)
        if handle:
            mdl.delete_item(handle)

    ja = mdl.get_item(name="jA_vmeas", parent=comp_handle)
    jab = mdl.get_item(name="jAB_vmeas", parent=comp_handle)
    jb = mdl.get_item(name="jB_vmeas", parent=comp_handle)

    if "A" in phases:
        mdl.create_connection(j1a, ja, name="verticalA")
    if "B" in phases:
        mdl.create_connection(j1b, jab, name="verticalB")
    if "C" in phases:
        mdl.create_connection(j1c, jb, name="verticalC")

    meas_dict = {}

    if v_meas_on == "True":
        comp_type = "Voltage RMS"
    else:
        comp_type = "el_open"

    if "AB" in phases:
        meas_dict["vAB_RMS"] = {"pos": (7564, 8200), "comp_type": comp_type, "j1": ja, "j2": jab}
    if "BC" in phases:
        meas_dict["vBC_RMS"] = {"pos": (7684, 8200), "comp_type": comp_type, "j1": jab, "j2": jb}
    if "ABC" in phases or "AC" in phases:
        meas_dict["vCA_RMS"] = {"pos": (7624, 8400), "comp_type": comp_type, "j1": jb, "j2": ja, "flip": "flip_horizontal"}

    for comp, props in meas_dict.items():
        new_meas = mdl.create_component(props.get("comp_type"),
                                        parent=comp_handle,
                                        name=comp,
                                        rotation=props.get("rot"),
                                        flip=props.get("flip"),
                                        position=(props.get("pos")[0], props.get("pos")[1])
                                        )
        mdl.create_connection(mdl.term(new_meas, "p_node"), props.get("j1"))
        mdl.create_connection(mdl.term(new_meas, "n_node"), props.get("j2"))


def i_meas_changed(mdl, mask_handle, i_meas_on, created_ports=None):
    """

    :param mdl:
    :param mask_handle:
    :param i_meas_on:
    :param created_ports:
    :return:
    """
    comp_handle = mdl.get_parent(mask_handle)
    phases = mdl.get_property_value(mdl.prop(mask_handle, "type"))

    j1a = mdl.get_item(name="Aj", parent=comp_handle)
    j1b = mdl.get_item(name="Bj", parent=comp_handle)
    j1c = mdl.get_item(name="Cj", parent=comp_handle)
    j2a = mdl.get_item(name="A_imeas_j", parent=comp_handle)
    j2b = mdl.get_item(name="B_imeas_j", parent=comp_handle)
    j2c = mdl.get_item(name="C_imeas_j", parent=comp_handle)

    for it in ["iA_RMS", "iB_RMS", "iC_RMS", "sc_imeas_A", "sc_imeas_B", "sc_imeas_C"]:
        handle = mdl.get_item(it, parent=comp_handle)
        if handle:
            mdl.delete_item(handle)

    if i_meas_on == "True":

        meas_dict = {
            f"iA_RMS": {"pos": (7792, 7856), "comp_type": "Current RMS", "j1": j1a, "j2": j2a},
            f"iB_RMS": {"pos": (7792, 7952), "comp_type": "Current RMS", "j1": j1b, "j2": j2b},
            f"iC_RMS": {"pos": (7792, 8048), "comp_type": "Current RMS", "j1": j1c, "j2": j2c}
        }

        for comp, props in meas_dict.items():
            new_meas = mdl.create_component(props.get("comp_type"),
                                            parent=comp_handle,
                                            name=comp,
                                            rotation=props.get("rot"),
                                            flip=props.get("flip"),
                                            position=(props.get("pos")[0], props.get("pos")[1])
                                            )
            mdl.create_connection(mdl.term(new_meas, "p_node"), props.get("j1"))
            mdl.create_connection(mdl.term(new_meas, "n_node"), props.get("j2"))

            # Create disabled if the phase is not available
            if "A" not in phases and props.get("j1") == j1a:
                mdl.disable_items(new_meas)
            elif "B" not in phases and props.get("j1") == j1b:
                mdl.disable_items(new_meas)
            elif "C" not in phases and props.get("j1") == j1c:
                mdl.disable_items(new_meas)

    else:
        if "A" in phases:
            mdl.create_connection(j1a, j2a, name="sc_imeas_A")
        if "B" in phases:
            mdl.create_connection(j1b, j2b, name="sc_imeas_B")
        if "C" in phases:
            mdl.create_connection(j1c, j2c, name="sc_imeas_C")


def circuit_dynamics(mdl, container_handle, caller_prop_handle=None, init=False):
    """

    :param mdl:
    :param container_handle:
    :param caller_prop_handle:
    :param init:
    :return:

    """
    conf_prop = mdl.prop(container_handle, "conf")
    type_prop = mdl.prop(container_handle, "type")
    ground_prop = mdl.prop(container_handle, "ground")
    i_rms_meas_prop = mdl.prop(container_handle, "i_rms_meas")
    i_inst_meas_prop = mdl.prop(container_handle, "i_inst_meas")
    v_line_rms_meas_prop = mdl.prop(container_handle, "v_line_rms_meas")
    v_line_inst_meas_prop = mdl.prop(container_handle, "v_line_inst_meas")
    v_phase_rms_meas_prop = mdl.prop(container_handle, "v_phase_rms_meas")
    v_phase_inst_meas_prop = mdl.prop(container_handle, "v_phase_inst_meas")

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
        # External Meters Vars - I'll remove it in future
        current_meas_handles = [mdl.get_item(name, parent=comp_handle) for name in ["iA_RMS", "iB_RMS", "iC_RMS"]]

        # Updating the Terminal Positions
        for cnt, handle in enumerate(comp_port_handles):
            if handle:
                mdl.set_port_properties(handle, terminal_position=port_attributes[comp_port_labels[cnt]]["term_pos"])

        if new_value == "On one side":
            # delete all downstream ports
            for cnt, handle in enumerate(comp_port_handles):
                if comp_port_handles[cnt]:
                    mdl.delete_item(comp_port_handles[cnt])
                    # TODO: Remove the external measurements
                    mdl.create_connection(meas_port_handles[cnt], mdl.term(current_meas_handles[cnt], "n_node"))
        else:
            # Create downstream ports depending on comp_type
            for cnt, action in enumerate(create_delete_ports):
                if not comp_port_handles[cnt] and action:
                    mdl.delete_item(mdl.find_connections(mdl.term(current_meas_handles[cnt], "n_node"))[0])
                    new_port = mdl.create_port(name=comp_port_labels[cnt],
                                               parent=comp_handle,
                                               kind="pe",
                                               direction="in",
                                               position=port_attributes[comp_port_labels[cnt]]["pos"],
                                               terminal_position=port_attributes[comp_port_labels[cnt]]["term_pos"],
                                               flip="flip_horizontal")
                    mdl.create_connection(mdl.term(current_meas_handles[cnt], "n_node"), new_port)

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
        # External Meters Vars - I'll remove it in future
        current_meas_handles = [mdl.get_item(name, parent=comp_handle) for name in ["iA_RMS", "iB_RMS", "iC_RMS"]]

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
                    # TODO: Remove the external measurements
                    mdl.create_connection(new_port, meas_port_handles[cnt])
                # Downstream Logic
                if not comp_port_handles[cnt+3]:
                    if conf == "On both sides":
                        mdl.delete_item(mdl.find_connections(mdl.term(current_meas_handles[cnt], "n_node"))[0])
                        new_port = mdl.create_port(name=comp_port_labels[cnt+3],
                                                   parent=comp_handle,
                                                   kind="pe",
                                                   direction="in",
                                                   position=port_attributes[comp_port_labels[cnt+3]]["pos"],
                                                   terminal_position=port_attributes[comp_port_labels[cnt+3]]["term_pos"],
                                                   flip="flip_horizontal")
                        mdl.create_connection(mdl.term(current_meas_handles[cnt], "n_node"), new_port)

            else:
                # Upstream Logic
                if comp_port_handles[cnt]:
                    mdl.delete_item(comp_port_handles[cnt])
                # Downstream Logic
                if comp_port_handles[cnt+3]:
                    mdl.delete_item(comp_port_handles[cnt+3])
                    # TODO: Remove the external rms meters from the schematic
                    mdl.create_connection(meas_port_handles[cnt], mdl.term(current_meas_handles[cnt], "n_node"))

        # Updating the icon
        mdl.refresh_icon(container_handle)

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
    #  "v_meas" property code
    # ------------------------------------------------------------------------------------------------------------------
    if caller_prop_handle == v_line_rms_meas_prop:
        mdl.info(new_value)

    # ------------------------------------------------------------------------------------------------------------------
    #  "i_meas" property code
    # ------------------------------------------------------------------------------------------------------------------
    if caller_prop_handle == i_rms_meas_prop:
        mdl.info(new_value)


def mask_dialog_dynamics(mdl, container_handle, caller_prop_handle=None, init=False):
    """

    :param mdl:
    :param container_handle:
    :param caller_prop_handle:
    :param init:
    :return:
    """
    conf_prop = mdl.prop(container_handle, "conf")
    type_prop = mdl.prop(container_handle, "type")
    ground_prop = mdl.prop(container_handle, "ground")
    v_meas_prop = mdl.prop(container_handle, "v_meas")
    i_meas_prop = mdl.prop(container_handle, "i_meas")

    phases = mdl.get_property_disp_value(type_prop)
    conf = mdl.get_property_disp_value(conf_prop)

    if conf == "on one side":
        mdl.set_property_disp_value(i_meas_prop, False)
        mdl.disable_property(i_meas_prop)
        mdl.set_property_disp_value(v_meas_prop, False)
        if len(phases) == 1:
            mdl.set_property_disp_value(v_meas_prop, False)
            mdl.set_property_disp_value(ground_prop, True)
            mdl.disable_property(v_meas_prop)
            mdl.disable_property(ground_prop)
        else:
            mdl.enable_property(v_meas_prop)
            mdl.enable_property(ground_prop)
    else:
        mdl.enable_property(i_meas_prop)
        mdl.enable_property(v_meas_prop)
        mdl.enable_property(ground_prop)


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
                 "A2": {"pos": (7984, 7856), "term_pos": term_positions[1]},
                 "B1": {"pos": (7400, 7952), "term_pos": term_positions[2]},
                 "B2": {"pos": (7984, 7952), "term_pos": term_positions[3]},
                 "C1": {"pos": (7400, 8048), "term_pos": term_positions[4]},
                 "C2": {"pos": (7984, 8048), "term_pos": term_positions[5]},
                 "GND": {"pos": (7552, 8144), "term_pos": [0, 16*len(comp_type)]}}

    return port_dict


def check_measurements(mdl, container_handle):
    """

    """
    comp_handle = mdl.get_parent(container_handle)

    comp_type = mdl.get_property_disp_value(mdl.prop(container_handle, "type"))
    comp_conf = mdl.get_property_disp_value(mdl.prop(container_handle, "conf"))

    phase_voltage_inst_names = ["VAn", "VBn", "VCn"]
    phase_voltage_rms_names = ["VAn", "VBn", "VCn"]
