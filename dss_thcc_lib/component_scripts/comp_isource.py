x0, y0 = (8192, 8192)


def update_source_values(mdl, mask_handle):
    comp_handle = mdl.get_parent(mask_handle)

    # Source handles
    Va = mdl.get_item("Va", parent=comp_handle)
    Vb = mdl.get_item("Vb", parent=comp_handle)
    Vc = mdl.get_item("Vc", parent=comp_handle)

    # Property handles
    frequency_prop = mdl.prop(comp_handle, "Frequency")
    angle_prop = mdl.prop(comp_handle, "Angle")
    amps_prop = mdl.prop(comp_handle, "amps")

    for idx, letter in enumerate(["a", "b", "c"]):

        # Source handles
        isource = mdl.get_item("I"+letter, parent=comp_handle)

        rms_prop = mdl.prop(isource, "init_rms_value")
        f_prop = mdl.prop(isource, "init_frequency")
        ph_prop = mdl.prop(isource, "init_phase")

        mdl.set_property_value(rms_prop, "amps")
        mdl.set_property_value(f_prop, "Frequency")
        mdl.set_property_value(ph_prop, f"Angle - {120 * idx}")


def toggle_frequency_prop(mdl, mask_handle, init=False):
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
        toggle_frequency_prop(mdl, mask_handle, init)


def mask_dialog_dynamics(mdl, mask_handle, caller_prop_handle=None, init=False):
    toggle_frequency_prop(mdl, mask_handle)


def port_dynamics(mdl, mask_handle, caller_prop_handle=None, init=False):
    comp_handle = mdl.get_parent(mask_handle)
    deleted_ports = []
    created_ports = {}

    return created_ports, deleted_ports


def define_icon(mdl, mask_handle):
    mdl.set_component_icon_image(mask_handle, 'images/isource.svg')

def resolve_backward_compatibility(mdl, mask_handle):
    if mdl.exists("BaseFreq", parent = mask_handle, item_type = "property"):
        old_prop = mdl.prop(mask_handle,"BaseFreq")
        old_prop_val = mdl.get_property_value(old_prop)
        new_prop = mdl.prop(mask_handle,"baseFreq")
        mdl.set_property_value(new_prop, old_prop_val)
