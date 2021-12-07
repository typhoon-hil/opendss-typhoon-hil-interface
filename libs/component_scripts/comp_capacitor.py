import numpy as np

x0, y0 = (8192, 8192)

def calculate_c(mdl, mask_handle):
    tp_connection_prop = mdl.prop(mask_handle, "tp_connection")
    tp_connection = mdl.get_property_value(tp_connection_prop)

    v_correction = 3**0.5 if tp_connection == "Δ" else 1
    f = mdl.get_property_value(mdl.prop(mask_handle, "BaseFreq"))
    kvar = mdl.get_property_value(mdl.prop(mask_handle, "Kvar"))
    kv = mdl.get_property_value(mdl.prop(mask_handle, "Kv"))
    C = kvar*1000/(2*np.pi*f*(1000*v_correction*kv)**2)

    mdl.set_property_value(mdl.prop(mask_handle, "C"), C)

def delete_ports(mdl, comp_handle):

    A2 = mdl.get_item('A2', parent=comp_handle, item_type="port")
    B2 = mdl.get_item('B2', parent=comp_handle, item_type="port")
    C2 = mdl.get_item('C2', parent=comp_handle, item_type="port")
    gnd = mdl.get_item('N1', parent=comp_handle, item_type="port")

    if A2:
        mdl.delete_item(A2)
    if B2:
        mdl.delete_item(B2)
    if C2:
        mdl.delete_item(C2)
    if gnd:
        mdl.delete_item(gnd)

    j = mdl.get_item('j', parent=comp_handle, item_type="junction")
    if j:
        mdl.delete_item(j)

def create_bottom_ports(mdl, comp_handle):

    A2 = mdl.create_port(
        name="A2",
        parent=comp_handle,
        kind="pe",
        terminal_position=(-32, 32),
        position=(x0-200, y0-100),
        rotation="up"
    )
    B2 = mdl.create_port(
        name="B2",
        parent=comp_handle,
        kind="pe",
        terminal_position=("bottom", "center"),
        position=(x0 - 200, y0),
        rotation="up"
    )
    C2 = mdl.create_port(
        name="C2",
        parent=comp_handle,
        kind="pe",
        terminal_position=(32, 32),
        position=(x0 - 200, y0 + 100),
        rotation="up"
    )

    return [A2, B2, C2]

def y_delta_connection(mdl, comp_handle, tp_connection):

    cap_a = mdl.get_item('Ca', parent=comp_handle)
    cap_b = mdl.get_item('Cb', parent=comp_handle)
    cap_c = mdl.get_item('Cc', parent=comp_handle)
    delta_conn_1 = mdl.get_item('delta_conn_1', parent=comp_handle, item_type="connection")
    delta_conn_2 = mdl.get_item('delta_conn_2', parent=comp_handle, item_type="connection")
    b1_conn = mdl.get_item('b1_conn', parent=comp_handle, item_type="connection")
    B1 = mdl.get_item('B1', parent=comp_handle, item_type="port")

    if b1_conn:
        mdl.delete_item(b1_conn)

    junc = mdl.create_junction(name="j", parent=comp_handle, position=(x0 - 200, y0))
    if tp_connection == "Δ":
        mdl.create_connection(junc, mdl.term(cap_a, "n_node"))
        mdl.create_connection(junc, mdl.term(cap_c, "n_node"))
        mdl.create_connection(mdl.term(cap_a, "p_node"), mdl.term(cap_b, "n_node"), name="delta_conn_1")
        mdl.create_connection(mdl.term(cap_c, "p_node"), mdl.term(cap_b, "p_node"), name="delta_conn_2")
        mdl.create_connection(junc, B1, name="b1_conn")

    elif tp_connection == "Y":
        if delta_conn_1:
            mdl.delete_item(delta_conn_1)
        if delta_conn_2:
            mdl.delete_item(delta_conn_2)
        mdl.create_connection(junc, mdl.term(cap_a, "n_node"))
        mdl.create_connection(junc, mdl.term(cap_b, "n_node"))
        mdl.create_connection(junc, mdl.term(cap_c, "n_node"))
        mdl.create_connection(B1, mdl.term(cap_b, "p_node"), name="b1_conn")

    elif tp_connection == "Y-grounded":

        if delta_conn_1:
            mdl.delete_item(delta_conn_1)
        if delta_conn_2:
            mdl.delete_item(delta_conn_2)

        gnd = mdl.create_port(
            name="N1",
            parent=comp_handle,
            kind="pe",
            terminal_position=("bottom", "center"),
            position=(x0 - 300, y0),
            rotation="up"
        )

        mdl.create_connection(junc, mdl.term(cap_a, "n_node"))
        mdl.create_connection(junc, mdl.term(cap_b, "n_node"))
        mdl.create_connection(junc, mdl.term(cap_c, "n_node"))
        mdl.create_connection(mdl.term(cap_b, "p_node"), B1, name="b1_conn")
        mdl.create_connection(junc, gnd)

def redo_connections(mdl, mask_handle):
    comp_handle = mdl.get_parent(mask_handle)

    cap_a = mdl.get_item('Ca', parent=comp_handle)
    cap_b = mdl.get_item('Cb', parent=comp_handle)
    cap_c = mdl.get_item('Cc', parent=comp_handle)

    tp_connection_prop = mdl.prop(comp_handle, "tp_connection")
    tp_connection = mdl.get_property_value(tp_connection_prop)

    delete_ports(mdl, comp_handle)

    if tp_connection == "Series":

        delta_conn_1 = mdl.get_item('delta_conn_1', parent=comp_handle, item_type="connection")
        delta_conn_2 = mdl.get_item('delta_conn_2', parent=comp_handle, item_type="connection")

        if delta_conn_1:
            mdl.delete_item(delta_conn_1)
        if delta_conn_2:
            mdl.delete_item(delta_conn_2)

        A2, B2, C2 = create_bottom_ports(mdl, comp_handle)

        B1 = mdl.get_item('B1', parent=comp_handle, item_type="port")
        b1_conn = mdl.get_item('b1_conn', parent=comp_handle, item_type="connection")
        if not b1_conn:
            mdl.create_connection(mdl.term(cap_b, "p_node"), B1, name="b1_conn")

        mdl.create_connection(A2, mdl.term(cap_a, "n_node"))
        mdl.create_connection(B2, mdl.term(cap_b, "n_node"))
        mdl.create_connection(C2, mdl.term(cap_c, "n_node"))
    else:
        y_delta_connection(mdl, comp_handle, tp_connection)

def define_image(mdl, mask_handle):
    tp_connection_prop = mdl.prop(mask_handle, "tp_connection")
    tp_connection = mdl.get_property_value(tp_connection_prop)

    filenames = {
        "Series": "cap_3S",
        "Y": "cap_3Y",
        "Y-grounded": "cap_3Yg",
        "Δ": "cap_3D",
    }

    return f'images/{filenames[tp_connection]}.svg'

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
        toggle_frequency_prop(mdl, mask_handle, init)
