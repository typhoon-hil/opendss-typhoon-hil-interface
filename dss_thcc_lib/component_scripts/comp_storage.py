import pathlib
import json
import ast
import pandas as pd

import dss_thcc_lib.component_scripts.util as util
import importlib

got_loadshape_points_list = []

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

def update_mode_int_comp(mdl, mask_handle):

    comp_handle = mdl.get_parent(mask_handle)

    mode_prop = mdl.prop(mask_handle, "T_mode")
    ls_calculator_comp = mdl.get_item("Loadshape Point Calculator", parent=comp_handle)
    mode_int_comp = mdl.get_item("mode_int", parent=ls_calculator_comp)

    # mode_int property handler
    mode_int_value_prop = mdl.prop(mode_int_comp, "value")

    # Get mode
    mode = mdl.get_property_value(mode_prop)

    # Save new value
    if mode == "Loadshape index":
        mdl.set_property_value(mode_int_value_prop, "0")
    elif mode == "Time":
        mdl.set_property_value(mode_int_value_prop, "1")


def load_loadshape(mdl, container_handle):
    import os

    # try:
    #     from tse_to_opendss.tse2tpt_base_converter import tse2tpt
    #     import tse_to_opendss
    # except:
    #     # If running from development folder instead of installed package
    #     dss_module_folder = str(pathlib.Path(__file__).parent.parent.parent.parent)
    #     if not dss_module_folder in sys.path:
    #         sys.path.append(dss_module_folder)
    #
    #     from tse_to_opendss.tse2tpt_base_converter import tse2tpt
    #     import tse_to_opendss

    import dss_thcc_lib.gui_scripts.load_object as load_obj

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

        # Property handles
        loadshape_prop = mdl.prop(container_handle, "loadshape")
        loadshape_prop_int = mdl.prop(container_handle, "loadshape_int")
        loadshape_time_range_prop = mdl.prop(container_handle, "T_Ts")
        useactual_prop = mdl.prop(container_handle, "useactual")
        loadshape_from_file_prop = mdl.prop(container_handle, "loadshape_from_file")
        loadshape_from_file_path_prop = mdl.prop(container_handle, "loadshape_from_file_path")
        loadshape_from_file_header_prop = mdl.prop(container_handle, "loadshape_from_file_header")
        loadshape_from_file_column_prop = mdl.prop(container_handle, "loadshape_from_file_column")

        selected_obj_dict = obj_dicts.get("loadshapes").get(selected_object)
        loadshape_name = selected_object

        useactual = selected_obj_dict.get("useactual")
        loadshape_from_file = selected_obj_dict.get("csv_file") == "True"
        loadshape_from_file_path = selected_obj_dict.get("csv_path")
        loadshape_from_file_header = selected_obj_dict.get("headers")
        loadshape_from_file_column = selected_obj_dict.get("column")

        selected_obj_dict = obj_dicts.get("loadshapes").get(selected_object)

        npts = selected_obj_dict.get("npts")
        if npts:
            npts = ast.literal_eval(npts)
        hour = selected_obj_dict.get("hour")
        if hour:
            hour = ast.literal_eval(hour)
        interval = selected_obj_dict.get("interval")
        if interval:
            interval = ast.literal_eval(interval)

        if not loadshape_from_file:
            loadshape = selected_obj_dict.get("mult")
        else:
            selected_obj_dict.update({"loadshape_name": selected_object})
            loadshape = str(read_loadshape_from_json(mdl, container_handle, reload_dict=selected_obj_dict))

        if loadshape:
            loadshape = ast.literal_eval(loadshape)

            if interval == 0:  # Check hour points
                if hour:
                    loadshape = loadshape[:npts]
                else:
                    mdl.info("interval property is zero, but hour property is not defined")
            else:
                loadshape = loadshape[:npts]

            mdl.set_property_disp_value(loadshape_prop, str(loadshape))

        mdl.set_property_disp_value(loadshape_name_prop, str(loadshape_name))
        mdl.set_property_disp_value(loadshape_prop_int, str(interval))
        mdl.set_property_disp_value(loadshape_from_file_prop, str(loadshape_from_file))
        mdl.set_property_disp_value(useactual_prop, useactual)
        if interval == 0:
            if hour:
                mdl.set_property_disp_value(loadshape_time_range_prop, str(hour))
        else:
            time_range_str = f"[{', '.join(str(interval * n) for n in range(1, len(loadshape) + 1))}]"
            mdl.set_property_disp_value(loadshape_time_range_prop, time_range_str)
        mdl.set_property_disp_value(loadshape_from_file_path_prop, str(loadshape_from_file_path))
        mdl.set_property_disp_value(loadshape_from_file_header_prop, str(loadshape_from_file_header))
        mdl.set_property_disp_value(loadshape_from_file_column_prop, str(loadshape_from_file_column))

def get_all_circuit_storages(mdl, mask_handle, parent_comp=None):
    component_list = []
    if parent_comp:  # Component inside a subsystem (recursive function)
        all_components = mdl.get_items(parent_comp)
    else:  # Top level call
        all_components = mdl.get_items()

    for comp in all_components:
        try:
            type_name = mdl.get_component_type_name(comp)
            if type_name and type_name == "Storage":
                component_list.append(comp)
            elif not type_name:  # Component is a subsystem
                component_list.extend(get_all_circuit_storages(mdl, mdl.get_mask(comp), parent_comp=comp))
        except:
            # Some components (such as ports and connections) cannot be used with
            # get_component_type_name
            pass
    # Return the list of component handles
    return component_list

def verify_time_loadshape_sizes(mdl, mask_handle, caller=None):
    import ast

    comp_handle = mdl.get_parent(mask_handle)
    comp_name = mdl.get_name(comp_handle)

    loadshape_prop = mdl.prop(mask_handle, "loadshape")
    time_prop = mdl.prop(mask_handle, "T_Ts")
    loadshape = mdl.get_property_value(loadshape_prop)

    time_list = ast.literal_eval(mdl.get_property_value(time_prop))
    ls_list = ast.literal_eval(loadshape)

    # Verify matching sizes
    mode = mdl.get_property_value(mdl.prop(mask_handle, "T_mode"))
    if mode == "Time" and time_list and ls_list:
        # The time vector and the loadshape must be the same size
        if not len(ls_list) == len(time_list):
            min_points = min(len(time_list), len(ls_list))
            warning_msg = (f"The number of points of the time range property "
                           f"({len(time_list)}) and of the loadshape "
                           f"({len(ls_list)}) must be equal for correct operation. "
                           f"HIL simulation will use the first {min_points} points.")
            mdl.warning(warning_msg, context=mask_handle)
            if caller == "pre_compile":
                if len(time_list) > len(ls_list):
                    mdl.set_property_value(time_prop, time_list[:min_points])
                elif len(time_list) < len(ls_list):
                    mdl.set_property_value(loadshape_prop, ls_list[:min_points])

def time_loadshape_preprocessing(mdl, mask_handle):

    verify_time_loadshape_sizes(mdl, mask_handle, caller="pre_compile")

    loadshape_prop = mdl.prop(mask_handle, "loadshape")
    loadshape = mdl.get_property_value(loadshape_prop)

    ls_list = ast.literal_eval(loadshape)
    ls_n_prop = mdl.prop(mask_handle, "loadshape_n_points")
    mdl.set_property_value(ls_n_prop, len(ls_list))

def restore_all_storages_points(mdl, mask_handle):
    global got_loadshape_points_list

    # Return all components (including inside subsystems)
    all_storages = get_all_circuit_storages(mdl, mask_handle)
    got_loadshape_points_list = []
    for storage in all_storages:
        if storage not in got_loadshape_points_list:
            storage_mask_handle = mdl.get_mask(storage)
            read_loadshape_from_json(mdl, storage_mask_handle)

def read_loadshape_from_json(mdl, mask_handle, reload_dict=None):
    global got_loadshape_points_list

    comp_handle = mdl.get_parent(mask_handle)

    try:
        current_points = ast.literal_eval(mdl.get_property_disp_value(mdl.prop(mask_handle, "loadshape")))
    except:
        current_points = []
    useactual = mdl.get_property_disp_value(mdl.prop(mask_handle, "useactual"))
    interval = mdl.get_property_disp_value(mdl.prop(mask_handle, "loadshape_int"))

    if not reload_dict:
        loadshape_name = mdl.get_property_disp_value(mdl.prop(mask_handle, "loadshape_name"))
        loadshape_from_file = mdl.get_property_value(mdl.prop(mask_handle, "loadshape_from_file")) == "True"
        loadshape_from_file_header = mdl.get_property_value(mdl.prop(mask_handle, "loadshape_from_file_header")) == "True"
        loadshape_from_file_column = mdl.get_property_value(mdl.prop(mask_handle, "loadshape_from_file_column"))
        loadshape_from_file_path = mdl.get_property_value(mdl.prop(mask_handle, "loadshape_from_file_path"))
    else:
        loadshape_name = reload_dict.get("loadshape_name")
        loadshape_from_file = reload_dict.get("csv_file") == "True"
        loadshape_from_file_header = reload_dict.get("headers") == "True"
        loadshape_from_file_column = reload_dict.get("column")
        loadshape_from_file_path = reload_dict.get("csv_path")

    model_path = pathlib.Path(mdl.get_model_file_path())

    if model_path:
        filename = model_path.stem
        data_folder_path = model_path.parent.joinpath(filename + " Target files").joinpath('dss').joinpath("data")
        general_objects_json = data_folder_path.joinpath(f"general_objects.json")
        if general_objects_json.is_file():
            with open(general_objects_json, 'r') as f:
                general_objects_dict = json.load(f)
            loadshape_points = general_objects_dict.get("loadshapes", {}).get(loadshape_name, {}).get("mult", [])
            if loadshape_from_file:
                if pathlib.Path(loadshape_from_file_path).is_file():
                    with open(pathlib.Path(loadshape_from_file_path), 'r', encoding='utf-8-sig') as ls_f:
                        if loadshape_from_file_header:
                            table = pd.read_csv(ls_f)
                            table = table.fillna(0)
                        else:
                            table = pd.read_csv(ls_f, header=None)
                            table = table.fillna(0)
                        loadshape_points = list(table.iloc[:, int(loadshape_from_file_column) - 1])
                    mdl.set_property_value(mdl.prop(mask_handle, "loadshape"), loadshape_points)
                    mdl.set_property_disp_value(mdl.prop(mask_handle, "loadshape"), loadshape_points)
                else:
                    mdl.error(f"Could not find the CSV file '{loadshape_from_file_path}'."
                              f" Please edit or choose a new LoadShape.", context=mdl.get_parent(mask_handle))
                if loadshape_name not in general_objects_dict.get("loadshapes"):
                    with open(general_objects_json, 'w') as f:
                        new_loadshape_dict = {
                            "npts": str(len(current_points)),
                            "mult": "[]",
                            "interval": interval,
                            "interval_unit": "h",
                            "hour": "",
                            "useactual": str(useactual),
                            "csv_file": str(loadshape_from_file),
                            "csv_path": loadshape_from_file_path,
                            "headers": str(loadshape_from_file_header),
                            "column": loadshape_from_file_column
                        }
                        general_objects_dict.get("loadshapes")[loadshape_name] = new_loadshape_dict
                        f.write(json.dumps(general_objects_dict, indent=4))
            elif not loadshape_points:
                new_loadshape_dict = {
                    "npts": str(len(current_points)),
                    "mult": str(current_points),
                    "interval": interval,
                    "interval_unit": "h",
                    "hour": "",
                    "useactual": str(useactual),
                    "csv_file": str(loadshape_from_file),
                    "csv_path": loadshape_from_file_path,
                    "headers": str(loadshape_from_file_header),
                    "column": loadshape_from_file_column
                }

                general_objects_dict.get("loadshapes")[loadshape_name] = new_loadshape_dict
                with open(general_objects_json, 'w') as f:
                    f.write(json.dumps(general_objects_dict, indent=4))
            else:
                mdl.set_property_value(mdl.prop(mask_handle, "loadshape"), loadshape_points)
                mdl.set_property_disp_value(mdl.prop(mask_handle, "loadshape"), loadshape_points)
        else:
            loadshape_points = str(current_points)
            if not data_folder_path.is_dir():
                data_folder_path.mkdir(parents=True)
            with open(general_objects_json, 'w') as f:
                new_loadshape_dict = {
                    "npts": str(len(current_points)),
                    "mult": str(current_points),
                    "interval": interval,
                    "interval_unit": "h",
                    "hour": "",
                    "useactual": str(useactual),
                    "csv_file": str(loadshape_from_file),
                    "csv_path": loadshape_from_file_path,
                    "headers": str(loadshape_from_file_header),
                    "column": loadshape_from_file_column
                }
                f.write(json.dumps({"loadshapes": {loadshape_name: new_loadshape_dict}}, indent=4))

    if comp_handle not in got_loadshape_points_list:
        got_loadshape_points_list.append(comp_handle)

    return loadshape_points

def toggle_frequency_prop(mdl, mask_handle):
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
        toggle_frequency_prop(mdl, mask_handle)


def port_dynamics(mdl, mask_handle, caller_prop_handle=None, init=False):
    comp_handle = mdl.get_parent(mask_handle)
    deleted_ports = []
    created_ports = {}

    return created_ports, deleted_ports


def define_icon(mdl, mask_handle):
    sld_mode_prop = mdl.prop(mask_handle, "sld_mode")
    sld_mode_disp = mdl.get_property_disp_value(sld_mode_prop)

    if sld_mode_disp in (True, "True"):
        mdl.set_component_icon_image(mask_handle, "images/storage_sld.svg")
    else:
        mdl.set_component_icon_image(mask_handle, "images/storage.svg")


def get_sld_conversion_info(mdl, mask_handle, props_state):

    multiline_ports_1 = ["A1", "B1", "C1"]

    port_config_dict = {
        "SLD1": {
            "multiline_ports": multiline_ports_1,
            "side": "right",
            "bus_terminal_position": (-40, 0),
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
        "A1": (-40, -32),
        "B1": (-40, 0),
        "C1": (-40, 32),
    }

    return port_config_dict, tag_config_dict, terminal_positions


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
        if isinstance(mdl.get_property_disp_value(p), str):
            disp_str = str(mdl.get_property_disp_value(p))
            if "[" in disp_str and "]" in disp_str:
                disp_value = str(json.loads(disp_str))
            else:
                disp_value = disp_str
        else:
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

    if new_prop_values.get("sld_mode") in (True, "True"):
        importlib.reload(util)
        sld_info = get_sld_conversion_info(mdl, mask_handle, current_pass_prop_values)
        util.convert_to_sld(mdl, mask_handle, sld_info)

    sld_post_processing(mdl, mask_handle)
    define_icon(mdl, mask_handle)


def sld_post_processing(mdl, mask_handle):
    comp_handle = mdl.get_parent(mask_handle)

    # Resize the buses to 4

    bus1 = mdl.get_item("SLD1_bus", parent=comp_handle)
    if bus1:
        bus1_size_prop = mdl.prop(bus1, "bus_size")
        mdl.set_property_value(bus1_size_prop, 4)
