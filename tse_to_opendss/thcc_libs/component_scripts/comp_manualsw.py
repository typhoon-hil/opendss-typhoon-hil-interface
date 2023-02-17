def update_inner_structure(mdl, mask_handle, new_value):
    comp_handle = mdl.get_parent(mask_handle)

    # new_value -> True = Short Circuit; False = Open Circuit
    for phase in ["A", "B", "C"]:
        if new_value:
            open_circuit = mdl.get_item(f"OC_{phase}", parent=comp_handle)
            if open_circuit:
                position = mdl.get_position(open_circuit)
                mdl.delete_item(open_circuit)

            short_circuit = mdl.get_item(f"SC_{phase}", parent=comp_handle)
            if not short_circuit:
                short_circuit = mdl.create_component("Short Circuit", parent=comp_handle,
                                                     name=f"SC_{phase}",
                                                     position=position)
                mdl.set_property_value(mdl.prop(short_circuit, "circuit_connector"), "true")

                port1 = mdl.get_item(f"{phase}1", parent=comp_handle, item_type="port")
                port2 = mdl.get_item(f"{phase}2", parent=comp_handle, item_type="port")
                mdl.create_connection(port1, mdl.term(short_circuit, "p_node"))
                mdl.create_connection(mdl.term(short_circuit, "n_node"), port2)

        else:
            short_circuit = mdl.get_item(f"SC_{phase}", parent=comp_handle)
            if short_circuit:
                position = mdl.get_position(short_circuit)
                mdl.delete_item(short_circuit)

            open_circuit = mdl.get_item(f"OC_{phase}", parent=comp_handle)
            if not open_circuit:
                open_circuit = mdl.create_component("Open Circuit", parent=comp_handle,
                                                    name=f"OC_{phase}",
                                                    position=position)
                mdl.set_property_value(mdl.prop(open_circuit, "circuit_connector"), "true")

                port1 = mdl.get_item(f"{phase}1", parent=comp_handle, item_type="port")
                port2 = mdl.get_item(f"{phase}2", parent=comp_handle, item_type="port")
                mdl.create_connection(port1, mdl.term(open_circuit, "p_node"))
                mdl.create_connection(mdl.term(open_circuit, "n_node"), port2)


def define_icon(mdl, mask_handle):
    switch_is_closed = mdl.get_property_value(mdl.prop(mask_handle, "switch_status"))
    if switch_is_closed:
        mdl.set_component_icon_image(mask_handle, 'images/switch_closed_3ph.svg')
    else:
        mdl.set_component_icon_image(mask_handle, 'images/switch_open_3ph.svg')
