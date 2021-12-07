import numpy as np

x0, y0 = (8192, 8192)

def update_dispatch_mode(mdl, mask_handle):

    dispatch_q = mdl.get_property_disp_value(mdl.prop(mask_handle, "dispatch_q"))
    dispatch_p = mdl.get_property_disp_value(mdl.prop(mask_handle, "dispatch_p"))

    kvar_prop = mdl.prop(mask_handle, "kvar")
    pf_prop = mdl.prop(mask_handle, "pf")

    if dispatch_q == "Constant PF":
        mdl.hide_property(kvar_prop)
        mdl.show_property(pf_prop)
    elif dispatch_q == "Constant kVAr":
        mdl.show_property(kvar_prop)
        mdl.hide_property(pf_prop)
    else:
        mdl.hide_property(kvar_prop)
        mdl.hide_property(pf_prop)

    charge_trigger_prop = mdl.prop(mask_handle, "chargetrigger")
    discharge_trigger_prop = mdl.prop(mask_handle, "dischargetrigger")
    pct_charge_prop = mdl.prop(mask_handle, "pct_charge")
    pct_discharge_prop = mdl.prop(mask_handle, "pct_discharge")

    if dispatch_p == "Default":
        mdl.show_property(charge_trigger_prop)
        mdl.show_property(discharge_trigger_prop)
        mdl.show_property(pct_charge_prop)
        mdl.show_property(pct_discharge_prop)
    elif dispatch_p == "Follow":
        mdl.hide_property(charge_trigger_prop)
        mdl.hide_property(discharge_trigger_prop)
        mdl.hide_property(pct_charge_prop)
        mdl.hide_property(pct_discharge_prop)

def calculate_kva(mdl, mask_handle):
    kva_prop = mdl.prop(mask_handle, "kva")
    dispatch_q_prop = mdl.prop(mask_handle, "dispatch_q")
    dispatch_q = mdl.get_property_value(dispatch_q_prop)
    kwrated_prop = mdl.prop(mask_handle, "kwrated")
    kwrated = mdl.get_property_value(kwrated_prop)
    pf_prop = mdl.prop(mask_handle, "pf")
    pf = mdl.get_property_value(pf_prop)
    kvar_prop = mdl.prop(mask_handle, "kvar")
    kvar = mdl.get_property_value(kvar_prop)

    if dispatch_q == "Unit PF":
        kva = kwrated
    elif dispatch_q == "Constant PF":
        kva = float(kwrated) / float(pf)
    elif dispatch_q == "Constant kVAr":
        kva = (float(kwrated) ** 2 + float(kvar) ** 2) ** 0.5

    mdl.set_property_value(kva_prop, str(kva))


def update_dispatch_int_comp(mdl, mask_handle):

    comp_handle = mdl.get_parent(mask_handle)

    dispatch_p_dict = {"Default": "1", "Follow": "2"}
    dispatch_q_dict = {"Unit PF": "1", "Constant PF": "2", "Constant kVAr": "3"}

    dispatch_int_dict = {"11": "1", "12": "2", "13": "3", "21": "4", "22": "5", "23": "6"}

    dispatch_p_prop = mdl.prop(comp_handle, "dispatch_p")
    dispatch_p = mdl.get_property_value(dispatch_p_prop)

    dispatch_q_prop = mdl.prop(comp_handle, "dispatch_q")
    dispatch_q = mdl.get_property_value(dispatch_q_prop)

    dispatch_int = dispatch_int_dict.get(dispatch_p_dict[dispatch_p]+dispatch_q_dict[dispatch_q])

    dispatch_int_comp = mdl.get_item("Dispatch Mode Integer", parent=comp_handle)
    mdl.set_property_value(mdl.prop(dispatch_int_comp, "dispatch_mode_int"), dispatch_int)

def load_loadshape(mdl, container_handle):
    import os
    import load_object as load_obj
    import pathlib
    import json
    import ast

    # Find objects file
    mdlfile = mdl.get_model_file_path()
    mdlfile_name = pathlib.Path(mdlfile).stem
    mdlfile_folder = pathlib.Path(mdlfile).parents[0]
    mdlfile_target_folder = mdlfile_folder.joinpath(mdlfile_name + ' Target files')
    dss_folder_path = pathlib.Path(mdlfile_target_folder).joinpath('dss')
    fname = os.path.join(dss_folder_path, 'data', 'general_objects.json')

    loadshape_name_prop = mdl.prop(container_handle, "loadshape_name")
    loadshape_name = mdl.get_property_disp_value(loadshape_name_prop)
    loadshape_name = "" if loadshape_name == "-" else loadshape_name

    obj_type = "LoadShape"

    try:
        with open(fname, 'r') as f:
            obj_dicts = json.load(f)
    except FileNotFoundError:
        obj_dicts = None

    if obj_dicts:
        new_load_window = load_obj.LoadObject(mdl, obj_type, obj_dicts=obj_dicts, starting_object=loadshape_name)
    else:
        new_load_window = load_obj.LoadObject(mdl, obj_type)

    if new_load_window.exec():
        selected_object = new_load_window.selected_object

        obj_dicts = new_load_window.obj_dicts

        selected_obj_dict = obj_dicts.get("loadshapes").get(selected_object)

        loadshape_name = selected_object
        npts = selected_obj_dict.get("npts")
        if npts:
            npts = ast.literal_eval(npts)
        loadshape = selected_obj_dict.get("mult")
        interval = selected_obj_dict.get("interval")
        if interval:
            interval = ast.literal_eval(interval)
        if loadshape:
            loadshape = ast.literal_eval(loadshape)
        hour = selected_obj_dict.get("hour")
        if hour:
            hour = ast.literal_eval(hour)

        if interval == 0:# Check hour points
            if hour:
                loadshape = loadshape[:npts]
            else:
                mdl.info("interval property is zero, but hour property is not defined")
        else:
            loadshape = loadshape[:npts]

        loadshape_prop = mdl.prop(container_handle, "loadshape")

        mdl.set_property_disp_value(loadshape_name_prop, str(loadshape_name))
        mdl.set_property_disp_value(loadshape_prop, str(loadshape))
        mdl.set_property_value(loadshape_name_prop, str(loadshape_name))
        mdl.set_property_value(loadshape_prop, str(loadshape))

def toggle_frequency_prop(mdl, mask_handle):
    frequency_prop = mdl.prop(mask_handle, "basefreq")
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

    frequency_prop = mdl.prop(mask_handle, "basefreq")
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
        toggle_frequency_prop(mdl, mask_handle)
