import importlib

x0, y0 = (8192, 8192)


def pick_comp_script(mdl, mask_handle, caller):
    if caller == "apply_button":
        type_prop = mdl.prop(mask_handle, "dss_container_mask_type")
        identifier = mdl.get_property_disp_value(type_prop)
    elif caller == "init":
        id_prop = mdl.prop(mask_handle, "dss_container_comp_identifier")
        identifier = mdl.get_property_disp_value(id_prop)

    if identifier == "Vsource":
        import component_scripts.comp_vsource as comp_script
    elif identifier == "Line":
        import component_scripts.comp_line as comp_script
    elif identifier == "Load":
        import component_scripts.comp_load as comp_script
    elif identifier == "Capacitor Bank":
        import component_scripts.comp_capacitor as comp_script
    elif identifier == "Controlled Switch":
        import component_scripts.comp_ctrlsw as comp_script
    elif identifier == "Fault":
        import component_scripts.comp_fault as comp_script
    elif identifier == "Isource":
        import component_scripts.comp_isource as comp_script
    elif identifier == "Three-Phase Transformer":
        import component_scripts.comp_tptransf as comp_script
    elif identifier == "Single-Phase Transformer":
        import component_scripts.comp_sptransf as comp_script
    elif identifier == "Generator":
        import component_scripts.comp_generator as comp_script
    elif identifier == "Storage":
        import component_scripts.comp_storage as comp_script
    elif identifier == "VSConverter":
        import component_scripts.comp_vsc as comp_script

    return comp_script

def pick_contained_comp_calls(mdl, mask_handle):
    id_prop = mdl.prop(mask_handle, "dss_container_comp_identifier")
    identifier = mdl.get_property_value(id_prop)

    if identifier == "Load":
        import component_scripts.container.load_container as contained_comp_calls
    elif identifier == "Vsource":
        import component_scripts.container.vsource_container as contained_comp_calls
    elif identifier == "Line":
        import component_scripts.container.line_container as contained_comp_calls
    elif identifier == "Capacitor Bank":
        import component_scripts.container.capacitor_bank_container as contained_comp_calls
    elif identifier == "Controlled Switch":
        import component_scripts.container.controlled_switch_container as contained_comp_calls
    elif identifier == "Fault":
        import component_scripts.container.fault_container as contained_comp_calls
    elif identifier == "Isource":
        import component_scripts.container.isource_container as contained_comp_calls
    elif identifier == "Three-Phase Transformer":
        import component_scripts.container.three_phase_transformer_container as contained_comp_calls
    elif identifier == "Single-Phase Transformer":
        import component_scripts.container.single_phase_transformer_container as contained_comp_calls
    elif identifier == "Generator":
        import component_scripts.container.generator_container as contained_comp_calls
    elif identifier == "Storage":
        import component_scripts.container.storage_container as contained_comp_calls
    elif identifier == "VSConverter":
        import component_scripts.container.vsconverter_container as contained_comp_calls

    importlib.reload(contained_comp_calls)
    return contained_comp_calls


def apply_mask_button_handler(mdl, mask_handle):

    # Save the mask type to identifier property
    type_prop = mdl.prop(mask_handle, "dss_container_mask_type")
    comp_type = mdl.get_property_disp_value(type_prop)
    id_prop = mdl.prop(mask_handle, "dss_container_comp_identifier")
    mdl.set_property_value(id_prop, comp_type)

    comp_script = pick_comp_script(mdl, mask_handle, "apply_button")

    # Get the contained component mask creation script
    contained_comp_calls = pick_contained_comp_calls(mdl, mask_handle)

    # Create the mask parameters
    contained_comp_calls.update_properties(mdl, mask_handle)

    # Update the image
    comp_script.define_icon(mdl, mask_handle)
    mdl.refresh_icon(mdl.get_parent(mask_handle))

    # Create ports
    contained_comp_calls.ports_initialization(mdl, mask_handle)

    # Run extra initialization functions
    initialization_function_calls(mdl, mask_handle)

    # Unlink the component
    mdl.unlink_component(mdl.get_parent(mask_handle))

    # Update ports
    comp_script.port_dynamics(mdl, mask_handle)

    # Remove the properties
    mdl.remove_property(mask_handle, "dss_container_mask_type")
    mdl.remove_property(mask_handle, "dss_apply_mask_type")

    # Close the dialog
    mask_dialog = mdl.get_ns_var("container_dialog_handler")
    mask_dialog.reject()


def initialization_function_calls(mdl, mask_handle):

    id_prop = mdl.prop(mask_handle, "dss_container_comp_identifier")
    comp_type = mdl.get_property_value(id_prop)

    if comp_type == "Line":
        import comp_line
        comp_line.show_hide_param_inputs(mdl, mask_handle, "Symmetrical")


def define_icon(mdl, mask_handle):
    mdl.set_component_icon_image(mask_handle, "images/container.svg")
    mdl.set_color(mask_handle, "red")
    mdl.disp_component_icon_text(mask_handle, "Select a type", relpos_x=0.5, relpos_y=0.5, size=8)
