def update_inner_constant(mdl, mask_handle, new_value):
    comp_handle = mdl.get_parent(mask_handle)
    inner_constant = mdl.get_item("status", parent=comp_handle)
    if new_value == True:
        mdl.set_property_value(mdl.prop(inner_constant, "value"), 1)
    else:
        mdl.set_property_value(mdl.prop(inner_constant, "value"), 0)