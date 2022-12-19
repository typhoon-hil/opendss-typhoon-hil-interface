def toggle_inner_fault(mdl, mask_handle, mode="delete"):
    comp_handle = mdl.get_parent(mask_handle)
    inner_fault = mdl.get_item("F1", parent=comp_handle)
    a1 = mdl.get_item("A1", parent=comp_handle, item_type="port")
    b1 = mdl.get_item("B1", parent=comp_handle, item_type="port")
    c1 = mdl.get_item("C1", parent=comp_handle, item_type="port")
    a2 = mdl.get_item("A2", parent=comp_handle, item_type="port")
    b2 = mdl.get_item("B2", parent=comp_handle, item_type="port")
    c2 = mdl.get_item("C2", parent=comp_handle, item_type="port")
    if inner_fault and mode == "delete":
        mdl.delete_item(inner_fault)
        mdl.create_connection(a1, a2)
        mdl.create_connection(b1, b2)
        mdl.create_connection(c1, c2)
    elif not inner_fault and mode == "restore":
        for conn in mdl.find_connections(a1):
            mdl.delete_item(conn)
        for conn in mdl.find_connections(b1):
            mdl.delete_item(conn)
        for conn in mdl.find_connections(c1):
            mdl.delete_item(conn)
        inner_fault = mdl.create_component(
            "core/Grid Fault",
            name="F1",
            parent=comp_handle,
            position=(7736, 7950)
        )
        res = mdl.get_property_value(mdl.prop(comp_handle, "resistance"))
        mdl.set_property_value(mdl.prop(inner_fault, "resistance"), res)
        mdl.create_connection(a1, mdl.term(inner_fault, "A1"))
        mdl.create_connection(b1, mdl.term(inner_fault, "B1"))
        mdl.create_connection(c1, mdl.term(inner_fault, "C1"))
        mdl.create_connection(a2, mdl.term(inner_fault, "A2"))
        mdl.create_connection(b2, mdl.term(inner_fault, "B2"))
        mdl.create_connection(c2, mdl.term(inner_fault, "C2"))


def update_inner_fault(mdl, mask_handle, prop_name, new_value):
    comp_handle = mdl.get_parent(mask_handle)
    type_prop = mdl.prop(mask_handle, "type")
    prop_type = mdl.get_property_value(type_prop)

    if prop_name == "fault_type":
        if new_value == "None":
            toggle_inner_fault(mdl, mask_handle, mode="delete")
        else:
            toggle_inner_fault(mdl, mask_handle, mode="restore")
            inner_fault = mdl.get_item("F1", parent=comp_handle)
            mdl.set_property_value(mdl.prop(inner_fault, prop_name), new_value)
    elif prop_name == "resistance":
        if prop_type in ['A-B-C-GND', 'A-B-C']:
            new_value = str(float(new_value) * 3)
        if prop_type in ['A-B', 'A-C', 'B-C', 'A-B-GND', 'A-C-GND', 'B-C-GND']:
            new_value = str(float(new_value) * 2)
        inner_fault = mdl.get_item("F1", parent=comp_handle)
        if inner_fault:
            mdl.set_property_value(mdl.prop(inner_fault, prop_name), new_value)


def update_inner_gnd(mdl, mask_handle, created_ports):
    comp_handle = mdl.get_parent(mask_handle)
    av_gnd = mdl.get_item("gnd", parent=comp_handle, item_type="port")
    inner_fault = mdl.get_item("F1", parent=comp_handle)
    type_prop = mdl.prop(comp_handle, "type")
    gnd_connection = True if "GND" in mdl.get_property_value(type_prop) else False

    if gnd_connection:
        if av_gnd and not (len(mdl.get_connected_items(av_gnd)) > 0):
            mdl.create_connection(av_gnd, mdl.term(inner_fault, 'GND'))


def mask_dialog_dynamics(mdl, mask_handle, caller_prop_handle=None, init=False):
    pass


def port_dynamics(mdl, mask_handle, caller_prop_handle=None, init=False):
    comp_handle = mdl.get_parent(mask_handle)
    deleted_ports = []
    created_ports = {}

    av_gnd = mdl.get_item("gnd", parent=comp_handle, item_type="port")
    type_prop = mdl.prop(comp_handle, "type")
    gnd_connection = True if "GND" in mdl.get_property_value(type_prop) else False

    if gnd_connection:
        if not av_gnd:
            gnd = mdl.create_port(
                name="gnd",
                parent=comp_handle,
                terminal_position=("bottom", "center"),
                rotation="left",
                position=(7736, 8142)
            )
            created_ports.update({"gnd": gnd})
    else:
        if av_gnd:
            deleted_ports.append(mdl.get_name(av_gnd))
            mdl.delete_item(av_gnd)

    return created_ports, deleted_ports


def define_icon(mdl, mask_handle):
    type_prop = mdl.prop(mask_handle, "type")
    type = mdl.get_property_value(type_prop)

    if type == "A-B-C-GND":
        mdl.set_component_icon_image(mask_handle, 'images/sc_abc-g.svg')
    elif type == "A-B-GND":
        mdl.set_component_icon_image(mask_handle, 'images/sc_ab-g.svg')
    elif type == "A-C-GND":
        mdl.set_component_icon_image(mask_handle, 'images/sc_ac-g.svg')
    elif type == "B-C-GND":
        mdl.set_component_icon_image(mask_handle, 'images/sc_bc-g.svg')
    elif type == "A-GND":
        mdl.set_component_icon_image(mask_handle, 'images/sc_a-g.svg')
    elif type == "B-GND":
        mdl.set_component_icon_image(mask_handle, 'images/sc_b-g.svg')
    elif type == "C-GND":
        mdl.set_component_icon_image(mask_handle, 'images/sc_c-g.svg')
    elif type == "A-B-C":
        mdl.set_component_icon_image(mask_handle, 'images/sc_abc.svg')
    elif type == "A-B":
        mdl.set_component_icon_image(mask_handle, 'images/sc_ab.svg')
    elif type == "A-C":
        mdl.set_component_icon_image(mask_handle, 'images/sc_ac.svg')
    elif type == "B-C":
        mdl.set_component_icon_image(mask_handle, 'images/sc_bc.svg')
    elif type == "None":
        mdl.set_component_icon_image(mask_handle, 'images/sc_none.svg')

