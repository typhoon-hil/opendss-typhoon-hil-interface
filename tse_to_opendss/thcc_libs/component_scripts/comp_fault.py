def toggle_inner_fault(mdl, mask_handle, mode="delete"):
    comp_handle = mdl.get_parent(mask_handle)
    inner_fault = mdl.get_item("F1", parent=comp_handle)
    A1 = mdl.get_item("A1", parent=comp_handle, item_type="port")
    B1 = mdl.get_item("B1", parent=comp_handle, item_type="port")
    C1 = mdl.get_item("C1", parent=comp_handle, item_type="port")
    A2 = mdl.get_item("A2", parent=comp_handle, item_type="port")
    B2 = mdl.get_item("B2", parent=comp_handle, item_type="port")
    C2 = mdl.get_item("C2", parent=comp_handle, item_type="port")
    if inner_fault and mode == "delete":
        mdl.delete_item(inner_fault)
        mdl.create_connection(A1, A2)
        mdl.create_connection(B1, B2)
        mdl.create_connection(C1, C2)
    elif not inner_fault and mode == "restore":
        for conn in mdl.find_connections(A1):
            mdl.delete_item(conn)
        for conn in mdl.find_connections(B1):
            mdl.delete_item(conn)
        for conn in mdl.find_connections(C1):
            mdl.delete_item(conn)
        inner_fault = mdl.create_component(
            "core/Grid Fault",
            name="F1",
            parent=comp_handle,
            position=(7736, 7950)
        )
        res = mdl.get_property_value(mdl.prop(comp_handle, "resistance"))
        mdl.set_property_value(mdl.prop(inner_fault, "resistance"), res)
        mdl.create_connection(A1, mdl.term(inner_fault, "A1"))
        mdl.create_connection(B1, mdl.term(inner_fault, "B1"))
        mdl.create_connection(C1, mdl.term(inner_fault, "C1"))
        mdl.create_connection(A2, mdl.term(inner_fault, "A2"))
        mdl.create_connection(B2, mdl.term(inner_fault, "B2"))
        mdl.create_connection(C2, mdl.term(inner_fault, "C2"))


def update_inner_fault(mdl, mask_handle, prop_name, new_value):
    comp_handle = mdl.get_parent(mask_handle)
    type_prop = mdl.prop(mask_handle, "type")
    type = mdl.get_property_value(type_prop)

    if prop_name == "fault_type":
        if new_value == "None":
            toggle_inner_fault(mdl, mask_handle, mode="delete")
        else:
            toggle_inner_fault(mdl, mask_handle, mode="restore")
            inner_fault = mdl.get_item("F1", parent=comp_handle)
            mdl.set_property_value(mdl.prop(inner_fault, prop_name), new_value)
    elif prop_name == "resistance":
        if type in ['A-B-C-GND', 'A-B-C']:
            new_value = str(float(new_value) * 3)
        if type in ['A-B', 'A-C', 'B-C', 'A-B-GND', 'A-C-GND', 'B-C-GND']:
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
        if not av_gnd:
            gnd = created_ports.get("gnd")
            mdl.create_connection(gnd, mdl.term(inner_fault, 'GND'))

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

