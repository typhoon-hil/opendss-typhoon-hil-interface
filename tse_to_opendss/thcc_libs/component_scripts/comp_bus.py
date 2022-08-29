def v_meas_changed(mdl, mask_handle, v_meas_on, created_ports=None):
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

def type_value_changed(mdl, mask_handle, new_type, created_ports=None):
    comp_handle = mdl.get_parent(mask_handle)
    conf = mdl.get_property_value(mdl.prop(mask_handle, "conf"))

    j1a = mdl.get_item(name="Aj", parent=comp_handle)
    j1b = mdl.get_item(name="Bj", parent=comp_handle)
    j1c = mdl.get_item(name="Cj", parent=comp_handle)
    j2a = mdl.get_item(name="A_imeas_j", parent=comp_handle)
    j2b = mdl.get_item(name="B_imeas_j", parent=comp_handle)
    j2c = mdl.get_item(name="C_imeas_j", parent=comp_handle)

    if new_type == "ABC":
        term_positions = [(-8.0, -32.0), (8.0, -32.0), (-8.0, 0), (8.0, 0), (-8.0, 32.0), (8.0, 32.0)]
    elif new_type == "AB":
        term_positions = [(-8.0, -16), (8.0, -16), (-8.0, 16), (8.0, 16), (0, 0), (0, 0)]
    elif new_type == "AC":
        term_positions = [(-8.0, -16), (8.0, -16), (0, 0), (0, 0), (-8.0, 16), (8.0, 16)]
    elif new_type == "BC":
        term_positions = [(0, 0), (0, 0), (-8.0, -16), (8.0, -16), (-8.0, 16), (8.0, 16)]
    elif new_type == "A":
        term_positions = [(-8.0, 0), (8.0, 0), (0, 0), (0, 0), (0, 0), (0, 0)]
    elif new_type == "B":
        term_positions = [(0, 0), (0, 0), (-8.0, 0), (8.0, 0), (0, 0), (0, 0)]
    elif new_type == "C":
        term_positions = [(0, 0), (0, 0), (0, 0), (0, 0), (-8.0, 0), (8.0, 0)]
    #
    port_dict = {
        f"A1": {"pos": (7400, 7856), "j1": j1a, "rotation": "up", "terminal_position": term_positions[0]},
        f"A2": {"pos": (7900, 7856), "j1": j2a, "rotation": "down", "terminal_position": term_positions[1]},
        f"B1": {"pos": (7400, 7952), "j1": j1b, "rotation": "up", "terminal_position": term_positions[2]},
        f"B2": {"pos": (7900, 7952), "j1": j2b, "rotation": "down", "terminal_position": term_positions[3]},
        f"C1": {"pos": (7400, 8048), "j1": j1c, "rotation": "up", "terminal_position": term_positions[4]},
        f"C2": {"pos": (7900, 8048), "j1": j2c, "rotation": "down", "terminal_position": term_positions[5]}
    }

    disable_items = []

    if "A" not in new_type:
        disable_items.extend(["iA_RMS", "ShortCircuitA"])
    if "B" not in new_type:
        disable_items.extend(["iB_RMS", "ShortCircuitB"])
    if "C" not in new_type:
        disable_items.extend(["iC_RMS", "ShortCircuitC"])

    for it in disable_items:
        handle = mdl.get_item(it, parent=comp_handle)
        if handle:
            mdl.disable_items(handle)

    # Restore

    create_ports = []
    enable_items = []

    if "A" in new_type:
        create_ports.append("A1")
        if conf == "on both sides":
            create_ports.append("A2")
        enable_items.extend(["iA_RMS"])
    if "B" in new_type:
        create_ports.append("B1")
        if conf == "on both sides":
            create_ports.append("B2")
        enable_items.extend(["iB_RMS"])
    if "C" in new_type:
        create_ports.append("C1")
        if conf == "on both sides":
            create_ports.append("C2")
        enable_items.extend(["iC_RMS"])

    for p in create_ports:
        # handle = mdl.get_item(p, parent=comp_handle, item_type="port")
        # if not handle:
        new_port = created_ports.get(p)
        mdl.create_connection(new_port, port_dict.get(p).get("j1"))
    for it in enable_items:
        handle = mdl.get_item(it, parent=comp_handle)
        if handle:
            mdl.enable_items(handle)

    v_meas = mdl.get_property_value(mdl.prop(mask_handle, "v_meas"))
    v_meas_changed(mdl, mask_handle, v_meas)
    i_meas = mdl.get_property_value(mdl.prop(mask_handle, "i_meas"))
    i_meas_changed(mdl, mask_handle, i_meas)

def ground_open_circuit(mdl, mask_handle, created_ports=None):
    comp_handle = mdl.get_parent(mask_handle)
    conf = mdl.get_property_disp_value(mdl.prop(mask_handle, "conf"))
    phases = mdl.get_property_disp_value(mdl.prop(mask_handle, "type"))
    ground = mdl.get_property_disp_value(mdl.prop(mask_handle, "ground"))

    gnd_oc = mdl.get_item("gnd_open", parent=comp_handle)
    if gnd_oc:
        mdl.delete_item(gnd_oc)

    ja = mdl.get_item(name="jA_vmeas", parent=comp_handle, item_type="junction")
    jab = mdl.get_item(name="jAB_vmeas", parent=comp_handle, item_type="junction")
    jb = mdl.get_item(name="jB_vmeas", parent=comp_handle, item_type="junction")

    if len(phases) == 1 and conf == "on one side":
        gnd = created_ports.get("0")
        gnd_oc = mdl.create_component("el_open",
                             parent=comp_handle,
                             name="gnd_open",
                             rotation="left",
                             position=(7624, 8250)
                             )
        mdl.create_connection(mdl.term(gnd_oc, "p_node"), gnd)
        if phases == "A":
            j = ja
        elif phases == "B":
            j = jab
        elif phases == "C":
            j = jb
        mdl.create_connection(mdl.term(gnd_oc, "n_node"), j)
    elif ground == "True" or ground is True:
        gnd_oc = mdl.create_component("el_open",
                             parent=comp_handle,
                             name="gnd_open",
                             rotation="left",
                             position=(7624, 8250)
                             )

        gnd = created_ports.get("0")

        mdl.create_connection(mdl.term(gnd_oc, "p_node"), gnd)
        if "B" in phases:
            j = jab
        elif "A" in phases:
            j = ja
        elif "C" in phases:
            j = jb
        mdl.create_connection(mdl.term(gnd_oc, "n_node"), j)

def port_dynamics(mdl, mask_handle, caller_prop_handle=None, init=False):
    comp_handle = mdl.get_parent(mask_handle)
    deleted_ports = []
    created_ports = {}

    prop_caller_name = mdl.get_name(caller_prop_handle)

    if prop_caller_name in ['type', 'conf']:
        conf = mdl.get_property_value(mdl.prop(mask_handle, "conf"))

        j1a = mdl.get_item(name="Aj", parent=comp_handle)
        j1b = mdl.get_item(name="Bj", parent=comp_handle)
        j1c = mdl.get_item(name="Cj", parent=comp_handle)
        j2a = mdl.get_item(name="A_imeas_j", parent=comp_handle)
        j2b = mdl.get_item(name="B_imeas_j", parent=comp_handle)
        j2c = mdl.get_item(name="C_imeas_j", parent=comp_handle)

        new_type = mdl.get_property_value(mdl.prop(mask_handle, "type"))

        if new_type == "ABC":
            term_positions = [(-8.0, -32.0), (8.0, -32.0), (-8.0, 0), (8.0, 0), (-8.0, 32.0), (8.0, 32.0)]
        elif new_type == "AB":
            term_positions = [(-8.0, -16), (8.0, -16), (-8.0, 16), (8.0, 16), (0, 0), (0, 0)]
        elif new_type == "AC":
            term_positions = [(-8.0, -16), (8.0, -16), (0, 0), (0, 0), (-8.0, 16), (8.0, 16)]
        elif new_type == "BC":
            term_positions = [(0, 0), (0, 0), (-8.0, -16), (8.0, -16), (-8.0, 16), (8.0, 16)]
        elif new_type == "A":
            term_positions = [(-8.0, 0), (8.0, 0), (0, 0), (0, 0), (0, 0), (0, 0)]
        elif new_type == "B":
            term_positions = [(0, 0), (0, 0), (-8.0, 0), (8.0, 0), (0, 0), (0, 0)]
        elif new_type == "C":
            term_positions = [(0, 0), (0, 0), (0, 0), (0, 0), (-8.0, 0), (8.0, 0)]

        port_dict = {
            f"A1": {"pos": (7400, 7856), "j1": j1a, "rotation": "up", "terminal_position": term_positions[0]},
            f"A2": {"pos": (7900, 7856), "j1": j2a, "rotation": "down", "terminal_position": term_positions[1]},
            f"B1": {"pos": (7400, 7952), "j1": j1b, "rotation": "up", "terminal_position": term_positions[2]},
            f"B2": {"pos": (7900, 7952), "j1": j2b, "rotation": "down", "terminal_position": term_positions[3]},
            f"C1": {"pos": (7400, 8048), "j1": j1c, "rotation": "up", "terminal_position": term_positions[4]},
            f"C2": {"pos": (7900, 8048), "j1": j2c, "rotation": "down", "terminal_position": term_positions[5]}
        }

        # Delete

        del_ports = ["A1", "A2", "B1", "B2", "C1", "C2"]
        for p in del_ports:
            handle = mdl.get_item(p, parent=comp_handle, item_type="port")
            if handle:
                deleted_ports.append(p)
                mdl.delete_item(handle)

        # Restore

        create_ports = []
        enable_items = []

        if "A" in new_type:
            create_ports.append("A1")
            if conf == "on both sides":
                create_ports.append("A2")
            enable_items.extend(["iA_RMS"])
        if "B" in new_type:
            create_ports.append("B1")
            if conf == "on both sides":
                create_ports.append("B2")
            enable_items.extend(["iB_RMS"])
        if "C" in new_type:
            create_ports.append("C1")
            if conf == "on both sides":
                create_ports.append("C2")
            enable_items.extend(["iC_RMS"])

        for p in create_ports:
            handle = mdl.get_item(p, parent=comp_handle, item_type="port")
            if not handle:
                new_port = mdl.create_port(name=p,
                                           parent=comp_handle,
                                           position=port_dict.get(p).get("pos"),
                                           terminal_position=port_dict.get(p).get("terminal_position"),
                                           rotation=port_dict.get(p).get("rotation")
                                           )
                created_ports.update({p: new_port})

    elif prop_caller_name == "ground":

        conf = mdl.get_property_disp_value(mdl.prop(mask_handle, "conf"))
        phases = mdl.get_property_disp_value(mdl.prop(mask_handle, "type"))
        ground = mdl.get_property_disp_value(mdl.prop(mask_handle, "ground"))

        gnd = mdl.get_item("0", parent=comp_handle, item_type="port")
        if gnd:
            deleted_ports.append("0")
            mdl.delete_item(gnd)

        if len(phases) == 1 and conf == "on one side":
            gnd = mdl.create_port(name="0",
                                  parent=comp_handle,
                                  position=(7624, 8300),
                                  terminal_position=(0, 8),
                                  rotation="left"
                                  )
            created_ports.update({"0": gnd})
        elif ground == "True" or ground is True:
            gnd = mdl.create_port(name="0",
                                  parent=comp_handle,
                                  position=(7624, 8300),
                                  terminal_position=(0, 16 * len(phases)),
                                  rotation="left"
                                  )
            created_ports.update({"0": gnd})

    return created_ports, deleted_ports

def mask_dialog_dynamics(mdl, mask_handle, caller_prop_handle=None, init=False):

    conf_prop = mdl.prop(mask_handle, "conf")
    type_prop = mdl.prop(mask_handle, "type")
    ground_prop = mdl.prop(mask_handle, "ground")
    v_meas_prop = mdl.prop(mask_handle, "v_meas")
    i_meas_prop = mdl.prop(mask_handle, "i_meas")

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

def define_icon(mdl, mask_handle):
    images = {
        "A": "images/bus_1ph.svg",
        "B": "images/bus_1ph.svg",
        "C": "images/bus_1ph.svg",
        "AB": "images/bus_2ph.svg",
        "AC": "images/bus_2ph.svg",
        "BC": "images/bus_2ph.svg",
        "ABC": "images/bus_3ph.svg"
    }
    type = mdl.get_property_value(mdl.prop(mask_handle, "type"))

    mdl.set_component_icon_image(mask_handle, images[type])


