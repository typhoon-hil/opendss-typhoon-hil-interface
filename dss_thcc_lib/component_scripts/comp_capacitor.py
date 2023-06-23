import numpy as np

x0, y0 = (8192, 8192)


'''*******************************************************************
This function manages the mask properties 
If tp_connection == "Y - Grounded", the fields for Rneut and Xneut 
will be available.
https://youtu.be/Al3vXVe9WVU
*******************************************************************'''
def tp_connection_edited(mdl, mask_handle, new_value):
    rneut_prop = mdl.prop(mask_handle, "Rneut")
    xneut_prop = mdl.prop(mask_handle, "Xneut")

    #tp_connection_prop = mdl.prop(mask_handle, "tp_connection")
    #tp_connection = mdl.get_property_disp_value(tp_connection_prop)

    if new_value == "Y - Grounded":
        # Enable user input fields for N to Gnd impedance
        mdl.enable_property(mdl.prop(mask_handle, "Rneut"))
        mdl.enable_property(mdl.prop(mask_handle, "Xneut"))
        # We don't want to modify Rneut and Xneut user values
        # on the 'on change' event. We put zeros only when
        # the user commuted from "Y" or "Δ" to "Y - Grounded"
        if mdl.get_property_disp_value(rneut_prop) == "'inf'":
            mdl.set_property_value(rneut_prop, "0.0")
        if mdl.get_property_disp_value(xneut_prop) == "'inf'":
            mdl.set_property_value(xneut_prop, "0.0")
    else:
        # Disable user input fields for N to Gnd impedance
        # show 'inf' because they are disconnected
        mdl.set_property_disp_value(rneut_prop, "'inf'")
        mdl.set_property_disp_value(xneut_prop, "'inf'")
        mdl.disable_property(mdl.prop(mask_handle, "Rneut"))
        mdl.disable_property(mdl.prop(mask_handle, "Xneut"))



def calculate_c(mdl, mask_handle):
    tp_connection_prop = mdl.prop(mask_handle, "tp_connection")
    tp_connection = mdl.get_property_value(tp_connection_prop)
    phases_prop = mdl.prop(mask_handle, "phases")
    phases = mdl.get_property_value(phases_prop)

    v_correction = 1 if tp_connection == "Δ" else (1/(3**0.5))
    f = mdl.get_property_value(mdl.prop(mask_handle, "BaseFreq"))
    kvar = mdl.get_property_value(mdl.prop(mask_handle, "Kvar"))
    kv = mdl.get_property_value(mdl.prop(mask_handle, "Kv"))
    cap = (1 / (int(phases))) * kvar * 1000 / (2 * np.pi * f * (1000 * v_correction * kv) ** 2)

    mdl.set_property_value(mdl.prop(mask_handle, "C"), cap)


def recreate_capacitors(mdl, comp_handle):
    cap_a = mdl.get_item('Ca', parent=comp_handle)
    cap_b = mdl.get_item('Cb', parent=comp_handle)
    cap_c = mdl.get_item('Cc', parent=comp_handle)
    phases_prop = mdl.prop(comp_handle, "phases")
    phase_num = mdl.get_property_disp_value(phases_prop)

    if phase_num == "3":
        if not cap_a:
            cap_a = mdl.create_component("Capacitor", parent=comp_handle,
                                         name="Ca", position=(8111, 8095), rotation="down")
            mdl.set_property_value(mdl.prop(cap_a, "capacitance"), "C")
        if not cap_b:
            cap_b = mdl.create_component("Capacitor", parent=comp_handle,
                                         name="Cb", position=(8111, 8191), rotation="down")
            mdl.set_property_value(mdl.prop(cap_b, "capacitance"), "C")
        if not cap_c:
            cap_c = mdl.create_component("Capacitor", parent=comp_handle,
                                         name="Cc", position=(8111, 8287), rotation="down")
            mdl.set_property_value(mdl.prop(cap_c, "capacitance"), "C")
    elif phase_num == "2":
        if not cap_a:
            cap_a = mdl.create_component("Capacitor", parent=comp_handle,
                                         name="Ca", position=(8111, 8095), rotation="down")
            mdl.set_property_value(mdl.prop(cap_a, "capacitance"), "C")
        if not cap_b:
            cap_b = mdl.create_component("Capacitor", parent=comp_handle,
                                         name="Cb", position=(8111, 8191), rotation="down")
            mdl.set_property_value(mdl.prop(cap_b, "capacitance"), "C")
        if cap_c:
            mdl.delete_item(cap_c)
    elif phase_num == "1":
        if not cap_a:
            cap_a = mdl.create_component("Capacitor", parent=comp_handle,
                                         name="Ca", position=(8111, 8095), rotation="down")
            mdl.set_property_value(mdl.prop(cap_a, "capacitance"), "C")
        if cap_b:
            mdl.delete_item(cap_b)
        if cap_c:
            mdl.delete_item(cap_c)


def y_delta_connection(mdl, comp_handle, tp_connection, phases):
    cap_a = mdl.get_item('Ca', parent=comp_handle)
    cap_b = mdl.get_item('Cb', parent=comp_handle)
    cap_c = mdl.get_item('Cc', parent=comp_handle)
    delta_conn_1 = mdl.get_item('delta_conn_1', parent=comp_handle, item_type="connection")
    delta_conn_2 = mdl.get_item('delta_conn_2', parent=comp_handle, item_type="connection")
    b1_conn = mdl.get_item('b1_conn', parent=comp_handle, item_type="connection")
    b1 = mdl.get_item('B1', parent=comp_handle, item_type="port")
    c1 = mdl.get_item('C1', parent=comp_handle, item_type="port")
    gnd_z = mdl.get_item("Gnd Z", parent=comp_handle, item_type="component")

    if tp_connection != "Y - Grounded" and gnd_z:
        mdl.delete_item(gnd_z)

    if cap_c and c1:
        c1_conn_list = mdl.find_connections(c1, mdl.term(cap_c, "p_node"))
    else:
        c1_conn_list = []
    gndc = mdl.get_item("gndc", parent=comp_handle)

    if b1_conn:
        mdl.delete_item(b1_conn)

    if gndc:
        mdl.delete_item(gndc)

    junc = mdl.create_junction(name="j", parent=comp_handle, position=(x0 - 200, y0))
    if tp_connection == "Δ":
        delta_conn_1 = mdl.get_item('delta_conn_1', parent=comp_handle, item_type="connection")
        delta_conn_2 = mdl.get_item('delta_conn_2', parent=comp_handle, item_type="connection")
        if delta_conn_1:
            mdl.delete_item(delta_conn_1)
        if delta_conn_2:
            mdl.delete_item(delta_conn_2)
        mdl.create_connection(junc, mdl.term(cap_a, "n_node"))
        mdl.create_connection(junc, mdl.term(cap_c, "n_node"))
        mdl.create_connection(mdl.term(cap_a, "p_node"), mdl.term(cap_b, "n_node"), name="delta_conn_1")
        mdl.create_connection(mdl.term(cap_c, "p_node"), mdl.term(cap_b, "p_node"), name="delta_conn_2")
        mdl.create_connection(junc, b1, name="b1_conn")
        if len(c1_conn_list) == 0:
            mdl.create_connection(c1, mdl.term(cap_c, "p_node"))

    elif tp_connection == "Y" or tp_connection == "Y - Grounded":
        if delta_conn_1:
            mdl.delete_item(delta_conn_1)
        if delta_conn_2:
            mdl.delete_item(delta_conn_2)
        if len(c1_conn_list) > 0:
            for c1_conn in c1_conn_list:
                mdl.delete_item(c1_conn)

        if phases == "1":
            mdl.create_connection(junc, mdl.term(cap_a, "n_node"))
        else:
            mdl.create_connection(junc, mdl.term(cap_a, "n_node"))
            mdl.create_connection(junc, mdl.term(cap_b, "n_node"))
            mdl.create_connection(junc, mdl.term(cap_c, "n_node"))
            mdl.create_connection(b1, mdl.term(cap_b, "p_node"), name="b1_conn")
            mdl.create_connection(c1, mdl.term(cap_c, "p_node"), name="c1_conn")

    if phases != "2":
        n1 = mdl.get_item('N1', parent=comp_handle, item_type="port")
        if tp_connection == "Y - Grounded":
            gndc = mdl.get_item("gndc", parent=comp_handle)
            if not gndc:
                gndc = mdl.create_component("src_ground", parent=comp_handle, name="gndc", position=(7923, 8350))

            if not gnd_z:
                gnd_z = mdl.create_component("OpenDSS/Ground Impedance", parent=comp_handle, name="Gnd Z",
                                             position=(7923, 8265), rotation="up")

            if len(mdl.find_connections(junc, mdl.term(gnd_z, "N"))) == 0:
                mdl.create_connection(junc, mdl.term(gnd_z, "N"))
            if len(mdl.find_connections(mdl.term(gndc, "node"), mdl.term(gnd_z, "G"))) == 0:
                mdl.create_connection(mdl.term(gnd_z, "G"), mdl.term(gndc, "node"))

            if len(mdl.find_connections(junc, n1)) == 0:
                mdl.create_connection(junc, n1)

        elif tp_connection == "Y": # "Y - Neutral point accessible"
            if len(mdl.find_connections(junc, n1)) == 0:
                mdl.create_connection(junc, n1)
            if gndc:
                mdl.delete_item(gnd_c)


def redo_connections(mdl, mask_handle):
    comp_handle = mdl.get_parent(mask_handle)

    cap_a = mdl.get_item('Ca', parent=comp_handle)

    tp_connection_prop = mdl.prop(comp_handle, "tp_connection")
    tp_connection = mdl.get_property_disp_value(tp_connection_prop)

    phases_prop = mdl.prop(comp_handle, "phases")
    phases = mdl.get_property_disp_value(phases_prop)

    # delete_ports(mdl, comp_handle)
    gndc = mdl.get_item("gndc", parent=comp_handle)
    j = mdl.get_item('j', parent=comp_handle, item_type="junction")
    if j:
        mdl.delete_item(j)

    if gndc:
        mdl.delete_item(gndc)

    # redo_ports_primary(mdl, comp_handle)
    recreate_capacitors(mdl, comp_handle)

    if tp_connection == "In series":

        delta_conn_1 = mdl.get_item('delta_conn_1', parent=comp_handle, item_type="connection")
        delta_conn_2 = mdl.get_item('delta_conn_2', parent=comp_handle, item_type="connection")
        gnd_z = mdl.get_item("Gnd Z", parent=comp_handle, item_type="component")

        if gnd_z:
            mdl.delete_item(gnd_z)

        if delta_conn_1:
            mdl.delete_item(delta_conn_1)
        if delta_conn_2:
            mdl.delete_item(delta_conn_2)

        # create_bottom_ports(mdl, comp_handle)

        if phases == "1":
            a2 = mdl.get_item('A2', parent=comp_handle, item_type="port")
            mdl.create_connection(a2, mdl.term(cap_a, "n_node"))
        elif phases == "2":
            a2 = mdl.get_item('A2', parent=comp_handle, item_type="port")
            b2 = mdl.get_item('B2', parent=comp_handle, item_type="port")
            b1 = mdl.get_item('B1', parent=comp_handle, item_type="port")
            cap_b = mdl.get_item('Cb', parent=comp_handle)
            b1_conn = mdl.get_item('b1_conn', parent=comp_handle, item_type="connection")
            if not b1_conn:
                mdl.create_connection(b1, mdl.term(cap_b, "p_node"), name="b1_conn")

            mdl.create_connection(a2, mdl.term(cap_a, "n_node"))
            mdl.create_connection(b2, mdl.term(cap_b, "n_node"))
        else:
            a2 = mdl.get_item('A2', parent=comp_handle, item_type="port")
            b2 = mdl.get_item('B2', parent=comp_handle, item_type="port")
            c2 = mdl.get_item('C2', parent=comp_handle, item_type="port")
            b1 = mdl.get_item('B1', parent=comp_handle, item_type="port")
            c1 = mdl.get_item('C1', parent=comp_handle, item_type="port")
            cap_b = mdl.get_item('Cb', parent=comp_handle)
            cap_c = mdl.get_item('Cc', parent=comp_handle)
            b1_conn = mdl.get_item('b1_conn', parent=comp_handle, item_type="connection")
            if not b1_conn:
                mdl.create_connection(b1, mdl.term(cap_b, "p_node"), name="b1_conn")

            if len(mdl.find_connections(c1, mdl.term(cap_c, "p_node"))) == 0:
                mdl.create_connection(c1, mdl.term(cap_c, "p_node"))

            mdl.create_connection(a2, mdl.term(cap_a, "n_node"))
            mdl.create_connection(b2, mdl.term(cap_b, "n_node"))
            mdl.create_connection(c2, mdl.term(cap_c, "n_node"))

    else:
        y_delta_connection(mdl, comp_handle, tp_connection, phases)


def toggle_frequency_prop(mdl, mask_handle):
    frequency_prop = mdl.prop(mask_handle, "BaseFreq")
    global_frequency_prop = mdl.prop(mask_handle, "global_basefreq")
    use_global = mdl.get_property_disp_value(global_frequency_prop)

    if use_global:
        if "simdss_basefreq" in mdl.get_ns_vars():
            mdl.set_property_value(frequency_prop, mdl.get_ns_var("simdss_basefreq"))
            mdl.hide_property(frequency_prop)
        else:
            mdl.set_property_disp_value(global_frequency_prop, False)
            mdl.info("Add a SimDSS component to define the global frequency value.")
    else:
        mdl.show_property(frequency_prop)


def update_frequency_property(mdl, mask_handle, init=False):

    frequency_prop = mdl.prop(mask_handle, "BaseFreq")
    global_frequency_prop = mdl.prop(mask_handle, "global_basefreq")
    use_global = mdl.get_property_value(global_frequency_prop)

    if init:
        mdl.hide_property(frequency_prop)
    else:
        if use_global:
            if "simdss_basefreq" in mdl.get_ns_vars():
                mdl.set_property_value(frequency_prop, mdl.get_ns_var("simdss_basefreq"))
            else:
                mdl.set_property_value(global_frequency_prop, False)
        toggle_frequency_prop(mdl, mask_handle)


def port_dynamics(mdl, mask_handle, caller_prop_handle=None, init=False):
    comp_handle = mdl.get_parent(mask_handle)
    deleted_ports = []
    created_ports = {}

    phases_prop = mdl.prop(comp_handle, "phases")
    phases = int(mdl.get_property_disp_value(phases_prop))

    tp_connection_prop = mdl.prop(comp_handle, "tp_connection")
    tp_connection = mdl.get_property_disp_value(tp_connection_prop)

    # Delete ports

    a2 = mdl.get_item('A2', parent=comp_handle, item_type="port")
    b2 = mdl.get_item('B2', parent=comp_handle, item_type="port")
    c2 = mdl.get_item('C2', parent=comp_handle, item_type="port")
    n1 = mdl.get_item('N1', parent=comp_handle, item_type="port")

    if not (tp_connection == "In Series" and phases == 3):
        if c2:
            deleted_ports.append(mdl.get_name(c2))
            mdl.delete_item(c2)
    if not (tp_connection == "In Series" and phases >= 2):
        if b2:
            deleted_ports.append(mdl.get_name(b2))
            mdl.delete_item(b2)
    if tp_connection != "In Series":
        if a2:
            deleted_ports.append(mdl.get_name(a2))
            mdl.delete_item(a2)
    if tp_connection != "Y - Grounded" and tp_connection != "Y": #"Y - Neutral point accessible":
        if n1:
            deleted_ports.append(mdl.get_name(n1))
            mdl.delete_item(n1)

    # Redo ports primary
    b1 = mdl.get_item('B1', parent=comp_handle, item_type="port")
    c1 = mdl.get_item('C1', parent=comp_handle, item_type="port")

    if phases >= 2:
        if not b1:
            b1 = mdl.create_port(
                name="B1",
                parent=comp_handle,
                kind="pe",
                terminal_position=("top", "center"),
                position=(x0 + 200, y0),
                rotation="down"
            )
            created_ports.update({"B1": b1})
    if phases >= 3:
        if not c1:
            c1 = mdl.create_port(
                name="C1",
                parent=comp_handle,
                kind="pe",
                terminal_position=("top", "right"),
                position=(x0 + 200, y0 + 100),
                rotation="down"
            )
            created_ports.update({"C1": c1})

    if phases < 3:
        if c1:
            deleted_ports.append(mdl.get_name(c1))
            mdl.delete_item(c1)
    if phases < 2:
        if b1:
            deleted_ports.append(mdl.get_name(b1))
            mdl.delete_item(b1)

    if tp_connection == "Y" or tp_connection == "Y - Grounded": #"Y - Neutral point accessible":
        if not n1:
            n1 = mdl.create_port(
                name="N1",
                parent=comp_handle,
                kind="pe",
                terminal_position=("bottom", "center"),
                position=(x0 - 400, y0),
                rotation="up"
            )
            created_ports.update({"N1": n1})


    elif tp_connection == "In series":  # Create bottom ports

        a2 = mdl.create_port(
            name="A2",
            parent=comp_handle,
            kind="pe",
            terminal_position=(-32, 32),
            position=(x0 - 200, y0 - 100),
            rotation="up"
        )
        created_ports.update({"A2": a2})

        if phases >= 2:
            b2 = mdl.create_port(
                name="B2",
                parent=comp_handle,
                kind="pe",
                terminal_position=("bottom", "center"),
                position=(x0 - 200, y0),
                rotation="up"
            )
            created_ports.update({"B2": b2})
        if phases >= 3:
            c2 = mdl.create_port(
                name="C2",
                parent=comp_handle,
                kind="pe",
                terminal_position=(32, 32),
                position=(x0 - 200, y0 + 100),
                rotation="up"
            )
            created_ports.update({"C2": c2})

    if phases == 1:
        if tp_connection == "Y - Grounded":
            ports_dict = {"A1": (8, -32),
                          "A2": (8, 32),
                          "N1": (8, 32)}
        else:
            ports_dict = {"A1": (0, -32),
                          "A2": (0, 32),
                          "N1": (0, 32)}
    elif phases == 2:
        ports_dict = {"A1": (-16, -32),
                      "A2": (-16, 32),
                      "B1": (16, 32),
                      "B2": (16, -32)}
    else:
        if tp_connection == "Y" or tp_connection == "Y - Grounded": #"Y - Neutral point accessible":
            ports_dict = {"A1": (-48, -32),
                          "B1": (-16, -32),
                          "C1": (16, -32),
                          "N1": (48, -32)}
        else:
            ports_dict = {"A1": (-32, -32),
                          "A2": (-32, 32),
                          "B1": (0, -32),
                          "B2": (0, 32),
                          "C1": (32, -32),
                          "C2": (32, 32)}

    for port in ports_dict.keys():
        port_handle = mdl.get_item(port, parent=comp_handle, item_type="port")
        if port_handle:
            mdl.set_port_properties(port_handle, terminal_position=ports_dict[port])

    return created_ports, deleted_ports


def mask_dialog_dynamics(mdl, mask_handle, caller_prop_handle=None, init=False):

    if caller_prop_handle:

        new_value = mdl.get_property_disp_value(caller_prop_handle)

        if mdl.get_name(caller_prop_handle) == "phases":
            if new_value == "2":
                mdl.set_property_disp_value(mdl.prop(mask_handle, 'tp_connection'), "In series")
        elif mdl.get_name(caller_prop_handle) == "global_basefreq":
            toggle_frequency_prop(mdl, mask_handle)
        elif mdl.get_name(caller_prop_handle) == "tp_connection":
            if new_value == "Δ":
                mdl.set_property_disp_value(mdl.prop(mask_handle, 'phases'), "3")
                mdl.disable_property(mdl.prop(mask_handle, "phases"))
            else:
                mdl.enable_property(mdl.prop(mask_handle, "phases"))

            phases_num = mdl.get_property_disp_value(mdl.prop(mask_handle, "phases"))

            if phases_num == "2":
                if not new_value == "In series":
                    mdl.set_property_disp_value(mdl.prop(mask_handle, 'phases'), "3")


def define_icon(mdl, mask_handle):

    tp_connection_prop = mdl.prop(mask_handle, "tp_connection")
    tp_connection = mdl.get_property_disp_value(tp_connection_prop)
    phases_prop = mdl.prop(mask_handle, "phases")
    phases = mdl.get_property_disp_value(phases_prop)

    map_dict = {"Y": "Y - Neutral point accessible",
                "Y-grounded": "Y - Grounded",
                "Series": "In series",
                "Δ": "Δ"}

    if tp_connection in map_dict.keys():
        tp_connection = map_dict[tp_connection]

    filenames = {"1": {"In series": "cap_1S",
                       "Y - Grounded": "cap_1Yg",
                       "Y - Neutral point accessible": "cap_1S"},
                 "2": {"In series": "cap_2S"},
                 "3": {"In series": "cap_3S",
                       "Y - Grounded": "cap_3Yg",
                       "Y - Neutral point accessible": "cap_3Y",
                       "Δ": "cap_3D"},
                 }

    mdl.set_component_icon_image(mask_handle, f'images/{filenames[phases][tp_connection]}.svg')


def ensure_forward_compatibility(mdl, container_handle):
    map_dict = {"Y": "Y - Neutral point accessible",
                "Y-grounded": "Y - Grounded",
                "Series": "In series",
                "Δ": "Δ"}
    tp_connection = mdl.get_property_disp_value(mdl.prop(container_handle, "tp_connection"))
    if tp_connection in map_dict.keys():
        mdl.set_property_value(mdl.prop(container_handle, "tp_connection"), map_dict[tp_connection])
