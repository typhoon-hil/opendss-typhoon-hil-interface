import pathlib
import json
import ast
import pandas as pd
from typhoon.api.schematic_editor.const import ITEM_JUNCTION, ITEM_CONNECTION, ITEM_PORT, ITEM_COMPONENT

got_loadshape_points_list = []



def tp_connection_dynamics(mdl, container_handle):
    mdl.info("phase_value_edited ini")
    load_model_prop = mdl.prop(container_handle, "load_model")
    load_model = mdl.get_property_disp_value(load_model_prop)

    phases_prop = mdl.prop(container_handle, "phases")
    phases = mdl.get_property_disp_value(phases_prop)

    tp_connection_prop = mdl.prop(container_handle, "tp_connection")
    #tp_connection = mdl.get_property_value(tp_connection_prop)

    mdl.enable_property(mdl.prop(container_handle, "tp_connection"))

    if phases == "3":

        if load_model == "Constant Impedance":
            mdl.set_property_combo_values(tp_connection_prop, {"Y - Grounded", "Y", "Δ"})
            mdl.set_property_disp_value(tp_connection_prop, "Y - Grounded")
        else:
            mdl.set_property_combo_values(tp_connection_prop, {"Y - Grounded", "Y"})
            mdl.enable_property(mdl.prop(container_handle, "zero_seq_remove"))

    else:
        mdl.set_property_combo_values(tp_connection_prop, {"Y - Grounded", "Y"})
        mdl.set_property_disp_value(tp_connection_prop, "Y - Grounded")
        mdl.set_property_value(mdl.prop(container_handle, 'zero_seq_remove'), False)
        mdl.disable_property(mdl.prop(container_handle, "zero_seq_remove"))

    new_connection = mdl.get_property_value(tp_connection_prop)
    tp_connection_edited(mdl, container_handle, new_connection)

    mdl.info("phase_value_edited end")

    mdl.info(f'The new phases value is: {phases}')


def zip_change_fnc(mdl, container_handle, new_value):
    # zip_internal_n_prop = mdl.prop(container_handle, "zip_internal_n")
    # zip_internal_n = mdl.get_property_value(zip_internal_n_prop)
    zip_vector_prop = mdl.prop(container_handle, "zip_vector")
    zip_vector = mdl.get_property_disp_value(zip_vector_prop)

    # zip_internal_n_q_prop = mdl.prop(container_handle, "zip_internal_n_Q")
    # zip_internal_n_q = mdl.get_property_value(zip_internal_n_q_prop)
    zip_vector_q_prop = mdl.prop(container_handle, "zip_vector_Q")
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
            zip_norm = [value / zip_total for value in [zip_list[0], zip_list[1], zip_list[2]]]
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
            zip_norm_q = [value / zip_total_q for value in [zip_list_q[0], zip_list_q[1], zip_list_q[2]]]
    elif zip_len_q == 2:
        zip_total_q = zip_list_q[0] + zip_list_q[1]
        if not zip_total_q == 0:
            zip_norm_q = [value / zip_total_q for value in [zip_list_q[0], zip_list_q[1], 0]]
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

    zipv_dss = [zip_norm[0], zip_norm[1], zip_norm[2], zip_norm_q[0], zip_norm_q[1], zip_norm_q[2], 0]

    mdl.set_property_disp_value(mdl.prop(container_handle, 'zip_internal_n'), str(zip_norm))
    mdl.set_property_value(mdl.prop(container_handle, 'zip_internal_n'), str(zip_norm))
    mdl.set_property_disp_value(mdl.prop(container_handle, 'zip_internal'), str(zip_norm))
    mdl.set_property_value(mdl.prop(container_handle, 'zip_internal'), str(zip_norm))

    mdl.set_property_disp_value(mdl.prop(container_handle, 'zip_internal_n_Q'), str(zip_norm_q))
    mdl.set_property_value(mdl.prop(container_handle, 'zip_internal_n_Q'), str(zip_norm_q))
    mdl.set_property_disp_value(mdl.prop(container_handle, 'zip_internal_Q'), str(zip_norm_q))
    mdl.set_property_value(mdl.prop(container_handle, 'zip_internal_Q'), str(zip_norm_q))

    mdl.set_property_disp_value(mdl.prop(container_handle, 'ZIPV'), str(zipv_dss))
    mdl.set_property_value(mdl.prop(container_handle, 'ZIPV'), str(zipv_dss))


def load_model_value_edited_fnc(mdl, container_handle, new_value):
    tp_connection_prop = mdl.prop(container_handle, "tp_connection")
    tp_connection = mdl.get_property_value(tp_connection_prop)

    zip_vector_prop = mdl.prop(container_handle, "zip_vector")
    # zip_vector = mdl.get_property_disp_value(zip_vector_prop)
    zip_vector_q_prop = mdl.prop(container_handle, "zip_vector_Q")
    # zip_vector_q = mdl.get_property_disp_value(zip_vector_q_prop)

    zip_internal_n_prop = mdl.prop(container_handle, "zip_internal_n")
    zip_internal_n = mdl.get_property_disp_value(zip_internal_n_prop)
    zip_internal_n_q_prop = mdl.prop(container_handle, "zip_internal_n_Q")
    zip_internal_n_q = mdl.get_property_disp_value(zip_internal_n_q_prop)

    phases_prop = mdl.prop(container_handle, "phases")
    phases = mdl.get_property_value(phases_prop)

    if new_value == "Constant Impedance":
        mdl.hide_property(zip_vector_prop)
        mdl.hide_property(zip_vector_q_prop)
        mdl.set_property_value(mdl.prop(container_handle, 'Pow_ref_s'), "Fixed")
        mdl.disable_property(mdl.prop(container_handle, "Pow_ref_s"))
        mdl.disable_property(mdl.prop(container_handle, "execution_rate"))
        mdl.disable_property(mdl.prop(container_handle, "Tfast"))
        mdl.disable_property(mdl.prop(container_handle, "CPL_LMT"))
        mdl.disable_property(mdl.prop(container_handle, "v_min_max"))
        mdl.disable_property(mdl.prop(container_handle, "rate_lmt"))
        mdl.disable_property(mdl.prop(container_handle, "q_gain_k"))
        mdl.disable_property(mdl.prop(container_handle, "r_gain_k"))
        mdl.enable_property(mdl.prop(container_handle, "tp_connection"))
        tp_connection_edited(mdl, container_handle, "Y - Grounded")
        '''
        if phases == "1":
            mdl.disable_property(mdl.prop(container_handle, "tp_connection"))
        else:
            mdl.enable_property(mdl.prop(container_handle, "tp_connection"))
        '''
        #if conn_type == "Y":
        #    mdl.enable_property(mdl.prop(container_handle, "ground_connected"))
    else:
        if new_value == "Constant Power":
            mdl.hide_property(zip_vector_prop)
            mdl.hide_property(zip_vector_q_prop)
            mdl.set_property_value(mdl.prop(container_handle, 'zip_internal'), "[0,0,1]")
            mdl.set_property_value(mdl.prop(container_handle, 'zip_internal_Q'), "[0,0,1]")
        elif new_value == "Constant Z,I,P":
            mdl.show_property(zip_vector_prop)
            mdl.show_property(zip_vector_q_prop)
            mdl.set_property_value(mdl.prop(container_handle, 'zip_internal'), zip_internal_n)
            mdl.set_property_value(mdl.prop(container_handle, 'zip_internal_Q'), zip_internal_n_q)
        mdl.enable_property(mdl.prop(container_handle, "Pow_ref_s"))
        mdl.enable_property(mdl.prop(container_handle, "execution_rate"))
        mdl.enable_property(mdl.prop(container_handle, "Tfast"))
        mdl.enable_property(mdl.prop(container_handle, "CPL_LMT"))
        mdl.enable_property(mdl.prop(container_handle, "v_min_max"))
        mdl.enable_property(mdl.prop(container_handle, "rate_lmt"))
        mdl.enable_property(mdl.prop(container_handle, "q_gain_k"))
        mdl.enable_property(mdl.prop(container_handle, "r_gain_k"))
        mdl.set_property_disp_value(mdl.prop(container_handle, "tp_connection"), "Y - Grounded")
        #tp_connection_edited(mdl, container_handle, "Y - Grounded")
        mdl.disable_property(mdl.prop(container_handle, "tp_connection"))
        #mdl.enable_property(mdl.prop(container_handle, "ground_connected"))

    mdl.info("End of function load_model_value_edited_fnc()")


def load_loadshape(mdl, container_handle):
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

    import tse_to_opendss.thcc_libs.gui_scripts.load_object as load_obj
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
    loadshape_name = mdl.get_property_value(loadshape_name_prop)
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
        loadshape_prop_time = mdl.prop(container_handle, "T_Ts")
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
                mdl.set_property_disp_value(loadshape_prop_time, str(hour))
        else:
            time_range_str = f"[{', '.join(str(interval * n) for n in range(1, len(loadshape) + 1))}]"
            mdl.set_property_disp_value(loadshape_prop_time, time_range_str)
        mdl.set_property_disp_value(loadshape_from_file_path_prop, str(loadshape_from_file_path))
        mdl.set_property_disp_value(loadshape_from_file_header_prop, str(loadshape_from_file_header))
        mdl.set_property_disp_value(loadshape_from_file_column_prop, str(loadshape_from_file_column))


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
                mdl.set_property_value(frequency_prop, mdl.get_ns_var("simdss_basefreq"))
            else:
                mdl.set_property_value(global_frequency_prop, False)
        toggle_frequency_prop(mdl, mask_handle, init)

'''
def define_icon(mdl, mask_handle):
    phases = mdl.get_property_value(mdl.prop(mask_handle, "phases"))
    grounded = mdl.get_property_value(mdl.prop(mask_handle, "ground_connected"))
    conn_type = mdl.get_property_value(mdl.prop(mask_handle, "conn_type"))
    if int(phases) == 1:
        if grounded:
            mdl.set_component_icon_image(mask_handle, 'images/load_1ph_gnd.svg')
        else:
            mdl.set_component_icon_image(mask_handle, 'images/load_1ph.svg')
    else:
        if grounded:
            mdl.set_component_icon_image(mask_handle, 'images/load_3Y_gnd.svg')
        else:
            if conn_type == 'Δ':
                mdl.set_component_icon_image(mask_handle, 'images/load_3D.svg')
            else:
                mdl.set_component_icon_image(mask_handle, 'images/load_3Y.svg')
'''

def define_icon(mdl, mask_handle):
    phases = mdl.get_property_value(mdl.prop(mask_handle, "phases"))
    tp_connection = mdl.get_property_value(mdl.prop(mask_handle, "tp_connection"))

    if tp_connection == "Y - Grounded":
        grounded = True
    else:
        grounded = False

    if int(phases) == 1:
        if grounded:
            mdl.set_component_icon_image(mask_handle, 'images/load_1ph_gnd.svg')
        else:
            mdl.set_component_icon_image(mask_handle, 'images/load_1ph.svg')
    else:
        if grounded:
            mdl.set_component_icon_image(mask_handle, 'images/load_3Y_gnd.svg')
        else:
            if tp_connection == 'Δ':
                mdl.set_component_icon_image(mask_handle, 'images/load_3D.svg')
            else:
                mdl.set_component_icon_image(mask_handle, 'images/load_3Y.svg')


def port_dynamics(mdl, mask_handle):
    mdl.info("port_dynamics ini")
    comp_handle = mdl.get_parent(mask_handle)
    # deleted_ports = []
    created_ports = {}

    tp_connection_prop = mdl.prop(mask_handle, "tp_connection")
    tp_connection = mdl.get_property_disp_value(tp_connection_prop)

    load_model_prop = mdl.prop(mask_handle, "load_model")
    load_model = mdl.get_property_disp_value(load_model_prop)

    #ground_connected_prop = mdl.prop(mask_handle, "ground_connected")
    #ground_connected = mdl.get_property_value(ground_connected_prop)
    if tp_connection == "Y - Grounded":
        gnd_check = True
    else:
        gnd_check = False

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

        if p_ext:
            mdl.set_port_properties(p_ext, terminal_position=(50, -15))
            created_ports.update({"P_ext": p_ext})
        if q_ext:
            mdl.set_port_properties(q_ext, terminal_position=(50, 15))
            created_ports.update({"Q_ext": q_ext})

        if not port_a:
            port_a = mdl.create_port(parent=comp_handle, name="A1", direction="out", kind="pe",
                                     terminal_position=(-30, -32),
                                     position=(7802, 7862), rotation="right")
            created_ports.update({"portA": port_a})
        else:
            mdl.set_port_properties(port_a, terminal_position=(-30, -32))
            created_ports.update({"portA": port_a})
        if not port_b:
            port_b = mdl.create_port(parent=comp_handle, name="B1", direction="out", kind="pe",
                                     terminal_position=(0.0, -32),
                                     position=(7919, 7862), rotation="right")
            created_ports.update({"portB": port_b})
        else:
            mdl.set_port_properties(port_b, terminal_position=(0.0, -32))
            created_ports.update({"portB": port_b})
        if not port_c:
            port_c = mdl.create_port(parent=comp_handle, name="C1", direction="out", kind="pe",
                                     terminal_position=(30, -32),
                                     position=(8055, 7862), rotation="right")
            created_ports.update({"portC": port_c})
        else:
            created_ports.update({"portC": port_c})

        if tp_connection == "Y" or tp_connection == "Y - Grounded":
            port_n = mdl.get_item("N1", parent=comp_handle, item_type="port")
            if not port_n:
                port_n = mdl.create_port(parent=comp_handle, name="N1", direction="out", kind="pe",
                                         terminal_position=(0, 30),
                                         position=(7921, 8384), rotation="left")
            created_ports.update({"portN": port_n})


    elif phases == "1":
        port_a = mdl.get_item("A1", parent=comp_handle, item_type="port")
        port_b = mdl.get_item("B1", parent=comp_handle, item_type="port")
        port_c = mdl.get_item("C1", parent=comp_handle, item_type="port")

        p_ext = mdl.get_item("P", parent=comp_handle, item_type="port")
        q_ext = mdl.get_item("Q", parent=comp_handle, item_type="port")
        if p_ext:
            mdl.set_port_properties(p_ext, terminal_position=(25, -15))
            created_ports.update({"P_ext": p_ext})
        if q_ext:
            mdl.set_port_properties(q_ext, terminal_position=(25, 15))
            created_ports.update({"Q_ext": q_ext})

        if not port_a:
            port_a = mdl.create_port(parent=comp_handle, name="A1", direction="out", kind="pe",
                                     terminal_position=(0, -32),
                                     position=(7802, 7862), rotation="right")
            created_ports.update({"portA": port_a})
        else:
            mdl.set_port_properties(port_a, terminal_position=(0, -32))
            created_ports.update({"portA": port_a})

        if not port_b:
            port_b = mdl.create_port(parent=comp_handle, name="B1", direction="out", kind="pe",
                                     terminal_position=(0, 15),
                                     position=(7919, 7862), rotation="right")
            created_ports.update({"portB": port_b})
        else:
            mdl.set_port_properties(port_b, terminal_position=(0, 15))
            created_ports.update({"portB": port_b})

        # In the single-phase system, we don't need the Neutral output
        port_n = mdl.get_item("N1", parent=comp_handle, item_type="port")
        if port_n:
            mdl.delete_item(port_n)
            created_ports.pop("portN", None)

        if port_c:
            mdl.delete_item(port_c)
            created_ports.pop("portC", None)



    if tp_connection == "Δ" and load_model == "Constant Impedance":
        # https://youtu.be/gqQertPg9wI?list=RDMM
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
                p_term_position = (25, -15)
                q_term_position = (25, 15)
            else:
                p_term_position = (50, -15)
                q_term_position = (50, 15)

            p_ext = mdl.get_item("P", parent=comp_handle, item_type="port")
            if not p_ext:
                p_ext = mdl.create_port(parent=comp_handle, name="P", direction="in", kind="sp",
                                        terminal_position=p_term_position,
                                        position=(7680, 8175))
            created_ports.update({"P_ext": p_ext})

            q_ext = mdl.get_item("Q", parent=comp_handle, item_type="port")
            if not q_ext:
                q_ext = mdl.create_port(parent=comp_handle, name="Q", direction="in", kind="sp",
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
                term_position = (25, 0)
            else:
                term_position = (50, 0)

            t_ext = mdl.get_item("T", parent=comp_handle, item_type="port")
            if not t_ext:
                t_ext = mdl.create_port(parent=comp_handle, name="T", direction="in", kind="sp",
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


    mdl.info("Line 668, end of port_dynamics() function")

    return created_ports



def create_tags_and_connections_to_ports(mdl, mask_handle, created_ports):
    comp_handle = mdl.get_parent(mask_handle)

    phases_prop = mdl.prop(mask_handle, "phases")
    phases = mdl.get_property_disp_value(phases_prop)

    mdl.info("create tags ... ")

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
            tag1 = mdl.create_tag(f"{phase}1", name=f"Tag{phase}1", parent=comp_handle, scope="local", kind="pe",
                                  rotation=tags_dict[f"Tag{phase}1"]["rotation"],
                                  position=tags_dict[f"Tag{phase}1"]["position"])

            mdl.create_connection(tag1, created_ports.get(f"port{phase}"))

            tag2 = mdl.get_item(f"Tag{phase}2", parent=comp_handle, item_type="tag")
            if tag2:
                mdl.delete_item(tag2)
            mdl.create_tag(f"{phase}1", name=f"Tag{phase}2", parent=comp_handle, scope="local", kind="pe",
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
                tag1 = mdl.create_tag(f"{phase}1", name=f"Tag{phase}1", parent=comp_handle, scope="local", kind="pe",
                                      rotation=tags_dict[f"Tag{phase}1"]["rotation"],
                                      position=tags_dict[f"Tag{phase}1"]["position"])
                mdl.create_connection(tag1, created_ports.get(f"port{phase}"))

                mdl.create_tag(f"{phase}1", name=f"Tag{phase}2", parent=comp_handle, scope="local", kind="pe",
                               rotation=tags_dict[f"Tag{phase}2"]["rotation"],
                               position=tags_dict[f"Tag{phase}2"]["position"])

            if phase == "B":
                tag3 = mdl.get_item(f"Tag{phase}3", parent=comp_handle, item_type="tag")
                if tag3:
                    mdl.delete_item(tag3)

                tag1 = mdl.create_tag(f"{phase}1", name=f"Tag{phase}1", parent=comp_handle, scope="local",
                                      kind="pe",
                                      rotation=tags_dict[f"Tag{phase}1"]["rotation"],
                                      position=tags_dict[f"Tag{phase}1"]["position"])
                mdl.create_connection(tag1, created_ports.get(f"port{phase}"))

                tag3 = mdl.create_tag(f"{phase}1", name=f"Tag{phase}3", parent=comp_handle,
                                      scope="local", kind="pe",
                                      rotation=tags_dict[f"Tag{phase}3"]["rotation"],
                                      position=tags_dict[f"Tag{phase}3"]["position"])

                jun_n = mdl.get_item("JN", parent=comp_handle, item_type="junction")
                mdl.info(f"L 764: jun_n: {jun_n}============")
                if jun_n:
                    mdl.create_connection(tag3, jun_n)


def connections_dynamics(mdl, mask_handle, created_ports):
    #create_tags_and_connections_to_ports(mdl, mask_handle, created_ports)

    comp_handle = mdl.get_parent(mask_handle)

    tp_connection_prop = mdl.prop(comp_handle, "tp_connection")
    tp_connection = mdl.get_property_disp_value(tp_connection_prop)

    load_model_prop = mdl.prop(mask_handle, "load_model")
    load_model = mdl.get_property_disp_value(load_model_prop)

    phases_prop = mdl.prop(mask_handle, "phases")
    phases = mdl.get_property_disp_value(phases_prop)

    if load_model == "Constant Impedance":
        load = mdl.get_item("CIL", parent=comp_handle, item_type="component")
        '''
        if not load:
            set_load_model(mdl, mask_handle, load_model)
            load = mdl.get_item("CIL", parent=comp_handle, item_type="component")
            mdl.info("Line 704 creating CIL......")
        '''
    elif load_model == "Constant Power":
        load = mdl.get_item("CPL", parent=comp_handle, item_type="component")
        '''
        if not load:
            set_load_model(mdl, mask_handle, load_model)
            load = mdl.get_item("CPL", parent=comp_handle, item_type="component")
            mdl.info("Line 711 creating CPL......")
        '''
    elif load_model == "Constant Z,I,P":
        load = mdl.get_item("CPL", parent=comp_handle, item_type="component")
        '''
        if not load:
            set_load_model(mdl, mask_handle, load_model)
            load = mdl.get_item("CPL", parent=comp_handle, item_type="component")
            mdl.info("Line 718 creating CPL for Constant Z,I,P......")
        '''

    mdl.info(f"***************** Load type: {load}")



    # This loop connects the Load tags to the CIL terminals
    if phases == "1":
        phase_list = ["A"]
    else:
        phase_list = ["A", "B", "C"]

    for phase in phase_list:
        tag = mdl.get_item(f"Tag{phase}2", parent=comp_handle, item_type="tag")
        mdl.info(f"tag list: {tag} ========")
        mdl.info(f"load: {load} =======")
        conn_tmp = mdl.find_connections(tag, mdl.term(load, f"{phase}1"))
        mdl.info(f"conn_tmp = {conn_tmp} =======")
        if len(conn_tmp) == 0:
            mdl.create_connection(tag, mdl.term(load, f"{phase}1"))

    #conn_n2port = mdl.get_item("Conn_N", parent=comp_handle, item_type=ITEM_CONNECTION)
    jun_n = mdl.get_item("JN", parent=comp_handle, item_type="junction")
    port_n = mdl.get_item("N1", parent=comp_handle, item_type="port")

    mdl.info("Line 820 ----------")

    mdl.info(f"Line 822: tp_connection: {tp_connection}")


    if tp_connection == "Y":
        #mdl.set_property_value(mdl.prop(cil1, "conn_type"), "Y")
        #mdl.set_property_value(mdl.prop(cil1, "ground_connected"), False)

        if not jun_n:
            jun_n = mdl.create_junction(name='JN', parent=comp_handle, kind='pe', position=(7921, 8326))

        conn_n_load = mdl.get_item("Conn_AN", parent=comp_handle, item_type=ITEM_CONNECTION)
        if not conn_n_load:
            mdl.create_connection(mdl.term(load, "N"), jun_n, name="Conn_AN")

        if phases == "3":
            conn_n2port = mdl.get_item("Conn_N", parent=comp_handle, item_type=ITEM_CONNECTION)
            if not conn_n2port:
                mdl.create_connection(jun_n, port_n, name="Conn_N")


    elif tp_connection == "Y - Grounded":
        #mdl.set_property_value(mdl.prop(load, "conn_type"), "Y")
        #mdl.set_property_value(mdl.prop(load, "ground_connected"), False)   # GND is managed on comp_load
        #conn_n_cil = mdl.get_item("Conn_AN", parent=comp_handle, item_type=ITEM_CONNECTION)

        if not jun_n:
            jun_n = mdl.create_junction(name='JN', parent=comp_handle, kind='pe',
                                        position=(7921, 8326))

        conn_n_load = mdl.get_item("Conn_AN", parent=comp_handle, item_type=ITEM_CONNECTION)
        if not conn_n_load:
            mdl.create_connection(mdl.term(load, "N"), jun_n, name="Conn_AN")

        if phases == "3":
            conn_n2port = mdl.get_item("Conn_N", parent=comp_handle, item_type=ITEM_CONNECTION)
            if not conn_n2port:
                mdl.create_connection(jun_n, port_n, name="Conn_N")

    elif tp_connection == "Δ":
        #mdl.set_property_value(mdl.prop(load, "conn_type"), "Δ")
        if jun_n:
            mdl.delete_item(jun_n)


'''*******************************************************************
This function manages the mask properties "on edit" 
If tp_connection == "Y - Grounded", the fields for Rneut and Xneut 
will be available.
https://youtu.be/Al3vXVe9WVU
*******************************************************************'''
def tp_connection_edited(mdl, mask_handle, new_value):
    rneut_prop = mdl.prop(mask_handle, "Rneut")
    xneut_prop = mdl.prop(mask_handle, "Xneut")

    if new_value == "Y - Grounded":
        # Enable user input fields for N to Gnd impedance
        mdl.enable_property(mdl.prop(mask_handle, "Rneut"))
        mdl.enable_property(mdl.prop(mask_handle, "Xneut"))
        # We don't want to modify Rneut and Xneut values
        # on the 'on change' event. We put zeros only when
        # the user commuted from "Y" or "Δ" to "Y - Grounded"
        if mdl.get_property_disp_value(rneut_prop) == "'inf'":
            mdl.set_property_value(rneut_prop, "0.0")
        if mdl.get_property_disp_value(xneut_prop) == "'inf'":
            mdl.set_property_value(xneut_prop, "0.0")
    else:
        # Disable user input fields for N to Gnd impedance
        # show 'inf' because they are disconnected
        mdl.set_property_disp_value(rneut_prop, "'inf'")
        mdl.set_property_disp_value(xneut_prop, "'inf'")
        mdl.disable_property(mdl.prop(mask_handle, "Rneut"))
        mdl.disable_property(mdl.prop(mask_handle, "Xneut"))



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

    mdl.info(f'gnd dyn ini phases: {phases}')


    if phases == "3":
        phase_list = ["A", "B", "C"]
    else:
        phase_list = ["A"]

    if load_model == "Constant Impedance":
        load_comp = mdl.get_item("CIL", parent=comp_handle, item_type="component")
    else:
        load_comp = mdl.get_item("CPL", parent=comp_handle, item_type="component")

    mdl.info(f"Line 855 load_comp is:     {load_comp}-----------")


    for phase in phase_list:
        tag = mdl.get_item(f"Tag{phase}2", parent=comp_handle, item_type="tag")
        if len(mdl.find_connections(tag, mdl.term(load_comp, f"{phase}1"))) == 0:
            mdl.create_connection(tag, mdl.term(load_comp, f"{phase}1"))


    gnd1 = mdl.get_item("gndc", parent=comp_handle, item_type="component")
    jun_n = mdl.get_item("JN", parent=comp_handle, item_type="junction")
    gnd_z = mdl.get_item("Gnd Z", parent=comp_handle, item_type=ITEM_COMPONENT)


    # Here we have the grounding through Rneut and Xneut AND the neutral terminal on Y configurations
    if tp_connection == "Y - Grounded":
        # https://www.youtube.com/playlist?list=PLtPtQsu5cwyq13GbLu6TqxIQUtcjjCbRt

        if not gnd1:
            #gnd1 = mdl.create_component("src_ground", parent=comp_handle, name="gndc", position=(8000, 8640))
            gnd1 = mdl.create_component("src_ground", parent=comp_handle, name="gndc", position=(8030, 8480))

        if not jun_n:
            jun_n = mdl.create_junction(name="JN", parent=comp_handle, position=(7920, 8328), kind="pe")


        if not gnd_z:
            gnd_z = mdl.create_component("OpenDSS/Ground Impedance", parent=comp_handle, name="Gnd Z",
                                         position=(8030, 8385), rotation="up")

        conn_gnd_z2gnd = mdl.find_connections(mdl.term(gnd_z, "G"), mdl.term(gnd1, "node"))
        if not conn_gnd_z2gnd:
            mdl.create_connection(mdl.term(gnd_z, "G"),  mdl.term(gnd1, "node"), "Conn_z2gnd")

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
    mdl.info("load dynamics() init")
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

    mdl.info("connections phase dynamics end")

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

            ts_mdl = mdl.get_item("TS_module", parent=comp_handle, item_type="component")
            if ts_mdl:
                set_timeseries_switch(mdl, mask_handle, False)

            mdl.set_property_value(mdl.prop(cpl1, "kP_inp"), "Fixed")
            mdl.set_property_value(mdl.prop(cpl1, "kQ_inp"), "Fixed")

        elif pow_ref_s == "External input":
            cpl1 = mdl.get_item("CPL", parent=comp_handle, item_type="component")
            if not cpl1:
                set_load_model(mdl, mask_handle, "Constant Power")
                cpl1 = mdl.get_item("CPL", parent=comp_handle, item_type="component")

            ts_mdl = mdl.get_item("TS_module", parent=comp_handle, item_type="component")
            if ts_mdl:
                set_timeseries_switch(mdl, mask_handle, False)

            mdl.set_property_value(mdl.prop(cpl1, "kP_inp"), "Variable input")
            mdl.set_property_value(mdl.prop(cpl1, "kQ_inp"), "Variable input")

            conn_p_int = mdl.get_item("connP", parent=comp_handle, item_type="connection")
            conn_q_int = mdl.get_item("connQ", parent=comp_handle, item_type="connection")

            conn_ts_p_int = mdl.get_item("ConnTsP", parent=comp_handle, item_type="connection")
            conn_ts_q_int = mdl.get_item("ConnTsQ", parent=comp_handle, item_type="connection")

            if conn_ts_p_int:
                mdl.delete_item(conn_ts_p_int)
            if conn_ts_q_int:
                mdl.delete_item(conn_ts_q_int)

            if conn_p_int:
                mdl.delete_item(conn_p_int)
            if conn_q_int:
                mdl.delete_item(conn_q_int)

            mdl.create_connection(mdl.term(cpl1, "P_set"), created_ports.get("P_ext"), "ConnP")
            mdl.create_connection(mdl.term(cpl1, "Q_set"), created_ports.get("Q_ext"), "ConnQ")

        else:
            cpl1 = mdl.get_item("CPL", parent=comp_handle, item_type="component")
            if not cpl1:
                set_load_model(mdl, mask_handle, "Constant Power")
                cpl1 = mdl.get_item("CPL", parent=comp_handle, item_type="component")
            mdl.set_property_value(mdl.prop(cpl1, "kP_inp"), "Variable input")
            mdl.set_property_value(mdl.prop(cpl1, "kQ_inp"), "Variable input")
            ts_mdl = mdl.get_item("TS_module", parent=comp_handle, item_type="component")
            if not ts_mdl:
                set_timeseries_switch(mdl, mask_handle, True)
                ts_mdl = mdl.get_item("TS_module", parent=comp_handle, item_type="component")
            conn_p_int = mdl.get_item("connP", parent=comp_handle, item_type="connection")
            conn_q_int = mdl.get_item("connQ", parent=comp_handle, item_type="connection")

            if conn_p_int:
                mdl.delete_item(conn_p_int)
            if conn_q_int:
                mdl.delete_item(conn_q_int)
            mdl.set_property_value(mdl.prop(ts_mdl, "P_mode"), "Manual input")
            conn_ts_p_int = mdl.get_item("ConnTsP", parent=comp_handle, item_type="connection")
            conn_ts_q_int = mdl.get_item("ConnTsQ", parent=comp_handle, item_type="connection")

            if not conn_ts_p_int:
                mdl.create_connection(mdl.term(cpl1, "P_set"), mdl.term(ts_mdl, "P"), "ConnTsP")
            if not conn_ts_q_int:
                mdl.create_connection(mdl.term(cpl1, "Q_set"), mdl.term(ts_mdl, "Q"), "ConnTsQ")
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
            ts_mdl = mdl.get_item("TS_module", parent=comp_handle, item_type="component")
            conn_ts_in = mdl.get_item("ConnTs", parent=comp_handle, item_type="connection")

            mdl.set_property_value(mdl.prop(ts_mdl, "P_mode"), "Manual input")
            if not conn_ts_in:
                mdl.create_connection(mdl.term(ts_mdl, "T"), created_ports.get("T_ext"), "ConnTs")


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
                component_list.extend(get_all_circuit_loads(mdl, mdl.get_mask(comp), parent_comp=comp))
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
        current_points = ast.literal_eval(mdl.get_property_value(mdl.prop(mask_handle, "loadshape")))
    except:
        current_points = []
    useactual = mdl.get_property_value(mdl.prop(mask_handle, "useactual"))
    interval = mdl.get_property_value(mdl.prop(mask_handle, "loadshape_int"))

    if not reload_dict:
        loadshape_name = mdl.get_property_value(mdl.prop(mask_handle, "loadshape_name"))
        loadshape_from_file = mdl.get_property_value(mdl.prop(mask_handle, "loadshape_from_file")) == "True"
        loadshape_from_file_header = mdl.get_property_value(
            mdl.prop(mask_handle, "loadshape_from_file_header")) == "True"
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

        signal_switch = mdl.get_item("Signal switch", parent=comp_handle, item_type="component")
        if not signal_switch:
            signal_switch = mdl.create_component("Signal switch", parent=comp_handle,
                                                 name="Signal switch", position=(7624, 8384))
            mdl.set_property_value(mdl.prop(signal_switch, "criterion"), "ctrl >= threshold")
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

        signal_switch = mdl.get_item("Signal switch", parent=comp_handle, item_type="component")
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


def set_load_model(mdl, mask_handle, new_value):

    tp_connection = mdl.get_property_disp_value(mdl.prop(mask_handle, "tp_connection"))
    comp_handle = mdl.get_parent(mask_handle)

    phss = mdl.get_property_disp_value(mdl.prop(mask_handle, "phases"))
    t_slow = mdl.get_property_value(mdl.prop(mask_handle, "execution_rate"))
    t_fast = mdl.get_property_value(mdl.prop(mask_handle, "Tfast"))
    pf_mode = mdl.get_property_value(mdl.prop(mask_handle, "pf_mode_3ph"))
    load_model = mdl.get_property_disp_value(mdl.prop(mask_handle, "load_model"))

    mdl.info(f"Line 1331 000 - the new_value is: {load_model}...............")

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
            mdl.info("Line 1386: CIL set to YPISILONE")
        else:
            mdl.set_property_value(mdl.prop(cil1, "conn_type"), "Δ")
            mdl.set_property_value(mdl.prop(cil1, "ground_connected"), False)
            mdl.info("Line 1389: CIL set to DELTA ............")

        if phss == "3":
            mdl.set_property_value(mdl.prop(cil1, "phases"), "3")
            mdl.info("Line 1338 set cil to 3 phases .........")
        else:
            mdl.set_property_value(mdl.prop(cil1, "phases"), "1")
            mdl.info("Line 1341 set cil to 1 phases .........")
        '''
        tag_a = mdl.get_item("TagA2", parent=comp_handle, item_type="tag")
        if len(mdl.find_connections(mdl.term(cil1, "A1"), tag_a)) == 0:
            mdl.create_connection(mdl.term(cil1, "A1"), tag_a)

        jun_n = mdl.get_item("JN", parent=comp_handle, item_type=ITEM_JUNCTION)
        conn_n0_cil = mdl.get_item("Conn_AN", parent=comp_handle, item_type=ITEM_CONNECTION)
        if not conn_n0_cil:
            if tp_connection == "Y - Grounded" or tp_connection == "Y":
                mdl.create_connection(mdl.term(cil1, "N"), jun_n, name="Conn_AN")

        if phss == "3":
            tag_b = mdl.get_item("TagB2", parent=comp_handle, item_type="tag")
            if len(mdl.find_connections(mdl.term(cil1, "B1"), tag_b)) == 0:
                mdl.create_connection(mdl.term(cil1, "B1"), tag_b)

            tag_c = mdl.get_item("TagC2", parent=comp_handle, item_type="tag")
            if len(mdl.find_connections(mdl.term(cil1, "C1"), tag_c)) == 0:
                mdl.create_connection(mdl.term(cil1, "C1"), tag_c)
        '''

    else:
        cil1 = mdl.get_item("CIL", parent=comp_handle, item_type=ITEM_COMPONENT)
        if cil1:
            mdl.delete_item(cil1)

        cpl1 = mdl.get_item("CPL", parent=comp_handle, item_type=ITEM_COMPONENT)
        if not cpl1:
            cpl1 = mdl.create_component("OpenDSS/CPL", parent=comp_handle,
                                        name="CPL", position=(7920, 8208),
                                        rotation="right", flip="flip_horizontal")

        if phss == "3":
            mdl.set_property_value(mdl.prop(cpl1, "phases"), "1")
            mdl.set_property_value(mdl.prop(cpl1, "phases"), "3")
        else:
            mdl.set_property_value(mdl.prop(cpl1, "phases"), "3")
            mdl.set_property_value(mdl.prop(cpl1, "phases"), "1")

        if t_slow == t_fast:
            mdl.set_property_value(mdl.prop(cpl1, "Fast_con"), "False")
        else:
            mdl.set_property_value(mdl.prop(cpl1, "Fast_con"), "True")

    mdl.info("Line 1396 ....")

    '''
        tag_a = mdl.get_item("TagA2", parent=comp_handle, item_type="tag")
        if len(mdl.find_connections(mdl.term(cpl1, "A1"), tag_a)) == 0:
            mdl.create_connection(mdl.term(cpl1, "A1"), tag_a)

        jun_n = mdl.get_item("JN", parent=comp_handle, item_type=ITEM_JUNCTION)
        conn_n0_cpl = mdl.get_item("Conn_AN_CPL", parent=comp_handle, item_type=ITEM_CONNECTION)
        #if not conn_n0_cpl:
        #    mdl.create_connection(mdl.term(cpl1, "N"), jun_n, name="Conn_AN_CPL")

        if phss == "3":
            tag_b = mdl.get_item("TagB2", parent=comp_handle, item_type="tag")
            if len(mdl.find_connections(mdl.term(cpl1, "B1"), tag_b)) == 0:
                mdl.create_connection(mdl.term(cpl1, "B1"), tag_b)

            tag_c = mdl.get_item("TagC2", parent=comp_handle, item_type="tag")
            if len(mdl.find_connections(mdl.term(cpl1, "C1"), tag_c)) == 0:
                mdl.create_connection(mdl.term(cpl1, "C1"), tag_c)
    '''

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


def load_pre_compile_function(mdl, item_handle, prop_dict):
    """

    Args:
        mdl: schematic editor API handle
        item_handle: component's mask handle
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
        if prop_dict["ground_connected"]:
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

    mdl.set_property_value(mdl.prop(item_handle, "basefreq"), basefreq)
    mdl.set_property_value(mdl.prop(item_handle, "kVA"), kva)
    mdl.set_property_value(mdl.prop(item_handle, "Vn_3ph_CPL"), vn_3ph_cpl)
    mdl.set_property_value(mdl.prop(item_handle, "P_CPL"), p_cpl)
    mdl.set_property_value(mdl.prop(item_handle, "Q_CPL"), q_cpl)
    mdl.set_property_value(mdl.prop(item_handle, "conn"), conn)
    mdl.set_property_value(mdl.prop(item_handle, "pf"), pf)
    mdl.set_property_value(mdl.prop(item_handle, "pf_3ph_set"), pf_3ph_set)
    mdl.set_property_value(mdl.prop(item_handle, "kV"), kv)
    mdl.set_property_value(mdl.prop(item_handle, "Vminpu"), vminpu)
    mdl.set_property_value(mdl.prop(item_handle, "Vmaxpu"), vmaxpu)
    mdl.set_property_value(mdl.prop(item_handle, "model"), model)

    mdl.set_property_value(mdl.prop(item_handle, "dssT"), dsst)
    mdl.set_property_value(mdl.prop(item_handle, "S_Ts"), s_ts)
    mdl.set_property_value(mdl.prop(item_handle, "T_Ts_internal"), t_ts_internal)
    mdl.set_property_value(mdl.prop(item_handle, "Slen"), slen)
    mdl.set_property_value(mdl.prop(item_handle, "dssnpts"), dssnpts)
    mdl.set_property_value(mdl.prop(item_handle, "T_lim_low"), t_lim_low)
    mdl.set_property_value(mdl.prop(item_handle, "T_lim_high"), t_lim_high)
    mdl.set_property_value(mdl.prop(item_handle, "Ts_switch"), ts_switch)


def pf_mode_3ph_value_edited(mdl, container_handle, new_value):
    if new_value == "Unit":
        mdl.disable_property(mdl.prop(container_handle, "pf_3ph"))
    else:
        mdl.enable_property(mdl.prop(container_handle, "pf_3ph"))


def validate_execution_rate(mdl, container_handle):
    comp_handle = mdl.get_sub_level_handle(container_handle)
    tfst_mask = mdl.get_property_value(mdl.prop(container_handle, "Tfast"))
    ts_mask = mdl.get_property_value(mdl.prop(container_handle, "execution_rate"))
    cpl_comp = mdl.get_item("CPL", parent=comp_handle, item_type="component")

    if cpl_comp:
        if ts_mask == tfst_mask:
            mdl.set_property_value(mdl.prop(cpl_comp, "Fast_con"), "False")
        else:
            mdl.set_property_value(mdl.prop(cpl_comp, "Fast_con"), "True")


def t_mode_value_edited(mdl, container_handle, new_value):
    if new_value == "Time":
        mdl.enable_property(mdl.prop(container_handle, "T_Ts"))
    else:
        mdl.disable_property(mdl.prop(container_handle, "T_Ts"))


def s_ts_mode_value_edited(mdl, container_handle, new_value):
    if new_value == "Manual input":
        mdl.disable_property(mdl.prop(container_handle, "T_Ts_max"))
        mdl.disable_property(mdl.prop(container_handle, "del_Ts"))
        mdl.enable_property(mdl.prop(container_handle, "T_Ts"))
    else:
        mdl.enable_property(mdl.prop(container_handle, "T_Ts_max"))
        mdl.enable_property(mdl.prop(container_handle, "del_Ts"))
        mdl.disable_property(mdl.prop(container_handle, "T_Ts"))



