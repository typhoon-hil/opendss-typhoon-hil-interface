import numpy as np

x0, y0 = (8192, 8192)


def calculate_l(mdl, mask_handle):
    tp_connection_prop = mdl.prop(mask_handle, "tp_connection")
    tp_connection = mdl.get_property_value(tp_connection_prop)
    phases_prop = mdl.prop(mask_handle, "phases")
    phases = mdl.get_property_value(phases_prop)

    v_correction = 1 if tp_connection == "Δ" else (1/(3**0.5))
    f = mdl.get_property_value(mdl.prop(mask_handle, "baseFreq"))
    kvar = mdl.get_property_value(mdl.prop(mask_handle, "Kvar"))
    kv = mdl.get_property_value(mdl.prop(mask_handle, "Kv"))
    inductor = int(phases) * ((1000 * v_correction * kv) ** 2) / (2 * np.pi * f * kvar * 1000)

    mdl.set_property_value(mdl.prop(mask_handle, "L"), inductor)


def recreate_inductors(mdl, comp_handle):
    ind_a = mdl.get_item('La', parent=comp_handle)
    ind_b = mdl.get_item('Lb', parent=comp_handle)
    ind_c = mdl.get_item('Lc', parent=comp_handle)
    phases_prop = mdl.prop(comp_handle, "phases")
    phase_num = mdl.get_property_disp_value(phases_prop)

    if phase_num == "3":
        if not ind_a:
            ind_a = mdl.create_component("Inductor", parent=comp_handle,
                                         name="La", position=(8111, 8095), rotation="down")
            mdl.set_property_value(mdl.prop(ind_a, "inductance"), "L")
        if not ind_b:
            ind_b = mdl.create_component("Inductor", parent=comp_handle,
                                         name="Lb", position=(8111, 8191), rotation="down")
            mdl.set_property_value(mdl.prop(ind_b, "inductance"), "L")
        if not ind_c:
            ind_c = mdl.create_component("Inductor", parent=comp_handle,
                                         name="Lc", position=(8111, 8287), rotation="down")
            mdl.set_property_value(mdl.prop(ind_c, "inductance"), "L")
    elif phase_num == "2":
        if not ind_a:
            ind_a = mdl.create_component("Capacitor", parent=comp_handle,
                                         name="Ca", position=(8111, 8095), rotation="down")
            mdl.set_property_value(mdl.prop(ind_a, "capacitance"), "C")
        if not ind_b:
            ind_b = mdl.create_component("Capacitor", parent=comp_handle,
                                         name="Cb", position=(8111, 8191), rotation="down")
            mdl.set_property_value(mdl.prop(ind_b, "capacitance"), "C")
        if ind_c:
            mdl.delete_item(ind_c)
    elif phase_num == "1":
        if not ind_a:
            ind_a = mdl.create_component("Capacitor", parent=comp_handle,
                                         name="Ca", position=(8111, 8095), rotation="down")
            mdl.set_property_value(mdl.prop(ind_a, "capacitance"), "C")
        if ind_b:
            mdl.delete_item(ind_b)
        if ind_c:
            mdl.delete_item(ind_c)


def y_delta_connection(mdl, comp_handle, tp_connection, phases):
    ind_a = mdl.get_item('La', parent=comp_handle)
    ind_b = mdl.get_item('Lb', parent=comp_handle)
    ind_c = mdl.get_item('Lc', parent=comp_handle)
    delta_conn_1 = mdl.get_item('delta_conn_1', parent=comp_handle, item_type="connection")
    delta_conn_2 = mdl.get_item('delta_conn_2', parent=comp_handle, item_type="connection")
    b1_conn = mdl.get_item('b1_conn', parent=comp_handle, item_type="connection")
    b1 = mdl.get_item('B1', parent=comp_handle, item_type="port")
    c1 = mdl.get_item('C1', parent=comp_handle, item_type="port")

    if ind_c and c1:
        c1_conn_list = mdl.find_connections(c1, mdl.term(ind_c, "p_node"))
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
        mdl.create_connection(junc, mdl.term(ind_a, "n_node"))
        mdl.create_connection(junc, mdl.term(ind_c, "n_node"))
        mdl.create_connection(mdl.term(ind_a, "p_node"), mdl.term(ind_b, "n_node"), name="delta_conn_1")
        mdl.create_connection(mdl.term(ind_c, "p_node"), mdl.term(ind_b, "p_node"), name="delta_conn_2")
        mdl.create_connection(junc, b1, name="b1_conn")
        if len(c1_conn_list) == 0:
            mdl.create_connection(c1, mdl.term(ind_c, "p_node"))

    elif tp_connection == "Y" or tp_connection == "Y - Grounded":
        if delta_conn_1:
            mdl.delete_item(delta_conn_1)
        if delta_conn_2:
            mdl.delete_item(delta_conn_2)
        if len(c1_conn_list) > 0:
            for c1_conn in c1_conn_list:
                mdl.delete_item(c1_conn)

        if phases == "1":
            mdl.create_connection(junc, mdl.term(ind_a, "n_node"))
        else:
            mdl.create_connection(junc, mdl.term(ind_a, "n_node"))
            mdl.create_connection(junc, mdl.term(ind_b, "n_node"))
            mdl.create_connection(junc, mdl.term(ind_c, "n_node"))
            mdl.create_connection(b1, mdl.term(ind_b, "p_node"), name="b1_conn")
            mdl.create_connection(c1, mdl.term(ind_c, "p_node"), name="c1_conn")

    if phases != "2":
        n1 = mdl.get_item('N1', parent=comp_handle, item_type="port")
        gndc = mdl.get_item("gndc", parent=comp_handle)
        if tp_connection == "Y - Grounded":
            if not gndc:
                gndc = mdl.create_component("src_ground", parent=comp_handle, name="gndc", position=(7923, 8350))
                j = mdl.get_item('j', parent=comp_handle, item_type="junction")
                mdl.create_connection(j, mdl.term(gndc, "node"))

            if len(mdl.find_connections(junc, n1)) == 0:
                mdl.create_connection(junc, n1)

        elif tp_connection == "Y": # "Y - Neutral point accessible"
            if len(mdl.find_connections(junc, n1)) == 0:
                mdl.create_connection(junc, n1)
            if gndc:
                mdl.delete_item(gndc)


def redo_connections(mdl, mask_handle):
    comp_handle = mdl.get_parent(mask_handle)

    ind_a = mdl.get_item('La', parent=comp_handle)

    tp_connection_prop = mdl.prop(comp_handle, "tp_connection")
    tp_connection = mdl.get_property_disp_value(tp_connection_prop)

    phases_prop = mdl.prop(comp_handle, "phases")
    phases = mdl.get_property_disp_value(phases_prop)

    gndc = mdl.get_item("gndc", parent=comp_handle)
    j = mdl.get_item('j', parent=comp_handle, item_type="junction")
    if j:
        mdl.delete_item(j)

    if gndc:
        mdl.delete_item(gndc)

    recreate_inductors(mdl, comp_handle)

    if tp_connection == "In series":

        delta_conn_1 = mdl.get_item('delta_conn_1', parent=comp_handle, item_type="connection")
        delta_conn_2 = mdl.get_item('delta_conn_2', parent=comp_handle, item_type="connection")

        if delta_conn_1:
            mdl.delete_item(delta_conn_1)
        if delta_conn_2:
            mdl.delete_item(delta_conn_2)

        if phases == "1":
            a2 = mdl.get_item('A2', parent=comp_handle, item_type="port")
            if not mdl.get_connected_items(a2):
                mdl.create_connection(a2, mdl.term(ind_a, "n_node"))
        elif phases == "2":
            a2 = mdl.get_item('A2', parent=comp_handle, item_type="port")
            b2 = mdl.get_item('B2', parent=comp_handle, item_type="port")
            b1 = mdl.get_item('B1', parent=comp_handle, item_type="port")
            ind_b = mdl.get_item('Lb', parent=comp_handle)
            b1_conn = mdl.get_item('b1_conn', parent=comp_handle, item_type="connection")
            if not b1_conn:
                mdl.create_connection(b1, mdl.term(ind_b, "p_node"), name="b1_conn")

            if not mdl.get_connected_items(a2):
                mdl.create_connection(a2, mdl.term(ind_a, "n_node"))
            if not mdl.get_connected_items(b2):
                mdl.create_connection(b2, mdl.term(ind_b, "n_node"))
        else:
            a2 = mdl.get_item('A2', parent=comp_handle, item_type="port")
            b2 = mdl.get_item('B2', parent=comp_handle, item_type="port")
            c2 = mdl.get_item('C2', parent=comp_handle, item_type="port")
            b1 = mdl.get_item('B1', parent=comp_handle, item_type="port")
            c1 = mdl.get_item('C1', parent=comp_handle, item_type="port")
            ind_b = mdl.get_item('Lb', parent=comp_handle)
            ind_c = mdl.get_item('Lc', parent=comp_handle)
            b1_conn = mdl.get_item('b1_conn', parent=comp_handle, item_type="connection")
            if not b1_conn:
                mdl.create_connection(b1, mdl.term(ind_b, "p_node"), name="b1_conn")

            if not mdl.find_connections(c1, mdl.term(ind_c, "p_node")):
                mdl.create_connection(c1, mdl.term(ind_c, "p_node"))

            if not mdl.get_connected_items(a2):
                mdl.create_connection(a2, mdl.term(ind_a, "n_node"))
            if not mdl.get_connected_items(b2):
                mdl.create_connection(b2, mdl.term(ind_b, "n_node"))
            if not mdl.get_connected_items(c2):
                mdl.create_connection(c2, mdl.term(ind_c, "n_node"))

    else:
        y_delta_connection(mdl, comp_handle, tp_connection, phases)


def toggle_frequency_prop(mdl, mask_handle):
    frequency_prop = mdl.prop(mask_handle, "baseFreq")
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

    frequency_prop = mdl.prop(mask_handle, "baseFreq")
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


def delete_port(mdl, name, parent):
    comp = mdl.get_item(name, parent=parent, item_type="port")
    if comp:
        mdl.delete_item(comp)
        return True


def delete_unused_ports(mdl, comp_handle, new_ports, current_ports):
    deleted_ports = []

    all_new_ports = [port for side in new_ports for port in new_ports[side]]
    for port_name in current_ports:
        if port_name not in all_new_ports:
            if delete_port(mdl, name=port_name, parent=comp_handle):
                deleted_ports.append(port_name)

    return deleted_ports


def port_dynamics(mdl, mask_handle, caller_prop_handle=None, init=False):
    comp_handle = mdl.get_parent(mask_handle)
    deleted_ports = []
    created_ports = {}

    phases_prop = mdl.prop(comp_handle, "phases")
    phases = int(mdl.get_property_disp_value(phases_prop))

    tp_connection_prop = mdl.prop(comp_handle, "tp_connection")
    tp_connection = mdl.get_property_disp_value(tp_connection_prop)

    # Get current ports
    current_ports = {mdl.get_name(port): port for port in mdl.get_items(parent=comp_handle, item_type="port")}

    #
    # New ports for the selected configuration
    #

    side_ports = {}
    if tp_connection == "In series":
        phase_chars = "ABC"[:phases]
        side_ports.update({1: [f"{phase}1" for phase in phase_chars]})
        side_ports.update({2: [f"{phase}2" for phase in phase_chars]})
    elif tp_connection == "Y":
        phase_chars = "ABC"[:phases] + "N"
        side_ports.update({1: [f"{phase}1" for phase in phase_chars]})
    elif tp_connection == "Y - Grounded":
        phase_chars = "ABC"[:phases]
        side_ports.update({1: [f"{phase}1" for phase in phase_chars]})
    else:
        side_ports.update({1: [f"{phase}1" for phase in "ABC"]})

    # Delete unused ports
    deleted_ports = delete_unused_ports(mdl, comp_handle, side_ports, current_ports)

    # Create missing ports
    for side, port_list in side_ports.items():
        for idx, port in enumerate(port_list):
            port_handle = mdl.get_item(port, parent=comp_handle, item_type="port")

            if port.startswith("N"):
                port_pos = (x0 - 400, y0)
                rotation = "up"
            else:
                port_pos = (x0 + 200 - ((side == 2) * 500), y0 - 100 + (100 * idx))
                rotation = "down" if side == 1 else "up"

            if not port_handle:
                port_handle = mdl.create_port(
                    name=port,
                    parent=comp_handle,
                    kind="pe",
                    hide_name=True,
                    position=port_pos,
                    rotation=rotation
                )
            created_ports.update({port: port_handle})

    #
    # Set terminal positions
    #
    if tp_connection == "In series":
        terminal_positions = {port_name: (-32 if side == 1 else 32,
                                          - 16 * (phases - 1) + port_list.index(port_name) * 32)
                              for side, port_list in side_ports.items() for port_name in port_list}
    elif tp_connection == "Y":
        if phases == 1:
            terminal_positions = {"A1": (-16, -32), "N1": (16, -32)}
        else:
            terminal_positions = {port_name: (-48 + 32 * port_list.index(port_name), -32)
                              for port_list in side_ports.values() for port_name in port_list}
    elif tp_connection in ("Δ", "Y - Grounded"):
        if phases == 1:
            terminal_positions = {"A1": (0, -32)}
        else:
            terminal_positions = {"A1": (-32, -32), "B1": (0, -32), "C1": (32, -32)}

    for port, position in terminal_positions.items():
        port_handle = mdl.get_item(port, parent=comp_handle, item_type="port")
        if port_handle:
            mdl.set_port_properties(port_handle, terminal_position=position)

    return created_ports, deleted_ports


def mask_dialog_dynamics(mdl, mask_handle, caller_prop_handle=None, init=False):

    if caller_prop_handle:

        new_value = mdl.get_property_disp_value(caller_prop_handle)

        phases_num = mdl.get_property_disp_value(mdl.prop(mask_handle, "phases"))
        tp_connection_prop = mdl.prop(mask_handle, 'tp_connection')
        tp_connection = mdl.get_property_disp_value(tp_connection_prop)

        if mdl.get_name(caller_prop_handle) == "phases":
            if new_value == "2":
                mdl.set_property_disp_value(tp_connection_prop, "In series")
            elif new_value == "1" and tp_connection == "Y":
                mdl.set_property_disp_value(tp_connection_prop, "In series")
        elif mdl.get_name(caller_prop_handle) == "global_basefreq":
            toggle_frequency_prop(mdl, mask_handle)
        elif mdl.get_name(caller_prop_handle) == "tp_connection":
            if new_value == "Δ":
                mdl.set_property_disp_value(mdl.prop(mask_handle, 'phases'), "3")
                mdl.disable_property(mdl.prop(mask_handle, "phases"))
            else:
                mdl.enable_property(mdl.prop(mask_handle, "phases"))
                if new_value == "Y" and phases_num == "1":
                    mdl.set_property_disp_value(mdl.prop(mask_handle, 'phases'), "3")

            if phases_num == "2":
                if not new_value == "In series":
                    mdl.set_property_disp_value(mdl.prop(mask_handle, 'phases'), "3")


def define_icon(mdl, mask_handle):

    tp_connection_prop = mdl.prop(mask_handle, "tp_connection")
    tp_connection = mdl.get_property_disp_value(tp_connection_prop)
    phases_prop = mdl.prop(mask_handle, "phases")
    phases = mdl.get_property_disp_value(phases_prop)

    #
    # Backward compatibility
    #
    map_dict = {"Y": "Y - Neutral point accessible",
                "Y-grounded": "Y - Grounded",
                "Series": "In series",
                "Δ": "Δ"}

    if tp_connection in map_dict.keys():
        tp_connection = map_dict[tp_connection]

    #
    # Set image
    #
    filenames = {"1": {"In series": "cap_1S",
                       "Y - Grounded": "cap_1Y_g"},
                 "2": {"In series": "cap_2S"},
                 "3": {"In series": "cap_3S",
                       "Y - Grounded": "cap_3Y_g",
                       "Y - Neutral point accessible": "cap_3Y_n",
                       "Δ": "cap_3D"},
                 }

    if filenames[phases].get(tp_connection):
        mdl.set_component_icon_image(mask_handle, f'images/{filenames[phases][tp_connection]}.svg')

    #
    # Set text
    #

    mdl.set_color(mask_handle, "blue")

    # Neutral
    if tp_connection == "Y - Neutral point accessible":
        if phases == "1":
            mdl.disp_component_icon_text(mask_handle, "N", rotate="rotate", relpos_x=0.92, relpos_y=0.5,
                                         size=8, trim_factor=2)
        else:
            mdl.disp_component_icon_text(mask_handle, "N", rotate="rotate", relpos_x=0.81, relpos_y=0.12,
                                         size=8, trim_factor=2)


