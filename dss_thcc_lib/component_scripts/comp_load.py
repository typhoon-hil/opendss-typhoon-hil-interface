import pathlib
import json
import ast
import pandas as pd
from typhoon.api.schematic_editor.const import ITEM_CONNECTION, ITEM_COMPONENT
import dss_thcc_lib.component_scripts.util as util
import importlib

got_loadshape_points_list = []
old_state = {}


def mask_edit_restore_visibility(mdl, mask_handle):
    # Restore properties' visual status on load
    prop_list = [
        "tp_connection",
        "phases",
        "pf_mode_3ph",
        "load_model",
        "T_mode",
        "S_Ts_mode",
     ]

    for prop_name in prop_list:
        prop_handle = mdl.prop(mask_handle, prop_name)
        prop_value = mdl.get_property_value(prop_handle)
        mask_dialog_dynamics(mdl, mask_handle, prop_handle, prop_value)

def mask_edit_neutral_impedances(mdl, mask_handle):
    tp_connection_prop = mdl.prop(mask_handle, "tp_connection")
    tp_connection = mdl.get_property_disp_value(tp_connection_prop)
    rneut_prop = mdl.prop(mask_handle, "Rneut")
    rneut_value = mdl.get_property_value(rneut_prop)
    xneut_prop = mdl.prop(mask_handle, "Xneut")
    xneut_value = mdl.get_property_value(xneut_prop)

    if tp_connection == "Y - Grounded":
        # Enable R and X
        mdl.enable_property(mdl.prop(mask_handle, "Rneut"))
        mdl.enable_property(mdl.prop(mask_handle, "Xneut"))
        #
        # We don't want to modify Rneut and Xneut user values.
        #
        if rneut_value == "inf":
            mdl.set_property_disp_value(rneut_prop, "0")
        else:
            mdl.set_property_disp_value(rneut_prop, rneut_value)
        if xneut_value == "inf":
            mdl.set_property_disp_value(xneut_prop, "0")
        else:
            mdl.set_property_disp_value(xneut_prop, xneut_value)
    else:
        # Disable R and X
        mdl.disable_property(mdl.prop(mask_handle, "Rneut"))
        mdl.disable_property(mdl.prop(mask_handle, "Xneut"))
        mdl.set_property_disp_value(rneut_prop, "inf")
        mdl.set_property_disp_value(xneut_prop, "inf")

def mask_edit_zero_sequence(mdl, mask_handle):
    load_model_prop = mdl.prop(mask_handle, "load_model")
    load_model = mdl.get_property_disp_value(load_model_prop)

    phases_prop = mdl.prop(mask_handle, "phases")
    phases = mdl.get_property_disp_value(phases_prop)

    if phases == "3" and (not load_model == "Constant Impedance"):
        mdl.enable_property(mdl.prop(mask_handle, "zero_seq_remove"))
    else:
        mdl.set_property_disp_value(mdl.prop(mask_handle, 'zero_seq_remove'),
                                    False)
        mdl.disable_property(mdl.prop(mask_handle, "zero_seq_remove"))

def mask_dialog_dynamics(mdl, mask_handle, prop_handle, new_value):

    prop_name = mdl.get_name(prop_handle)

    if prop_name == "tp_connection":
        mask_edit_neutral_impedances(mdl, mask_handle)

    elif prop_name == "sld_mode":

        phases_prop = mdl.prop(mask_handle, "phases")
        phases_disp = mdl.get_property_disp_value(phases_prop)
        sld_1ph_pick_prop = mdl.prop(mask_handle, "sld_1ph_pick")
        load_model_prop = mdl.prop(mask_handle, "load_model")
        load_model_disp = mdl.get_property_disp_value(load_model_prop)

        if new_value:
            if phases_disp == "1":
                mdl.show_property(sld_1ph_pick_prop)
            else:
                mdl.hide_property(sld_1ph_pick_prop)
        else:
            mdl.hide_property(sld_1ph_pick_prop)

    elif prop_name == "phases":
        mask_edit_zero_sequence(mdl, mask_handle)

        # 3-phase CPL demands grounded connection
        tp_connection_prop = mdl.prop(mask_handle, "tp_connection")
        if new_value == "3":
            if not load_model_disp == "Constant Impedance":
                mdl.set_property_disp_value(tp_connection_prop, "Y - Grounded")
                mdl.disable_property(tp_connection_prop)
            else:
                mdl.enable_property(tp_connection_prop)
        else:
            mdl.enable_property(tp_connection_prop)
        mask_edit_neutral_impedances(mdl, mask_handle)

        sld_mode_prop = mdl.prop(mask_handle, "sld_mode")
        sld_mode_disp = mdl.get_property_disp_value(sld_mode_prop)
        sld_1ph_pick_prop = mdl.prop(mask_handle, "sld_1ph_pick")

        if new_value == "1":
            if sld_mode_disp in (True, "True"):
                mdl.show_property(sld_1ph_pick_prop)
            else:
                mdl.hide_property(sld_1ph_pick_prop)
        else:
            mdl.hide_property(sld_1ph_pick_prop)

    elif prop_name == "load_model":
        
        mask_edit_zero_sequence(mdl, mask_handle)

        tp_connection_prop = mdl.prop(mask_handle, "tp_connection")

        zip_vector_prop = mdl.prop(mask_handle, "zip_vector")
        zip_vector_q_prop = mdl.prop(mask_handle, "zip_vector_Q")

        zip_internal_n_prop = mdl.prop(mask_handle, "zip_internal_n")
        zip_internal_n = mdl.get_property_disp_value(zip_internal_n_prop)
        zip_internal_n_q_prop = mdl.prop(mask_handle, "zip_internal_n_Q")
        zip_internal_n_q = mdl.get_property_disp_value(zip_internal_n_q_prop)

        enable_prop_list = [
            "Pow_ref_s",
            "execution_rate",
            "Tfast",
            "CPL_LMT",
            "v_min_max",
            "rate_lmt",
            "q_gain_k",
            "r_gain_k",
        ]
        if new_value == "Constant Impedance":
            # Enable properties of the list
            for pname in enable_prop_list:
                mdl.disable_property(mdl.prop(mask_handle, pname))

            mdl.enable_property(tp_connection_prop)
            mdl.set_property_disp_value(mdl.prop(mask_handle, 'Pow_ref_s'),
                                        "Fixed")
        else:
            # Disable properties of the list
            for pname in enable_prop_list:
                mdl.enable_property(mdl.prop(mask_handle, pname))

            # 3-phase CPL demands grounded connection
            phases_prop = mdl.prop(mask_handle, "phases")
            phases = mdl.get_property_disp_value(phases_prop)
            tp_connection_prop = mdl.prop(mask_handle, "tp_connection")

            if phases == "3":
                mdl.set_property_disp_value(tp_connection_prop, "Y - Grounded")
                mdl.disable_property(tp_connection_prop)
            else:
                mdl.enable_property(tp_connection_prop)
            mask_edit_neutral_impedances(mdl, mask_handle)

        if new_value == "Constant Power":
            mdl.set_property_disp_value(mdl.prop(mask_handle, 'zip_internal'),
                                        "[0,0,1]")
            mdl.set_property_disp_value(mdl.prop(mask_handle, 'zip_internal_Q'),
                                        "[0,0,1]")

        if new_value == "Constant Z,I,P":
            mdl.show_property(zip_vector_prop)
            mdl.show_property(zip_vector_q_prop)
            mdl.set_property_disp_value(mdl.prop(mask_handle, 'zip_internal'),
                                        zip_internal_n)
            mdl.set_property_disp_value(mdl.prop(mask_handle, 'zip_internal_Q'),
                                        zip_internal_n_q)
        else:
            mdl.hide_property(zip_vector_prop)
            mdl.hide_property(zip_vector_q_prop)

    elif prop_name == "pf_mode_3ph":
        if new_value == "Unit":
            mdl.disable_property(mdl.prop(mask_handle, "pf_3ph"))
        else:
            mdl.enable_property(mdl.prop(mask_handle, "pf_3ph"))

    elif prop_name == "T_mode":
        if new_value == "Time":
            mdl.enable_property(mdl.prop(mask_handle, "T_Ts"))
        else:
            mdl.disable_property(mdl.prop(mask_handle, "T_Ts"))

    elif prop_name == "S_Ts_mode":
        if new_value == "Manual input":
            mdl.disable_property(mdl.prop(mask_handle, "T_Ts_max"))
            mdl.disable_property(mdl.prop(mask_handle, "del_Ts"))
            mdl.enable_property(mdl.prop(mask_handle, "T_Ts"))
        else:
            mdl.enable_property(mdl.prop(mask_handle, "T_Ts_max"))
            mdl.enable_property(mdl.prop(mask_handle, "del_Ts"))
            mdl.disable_property(mdl.prop(mask_handle, "T_Ts"))

def zip_change_fnc(mdl, mask_handle, new_value):
    zip_vector_prop = mdl.prop(mask_handle, "zip_vector")
    zip_vector = mdl.get_property_disp_value(zip_vector_prop)

    zip_vector_q_prop = mdl.prop(mask_handle, "zip_vector_Q")
    zip_vector_q = mdl.get_property_disp_value(zip_vector_q_prop)

    no_bracket = zip_vector.strip("[]")
    no_bracket_q = zip_vector_q.strip("[]")
    zip_list = [float(s) for s in no_bracket.split(',')]
    zip_list_q = [float(s) for s in no_bracket_q.split(',')]
    zip_len = len(zip_list)
    zip_len_q = len(zip_list_q)
    zip_norm = [0, 0, 0]
    zip_norm_q = [0, 0, 0]

    if zip_len == 3:
        zip_total = zip_list[0] + zip_list[1] + zip_list[2]
        if not zip_total == 0:
            zip_norm = [value / zip_total for value in zip_list]
    elif zip_len > 3:
        zip_total = zip_list[0] + zip_list[1] + zip_list[2]
        if not zip_total == 0:
            zip_norm = [value / zip_total for value in
                        [zip_list[0], zip_list[1], zip_list[2]]]
    elif zip_len == 2:
        zip_total = zip_list[0] + zip_list[1]
        if not zip_total == 0:
            zip_norm = [value / zip_total for value in [zip_list[0], zip_list[1], 0]]
    else:
        if not zip_list[0] == 0:
            zip_norm = [1, 0, 0]

    if zip_len_q == 3:
        zip_total_q = zip_list_q[0] + zip_list_q[1] + zip_list_q[2]
        if not zip_total_q == 0:
            zip_norm_q = [value / zip_total_q for value in zip_list_q]
    elif zip_len_q > 3:
        zip_total_q = zip_list_q[0] + zip_list_q[1] + zip_list_q[2]
        if not zip_total_q == 0:
            zip_norm_q = [value / zip_total_q for value in
                          [zip_list_q[0], zip_list_q[1], zip_list_q[2]]]
    elif zip_len_q == 2:
        zip_total_q = zip_list_q[0] + zip_list_q[1]
        if not zip_total_q == 0:
            zip_norm_q = [value / zip_total_q for value in
                          [zip_list_q[0], zip_list_q[1], 0]]
    else:
        if not zip_list_q[0] == 0:
            zip_norm_q = [1, 0, 0]

    idx = 0
    for elem in zip_norm:
        zip_norm[idx] = round(elem, 3)
        idx = idx + 1

    idx_q = 0
    for elem in zip_norm_q:
        zip_norm_q[idx_q] = round(elem, 3)
        idx_q = idx_q + 1

    zipv_dss = [zip_norm[0], zip_norm[1], zip_norm[2], zip_norm_q[0], zip_norm_q[1],
                zip_norm_q[2], 0]

    mdl.set_property_disp_value(mdl.prop(mask_handle, 'zip_internal_n'),
                                str(zip_norm))
    mdl.set_property_value(mdl.prop(mask_handle, 'zip_internal_n'), str(zip_norm))
    mdl.set_property_disp_value(mdl.prop(mask_handle, 'zip_internal'),
                                str(zip_norm))
    mdl.set_property_value(mdl.prop(mask_handle, 'zip_internal'), str(zip_norm))

    mdl.set_property_disp_value(mdl.prop(mask_handle, 'zip_internal_n_Q'),
                                str(zip_norm_q))
    mdl.set_property_value(mdl.prop(mask_handle, 'zip_internal_n_Q'),
                           str(zip_norm_q))
    mdl.set_property_disp_value(mdl.prop(mask_handle, 'zip_internal_Q'),
                                str(zip_norm_q))
    mdl.set_property_value(mdl.prop(mask_handle, 'zip_internal_Q'),
                           str(zip_norm_q))

    mdl.set_property_disp_value(mdl.prop(mask_handle, 'ZIPV'), str(zipv_dss))
    mdl.set_property_value(mdl.prop(mask_handle, 'ZIPV'), str(zipv_dss))


def load_loadshape(mdl, mask_handle):
    import os
    import sys
    import pathlib

    try:
        from tse_to_opendss.tse2tpt_base_converter import tse2tpt
        import tse_to_opendss
    except:
        # If running from development folder instead of installed package
        dss_module_folder = str(pathlib.Path(__file__).parent.parent.parent.parent)
        if dss_module_folder not in sys.path:
            sys.path.append(dss_module_folder)

        from tse_to_opendss.tse2tpt_base_converter import tse2tpt
        import tse_to_opendss

    import dss_thcc_lib.gui_scripts.load_object as load_obj
    import json
    import ast

    # Find objects file
    mdlfile = mdl.get_model_file_path()
    mdlfile_name = pathlib.Path(mdlfile).stem
    mdlfile_folder = pathlib.Path(mdlfile).parents[0]
    mdlfile_target_folder = mdlfile_folder.joinpath(mdlfile_name + ' Target files')
    dss_folder_path = pathlib.Path(mdlfile_target_folder).joinpath('dss')
    fname = os.path.join(dss_folder_path, 'data', 'general_objects.json')

    loadshape_name_prop = mdl.prop(mask_handle, "loadshape_name")
    loadshape_name = mdl.get_property_value(loadshape_name_prop)
    loadshape_name = "" if loadshape_name == "-" else loadshape_name

    obj_type = "LoadShape"

    try:
        with open(fname, 'r') as f:
            obj_dicts = json.load(f)
    except FileNotFoundError:
        obj_dicts = None

    if obj_dicts:
        new_load_window = load_obj.LoadObject(mdl, obj_type, obj_dicts=obj_dicts,
                                              starting_object=loadshape_name)
    else:
        new_load_window = load_obj.LoadObject(mdl, obj_type)

    if new_load_window.exec():
        selected_object = new_load_window.selected_object

        obj_dicts = new_load_window.obj_dicts

        # Property handles
        loadshape_prop = mdl.prop(mask_handle, "loadshape")
        loadshape_prop_int = mdl.prop(mask_handle, "loadshape_int")
        loadshape_prop_time = mdl.prop(mask_handle, "T_Ts")
        useactual_prop = mdl.prop(mask_handle, "useactual")
        loadshape_from_file_prop = mdl.prop(mask_handle, "loadshape_from_file")
        loadshape_from_file_path_prop = mdl.prop(mask_handle,
                                                 "loadshape_from_file_path")
        loadshape_from_file_header_prop = mdl.prop(mask_handle,
                                                   "loadshape_from_file_header")
        loadshape_from_file_column_prop = mdl.prop(mask_handle,
                                                   "loadshape_from_file_column")

        selected_obj_dict = obj_dicts.get("loadshapes").get(selected_object)
        loadshape_name = selected_object

        useactual = selected_obj_dict.get("useactual")
        loadshape_from_file = selected_obj_dict.get("csv_file") == "True"
        loadshape_from_file_path = selected_obj_dict.get("csv_path")
        loadshape_from_file_header = selected_obj_dict.get("headers")
        loadshape_from_file_column = selected_obj_dict.get("column")

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
            loadshape = str(read_loadshape_from_json(mdl, mask_handle,
                                                     reload_dict=selected_obj_dict))

        if loadshape:
            loadshape = ast.literal_eval(loadshape)

            if interval == 0:  # Check hour points
                if hour:
                    loadshape = loadshape[:npts]
                else:
                    mdl.info(
                        "interval property is zero, but hour property is not defined")
            else:
                loadshape = loadshape[:npts]

            mdl.set_property_disp_value(loadshape_prop, str(loadshape))

        mdl.set_property_disp_value(loadshape_name_prop, str(loadshape_name))
        mdl.set_property_disp_value(loadshape_prop_int, str(interval))
        mdl.set_property_disp_value(loadshape_from_file_prop, str(loadshape_from_file))
        mdl.set_property_disp_value(useactual_prop, useactual)
        if interval == 0:
            if hour:
                mdl.set_property_disp_value(loadshape_prop_time, str(hour))
        else:
            time_range_str = f"[{', '.join(str(interval * n) for n in range(1, len(loadshape) + 1))}]"
            mdl.set_property_disp_value(loadshape_prop_time, time_range_str)
        mdl.set_property_disp_value(loadshape_from_file_path_prop,
                                    str(loadshape_from_file_path))
        mdl.set_property_disp_value(loadshape_from_file_header_prop,
                                    str(loadshape_from_file_header))
        mdl.set_property_disp_value(loadshape_from_file_column_prop,
                                    str(loadshape_from_file_column))


def toggle_frequency_prop(mdl, mask_handle, init=False):
    frequency_prop = mdl.prop(mask_handle, "fn")
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
    frequency_prop = mdl.prop(mask_handle, "fn")
    global_frequency_prop = mdl.prop(mask_handle, "global_basefreq")
    use_global = mdl.get_property_value(global_frequency_prop)

    if init:
        mdl.hide_property(frequency_prop)
    else:
        if use_global:
            if "simdss_basefreq" in mdl.get_ns_vars():
                mdl.set_property_value(frequency_prop,
                                       mdl.get_ns_var("simdss_basefreq"))
            else:
                mdl.set_property_value(global_frequency_prop, False)
        toggle_frequency_prop(mdl, mask_handle, init)


def define_icon(mdl, mask_handle):
    phases = mdl.get_property_disp_value(mdl.prop(mask_handle, "phases"))
    tp_connection = mdl.get_property_disp_value(mdl.prop(mask_handle, "tp_connection"))
    sld_mode = mdl.get_property_disp_value(mdl.prop(mask_handle, "sld_mode"))
    sld_1ph_pick = mdl.get_property_disp_value(mdl.prop(mask_handle, "sld_1ph_pick"))

    if tp_connection == "Y - Grounded":
        grounded = True
    else:
        grounded = False

    if int(phases) == 1:
        if grounded:
            if sld_mode in (True, "True"):
                if sld_1ph_pick == "A":
                    mdl.set_component_icon_image(mask_handle, 'images/load_1Yg_sld_a.svg')
                elif sld_1ph_pick == "B":
                    mdl.set_component_icon_image(mask_handle, 'images/load_1Yg_sld_b.svg')
                elif sld_1ph_pick == "C":
                    mdl.set_component_icon_image(mask_handle, 'images/load_1Yg_sld_c.svg')
                else:
                    mdl.set_component_icon_image(mask_handle, 'images/load_1Yg_sld_a.svg')
            else:
                mdl.set_component_icon_image(mask_handle, 'images/load_1Yg.svg')
        else:
            if sld_mode in (True, "True"):
                if tp_connection == 'Δ':
                    if sld_1ph_pick == "A":
                        mdl.set_component_icon_image(mask_handle, 'images/load_1D_sld_ab.svg')
                    elif sld_1ph_pick == "B":
                        mdl.set_component_icon_image(mask_handle, 'images/load_1D_sld_bc.svg')
                    elif sld_1ph_pick == "C":
                        mdl.set_component_icon_image(mask_handle, 'images/load_1D_sld_ca.svg')
                    else:
                        mdl.set_component_icon_image(mask_handle, 'images/load_1D_sld_ab.svg')
                else:
                    if sld_1ph_pick == "A":
                        mdl.set_component_icon_image(mask_handle, 'images/load_1Y_sld_a.svg')
                    elif sld_1ph_pick == "B":
                        mdl.set_component_icon_image(mask_handle, 'images/load_1Y_sld_b.svg')
                    elif sld_1ph_pick == "C":
                        mdl.set_component_icon_image(mask_handle, 'images/load_1Y_sld_c.svg')
                    else:
                        mdl.set_component_icon_image(mask_handle, 'images/load_1Y_sld_a.svg')
            else:
                mdl.set_component_icon_image(mask_handle, 'images/load_1Y.svg')
    else:
        if grounded:
            if sld_mode in (True, "True"):
                mdl.set_component_icon_image(mask_handle, 'images/load_3Yg_sld.svg')
            else:
                mdl.set_component_icon_image(mask_handle, 'images/load_3Yg.svg')
        else:
            if tp_connection == 'Δ':
                if sld_mode in (True, "True"):
                    mdl.set_component_icon_image(mask_handle, 'images/load_3D_sld.svg')
                else:
                    mdl.set_component_icon_image(mask_handle, 'images/load_3D.svg')
            else:
                if sld_mode in (True, "True"):
                    mdl.set_component_icon_image(mask_handle, 'images/load_3Y_sld.svg')
                else:
                    mdl.set_component_icon_image(mask_handle, 'images/load_3Y.svg')

    #
    # Set text
    #

    mdl.set_color(mask_handle, "blue")
    if sld_mode in (False, "False"):
        # Neutral
        if tp_connection in ("Y", "Y - Grounded"):
            if phases == "3":
                mdl.disp_component_icon_text(mask_handle, "N", rotate="rotate",
                                             relpos_x=0.81, relpos_y=0.12,
                                             size=8, trim_factor=2)
            elif tp_connection == "Y":
                mdl.disp_component_icon_text(mask_handle, "N", rotate="rotate",
                                             relpos_x=0.92, relpos_y=0.5,
                                             size=8, trim_factor=2)


def port_dynamics(mdl, mask_handle, caller_prop_handle=None, init=False):
    comp_handle = mdl.get_parent(mask_handle)
    # deleted_ports = []
    created_ports = {}

    tp_connection_prop = mdl.prop(mask_handle, "tp_connection")
    tp_connection = mdl.get_property_disp_value(tp_connection_prop)

    load_model_prop = mdl.prop(mask_handle, "load_model")
    load_model = mdl.get_property_disp_value(load_model_prop)

    phases_prop = mdl.prop(mask_handle, "phases")
    phases = mdl.get_property_disp_value(phases_prop)

    pow_ref_s_prop = mdl.prop(mask_handle, "Pow_ref_s")
    pow_ref_s = mdl.get_property_disp_value(pow_ref_s_prop)

    if phases == "3":
        port_a = mdl.get_item("A1", parent=comp_handle, item_type="port")
        port_b = mdl.get_item("B1", parent=comp_handle, item_type="port")
        port_c = mdl.get_item("C1", parent=comp_handle, item_type="port")

        p_ext = mdl.get_item("P", parent=comp_handle, item_type="port")
        q_ext = mdl.get_item("Q", parent=comp_handle, item_type="port")

        if tp_connection == 'Δ':
            pos_port_a1 = (-32, -24)
            pos_port_b1 = (0, -24)
            pos_port_c1 = (32, -24)
            pos_p_ext = (50, -15)
            pos_q_ext = (50, 15)
        else:
            pos_port_a1 = (-48, -24)
            pos_port_b1 = (-16, -24)
            pos_port_c1 = (16, -24)
            pos_p_ext = (65, -15)
            pos_q_ext = (65, 15)

        if p_ext:
            mdl.set_port_properties(p_ext, terminal_position=pos_p_ext)
            created_ports.update({"P_ext": p_ext})
        if q_ext:
            mdl.set_port_properties(q_ext, terminal_position=pos_q_ext)
            created_ports.update({"Q_ext": q_ext})

        if not port_a:
            port_a = mdl.create_port(parent=comp_handle, name="A1", direction="out",
                                     kind="pe",
                                     terminal_position=pos_port_a1, hide_name=True,
                                     position=(7802, 7862), rotation="right")
        else:
            mdl.set_port_properties(port_a, terminal_position=pos_port_a1)
        created_ports.update({"portA": port_a})

        if not port_b:
            port_b = mdl.create_port(parent=comp_handle, name="B1", direction="out",
                                     kind="pe",
                                     terminal_position=pos_port_b1, hide_name=True,
                                     position=(7919, 7862), rotation="right")
        else:
            mdl.set_port_properties(port_b, terminal_position=pos_port_b1)
        created_ports.update({"portB": port_b})

        if not port_c:
            port_c = mdl.create_port(parent=comp_handle, name="C1", direction="out",
                                     kind="pe",
                                     terminal_position=pos_port_c1, hide_name=True,
                                     position=(8055, 7862), rotation="right")
        else:
            mdl.set_port_properties(port_c, terminal_position=pos_port_c1)
        created_ports.update({"portC": port_c})

        port_n = mdl.get_item("N1", parent=comp_handle, item_type="port")
        if tp_connection in ("Y", "Y - Grounded"):
            if not port_n:
                port_n = mdl.create_port(parent=comp_handle, name="N1", direction="out",
                                         kind="pe",
                                         terminal_position=(48, -24), hide_name=True,
                                         position=(7921, 8384), rotation="right")
            else:
                mdl.set_port_properties(port_n, terminal_position=(48, -24))

            created_ports.update({"portN": port_n})
        else:
            if port_n:
                mdl.delete_item(port_n)

    elif phases == "1":
        port_a = mdl.get_item("A1", parent=comp_handle, item_type="port")
        port_b = mdl.get_item("B1", parent=comp_handle, item_type="port")
        port_c = mdl.get_item("C1", parent=comp_handle, item_type="port")

        p_ext = mdl.get_item("P", parent=comp_handle, item_type="port")
        q_ext = mdl.get_item("Q", parent=comp_handle, item_type="port")

        if tp_connection == "Y - Grounded":
            pos_port_a = (0, -24)
            pos_p_ext = (24, -16)
            pos_q_ext = (24, 16)

            if port_b:
                mdl.delete_item(port_b)
                created_ports.pop("portB", None)

        else:
            pos_port_a = (-16, -12)
            pos_port_b = (16, -12)
            pos_p_ext = (16, -16)
            pos_q_ext = (16, 16)

            if not port_b:
                port_b = mdl.create_port(parent=comp_handle, name="B1", direction="out",
                                         kind="pe",
                                         terminal_position=pos_port_b, hide_name=True,
                                         position=(7919, 7862), rotation="right")
            else:
                mdl.set_port_properties(port_b, terminal_position=pos_port_b)

            created_ports.update({"portB": port_b})

        if p_ext:
            mdl.set_port_properties(p_ext, terminal_position=pos_p_ext)
            created_ports.update({"P_ext": p_ext})
        if q_ext:
            mdl.set_port_properties(q_ext, terminal_position=pos_q_ext)
            created_ports.update({"Q_ext": q_ext})

        if not port_a:
            port_a = mdl.create_port(parent=comp_handle, name="A1", direction="out",
                                     kind="pe",
                                     terminal_position=pos_port_a, hide_name=True,
                                     position=(7802, 7862), rotation="right")
        else:
            mdl.set_port_properties(port_a, terminal_position=pos_port_a)

        created_ports.update({"portA": port_a})

        # In the single-phase system, we don't need the Neutral output
        port_n = mdl.get_item("N1", parent=comp_handle, item_type="port")
        if port_n:
            mdl.delete_item(port_n)
            created_ports.pop("portN", None)

        if port_c:
            mdl.delete_item(port_c)
            created_ports.pop("portC", None)

    if tp_connection == "Δ" and load_model == "Constant Impedance":
        port_n = mdl.get_item("N1", parent=comp_handle, item_type="port")
        if port_n:
            mdl.delete_item(port_n)
            created_ports.pop("portN", None)

    if load_model == "Constant Power" or load_model == "Constant Z,I,P":
        if pow_ref_s == "Fixed":

            p_ext = mdl.get_item("P", parent=comp_handle, item_type="port")
            q_ext = mdl.get_item("Q", parent=comp_handle, item_type="port")

            if p_ext:
                mdl.delete_item(p_ext)
                created_ports.pop("P_ext", None)
            if q_ext:
                mdl.delete_item(q_ext)
                created_ports.pop("Q_ext", None)

            t_ext = mdl.get_item("T", parent=comp_handle, item_type="port")
            if t_ext:
                mdl.delete_item(t_ext)
            created_ports.pop("T_ext", None)

        elif pow_ref_s == "External input":
            if phases == "1":
                if tp_connection == "Y - Grounded":
                    p_term_position = (24, -15)
                    q_term_position = (24, 15)
                else:
                    p_term_position = (16, -15)
                    q_term_position = (16, 15)
            else:
                if tp_connection == 'Δ':
                    p_term_position = (48, -15)
                    q_term_position = (48, 15)
                else:
                    p_term_position = (64, -15)
                    q_term_position = (64, 15)

            p_ext = mdl.get_item("P", parent=comp_handle, item_type="port")
            if not p_ext:
                p_ext = mdl.create_port(parent=comp_handle, name="P", direction="in",
                                        kind="sp",
                                        terminal_position=p_term_position,
                                        position=(7680, 8175))
            created_ports.update({"P_ext": p_ext})

            q_ext = mdl.get_item("Q", parent=comp_handle, item_type="port")
            if not q_ext:
                q_ext = mdl.create_port(parent=comp_handle, name="Q", direction="in",
                                        kind="sp",
                                        terminal_position=q_term_position,
                                        position=(7680, 8240))
            created_ports.update({"Q_ext": q_ext})

            t_ext = mdl.get_item("T", parent=comp_handle, item_type="port")
            if t_ext:
                mdl.delete_item(t_ext)
            created_ports.pop("T_ext", None)

        else:  # if pow_ref_s == "Time Series"

            p_ext = mdl.get_item("P", parent=comp_handle, item_type="port")
            q_ext = mdl.get_item("Q", parent=comp_handle, item_type="port")

            if p_ext:
                mdl.delete_item(p_ext)
                created_ports.pop("P_ext", None)
            if q_ext:
                mdl.delete_item(q_ext)
                created_ports.pop("Q_ext", None)

            if phases == "1":
                if tp_connection == "Y - Grounded":
                    term_position = (25, 0)
                else:
                    term_position = (16, 0)
            else:
                if tp_connection == 'Δ':
                    term_position = (50, 0)
                else:
                    term_position = (65, 0)

            t_ext = mdl.get_item("T", parent=comp_handle, item_type="port")
            if not t_ext:
                t_ext = mdl.create_port(parent=comp_handle, name="T", direction="in",
                                        kind="sp",
                                        terminal_position=term_position,
                                        position=(7368, 8400))
            else:
                mdl.set_port_properties(t_ext, terminal_position=term_position)
            created_ports.update({"T_ext": t_ext})
    else:
        p_ext = mdl.get_item("P", parent=comp_handle, item_type="port")
        q_ext = mdl.get_item("Q", parent=comp_handle, item_type="port")
        t_ext = mdl.get_item("T", parent=comp_handle, item_type="port")

        if p_ext:
            mdl.delete_item(p_ext)
            created_ports.pop("P_ext", None)
        if q_ext:
            mdl.delete_item(q_ext)
            created_ports.pop("Q_ext", None)
        if t_ext:
            mdl.delete_item(t_ext)
        created_ports.pop("T_ext", None)

    return created_ports


def create_tags_and_connections_to_ports(mdl, mask_handle, created_ports):
    comp_handle = mdl.get_parent(mask_handle)

    phases_prop = mdl.prop(mask_handle, "phases")
    phases = mdl.get_property_disp_value(phases_prop)

    tp_connection_prop = mdl.prop(mask_handle, "tp_connection")
    tp_connection = mdl.get_property_disp_value(tp_connection_prop)

    tags_dict = {"TagA1": {"position": (7800, 7944), "rotation": "left"},
                 "TagB1": {"position": (7920, 7944), "rotation": "left"},
                 "TagC1": {"position": (8056, 7944), "rotation": "left"},
                 "TagA2": {"position": (7856, 8088), "rotation": "right"},
                 "TagB2": {"position": (7920, 8088), "rotation": "right"},
                 "TagC2": {"position": (7984, 8088), "rotation": "right"},
                 "TagB3": {"position": (7920, 8400), "rotation": "left"}}

    if int(phases) == 3:
        for phase in ["A", "B", "C"]:
            tag1 = mdl.get_item(f"Tag{phase}1", parent=comp_handle, item_type="tag")
            if tag1:
                mdl.delete_item(tag1)
            tag1 = mdl.create_tag(f"{phase}1", name=f"Tag{phase}1", parent=comp_handle,
                                  scope="local", kind="pe",
                                  rotation=tags_dict[f"Tag{phase}1"]["rotation"],
                                  position=tags_dict[f"Tag{phase}1"]["position"])

            mdl.create_connection(tag1, created_ports.get(f"port{phase}"))

            tag2 = mdl.get_item(f"Tag{phase}2", parent=comp_handle, item_type="tag")
            if tag2:
                mdl.delete_item(tag2)
            mdl.create_tag(f"{phase}1", name=f"Tag{phase}2", parent=comp_handle,
                           scope="local", kind="pe",
                           rotation=tags_dict[f"Tag{phase}2"]["rotation"],
                           position=tags_dict[f"Tag{phase}2"]["position"])

            if phase == "B":
                tag3 = mdl.get_item(f"Tag{phase}3", parent=comp_handle, item_type="tag")
                if tag3:
                    mdl.delete_item(tag3)

    elif int(phases) == 1:
        for phase in ["A", "B", "C"]:
            tag1 = mdl.get_item(f"Tag{phase}1", parent=comp_handle, item_type="tag")
            if tag1:
                mdl.delete_item(tag1)

            tag2 = mdl.get_item(f"Tag{phase}2", parent=comp_handle, item_type="tag")
            if tag2:
                mdl.delete_item(tag2)

            if phase == "A":
                tag1 = mdl.create_tag(f"{phase}1", name=f"Tag{phase}1",
                                      parent=comp_handle, scope="local", kind="pe",
                                      rotation=tags_dict[f"Tag{phase}1"]["rotation"],
                                      position=tags_dict[f"Tag{phase}1"]["position"])
                mdl.create_connection(tag1, created_ports.get(f"port{phase}"))

                mdl.create_tag(f"{phase}1", name=f"Tag{phase}2", parent=comp_handle,
                               scope="local", kind="pe",
                               rotation=tags_dict[f"Tag{phase}2"]["rotation"],
                               position=tags_dict[f"Tag{phase}2"]["position"])

            if phase == "B":
                tag3 = mdl.get_item(f"Tag{phase}3", parent=comp_handle, item_type="tag")
                if tag3:
                    mdl.delete_item(tag3)

                if tp_connection in ("Y", "Δ"):
                    tag1 = mdl.create_tag(f"{phase}1", name=f"Tag{phase}1",
                                          parent=comp_handle, scope="local",
                                          kind="pe",
                                          rotation=tags_dict[f"Tag{phase}1"][
                                              "rotation"],
                                          position=tags_dict[f"Tag{phase}1"][
                                              "position"])
                    mdl.create_connection(tag1, created_ports.get(f"port{phase}"))

                    tag3 = mdl.create_tag(f"{phase}1", name=f"Tag{phase}3",
                                          parent=comp_handle,
                                          scope="local", kind="pe",
                                          rotation=tags_dict[f"Tag{phase}3"][
                                              "rotation"],
                                          position=tags_dict[f"Tag{phase}3"][
                                              "position"])

                    jun_n = mdl.get_item("JN", parent=comp_handle, item_type="junction")
                    if jun_n:
                        mdl.create_connection(tag3, jun_n)


def connections_dynamics(mdl, mask_handle, created_ports):

    comp_handle = mdl.get_parent(mask_handle)

    tp_connection_prop = mdl.prop(comp_handle, "tp_connection")
    tp_connection = mdl.get_property_disp_value(tp_connection_prop)

    load_model_prop = mdl.prop(mask_handle, "load_model")
    load_model = mdl.get_property_disp_value(load_model_prop)

    phases_prop = mdl.prop(mask_handle, "phases")
    phases = mdl.get_property_disp_value(phases_prop)

    if load_model == "Constant Impedance":
        load = mdl.get_item("CIL", parent=comp_handle, item_type="component")

    elif load_model == "Constant Power":
        load = mdl.get_item("CPL", parent=comp_handle, item_type="component")

    elif load_model == "Constant Z,I,P":
        load = mdl.get_item("CPL", parent=comp_handle, item_type="component")

    # This loop connects the Load tags to the CIL terminals
    if int(phases) == 1:
        phase_list = ["A"]
    else:
        phase_list = ["A", "B", "C"]

    for phase in phase_list:
        tag = mdl.get_item(
            f"Tag{phase}2",
            parent=comp_handle,
            item_type="tag",
        )
        if tag:
            conn_tmp = mdl.find_connections(tag, mdl.term(load, f"{phase}1"))
            if len(conn_tmp) == 0:
                mdl.create_connection(tag, mdl.term(load, f"{phase}1"))

    jun_n = mdl.get_item("JN", parent=comp_handle, item_type="junction")
    port_n = mdl.get_item("N1", parent=comp_handle, item_type="port")

    if tp_connection == "Y":
        if not jun_n:
            jun_n = mdl.create_junction(name='JN', parent=comp_handle, kind='pe',
                                        position=(7921, 8326))

        conn_n_load = mdl.get_item("Conn_AN", parent=comp_handle,
                                   item_type=ITEM_CONNECTION)
        if not conn_n_load:
            mdl.create_connection(mdl.term(load, "N"), jun_n, name="Conn_AN")

        if int(phases) == 3:
            conn_n2port = mdl.get_item("Conn_N", parent=comp_handle,
                                       item_type=ITEM_CONNECTION)
            if not conn_n2port:
                mdl.create_connection(jun_n, port_n, name="Conn_N")

    elif tp_connection == "Y - Grounded":
        if not jun_n:
            jun_n = mdl.create_junction(name='JN', parent=comp_handle, kind='pe',
                                        position=(7921, 8326))

        conn_n_load = mdl.get_item("Conn_AN", parent=comp_handle,
                                   item_type=ITEM_CONNECTION)
        if not conn_n_load:
            mdl.create_connection(mdl.term(load, "N"), jun_n, name="Conn_AN")

        if int(phases) == 3:
            conn_n2port = mdl.get_item("Conn_N", parent=comp_handle,
                                       item_type=ITEM_CONNECTION)
            if not conn_n2port:
                mdl.create_connection(jun_n, port_n, name="Conn_N")

    elif tp_connection == "Δ":
        if int(phases) == 1:
            if not jun_n:
                jun_n = mdl.create_junction(name='JN', parent=comp_handle, kind='pe',
                                            position=(7921, 8326))

            conn_n_load = mdl.get_item("Conn_AN", parent=comp_handle,
                                       item_type=ITEM_CONNECTION)
            if not conn_n_load:
                mdl.create_connection(mdl.term(load, "N"), jun_n, name="Conn_AN")
        else:
            if jun_n:
                mdl.delete_item(jun_n)


#
# This function manages the mask properties
# If tp_connection == "Y - Grounded", the fields for Rneut and Xneut
# will be available.
#

# def tp_connection_edited(mdl, mask_handle, new_value):
#     rneut_prop = mdl.prop(mask_handle, "Rneut")
#     xneut_prop = mdl.prop(mask_handle, "Xneut")
#
#     if new_value == "Y - Grounded":
#         # Enable user input fields for N to Gnd impedance
#         mdl.enable_property(mdl.prop(mask_handle, "Rneut"))
#         mdl.enable_property(mdl.prop(mask_handle, "Xneut"))
#         # We don't want to modify Rneut and Xneut user values
#         # on the 'on change' event. We put zeros only when
#         # the user commuted from "Y" or "Δ" to "Y - Grounded"
#         if mdl.get_property_disp_value(rneut_prop) == "'inf'":
#             mdl.set_property_disp_value(rneut_prop, "0.0")
#         if mdl.get_property_disp_value(xneut_prop) == "'inf'":
#             mdl.set_property_disp_value(xneut_prop, "0.0")
#     else:
#         # Disable user input fields for N to Gnd impedance
#         # show 'inf' because they are disconnected
#         mdl.set_property_disp_value(rneut_prop, "'inf'")
#         mdl.set_property_disp_value(xneut_prop, "'inf'")
#         mdl.disable_property(mdl.prop(mask_handle, "Rneut"))
#         mdl.disable_property(mdl.prop(mask_handle, "Xneut"))


'''*******************************************************************
This function manages the GND connection according to the type of the 
Load connection (Δ or Y). 
*******************************************************************'''

def connections_gnd_dynamics(mdl, mask_handle, created_ports):
    create_tags_and_connections_to_ports(mdl, mask_handle, created_ports)

    comp_handle = mdl.get_parent(mask_handle)

    tp_connection_prop = mdl.prop(mask_handle, "tp_connection")
    tp_connection = mdl.get_property_disp_value(tp_connection_prop)

    load_model_prop = mdl.prop(mask_handle, "load_model")
    load_model = mdl.get_property_disp_value(load_model_prop)

    phases_prop = mdl.prop(mask_handle, "phases")
    phases = mdl.get_property_disp_value(phases_prop)

    if phases == "3":
        phase_list = ["A", "B", "C"]
    else:
        phase_list = ["A"]

    if load_model == "Constant Impedance":
        load_comp = mdl.get_item("CIL", parent=comp_handle, item_type="component")
    else:
        load_comp = mdl.get_item("CPL", parent=comp_handle, item_type="component")

    for phase in phase_list:
        tag = mdl.get_item(f"Tag{phase}2", parent=comp_handle, item_type="tag")
        if len(mdl.find_connections(tag, mdl.term(load_comp, f"{phase}1"))) == 0:
            mdl.create_connection(tag, mdl.term(load_comp, f"{phase}1"))

    gnd1 = mdl.get_item("gndc", parent=comp_handle, item_type="component")
    jun_n = mdl.get_item("JN", parent=comp_handle, item_type="junction")
    gnd_z = mdl.get_item("Gnd Z", parent=comp_handle, item_type=ITEM_COMPONENT)

    # Here we have the grounding through Rneut and Xneut
    # AND the neutral terminal on Y configurations
    if tp_connection == "Y - Grounded":

        if not gnd1:
            gnd1 = mdl.create_component("src_ground", parent=comp_handle, name="gndc",
                                        position=(8030, 8480))

        if not jun_n:
            jun_n = mdl.create_junction(name="JN", parent=comp_handle,
                                        position=(7920, 8328), kind="pe")

        if not gnd_z:
            gnd_z = mdl.create_component("OpenDSS/Ground Impedance", parent=comp_handle,
                                         name="Gnd Z",
                                         position=(8030, 8385), rotation="up")

        conn_gnd_z2gnd = mdl.find_connections(mdl.term(gnd_z, "G"),
                                              mdl.term(gnd1, "node"))
        if not conn_gnd_z2gnd:
            mdl.create_connection(mdl.term(gnd_z, "G"), mdl.term(gnd1, "node"),
                                  "Conn_z2gnd")

        conn_gnd_z2jn = mdl.find_connections(mdl.term(gnd_z, "N"), jun_n)
        if not conn_gnd_z2jn:
            mdl.create_connection(mdl.term(gnd_z, "N"), jun_n, "Conn_gnd_z2jn")

    # In this case, we don't use Grounding, but the neutral remains connected in Y configurations!
    else:
        if gnd_z:
            mdl.delete_item(gnd_z)

        # Delete the GND component - no grounding here!
        if gnd1:
            mdl.delete_item(gnd1)


def load_dynamics(mdl, mask_handle, created_ports):
    create_tags_and_connections_to_ports(mdl, mask_handle, created_ports)

    comp_handle = mdl.get_parent(mask_handle)

    load_model_prop = mdl.prop(mask_handle, "load_model")
    load_model = mdl.get_property_disp_value(load_model_prop)

    phases_prop = mdl.prop(mask_handle, "phases")
    phases = mdl.get_property_disp_value(phases_prop)

    if load_model == "Constant Impedance":
        load_name = "CIL"
        load_type = "Constant Impedance"
    else:
        load_name = "CPL"
        load_type = "Constant Power"

    load_comp = mdl.get_item(load_name, parent=comp_handle, item_type="component")

    if not load_comp:
        set_load_model(mdl, mask_handle, load_type)
        load_comp = mdl.get_item(load_name, parent=comp_handle, item_type="component")
    mdl.set_property_value(mdl.prop(load_comp, "phases"), phases)
    if int(phases) == 3:
        phase_list = ["A", "B", "C"]
    elif int(phases) == 1:
        phase_list = ["A"]
    else:
        phase_list = ["A"]

    for phase in phase_list:
        tag = mdl.get_item(f"Tag{phase}2", parent=comp_handle, item_type="tag")
        if len(mdl.find_connections(tag)) == 0:
            mdl.create_connection(tag, mdl.term(load_comp, f"{phase}1"))


def connections_pow_ref_dynamics(mdl, mask_handle, created_ports):
    comp_handle = mdl.get_parent(mask_handle)

    pow_ref_s_prop = mdl.prop(mask_handle, "Pow_ref_s")
    pow_ref_s = mdl.get_property_value(pow_ref_s_prop)

    load_model = mdl.get_property_value(mdl.prop(mask_handle, "load_model"))
    if load_model != "Constant Impedance":
        if pow_ref_s == "Fixed":
            cpl1 = mdl.get_item("CPL", parent=comp_handle, item_type="component")
            if not cpl1:
                set_load_model(mdl, mask_handle, "Constant Power")
                cpl1 = mdl.get_item("CPL", parent=comp_handle, item_type="component")

            ts_mdl = mdl.get_item("TS_module", parent=comp_handle,
                                  item_type="component")
            if ts_mdl:
                set_timeseries_switch(mdl, mask_handle, False)

            mdl.set_property_value(mdl.prop(cpl1, "kP_inp"), "Fixed")
            mdl.set_property_value(mdl.prop(cpl1, "kQ_inp"), "Fixed")

        elif pow_ref_s == "External input":
            cpl1 = mdl.get_item("CPL", parent=comp_handle, item_type="component")
            if not cpl1:
                set_load_model(mdl, mask_handle, "Constant Power")
                cpl1 = mdl.get_item("CPL", parent=comp_handle, item_type="component")

            ts_mdl = mdl.get_item("TS_module", parent=comp_handle,
                                  item_type="component")
            if ts_mdl:
                set_timeseries_switch(mdl, mask_handle, False)

            mdl.set_property_value(mdl.prop(cpl1, "kP_inp"), "Variable input")
            mdl.set_property_value(mdl.prop(cpl1, "kQ_inp"), "Variable input")

            conn_p_int = mdl.get_item("connP", parent=comp_handle,
                                      item_type="connection")
            conn_q_int = mdl.get_item("connQ", parent=comp_handle,
                                      item_type="connection")

            conn_ts_p_int = mdl.get_item("ConnTsP", parent=comp_handle,
                                         item_type="connection")
            conn_ts_q_int = mdl.get_item("ConnTsQ", parent=comp_handle,
                                         item_type="connection")

            if conn_ts_p_int:
                mdl.delete_item(conn_ts_p_int)
            if conn_ts_q_int:
                mdl.delete_item(conn_ts_q_int)

            if conn_p_int:
                mdl.delete_item(conn_p_int)
            if conn_q_int:
                mdl.delete_item(conn_q_int)

            mdl.create_connection(mdl.term(cpl1, "P_set"), created_ports.get("P_ext"),
                                  "ConnP")
            mdl.create_connection(mdl.term(cpl1, "Q_set"), created_ports.get("Q_ext"),
                                  "ConnQ")

        else:
            cpl1 = mdl.get_item("CPL", parent=comp_handle, item_type="component")
            if not cpl1:
                set_load_model(mdl, mask_handle, "Constant Power")
                cpl1 = mdl.get_item("CPL", parent=comp_handle, item_type="component")
            mdl.set_property_value(mdl.prop(cpl1, "kP_inp"), "Variable input")
            mdl.set_property_value(mdl.prop(cpl1, "kQ_inp"), "Variable input")
            ts_mdl = mdl.get_item("TS_module", parent=comp_handle,
                                  item_type="component")
            if not ts_mdl:
                set_timeseries_switch(mdl, mask_handle, True)
                ts_mdl = mdl.get_item("TS_module", parent=comp_handle,
                                      item_type="component")
            conn_p_int = mdl.get_item("connP", parent=comp_handle,
                                      item_type="connection")
            conn_q_int = mdl.get_item("connQ", parent=comp_handle,
                                      item_type="connection")

            if conn_p_int:
                mdl.delete_item(conn_p_int)
            if conn_q_int:
                mdl.delete_item(conn_q_int)
            mdl.set_property_value(mdl.prop(ts_mdl, "P_mode"), "Manual input")
            conn_ts_p_int = mdl.get_item("ConnTsP", parent=comp_handle,
                                         item_type="connection")
            conn_ts_q_int = mdl.get_item("ConnTsQ", parent=comp_handle,
                                         item_type="connection")

            if not conn_ts_p_int:
                mdl.create_connection(mdl.term(cpl1, "P_set"), mdl.term(ts_mdl, "P"),
                                      "ConnTsP")
            if not conn_ts_q_int:
                mdl.create_connection(mdl.term(cpl1, "Q_set"), mdl.term(ts_mdl, "Q"),
                                      "ConnTsQ")
    elif load_model == "Constant Impedance":
        set_timeseries_switch(mdl, mask_handle, False)


def connections_ts_mode_dynamics(mdl, mask_handle, created_ports):
    comp_handle = mdl.get_parent(mask_handle)

    load_model_prop = mdl.prop(mask_handle, "load_model")
    load_model = mdl.get_property_value(load_model_prop)

    pow_ref_s_prop = mdl.prop(mask_handle, "Pow_ref_s")
    pow_ref_s = mdl.get_property_value(pow_ref_s_prop)

    if load_model == "Constant Power" or load_model == "Constant Z,I,P":
        if pow_ref_s == "Time Series":
            ts_mdl = mdl.get_item("TS_module", parent=comp_handle,
                                  item_type="component")
            conn_ts_in = mdl.get_item("ConnTs", parent=comp_handle,
                                      item_type="connection")

            mdl.set_property_value(mdl.prop(ts_mdl, "P_mode"), "Manual input")
            if not conn_ts_in:
                mdl.create_connection(mdl.term(ts_mdl, "T"), created_ports.get("T_ext"),
                                      "ConnTs")


def get_all_circuit_loads(mdl, mask_handle, parent_comp=None):
    component_list = []
    if parent_comp:  # Component inside a subsystem (recursive function)
        all_components = mdl.get_items(parent_comp)
    else:  # Top level call
        all_components = mdl.get_items()

    for comp in all_components:
        try:
            type_name = mdl.get_component_type_name(comp)
            if type_name and type_name == "Load":
                component_list.append(comp)
            elif not type_name:  # Component is a subsystem
                component_list.extend(
                    get_all_circuit_loads(mdl, mdl.get_mask(comp), parent_comp=comp))
        except:
            # Some components (such as ports and connections) cannot be used with
            # get_component_type_name
            pass
    # Return the list of component handles
    return component_list


def restore_all_loads_points(mdl, mask_handle):
    global got_loadshape_points_list

    # Return all components (including inside subsystems)
    all_loads = get_all_circuit_loads(mdl, mask_handle)
    got_loadshape_points_list = []
    for load in all_loads:
        if load not in got_loadshape_points_list:
            load_mask_handle = mdl.get_mask(load)
            read_loadshape_from_json(mdl, load_mask_handle)


def read_loadshape_from_json(mdl, mask_handle, reload_dict=None):
    global got_loadshape_points_list

    comp_handle = mdl.get_parent(mask_handle)

    try:
        current_points = ast.literal_eval(
            mdl.get_property_value(mdl.prop(mask_handle, "loadshape")))
    except:
        current_points = []
    useactual = mdl.get_property_value(mdl.prop(mask_handle, "useactual"))
    interval = mdl.get_property_value(mdl.prop(mask_handle, "loadshape_int"))

    if not reload_dict:
        loadshape_name = mdl.get_property_value(mdl.prop(mask_handle, "loadshape_name"))
        loadshape_from_file = mdl.get_property_value(
            mdl.prop(mask_handle, "loadshape_from_file")) == "True"
        loadshape_from_file_header = mdl.get_property_value(
            mdl.prop(mask_handle, "loadshape_from_file_header")) == "True"
        loadshape_from_file_column = mdl.get_property_value(
            mdl.prop(mask_handle, "loadshape_from_file_column"))
        loadshape_from_file_path = mdl.get_property_value(
            mdl.prop(mask_handle, "loadshape_from_file_path"))
    else:
        loadshape_name = reload_dict.get("loadshape_name")
        loadshape_from_file = reload_dict.get("csv_file") == "True"
        loadshape_from_file_header = reload_dict.get("headers") == "True"
        loadshape_from_file_column = reload_dict.get("column")
        loadshape_from_file_path = reload_dict.get("csv_path")

    model_path = pathlib.Path(mdl.get_model_file_path())

    if model_path:
        filename = model_path.stem
        data_folder_path = model_path.parent.joinpath(
            filename + " Target files").joinpath('dss').joinpath("data")
        general_objects_json = data_folder_path.joinpath(f"general_objects.json")
        if general_objects_json.is_file():
            with open(general_objects_json, 'r') as f:
                general_objects_dict = json.load(f)
            loadshape_points = general_objects_dict.get("loadshapes", {}).get(
                loadshape_name, {}).get("mult", [])
            if loadshape_from_file:
                if pathlib.Path(loadshape_from_file_path).is_file():
                    with open(pathlib.Path(loadshape_from_file_path), 'r',
                              encoding='utf-8-sig') as ls_f:
                        if loadshape_from_file_header:
                            table = pd.read_csv(ls_f)
                            table = table.fillna(0)
                        else:
                            table = pd.read_csv(ls_f, header=None)
                            table = table.fillna(0)
                        loadshape_points = list(
                            table.iloc[:, int(loadshape_from_file_column) - 1])
                    mdl.set_property_value(mdl.prop(mask_handle, "loadshape"),
                                           loadshape_points)
                    mdl.set_property_disp_value(mdl.prop(mask_handle, "loadshape"),
                                                loadshape_points)
                else:
                    mdl.error(
                        f"Could not find the CSV file '{loadshape_from_file_path}'."
                        f" Please edit or choose a new LoadShape.",
                        context=mdl.get_parent(mask_handle))
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
                        general_objects_dict.get("loadshapes")[
                            loadshape_name] = new_loadshape_dict
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

                general_objects_dict.get("loadshapes")[
                    loadshape_name] = new_loadshape_dict
                with open(general_objects_json, 'w') as f:
                    f.write(json.dumps(general_objects_dict, indent=4))
            else:
                mdl.set_property_value(mdl.prop(mask_handle, "loadshape"),
                                       loadshape_points)
                mdl.set_property_disp_value(mdl.prop(mask_handle, "loadshape"),
                                            loadshape_points)
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
                f.write(json.dumps({"loadshapes": {loadshape_name: new_loadshape_dict}},
                                   indent=4))

    if comp_handle not in got_loadshape_points_list:
        got_loadshape_points_list.append(comp_handle)

    return loadshape_points


def set_timeseries_switch(mdl, mask_handle, new_value):
    comp_handle = mdl.get_sub_level_handle(mask_handle)

    if new_value is True:
        ts_switch = mdl.get_item("Ts_switch", parent=comp_handle, item_type="component")
        if not ts_switch:
            ts_switch = mdl.create_component("Constant", parent=comp_handle,
                                             name="Ts_switch", position=(7368, 8272))
            mdl.set_property_value(mdl.prop(ts_switch, "value"), "Ts_switch")
            mdl.set_property_value(mdl.prop(ts_switch, "execution_rate"), "Tfast")

        port_t = mdl.get_item("T", parent=comp_handle, item_type="port")

        signal_switch = mdl.get_item("Signal switch", parent=comp_handle,
                                     item_type="component")
        if not signal_switch:
            signal_switch = mdl.create_component("Signal switch", parent=comp_handle,
                                                 name="Signal switch",
                                                 position=(7624, 8384))
            mdl.set_property_value(mdl.prop(signal_switch, "criterion"),
                                   "ctrl >= threshold")
            mdl.set_property_value(mdl.prop(signal_switch, "threshold"), 0.5)

        round_comp = mdl.get_item("Round", parent=comp_handle, item_type="component")
        if not round_comp:
            round_comp = mdl.create_component("Round", parent=comp_handle,
                                              name="Round", position=(7496, 8400))
            mdl.set_property_value(mdl.prop(round_comp, "round_fn"), "floor")

        limit = mdl.get_item("Limit", parent=comp_handle, item_type="component")
        if not limit:
            limit = mdl.create_component("Limit", parent=comp_handle,
                                         name="Limit", position=(7744, 8384))
            mdl.set_property_value(mdl.prop(limit, "upper_limit"), "T_lim_high")
            mdl.set_property_value(mdl.prop(limit, "lower_limit"), "T_lim_low")

        ts_module = mdl.get_item("TS_module", parent=comp_handle, item_type="component")
        if not ts_module:
            ts_module = mdl.create_component("OpenDSS/TS_module", parent=comp_handle,
                                             name="TS_module", position=(7824, 8320),
                                             rotation="left")
        conn_term_list = [(mdl.term(ts_switch, "out"), mdl.term(signal_switch, "in2")),
                          (port_t, mdl.term(signal_switch, "in")),
                          (port_t, mdl.term(round_comp, "in")),
                          (mdl.term(round_comp, "out"), mdl.term(signal_switch, "in1")),
                          (mdl.term(signal_switch, "out"), mdl.term(limit, "in")),
                          (mdl.term(limit, "out"), mdl.term(ts_module, "T"))]
        for conn_term in conn_term_list:
            if len(mdl.find_connections(conn_term[0], conn_term[1])) == 0:
                mdl.create_connection(conn_term[0], conn_term[1])

    else:
        ts_switch = mdl.get_item("Ts_switch", parent=comp_handle, item_type="component")
        if ts_switch:
            mdl.delete_item(ts_switch)

        signal_switch = mdl.get_item("Signal switch", parent=comp_handle,
                                     item_type="component")
        if signal_switch:
            mdl.delete_item(signal_switch)

        round_comp = mdl.get_item("Round", parent=comp_handle, item_type="component")
        if round_comp:
            mdl.delete_item(round_comp)

        limit = mdl.get_item("Limit", parent=comp_handle, item_type="component")
        if limit:
            mdl.delete_item(limit)

        ts_module = mdl.get_item("TS_module", parent=comp_handle, item_type="component")
        if ts_module:
            mdl.delete_item(ts_module)


def set_load_model(mdl, mask_handle):
    tp_connection = mdl.get_property_disp_value(mdl.prop(mask_handle, "tp_connection"))
    comp_handle = mdl.get_parent(mask_handle)

    phases = mdl.get_property_disp_value(mdl.prop(mask_handle, "phases"))
    t_slow = mdl.get_property_value(mdl.prop(mask_handle, "execution_rate"))
    t_fast = mdl.get_property_value(mdl.prop(mask_handle, "Tfast"))
    pf_mode = mdl.get_property_value(mdl.prop(mask_handle, "pf_mode_3ph"))
    load_model = mdl.get_property_disp_value(mdl.prop(mask_handle, "load_model"))

    if load_model == "Constant Impedance":
        mdl.set_property_disp_value(mdl.prop(mask_handle, 'Pow_ref_s'), "Fixed")

        cpl1 = mdl.get_item("CPL", parent=comp_handle, item_type=ITEM_COMPONENT)
        if cpl1:
            mdl.delete_item(cpl1)

        cil1 = mdl.get_item("CIL", parent=comp_handle, item_type=ITEM_COMPONENT)
        if not cil1:
            cil1 = mdl.create_component("OpenDSS/CIL", parent=comp_handle,
                                        name="CIL", position=(7920, 8208),
                                        rotation="up")
        set_pf_mode(mdl, mask_handle, pf_mode)

        if tp_connection == "Y" or tp_connection == "Y - Grounded":
            mdl.set_property_value(mdl.prop(cil1, "conn_type"), "Y")
            mdl.set_property_value(mdl.prop(cil1, "ground_connected"), False)

        else:
            if phases == "1":
                mdl.set_property_value(mdl.prop(cil1, "conn_type"), "Y")
            else:
                mdl.set_property_value(mdl.prop(cil1, "conn_type"), "Δ")
            mdl.set_property_value(mdl.prop(cil1, "ground_connected"), False)

        if phases == "3":
            mdl.set_property_value(mdl.prop(cil1, "phases"), "3")

        else:
            mdl.set_property_value(mdl.prop(cil1, "phases"), "1")

    else:
        cil1 = mdl.get_item("CIL", parent=comp_handle, item_type=ITEM_COMPONENT)
        if cil1:
            mdl.delete_item(cil1)

        cpl1 = mdl.get_item("CPL", parent=comp_handle, item_type=ITEM_COMPONENT)
        if not cpl1:
            cpl1 = mdl.create_component("OpenDSS/CPL", parent=comp_handle,
                                        name="CPL", position=(7920, 8208),
                                        rotation="right", flip="flip_horizontal")

        if phases == "3":
            mdl.set_property_value(mdl.prop(cpl1, "phases"), "3")
        else:
            mdl.set_property_value(mdl.prop(cpl1, "phases"), "1")

        if t_slow == t_fast:
            mdl.set_property_value(mdl.prop(cpl1, "Fast_con"), "False")
        else:
            mdl.set_property_value(mdl.prop(cpl1, "Fast_con"), "True")


def zero_seq_removal(mdl, mask_handle, new_value):
    comp_handle = mdl.get_sub_level_handle(mask_handle)
    cpl1 = mdl.get_item("CPL", parent=comp_handle, item_type=ITEM_COMPONENT)

    if cpl1:
        mdl.set_property_value(mdl.prop(cpl1, "zero_seq_remove"), new_value)


def set_pf_mode(mdl, mask_handle, new_value):
    comp_handle = mdl.get_sub_level_handle(mask_handle)

    load_model = mdl.get_property_value(mdl.prop(mask_handle, "load_model"))

    if load_model == "Constant Impedance":
        if new_value == "Unit":
            cil1 = mdl.get_item("CIL", parent=comp_handle, item_type=ITEM_COMPONENT)
            mdl.set_property_value(mdl.prop(cil1, "pf_mode_3ph"), "Unit")
        elif new_value == "Lead":
            cil1 = mdl.get_item("CIL", parent=comp_handle, item_type=ITEM_COMPONENT)
            mdl.set_property_value(mdl.prop(cil1, "pf_mode_3ph"), "Lead")
        elif new_value == "Lag":
            cil1 = mdl.get_item("CIL", parent=comp_handle, item_type=ITEM_COMPONENT)
            mdl.set_property_value(mdl.prop(cil1, "pf_mode_3ph"), "Lag")


def load_pre_compile_function(mdl, mask_handle, prop_dict):
    """

    Args:
        mdl: schematic editor API handle
        mask_handle: component's mask handle
        prop_dict: dictionary of property values

    Returns:

    """

    basefreq = prop_dict["fn"]
    kva = prop_dict["Sn_3ph"]

    if prop_dict["conn_type"] == 'Δ':
        conn = "delta"
    else:
        conn = "wye"

    vminpu = prop_dict["v_min_max"][0]
    vmaxpu = prop_dict["v_min_max"][1]

    if prop_dict["pf_mode_3ph"] == "Unit":
        pf = 1.0
        p_cpl = prop_dict["Sn_3ph"]
        q_cpl = 0
        pf_3ph_set = 0.99
    elif prop_dict["pf_mode_3ph"] == "Lag":
        pf = prop_dict["pf_3ph"]
        p_cpl = prop_dict["Sn_3ph"] * pf
        q_cpl = prop_dict["Sn_3ph"] * ((1 - pf * pf) ** 0.5)
        pf_3ph_set = prop_dict["pf_3ph"]
    else:
        pf = -1 * prop_dict["pf_3ph"]
        p_cpl = prop_dict["Sn_3ph"] * pf
        q_cpl = -prop_dict["Sn_3ph"] * ((1 - pf * pf) ** 0.5)
        pf_3ph_set = prop_dict["pf_3ph"]

    if prop_dict["phases"] == "1":
        if prop_dict["conn_type"] == "Y - Grounded":
            kv = (prop_dict["Vn_3ph"] / 1) / 1
            vn_3ph_cpl = kv / (3 ** 0.5)
        else:
            kv = prop_dict["Vn_3ph"]
            vn_3ph_cpl = kv
    else:
        kv = prop_dict["Vn_3ph"]
        vn_3ph_cpl = kv

    dssnpts = len(prop_dict["S_Ts"])

    if prop_dict["load_model"] == "Constant Power":
        model = 1
    elif prop_dict["load_model"] == "Constant Z,I,P":
        model = 8
    else:
        model = 2

    s_ts = prop_dict["loadshape"]
    dsst = prop_dict["loadshape_int"]
    slen = len(s_ts)

    if prop_dict["T_mode"] == "Time":
        t_ts_internal = [0] * slen
        s_vec1 = [0] * slen
        idxs = 0
        for t_val in prop_dict["T_Ts"]:
            t_ts_internal[idxs] = t_val
            idxs += 1
        t_lim_low = prop_dict["T_Ts"][0]
        t_lim_high = prop_dict["T_Ts"][len(prop_dict["T_Ts"]) - 1]
    else:
        t_ts_internal = [0] * slen
        s_vec1 = [0] * slen
        idxs = 0
        for S_val in s_vec1:
            t_ts_internal[idxs] = idxs
            idxs += 1
        t_lim_low = t_ts_internal[0]
        t_lim_high = t_ts_internal[slen - 1]

    if prop_dict["T_mode"] == "Time":
        ts_switch = 1
    else:
        ts_switch = 0

    mdl.set_property_value(mdl.prop(mask_handle, "baseFreq"), basefreq)
    mdl.set_property_value(mdl.prop(mask_handle, "kVA"), kva)
    mdl.set_property_value(mdl.prop(mask_handle, "Vn_3ph_CPL"), vn_3ph_cpl)
    mdl.set_property_value(mdl.prop(mask_handle, "P_CPL"), p_cpl)
    mdl.set_property_value(mdl.prop(mask_handle, "Q_CPL"), q_cpl)
    mdl.set_property_value(mdl.prop(mask_handle, "conn"), conn)
    mdl.set_property_value(mdl.prop(mask_handle, "pf"), pf)
    mdl.set_property_value(mdl.prop(mask_handle, "pf_3ph_set"), pf_3ph_set)
    mdl.set_property_value(mdl.prop(mask_handle, "kV"), kv)
    mdl.set_property_value(mdl.prop(mask_handle, "Vminpu"), vminpu)
    mdl.set_property_value(mdl.prop(mask_handle, "Vmaxpu"), vmaxpu)
    mdl.set_property_value(mdl.prop(mask_handle, "model"), model)

    mdl.set_property_value(mdl.prop(mask_handle, "dssT"), dsst)
    mdl.set_property_value(mdl.prop(mask_handle, "S_Ts"), s_ts)
    mdl.set_property_value(mdl.prop(mask_handle, "T_Ts_internal"), t_ts_internal)
    mdl.set_property_value(mdl.prop(mask_handle, "Slen"), slen)
    mdl.set_property_value(mdl.prop(mask_handle, "dssnpts"), dssnpts)
    mdl.set_property_value(mdl.prop(mask_handle, "T_lim_low"), t_lim_low)
    mdl.set_property_value(mdl.prop(mask_handle, "T_lim_high"), t_lim_high)
    mdl.set_property_value(mdl.prop(mask_handle, "Ts_switch"), ts_switch)


# def pf_mode_3ph_value_edited(mdl, mask_handle, new_value):
#     if new_value == "Unit":
#         mdl.disable_property(mdl.prop(mask_handle, "pf_3ph"))
#     else:
#         mdl.enable_property(mdl.prop(mask_handle, "pf_3ph"))


def validate_execution_rate(mdl, mask_handle):
    comp_handle = mdl.get_sub_level_handle(mask_handle)
    tfst_mask = mdl.get_property_value(mdl.prop(mask_handle, "Tfast"))
    ts_mask = mdl.get_property_value(mdl.prop(mask_handle, "execution_rate"))
    cpl_comp = mdl.get_item("CPL", parent=comp_handle, item_type="component")

    if cpl_comp:
        if ts_mask == tfst_mask:
            mdl.set_property_value(mdl.prop(cpl_comp, "Fast_con"), "False")
        else:
            mdl.set_property_value(mdl.prop(cpl_comp, "Fast_con"), "True")


# def t_mode_value_edited(mdl, mask_handle, new_value):
#     if new_value == "Time":
#         mdl.enable_property(mdl.prop(mask_handle, "T_Ts"))
#     else:
#         mdl.disable_property(mdl.prop(mask_handle, "T_Ts"))


# def s_ts_mode_value_edited(mdl, mask_handle, new_value):
#     if new_value == "Manual input":
#         mdl.disable_property(mdl.prop(mask_handle, "T_Ts_max"))
#         mdl.disable_property(mdl.prop(mask_handle, "del_Ts"))
#         mdl.enable_property(mdl.prop(mask_handle, "T_Ts"))
#     else:
#         mdl.enable_property(mdl.prop(mask_handle, "T_Ts_max"))
#         mdl.enable_property(mdl.prop(mask_handle, "del_Ts"))
#         mdl.disable_property(mdl.prop(mask_handle, "T_Ts"))


def get_sld_conversion_info(mdl, mask_handle, multiline_ports, terminal_positions, sld_term_position):

    # multiline_ports_1 = ["A1", "B1", "C1"]

    port_config_dict = {
        "SLD1": {
            "multiline_ports": multiline_ports,
            "side": "top",
            "bus_terminal_position": sld_term_position,
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
    # terminal_positions = {
    #     "A1": (-48, -24),
    #     "B1": (-16, -24),
    #     "C1": (16, -24),
    # }

    return port_config_dict, tag_config_dict, terminal_positions


def topology_dynamics(mdl, mask_handle, prop_handle):
    """
    This function is called when the user changes the configuration on the mask
    """

    comp_handle = mdl.get_parent(mask_handle)

    if prop_handle:
        calling_prop_name = mdl.get_name(prop_handle)
    else:
        calling_prop_name = "init_code"


    current_pass_prop_values = {
        k: str(v) for k, v in mdl.get_property_values(comp_handle).items()
    }

    #
    # Get new property values to be applied (display values)
    #
    current_values = {}
    new_prop_values = {}
    for prop in mdl.get_property_values(comp_handle):
        p = mdl.prop(mask_handle, prop)
        new_prop_values[prop] = mdl.get_property_disp_value(p)
        current_values[prop] = mdl.get_property_value(p)
    #
    # If the property values are the same as on the previous run, stop
    #
    global old_state
    if new_prop_values == old_state.get(comp_handle):
        return

    if calling_prop_name == "init_code":
        define_icon(mdl, mask_handle)
        ports = port_dynamics(mdl, mask_handle)
        set_load_model(mdl, mask_handle)
        load_dynamics(mdl, mask_handle, ports)
        connections_gnd_dynamics(mdl, mask_handle, ports)
        connections_dynamics(mdl, mask_handle, ports)

    if calling_prop_name not in ["sld_mode", "sld_1ph_pick", "init_code"]:

        if old_state:
            current_state = old_state[comp_handle]
        else:
            current_state = new_prop_values

        currently_sld = mdl.get_item("SLD1", parent=comp_handle, item_type="port")
        if currently_sld:
            # The terminal related to the current property hasn't been created yet
            importlib.reload(util)
            phases = current_state.get("phases")
            tp_connection = current_state.get("tp_connection")
            sld_1ph_pick = current_state.get("sld_1ph_pick")
            if phases == "3":
                if tp_connection == "Δ":
                    multi_port_list = ["A1", "B1", "C1"]
                    terminal_positions = {
                        "A1": (-32, -24),
                        "B1": (0, -24),
                        "C1": (32, -24),
                    }
                    sld_term_position = (0, -24)
                else:
                    multi_port_list = ["A1", "B1", "C1", "N1"]
                    terminal_positions = {
                        "A1": (-48, -24),
                        "B1": (-16, -24),
                        "C1": (16, -24),
                        "N1": (48, -24),
                    }
                    sld_term_position = (0, -24)
            elif phases == "1":
                if tp_connection == "Y - Grounded":
                    terminal_positions = {
                        "A1": (0, -24),
                    }
                    sld_term_position = (0, -24)
                    if sld_1ph_pick == "A":
                        multi_port_list = ["A1", None, None]
                    elif sld_1ph_pick == "B":
                        multi_port_list = [None, "A1", None]
                    elif sld_1ph_pick == "C":
                        multi_port_list = [None, None, "A1"]
                    else:
                        multi_port_list = ["A1", None, None]
                elif tp_connection == "Y":
                    terminal_positions = {
                        "A1": (-16, -12),
                        "B1": (16, -12),
                    }
                    sld_term_position = (0, -24)
                    if sld_1ph_pick == "A":
                        multi_port_list = ["A1", None, None, "B1"]
                    elif sld_1ph_pick == "B":
                        multi_port_list = [None, "A1", None, "B1"]
                    elif sld_1ph_pick == "C":
                        multi_port_list = [None, None, "A1", "B1"]
                    else:
                        multi_port_list = ["A1", None, None, "B1"]
                else:
                    terminal_positions = {
                        "A1": (-16, -12),
                        "B1": (16, -12),
                    }
                    sld_term_position = (0, -16)
                    if sld_1ph_pick == "A":
                        multi_port_list = ["A1", "B1", None]
                    elif sld_1ph_pick == "B":
                        multi_port_list = [None, "A1", "B1"]
                    elif sld_1ph_pick == "C":
                        multi_port_list = ["B1", None, "A1"]
                    else:
                        multi_port_list = ["A1", "B1", None]
            else:
                multi_port_list = ["A1", "B1", "C1"]
                terminal_positions = {
                    "A1": (-48, -24),
                    "B1": (-16, -24),
                    "C1": (16, -24),
                }
                sld_term_position = (0, -24)

            sld_info = get_sld_conversion_info(mdl, mask_handle, multi_port_list, terminal_positions, sld_term_position)
            util.convert_to_multiline(mdl, mask_handle, sld_info)

        define_icon(mdl, mask_handle)
        ports = port_dynamics(mdl, mask_handle)
        set_load_model(mdl, mask_handle)
        load_dynamics(mdl, mask_handle, ports)
        connections_gnd_dynamics(mdl, mask_handle, ports)
        connections_dynamics(mdl, mask_handle, ports)
        old_state[comp_handle] = current_values

    currently_sld = mdl.get_item("SLD1", parent=comp_handle, item_type="port")
    if currently_sld:
        # The terminal related to the current property hasn't been created yet
        importlib.reload(util)
        phases = new_prop_values.get("phases")
        tp_connection = new_prop_values.get("tp_connection")
        sld_1ph_pick = new_prop_values.get("sld_1ph_pick")
        if phases == "3":
            if tp_connection == "Δ":
                multi_port_list = ["A1", "B1", "C1"]
                terminal_positions = {
                    "A1": (-32, -24),
                    "B1": (0, -24),
                    "C1": (32, -24),
                }
                sld_term_position = (0, -24)
            else:
                multi_port_list = ["A1", "B1", "C1", "N1"]
                terminal_positions = {
                    "A1": (-48, -24),
                    "B1": (-16, -24),
                    "C1": (16, -24),
                    "N1": (48, -24),
                }
                sld_term_position = (0, -24)
        elif phases == "1":
            if tp_connection == "Y - Grounded":
                terminal_positions = {
                    "A1": (0, -24),
                }
                sld_term_position = (0, -24)
                if sld_1ph_pick == "A":
                    multi_port_list = ["A1", None, None]
                elif sld_1ph_pick == "B":
                    multi_port_list = [None, "A1", None]
                elif sld_1ph_pick == "C":
                    multi_port_list = [None, None, "A1"]
                else:
                    multi_port_list = ["A1", None, None]
            elif tp_connection == "Y":
                terminal_positions = {
                    "A1": (-16, -12),
                    "B1": (16, -12),
                }
                sld_term_position = (0, -24)
                if sld_1ph_pick == "A":
                    multi_port_list = ["A1", None, None, "B1"]
                elif sld_1ph_pick == "B":
                    multi_port_list = [None, "A1", None, "B1"]
                elif sld_1ph_pick == "C":
                    multi_port_list = [None, None, "A1", "B1"]
                else:
                    multi_port_list = ["A1", None, None, "B1"]
            else:
                terminal_positions = {
                    "A1": (-16, -12),
                    "B1": (16, -12),
                }
                sld_term_position = (0, -16)
                if sld_1ph_pick == "A":
                    multi_port_list = ["A1", "B1", None]
                elif sld_1ph_pick == "B":
                    multi_port_list = [None, "A1", "B1"]
                elif sld_1ph_pick == "C":
                    multi_port_list = ["B1", None, "A1"]
                else:
                    multi_port_list = ["A1", "B1", None]
        else:
            multi_port_list = ["A1", "B1", "C1"]
            terminal_positions = {
                "A1": (-48, -24),
                "B1": (-16, -24),
                "C1": (16, -24),
            }
            sld_term_position = (0, -24)

        sld_info = get_sld_conversion_info(mdl, mask_handle, multi_port_list, terminal_positions, sld_term_position)
        util.convert_to_multiline(mdl, mask_handle, sld_info)

    #
    # When property values reach the final state, return to single-line if needed
    #
    good_for_sld = []
    for prop_name in new_prop_values:
        if prop_name in ["phases", "tp_connection", "ground_connected"]:
            cur_pass_value = current_pass_prop_values[prop_name]
            new_value = new_prop_values[prop_name]
            if util.is_float(str(cur_pass_value)) or util.is_float(str(new_value)):
                if float(cur_pass_value) == float(new_value):
                    good_for_sld.append(True)
                    continue
            else:
                if str(current_pass_prop_values[prop_name]) == str(new_prop_values[prop_name]):
                    good_for_sld.append(True)
                    continue
            good_for_sld.append(False)

    final_state = all(good_for_sld)
    # final_state = True

    if final_state:
        old_state[comp_handle] = new_prop_values
        if new_prop_values.get("sld_mode") in (True, "True"):
            importlib.reload(util)
            phases = new_prop_values.get("phases")
            tp_connection = new_prop_values.get("tp_connection")
            sld_1ph_pick = new_prop_values.get("sld_1ph_pick")
            if phases == "3":
                if tp_connection == "Δ":
                    multi_port_list = ["A1", "B1", "C1"]
                    terminal_positions = {
                        "A1": (-32, -24),
                        "B1": (0, -24),
                        "C1": (32, -24),
                    }
                    sld_term_position = (0, -24)
                else:
                    multi_port_list = ["A1", "B1", "C1", "N1"]
                    terminal_positions = {
                        "A1": (-48, -24),
                        "B1": (-16, -24),
                        "C1": (16, -24),
                        "N1": (48, -24),
                    }
                    sld_term_position = (0, -24)
            elif phases == "1":
                if tp_connection == "Y - Grounded":
                    terminal_positions = {
                        "A1": (0, -24),
                    }
                    sld_term_position = (0, -24)
                    if sld_1ph_pick == "A":
                        multi_port_list = ["A1", None, None]
                    elif sld_1ph_pick == "B":
                        multi_port_list = [None, "A1", None]
                    elif sld_1ph_pick == "C":
                        multi_port_list = [None, None, "A1"]
                    else:
                        multi_port_list = ["A1", None, None]
                elif tp_connection == "Y":
                    terminal_positions = {
                        "A1": (-16, -12),
                        "B1": (16, -12),
                    }
                    sld_term_position = (0, -24)
                    if sld_1ph_pick == "A":
                        multi_port_list = ["A1", None, None, "B1"]
                    elif sld_1ph_pick == "B":
                        multi_port_list = [None, "A1", None, "B1"]
                    elif sld_1ph_pick == "C":
                        multi_port_list = [None, None, "A1", "B1"]
                    else:
                        multi_port_list = ["A1", None, None, "B1"]
                else:
                    terminal_positions = {
                        "A1": (-16, -12),
                        "B1": (16, -12),
                    }
                    sld_term_position = (0, -16)
                    if sld_1ph_pick == "A":
                        multi_port_list = ["A1", "B1", None]
                    elif sld_1ph_pick == "B":
                        multi_port_list = [None, "A1", "B1"]
                    elif sld_1ph_pick == "C":
                        multi_port_list = ["B1", None, "A1"]
                    else:
                        multi_port_list = ["A1", "B1", None]
            else:
                multi_port_list = ["A1", "B1", "C1"]
                terminal_positions = {
                    "A1": (-48, -24),
                    "B1": (-16, -24),
                    "C1": (16, -24),
                }
                sld_term_position = (0, -24)

            sld_info = get_sld_conversion_info(mdl, mask_handle, multi_port_list, terminal_positions, sld_term_position)
            util.convert_to_sld(mdl, mask_handle, sld_info)

    sld_post_processing(mdl, mask_handle)


def sld_post_processing(mdl, mask_handle):
    comp_handle = mdl.get_parent(mask_handle)

    # Resize the buses to 4

    bus1 = mdl.get_item("SLD1_bus", parent=comp_handle)
    if bus1:
        bus1_size_prop = mdl.prop(bus1, "bus_size")
        mdl.set_property_value(bus1_size_prop, 4)


def dialog_close(mdl, mask_handle, reason):
    """
    Manages the dialog close: If the user cancels the modifications,
    restore the combo tp_connections initial state.
    """

    # Get tp combo values after closing
    tp_connection_prop = mdl.prop(mask_handle, "tp_connection")
    new_tp_combo_values = mdl.get_property_combo_values(tp_connection_prop)

    # Get original tp combo values
    tp_connection_combo_values_prop = mdl.prop(mask_handle,
                                               "tp_connection_combo_values")
    tp_connection_combo_values = mdl.get_property_value(tp_connection_combo_values_prop)
    old_tp_combo_values = ast.literal_eval(tp_connection_combo_values)

    # Restore to the original if the user cancels
    if reason == "reason_close_cancel":
        if not (old_tp_combo_values == new_tp_combo_values):
            mdl.set_property_combo_values(tp_connection_prop, old_tp_combo_values)


def retro_compatibility(mdl, mask_handle):

    tp_connection_prop = mdl.prop(mask_handle, "tp_connection")
    rneut_prop = mdl.prop(mask_handle, "Rneut")
    xneut_prop = mdl.prop(mask_handle, "Xneut")
    old_ground_connected = mdl.get_property_value(
        mdl.prop(mask_handle, "ground_connected")
    )
    if old_ground_connected in ("True", True):
        mdl.set_property_value(tp_connection_prop, "Y - Grounded")
        if mdl.get_property_value(rneut_prop) == "inf":
            mdl.set_property_value(rneut_prop, "0")
        if mdl.get_property_value(xneut_prop) == "inf":
            mdl.set_property_value(xneut_prop, "0")
