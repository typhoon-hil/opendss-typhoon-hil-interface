def update_inner_property(mdl, mask_handle, prop_name, new_value):
    comp_handle = mdl.get_parent(mask_handle)
    inner_contactor = mdl.get_item("S", parent=comp_handle)
    inner_prop = mdl.prop(inner_contactor, prop_name)
    mdl.set_property_value(inner_prop, new_value)


def dialog_dynamics(mdl, mask_handle, prop_name, new_value):
    if prop_name == "enable_fb_out":
        execution_rate = mdl.prop(mask_handle, "execution_rate")
        fb_out_type = mdl.prop(mask_handle, "fb_out_type")

        if new_value == "True":
            mdl.show_property(fb_out_type)
        else:
            mdl.hide_property(fb_out_type)


def update_fb_connection(mdl, mask_handle):
    comp_handle = mdl.get_parent(mask_handle)
    fb_conn = mdl.get_item("fb", parent=comp_handle, item_type="port")
    inner_contactor = mdl.get_item("S", parent=comp_handle)

    enable_fb_prop = mdl.prop(comp_handle, "enable_fb_out")
    enable_fb_terminal = True if mdl.get_property_value(enable_fb_prop) == "True" else False

    if enable_fb_terminal:
        if not fb_conn:
            fb_conn = mdl.create_port(
                name="fb",
                kind="sp",
                direction="out",
                parent=comp_handle,
                terminal_position=("top", "right"),
                rotation="left",
                position=(7786, 7800)
            )

            mdl.create_connection(fb_conn, mdl.term(inner_contactor, 'feedback_out'))
    else:
        if fb_conn:
            mdl.delete_item(fb_conn)