import dss_thcc_lib.component_scripts.util as util
import importlib

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


def get_sld_conversion_info(mdl, mask_handle, props_state):

    multiline_ports_1 = ["A1", "B1", "C1"]

    port_config_dict = {
        "SLD1": {
            "multiline_ports": multiline_ports_1,
            "side": "right",
            "bus_terminal_position": (24, 0),
            "hide_name": True,
        },
    }
    #
    # Tag info
    #
    tag_config_dict = {}

    #
    # Terminal positions
    #
    terminal_positions = {
        "A1": (32, -32),
        "B1": (32, 0),
        "C1": (32, 32),
    }

    return port_config_dict, tag_config_dict, terminal_positions


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


def topology_dynamics(mdl, mask_handle, prop_handle, new_value, old_value):
    comp_handle = mdl.get_parent(mask_handle)

    if prop_handle:
        calling_prop_name = mdl.get_name(prop_handle)
    else:
        calling_prop_name = "init_code"

    #
    # Get new property values to be applied
    # If multiple properties are changed, there is a temporary mismatch between
    # display values (the final values) and current values.
    #
    new_prop_values = {}
    current_pass_prop_values = {
        k: str(v) for k, v in mdl.get_property_values(comp_handle).items()
    }
    for prop in mdl.get_property_values(comp_handle):
        p = mdl.prop(mask_handle, prop)
        disp_value = str(mdl.get_property_disp_value(p))
        new_prop_values[prop] = disp_value

    #
    # Topology dynamics need to be applied on multiline format
    #
    currently_sld = mdl.get_item("SLD1", parent=comp_handle, item_type="port")
    if currently_sld:
        # The terminal related to the current property hasn't been created yet
        modified_prop_values = dict(current_pass_prop_values)
        modified_prop_values[calling_prop_name] = old_value
        sld_info = get_sld_conversion_info(mdl, mask_handle, modified_prop_values)
        util.convert_to_multiline(mdl, mask_handle, sld_info)

    #
    # When property values reach the final state, return to single-line if needed
    #
    values_equal = []
    for prop_name in new_prop_values:
        cur_pass_value = current_pass_prop_values[prop_name]
        new_value = new_prop_values[prop_name]
        if util.is_float(cur_pass_value) or util.is_float(new_value):
            if float(cur_pass_value) == float(new_value):
                values_equal.append(True)
                continue
        else:
            if current_pass_prop_values[prop_name] == new_prop_values[prop_name]:
                values_equal.append(True)
                continue
        values_equal.append(False)

    final_state = all(values_equal)

    if final_state:
        if new_prop_values.get("sld_mode") in (True, "True"):
            importlib.reload(util)
            sld_info = get_sld_conversion_info(mdl, mask_handle, current_pass_prop_values)
            util.convert_to_sld(mdl, mask_handle, sld_info)

    sld_post_processing(mdl, mask_handle)


def sld_post_processing(mdl, mask_handle):
    comp_handle = mdl.get_parent(mask_handle)

    # Resize the buses to 4

    bus1 = mdl.get_item("SLD1_bus", parent=comp_handle)
    if bus1:
        bus1_size_prop = mdl.prop(bus1, "bus_size")
        mdl.set_property_value(bus1_size_prop, 4)


def mask_dialog_dynamics(mdl, mask_handle, caller_prop_handle=None, init=False):
    toggle_frequency_prop(mdl, mask_handle)


def port_dynamics(mdl, mask_handle, caller_prop_handle=None, init=False):
    comp_handle = mdl.get_parent(mask_handle)
    deleted_ports = []
    created_ports = {}

    return created_ports, deleted_ports


def define_icon(mdl, mask_handle):
    sld_mode = mdl.get_property_value(mdl.prop(mask_handle, "sld_mode"))

    if sld_mode:
        image_path = 'images/isource_gnd__sld.svg'
    else:
        image_path = 'images/isource.svg'

    mdl.set_component_icon_image(mask_handle, image_path)

