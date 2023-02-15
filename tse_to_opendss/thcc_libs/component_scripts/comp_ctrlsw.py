def update_inner_property(mdl, mask_handle, prop_name, new_value):
    comp_handle = mdl.get_parent(mask_handle)
    inner_contactor = mdl.get_item("S", parent=comp_handle)
    inner_prop = mdl.prop(inner_contactor, prop_name)
    mdl.set_property_value(inner_prop, new_value)


def mask_dialog_dynamics(mdl, mask_handle, caller_prop_handle=None, init=False):
    prop_name = mdl.get_name(caller_prop_handle)
    new_value = mdl.get_property_disp_value(caller_prop_handle)

    if prop_name == "enable_fb_out":
        fb_out_type = mdl.prop(mask_handle, "fb_out_type")

        if new_value == "True":
            mdl.show_property(fb_out_type)
        else:
            mdl.hide_property(fb_out_type)


def port_dynamics(mdl, mask_handle, caller_prop_handle=None, init=False):
    comp_handle = mdl.get_parent(mask_handle)
    deleted_ports = []
    created_ports = {}

    ctrl_input_port = mdl.get_item("ctrl", parent=comp_handle, item_type="port")
    enable_fb_prop = mdl.prop(comp_handle, "enable_fb_out")
    enable_fb_terminal = True if mdl.get_property_value(enable_fb_prop) == "True" else False
    fb_conn = mdl.get_item("fb", parent=comp_handle, item_type="port")

    if enable_fb_terminal:
        if not fb_conn:
            fb_conn = mdl.create_port(
                name="fb",
                kind="sp",
                direction="out",
                parent=comp_handle,
                terminal_position=("top", "right"),
                rotation="left",
                position=(7786, 7800),
                hide_name=True
            )
            created_ports.update({"fb": fb_conn})
            mdl.set_port_properties(ctrl_input_port, terminal_position=("top", "left"))
    else:
        if fb_conn:
            deleted_ports.append(mdl.get_name(fb_conn))
            mdl.delete_item(fb_conn)
            mdl.set_port_properties(ctrl_input_port, terminal_position=("top", "center"))

    # Container workaround
    mdl.refresh_icon(comp_handle)
    C2 = mdl.get_item("C2", parent=comp_handle, item_type="port")
    mdl.set_port_properties(C2, terminal_position=("right", "bottom"))

    return created_ports, deleted_ports


def update_fb_connection(mdl, mask_handle):
    comp_handle = mdl.get_parent(mask_handle)
    fb_conn = mdl.get_item("fb", parent=comp_handle, item_type="port")
    inner_contactor = mdl.get_item("S", parent=comp_handle)
    enable_fb_prop = mdl.prop(comp_handle, "enable_fb_out")
    enable_fb_terminal = True if mdl.get_property_value(enable_fb_prop) == "True" else False

    if fb_conn:
        if enable_fb_terminal:
            mdl.create_connection(fb_conn, mdl.term(inner_contactor, 'feedback_out'))


def define_icon(mdl, mask_handle):
    initial_state = mdl.get_property_value(mdl.prop(mask_handle, "initial_state"))
    if initial_state == "on":
        mdl.set_component_icon_image(mask_handle, 'images/switch_closed.svg')
    else:
        mdl.set_component_icon_image(mask_handle, 'images/switch_open.svg')
