import numpy as np

x0, y0 = (8192, 8192)

def update_source_values(mdl, mask_handle):
    comp_handle = mdl.get_parent(mask_handle)

    # Property handles
    basekv_prop = mdl.prop(comp_handle, "basekv")
    frequency_prop = mdl.prop(comp_handle, "Frequency")
    angle_prop = mdl.prop(comp_handle, "Angle")
    pu_prop = mdl.prop(comp_handle, "pu")

    r1_prop = mdl.prop(comp_handle, "r1")
    x1_prop = mdl.prop(comp_handle, "x1")
    r0_prop = mdl.prop(comp_handle, "r0")
    x0_prop = mdl.prop(comp_handle, "x0")

    r1 = mdl.get_property_value(r1_prop)
    x1 = mdl.get_property_value(x1_prop)
    r0 = mdl.get_property_value(r0_prop)
    x0 = mdl.get_property_value(x0_prop)

    # Inner TL
    tl_comp = mdl.get_item("TL1", parent=comp_handle)
    tl_f_prop = mdl.prop(tl_comp, "Frequency")
    freq = mdl.get_property_value(frequency_prop)
    mdl.set_property_value(tl_f_prop, freq)

    rseq = f'[[{r0}, 0, 0], [0, {r1}, 0], [0, 0, {r1}]]'
    lseq = f'[[{x0 / 2 / np.pi / freq}, 0, 0], [0, {x1 / 2 / np.pi / freq}, 0], [0, 0, {x1 / 2 / np.pi / freq}]]'

    r_seq_prop = mdl.prop(tl_comp, "R_sequence_metric")
    l_seq_prop = mdl.prop(tl_comp, "L_sequence_metric")
    mdl.set_property_value(r_seq_prop, rseq)
    mdl.set_property_value(l_seq_prop, lseq)

    for idx, letter in enumerate(["a", "b", "c"]):
        # Source handles
        vsource = mdl.get_item("V" + letter, parent=comp_handle)

        rms_prop = mdl.prop(vsource, "init_rms_value")
        f_prop = mdl.prop(vsource, "init_frequency")
        ph_prop = mdl.prop(vsource, "init_phase")

        mdl.set_property_value(rms_prop, round(
            mdl.get_property_value(basekv_prop) * 1000 * mdl.get_property_value(pu_prop) / np.sqrt(3), 8))
        mdl.set_property_value(f_prop, mdl.get_property_value(frequency_prop))
        mdl.set_property_value(ph_prop, mdl.get_property_value(angle_prop) - 120 * idx)

def toggle_frequency_prop(mdl, mask_handle, init=False):
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


def update_connections(mdl, mask_handle, ports):
    comp_handle = mdl.get_parent(mask_handle)

    # Source handles
    va = mdl.get_item("Va", parent=comp_handle)
    vb = mdl.get_item("Vb", parent=comp_handle)
    vc = mdl.get_item("Vc", parent=comp_handle)

    ground_connected = mdl.get_property_value(mdl.prop(mask_handle, "ground_connected"))
    if ground_connected:
        gnd = mdl.create_component(
            "core/Ground",
            name="gnd1",
            parent=comp_handle,
            position=(8000, 8400)
        )

        mdl.create_connection(mdl.term(gnd, "node"), mdl.term(va, 'n_node'))
        mdl.create_connection(mdl.term(gnd, "node"), mdl.term(vb, 'n_node'))
        mdl.create_connection(mdl.term(gnd, "node"), mdl.term(vc, 'n_node'))
    else:
        # Ground handle
        gnd = mdl.get_item("gnd1", parent=comp_handle)
        mdl.delete_item(gnd)

        mdl.create_connection(ports.get("A2"), mdl.term(va, 'n_node'))
        mdl.create_connection(ports.get("B2"), mdl.term(vb, 'n_node'))
        mdl.create_connection(ports.get("C2"), mdl.term(vc, 'n_node'))

def port_dynamics(mdl, mask_handle, caller_prop_handle=None, init=False):
    comp_handle = mdl.get_parent(mask_handle)
    deleted_ports = []
    created_ports = {}

    ground_connected = mdl.get_property_value(mdl.prop(mask_handle, "ground_connected"))
    if ground_connected:
        # Delete A2-C2 ports
        a2 = mdl.get_item("A2", parent=comp_handle, item_type="port")
        b2 = mdl.get_item("B2", parent=comp_handle, item_type="port")
        c2 = mdl.get_item("C2", parent=comp_handle, item_type="port")

        for port in [a2, b2, c2]:
            if port:
                deleted_ports.append(mdl.get_name(port))
                mdl.delete_item(port)

    else:

        a2 = mdl.create_port(
            name="A2",
            parent=comp_handle,
            terminal_position=[-32, -32],
            position=(x0 - 200, y0 - 100)
        )
        b2 = mdl.create_port(
            name="B2",
            parent=comp_handle,
            terminal_position=[-32, 0],
            position=(x0 - 200, y0 - 0)
        )
        c2 = mdl.create_port(
            name="C2",
            parent=comp_handle,
            terminal_position=[-32, 32],
            position=(x0 - 200, y0 + 100)
        )

        created_ports.update({
            "A2": a2,
            "B2": b2,
            "C2": c2
        })

    return created_ports, deleted_ports


def mask_dialog_dynamics(mdl, mask_handle, caller_prop_handle=None, init=False):

    toggle_frequency_prop(mdl, mask_handle, init=False)


def define_icon(mdl, mask_handle):
    ground_connected = mdl.get_property_value(mdl.prop(mask_handle, "ground_connected"))
    if ground_connected:
        mdl.set_component_icon_image(mask_handle, 'images/vsource_gnd.svg')
    else:
        mdl.set_component_icon_image(mask_handle, 'images/vsource.svg')
